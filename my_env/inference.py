import argparse
import json
import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from server.your_environment import CustomerSupportEnvironment
from tasks.easy import grade as grade_easy
from tasks.hard import grade as grade_hard
from tasks.medium import grade as grade_medium


# Mandatory hackathon variables (LOCAL_IMAGE_NAME kept for spec compatibility).
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")


def _bool_text(value: bool) -> str:
	return "true" if value else "false"


def log_start(task: str, env: str, model: str) -> None:
	print(f"[START] task={task} env={env} model={model}")


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
	reward_text = f"{reward:.2f}"
	done_text = _bool_text(done)
	error_text = "null" if error is None else str(error)
	print(
		f"[STEP] step={step} action={action} reward={reward_text} "
		f"done={done_text} error={error_text}"
	)


def log_end(success: bool, steps: int, rewards: List[float]) -> None:
	rewards_text = ",".join(f"{r:.2f}" for r in rewards)
	print(f"[END] success={_bool_text(success)} steps={steps} rewards={rewards_text}")


class SupportPolicy:
	def __init__(self, model_name: Optional[str], agent_type: str = "openai") -> None:
		self.agent_type = agent_type
		self.model_name = model_name or MODEL_NAME
		self.client: Optional[OpenAI] = None

		# Per hackathon requirement: use OpenAI client for model calls.
		if agent_type == "openai":
			if HF_TOKEN:
				self.client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
			elif os.getenv("OPENAI_API_KEY"):
				self.client = OpenAI()

	def _fallback_action(self, state: Dict[str, Any]) -> Dict[str, str]:
		query = (state.get("customer_query") or "").lower()
		phase = state.get("phase")

		if "refund" in query:
			issue, response, resolution = "refund", "refund_policy", "refund_processed"
		elif "delay" in query or "delayed" in query or "arrive" in query:
			issue, response, resolution = "delivery", "delivery_update", "delivery_escalated"
		else:
			issue, response, resolution = "payment", "payment_verification", "payment_reconciled"

		if phase == "classify_issue":
			return {"issue_type": issue}
		if phase == "generate_response":
			return {"response": response}
		return {"resolution": resolution}

	def _model_action(self, state: Dict[str, Any]) -> Dict[str, str]:
		if not self.client:
			return self._fallback_action(state)

		phase = state.get("phase")
		prompt = {
			"phase": phase,
			"customer_query": state.get("customer_query"),
			"allowed_labels": {
				"classify_issue": ["refund", "delivery", "payment"],
				"generate_response": ["refund_policy", "delivery_update", "payment_verification"],
				"resolve_issue": ["refund_processed", "delivery_escalated", "payment_reconciled"],
			},
			"output_rule": (
				"Return only a JSON object with one key for the active phase: "
				"issue_type OR response OR resolution."
			),
		}

		try:
			completion = self.client.chat.completions.create(
				model=self.model_name,
				temperature=0,
				max_tokens=64,
				messages=[
					{
						"role": "system",
						"content": "You are a strict policy model for a customer support environment.",
					},
					{"role": "user", "content": json.dumps(prompt)},
				],
				stream=False,
			)
			content = (completion.choices[0].message.content or "").strip()
			parsed = json.loads(content) if content else {}
			if isinstance(parsed, dict):
				return parsed
		except Exception:
			pass

		return self._fallback_action(state)

	def action(self, state: Dict[str, Any]) -> Dict[str, str]:
		if self.agent_type == "rule_based":
			return self._fallback_action(state)
		return self._model_action(state)


def evaluate_task(task_name: str, episode: Dict[str, Any]) -> float:
	if task_name == "easy":
		return grade_easy(episode)
	if task_name == "medium":
		return grade_medium(episode)
	return grade_hard(episode)


def run(task_name: str, env_name: str, model_name: str, agent_type: str, max_steps: int = 6) -> None:
	env = CustomerSupportEnvironment()
	policy = SupportPolicy(model_name=model_name, agent_type=agent_type)

	rewards: List[float] = []
	steps_taken = 0
	success = False

	log_start(task=task_name, env=env_name, model=model_name)

	try:
		state = env.reset()

		for step in range(1, max_steps + 1):
			action_dict = policy.action(state)
			action_text = json.dumps(action_dict, separators=(",", ":"))

			state, reward, done, error = env.step(action_dict)
			rewards.append(float(reward))
			steps_taken = step

			log_step(step=step, action=action_text, reward=float(reward), done=bool(done), error=error)

			if done:
				break

		episode = env.episode_result()
		task_score = evaluate_task(task_name, episode)
		success = task_score >= (1.0 if task_name in ("easy", "medium") else 0.8)

	finally:
		close_fn = getattr(env, "close", None)
		if callable(close_fn):
			try:
				close_fn()
			except Exception:
				pass
		log_end(success=success, steps=steps_taken, rewards=rewards)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser()
	parser.add_argument("--task", default="hard", choices=["easy", "medium", "hard"])
	parser.add_argument("--env", default="customer_support_agent")
	parser.add_argument("--model", default=MODEL_NAME)
	parser.add_argument("--agent", default="openai", choices=["openai", "rule_based"])
	parser.add_argument("--max-steps", type=int, default=6)
	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()
	run(
		task_name=args.task,
		env_name=args.env,
		model_name=args.model,
		agent_type=args.agent,
		max_steps=args.max_steps,
	)
