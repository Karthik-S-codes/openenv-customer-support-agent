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


def grade(episode: Dict[str, Any]) -> float:
    classification_correct = _infer_classification_correct(episode)
    score_value = 1.0 if classification_correct else 0.0
    return max(0.0, min(1.0, float(score_value)))


def grader(episode: Dict[str, Any]) -> float:
    return grade(episode)


def score(episode: Dict[str, Any]) -> float:
    return grade(episode)
