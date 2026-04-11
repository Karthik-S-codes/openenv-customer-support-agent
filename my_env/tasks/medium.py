"""Medium task grading for classification + response quality."""

from typing import Any, Dict, List


TASK_NAME = "medium"
DESCRIPTION = "Classification (50%) + response keyword quality (50%)."

MEDIUM_SCENARIOS: List[Dict[str, Any]] = [
    {
        "query": "My order is damaged and I need a refund right away.",
        "expected_issue_type": "refund",
        "required_keywords": ["refund", "policy", "processed"],
    },
    {
        "query": "Delivery is delayed and I cannot track my package.",
        "expected_issue_type": "delivery",
        "required_keywords": ["delivery", "tracking", "update"],
    },
    {
        "query": "Payment failed but amount was deducted from account.",
        "expected_issue_type": "payment",
        "required_keywords": ["payment", "verify", "charge"],
    },
    {
        "query": "I want return support and a refund timeline.",
        "expected_issue_type": "refund",
        "required_keywords": ["return", "refund", "policy"],
    },
]


def _normalize_issue(value: Any) -> str:
    """Normalize issue labels for safe comparisons."""
    if not isinstance(value, str):
        return ""
    text = value.strip().lower()
    if text in {"return", "returns", "money_back"}:
        return "refund"
    return text


def _extract_action_field(actions_taken: List[Any], index: int, keys: List[str]) -> str:
    """Extract action field value from a specific action index safely."""
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
    """Compute 50% classification score with partial credit."""
    if not predicted or not expected:
        return 0.0
    if predicted == expected:
        return 0.5
    if {predicted, expected} == {"refund", "return"}:
        return 0.25
    return 0.0


def _response_score(response_text: str, required_keywords: List[Any]) -> float:
    """Compute 50% response score from required keyword coverage."""
    if not response_text or not isinstance(required_keywords, list):
        return 0.0

    keywords = [str(k).strip().lower() for k in required_keywords if str(k).strip()]
    if not keywords:
        return 0.0

    matches = sum(1 for kw in keywords if kw in response_text)
    raw = (matches / len(keywords)) * 0.5
    return float(max(0.0, min(0.5, raw)))


def grade(actions_taken: list, scenario_data: dict) -> float:
    """Grade medium task actions.

    Args:
        actions_taken: List of action dictionaries from the agent.
        scenario_data: Scenario metadata containing expected label and keywords.

    Returns:
        Float score in [0.0, 1.0].
    """
    try:
        actions: List[Any] = actions_taken if isinstance(actions_taken, list) else []
        scenario: Dict[str, Any] = scenario_data if isinstance(scenario_data, dict) else {}

        predicted_issue = _normalize_issue(_extract_action_field(actions, 0, ["issue_type", "classification"]))
        expected_issue = _normalize_issue(scenario.get("expected_issue_type"))
        response_text = _extract_action_field(actions, 1, ["response", "message", "text"])
        required_keywords = scenario.get("required_keywords", [])

        classification_part = _classification_score(predicted_issue, expected_issue)
        response_part = _response_score(response_text, required_keywords)

        total_score = classification_part + response_part
        return float(max(0.0, min(1.0, total_score)))
    except Exception:
        return 0.0


def grader(actions_taken: list, scenario_data: dict) -> float:
    """Compatibility alias for systems expecting grader()."""
    return grade(actions_taken, scenario_data)


def score(actions_taken: list, scenario_data: dict) -> float:
    """Compatibility alias for systems expecting score()."""
    return grade(actions_taken, scenario_data)
