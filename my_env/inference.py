"""HTTP-based baseline inference runner for OpenEnv customer support.

This script intentionally avoids importing any `tasks.*` modules so it cannot
fail due to grader import mismatches during validation.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import requests


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
MODEL_NAME = os.getenv("MODEL_NAME", "rule_based_baseline")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

DEFAULT_MAX_STEPS = 6
TASKS = ("easy", "medium", "hard")


def _log(tag: str, message: str) -> None:
	"""Print standardized log messages."""
	print(f"[{tag}] {message}")


def _headers() -> Dict[str, str]:
	"""Build HTTP headers, optionally including bearer auth."""
	headers = {"Content-Type": "application/json"}
	if HF_TOKEN:
		headers["Authorization"] = f"Bearer {HF_TOKEN}"
	return headers


def _extract_state(payload: Any) -> Dict[str, Any]:
	"""Normalize API responses that may wrap state in different shapes."""
	if isinstance(payload, dict) and isinstance(payload.get("state"), dict):
		return payload["state"]
	if isinstance(payload, dict):
		return payload
	return {}


def _post_reset(issue_type: Optional[str] = None, timeout: int = 20) -> Dict[str, Any]:
	"""Call /reset endpoint with schema fallbacks for broad compatibility."""
	url = f"{API_BASE_URL}/reset"
	candidate_payloads: List[Any] = []
	if issue_type:
		candidate_payloads.append({"issue_type": issue_type})
		candidate_payloads.append(issue_type)
	candidate_payloads.append(None)

	last_error: Optional[Exception] = None
	for payload in candidate_payloads:
		try:
			if payload is None:
				response = requests.post(url, headers=_headers(), timeout=timeout)
			else:
				response = requests.post(url, headers=_headers(), data=json.dumps(payload), timeout=timeout)
			response.raise_for_status()
			return _extract_state(response.json())
		except Exception as exc:
			last_error = exc

	raise RuntimeError(f"reset_failed: {last_error}")


def _post_step(action: Dict[str, Any], timeout: int = 20) -> Tuple[Dict[str, Any], float, bool, Optional[str]]:
	"""Call /step endpoint and normalize response fields."""
	url = f"{API_BASE_URL}/step"
	response = requests.post(url, headers=_headers(), data=json.dumps({"action": action}), timeout=timeout)
	response.raise_for_status()

	payload = response.json()
	state = _extract_state(payload)
	reward_obj = payload.get("reward") if isinstance(payload, dict) else 0.0
	done = bool(payload.get("done", False)) if isinstance(payload, dict) else False
	error = payload.get("error") if isinstance(payload, dict) else None

	reward_value = 0.0
	if isinstance(reward_obj, dict):
		reward_value = float(reward_obj.get("value", 0.0) or 0.0)
	else:
		reward_value = float(reward_obj or 0.0)

	return state, reward_value, done, error


def _infer_issue_type(customer_query: str) -> str:
	"""Infer issue type from customer query text."""
	text = (customer_query or "").lower()
	if any(token in text for token in ("refund", "money back", "damaged", "broken", "return")):
		return "refund"
	if any(token in text for token in ("delivery", "delayed", "tracking", "shipment", "arrive")):
		return "delivery"
	return "payment"


def _response_for_issue(issue_type: str) -> str:
	"""Generate response label from issue type."""
	mapping = {
		"refund": "refund_policy",
		"delivery": "delivery_update",
		"payment": "payment_verification",
	}
	return mapping.get(issue_type, "payment_verification")


def _resolution_for_issue(issue_type: str) -> str:
	"""Generate resolution label from issue type."""
	mapping = {
		"refund": "refund_processed",
		"delivery": "delivery_escalated",
		"payment": "payment_reconciled",
	}
	return mapping.get(issue_type, "payment_reconciled")


def _choose_action(state: Dict[str, Any], remembered_issue: Optional[str]) -> Tuple[Dict[str, str], Optional[str]]:
	"""Choose the next action from the environment phase."""
	phase = str(state.get("phase", "")).strip().lower()
	query = str(state.get("customer_query", ""))
	issue_type = remembered_issue or _infer_issue_type(query)

	if phase == "classify_issue":
		issue_type = _infer_issue_type(query)
		return {"issue_type": issue_type}, issue_type
	if phase == "generate_response":
		return {"response": _response_for_issue(issue_type)}, issue_type
	if phase == "resolve_issue":
		return {"resolution": _resolution_for_issue(issue_type)}, issue_type

	# Fallback to a safe classification action if phase is unknown.
	return {"issue_type": issue_type}, issue_type


def run_task(task_name: str, max_steps: int = DEFAULT_MAX_STEPS) -> bool:
	"""Execute one task episode against the HTTP API."""
	_log("START", f"task={task_name} base_url={API_BASE_URL} model={MODEL_NAME}")

	rewards: List[float] = []
	remembered_issue: Optional[str] = None

	try:
		state = _post_reset(issue_type=None)
	except Exception as exc:
		_log("ERROR", f"task={task_name} reset_failed={exc}")
		_log("END", f"task={task_name} success=false steps=0 rewards=")
		return False

	done = bool(state.get("done", False))
	step_count = 0

	while (not done) and step_count < max_steps:
		step_count += 1

		try:
			action, remembered_issue = _choose_action(state, remembered_issue)
			state, reward, done, error = _post_step(action)
			rewards.append(reward)
			_log(
				"STEP",
				"step={} task={} action={} reward={:.2f} done={} error={}".format(
					step_count,
					task_name,
					json.dumps(action, separators=(",", ":")),
					reward,
					str(done).lower(),
					"null" if error is None else error,
				),
			)
		except requests.RequestException as exc:
			_log("ERROR", f"task={task_name} network_error={exc}")
			_log("END", f"task={task_name} success=false steps={step_count} rewards={','.join(f'{r:.2f}' for r in rewards)}")
			return False
		except Exception as exc:
			_log("ERROR", f"task={task_name} runtime_error={exc}")
			_log("END", f"task={task_name} success=false steps={step_count} rewards={','.join(f'{r:.2f}' for r in rewards)}")
			return False

	success = bool(done)
	_log("END", f"task={task_name} success={str(success).lower()} steps={step_count} rewards={','.join(f'{r:.2f}' for r in rewards)}")
	return success


def main() -> int:
	"""Run baseline inference across easy/medium/hard tasks."""
	try:
		task_results = [run_task(task) for task in TASKS]
		if all(task_results):
			_log("SUCCESS", "Inference completed successfully")
			return 0
		_log("ERROR", "Inference completed with failures")
		return 1
	except Exception as exc:
		_log("ERROR", f"Unhandled exception: {exc}")
		return 1


if __name__ == "__main__":
	sys.exit(main())
