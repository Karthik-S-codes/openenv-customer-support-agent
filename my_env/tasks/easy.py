"""Easy task grading for classification-only customer support scenarios."""

from typing import Any, Dict, List, Optional


TASK_NAME = "easy"
DESCRIPTION = "Classification only with robust edge-case handling."

EASY_SCENARIOS: List[Dict[str, str]] = [
    {
        "query": "My order arrived damaged and I want my money back.",
        "expected_issue_type": "refund",
    },
    {
        "query": "My package is delayed and tracking has not updated.",
        "expected_issue_type": "delivery",
    },
    {
        "query": "Payment failed but my bank account was charged.",
        "expected_issue_type": "payment",
    },
    {
        "query": "I need to return this order and get a refund.",
        "expected_issue_type": "refund",
    },
]


def _normalize_issue(value: Any) -> str:
    """Normalize issue labels to stable comparable values."""
    if not isinstance(value, str):
        return ""
    text = value.strip().lower()
    if text in {"return", "returns", "money_back"}:
        return "refund"
    return text


def _first_action_issue(actions_taken: List[Any]) -> str:
    """Extract issue_type/classification from first action safely."""
    if not isinstance(actions_taken, list) or not actions_taken:
        return ""

    first = actions_taken[0]
    if not isinstance(first, dict):
        return ""

    issue = first.get("issue_type")
    if issue is None:
        issue = first.get("classification")
    return _normalize_issue(issue)


def _expected_issue(scenario_data: Dict[str, Any]) -> str:
    """Extract expected issue type from scenario data safely."""
    if not isinstance(scenario_data, dict):
        return ""
    return _normalize_issue(scenario_data.get("expected_issue_type"))


def _is_partial_match(predicted: str, expected: str) -> bool:
    """Return True for requested partial relation: refund and return."""
    synonyms = {
        "refund": {"refund", "return"},
        "return": {"refund", "return"},
    }
    if not predicted or not expected:
        return False
    return predicted in synonyms.get(expected, set()) and predicted != expected


def grade(actions_taken: list, scenario_data: dict) -> float:
    """Grade easy task actions.

    Args:
        actions_taken: List of action dictionaries from the agent.
        scenario_data: Scenario metadata with expected issue label.

    Returns:
        Float score in [0.0, 1.0].
    """
    try:
        predicted = _first_action_issue(actions_taken if isinstance(actions_taken, list) else [])
        expected = _expected_issue(scenario_data if isinstance(scenario_data, dict) else {})

        score_value = 0.0
        if predicted and expected and predicted == expected:
            score_value = 1.0
        elif _is_partial_match(predicted, expected):
            score_value = 0.5

        return float(max(0.0, min(1.0, score_value)))
    except Exception:
        return 0.0


def grader(actions_taken: list, scenario_data: dict) -> float:
    """Compatibility alias for systems expecting grader()."""
    return grade(actions_taken, scenario_data)


def score(actions_taken: list, scenario_data: dict) -> float:
    """Compatibility alias for systems expecting score()."""
    return grade(actions_taken, scenario_data)
