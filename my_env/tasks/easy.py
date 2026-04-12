from typing import Any, Dict


TASK_NAME = "easy"
DESCRIPTION = "Classification only. Score is 1.0 if classification is correct, else 0.0."


VALID_ISSUES = {"refund", "delivery", "payment"}


def _infer_classification_correct(episode: Dict[str, Any]) -> bool:
    if "classification_correct" in episode:
        return bool(episode.get("classification_correct", False))

    steps = episode.get("steps", [])
    if not isinstance(steps, list) or not steps:
        return False

    first_action = steps[0].get("action", {}) if isinstance(steps[0], dict) else {}
    if not isinstance(first_action, dict):
        return False

    value = first_action.get("issue_type") or first_action.get("classification")
    expected = episode.get("expected_issue_type")

    if isinstance(value, str) and expected:
        candidate = value.strip().lower()
        expected_value = str(expected).strip().lower()
        if expected_value in VALID_ISSUES:
            return candidate == expected_value

    return isinstance(value, str) and value.strip().lower() in VALID_ISSUES


def grader(episode: dict) -> float:
    try:
        if not isinstance(episode, dict):
            return 0.05
        classification_correct = episode.get("classification_correct", False)
        classification_partial = episode.get("classification_partial", False)
        if classification_correct:
            return 0.95
        elif classification_partial:
            return 0.5
        else:
            return 0.05
    except Exception:
        return 0.05

# Keep the old grade name as alias so nothing else breaks
grade = grader
