"""Hard task grading for classification + response + resolution quality."""

from typing import Any, Dict, List


TASK_NAME = "hard"
DESCRIPTION = "Classification (40%) + response (40%) + resolution (20%)."

HARD_SCENARIOS: List[Dict[str, Any]] = [
    {
        "query": "Item arrived broken and I need a refund immediately.",
        "expected_issue_type": "refund",
        "required_keywords": ["refund", "policy", "processed"],
        "valid_resolutions": ["refund_processed", "send_replacement"],
    },
    {
        "query": "Shipment is delayed and tracking has not changed for days.",
        "expected_issue_type": "delivery",
        "required_keywords": ["delivery", "tracking", "update"],
        "valid_resolutions": ["delivery_escalated", "priority_dispatch"],
    },
    {
        "query": "Payment failed but amount was deducted from my account.",
        "expected_issue_type": "payment",
        "required_keywords": ["payment", "verify", "charge"],
        "valid_resolutions": ["payment_reconciled", "refund_processed"],
    },
    {
        "query": "I want to return this and get my money back quickly.",
        "expected_issue_type": "refund",
        "required_keywords": ["return", "refund", "policy"],
        "valid_resolutions": ["refund_processed", "return_pickup_scheduled"],
    },
]


def _normalize_issue(value: Any) -> str:
    """Normalize issue labels for comparison."""
    if not isinstance(value, str):
        return ""
    text = value.strip().lower()
    if text in {"return", "returns", "money_back"}:
        return "refund"
    return text


def _extract_action_field(actions_taken: List[Any], index: int, keys: List[str]) -> str:
    """Extract field from indexed action safely."""
    if not isinstance(actions_taken, list) or len(actions_taken) <= index:
        return ""
    action = actions_taken[index]
    if not isinstance(action, dict):
        return ""
    for key in keys:
        value = action.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return ""


def _classification_score(predicted: str, expected: str) -> float:
    """Compute classification score out of 0.4."""
    if not predicted or not expected:
        return 0.0
    if predicted == expected:
        return 0.4
    if {predicted, expected} == {"refund", "return"}:
        return 0.2
    return 0.0


def _response_score(response_text: str, required_keywords: List[Any]) -> float:
    """Compute response score out of 0.4 by keyword coverage."""
    if not response_text or not isinstance(required_keywords, list):
        return 0.0

    keywords = [str(k).strip().lower() for k in required_keywords if str(k).strip()]
    if not keywords:
        return 0.0

    matches = sum(1 for kw in keywords if kw in response_text)
    raw = (matches / len(keywords)) * 0.4
    return float(max(0.0, min(0.4, raw)))


def _resolution_score(resolution_text: str, valid_resolutions: List[Any]) -> float:
    """Compute resolution score out of 0.2 with partial attempt credit."""
    if not resolution_text:
        return 0.0
    if not isinstance(valid_resolutions, list):
        return 0.0

    valid = [str(v).strip().lower() for v in valid_resolutions if str(v).strip()]
    if not valid:
        return 0.0

    if resolution_text in valid:
        return 0.2

    # Partial attempt: shares a token with any valid resolution.
    resolution_tokens = set(token for token in resolution_text.replace("-", "_").split("_") if token)
    for candidate in valid:
        candidate_tokens = set(token for token in candidate.replace("-", "_").split("_") if token)
        if resolution_tokens.intersection(candidate_tokens):
            return 0.05
    return 0.0


def grade(actions_taken: list, scenario_data: dict) -> float:
    """Grade hard task actions.

    Args:
        actions_taken: List of action dictionaries from the agent.
        scenario_data: Scenario metadata containing expected label, keywords,
            and valid resolutions.

    Returns:
        Float score in [0.0, 1.0].
    """
    try:
        actions: List[Any] = actions_taken if isinstance(actions_taken, list) else []
        scenario: Dict[str, Any] = scenario_data if isinstance(scenario_data, dict) else {}

        predicted_issue = _normalize_issue(_extract_action_field(actions, 0, ["issue_type", "classification"]))
        expected_issue = _normalize_issue(scenario.get("expected_issue_type"))
        response_text = _extract_action_field(actions, 1, ["response", "message", "text"])
        resolution_text = _extract_action_field(actions, 2, ["resolution", "action", "next_step"])

        required_keywords = scenario.get("required_keywords", [])
        valid_resolutions = scenario.get("valid_resolutions", [])

        class_part = _classification_score(predicted_issue, expected_issue)
        response_part = _response_score(response_text, required_keywords)
        resolution_part = _resolution_score(resolution_text, valid_resolutions)

        total_score = class_part + response_part + resolution_part
        return float(max(0.0, min(1.0, total_score)))
    except Exception:
        return 0.0


def grader(actions_taken: list, scenario_data: dict) -> float:
    """Compatibility alias for systems expecting grader()."""
    return grade(actions_taken, scenario_data)


def score(actions_taken: list, scenario_data: dict) -> float:
    """Compatibility alias for systems expecting score()."""
    return grade(actions_taken, scenario_data)
