from typing import Any, Dict


TASK_NAME = "medium"
DESCRIPTION = "Classification + response. Score uses 0.5 for classification and up to 0.5 for response."


VALID_ISSUES = {"refund", "delivery", "payment"}
EXPECTED_RESPONSES = {"refund_policy", "delivery_update", "payment_verification"}
PARTIAL_RESPONSE_TOKENS = (
    "refund",
    "policy",
    "return",
    "delivery",
    "delay",
    "tracking",
    "payment",
    "verify",
    "charge",
)


def _fallback_flags(episode: Dict[str, Any]) -> Dict[str, bool]:
    steps = episode.get("steps", [])
    if not isinstance(steps, list):
        steps = []

    classification_value = ""
    response_value = ""

    if len(steps) > 0 and isinstance(steps[0], dict):
        action = steps[0].get("action", {})
        if isinstance(action, dict):
            value = action.get("issue_type") or action.get("classification")
            if isinstance(value, str):
                classification_value = value.strip().lower()

    if len(steps) > 1 and isinstance(steps[1], dict):
        action = steps[1].get("action", {})
        if isinstance(action, dict):
            value = action.get("response")
            if isinstance(value, str):
                response_value = value.strip().lower()

    expected = episode.get("expected_issue_type")
    expected_issue = str(expected).strip().lower() if expected else ""
    related = episode.get("related_issue_types", [])
    related_set = {str(x).strip().lower() for x in related if isinstance(x, str)}

    classification_correct = (
        isinstance(classification_value, str)
        and bool(expected_issue)
        and classification_value == expected_issue
    )
    classification_partial = (
        isinstance(classification_value, str)
        and classification_value in related_set
    )

    return {
        "classification_correct": classification_correct,
        "classification_partial": classification_partial,
        "response_correct": response_value in EXPECTED_RESPONSES,
        "response_partial": any(token in response_value for token in PARTIAL_RESPONSE_TOKENS),
    }


def grader(episode: dict) -> float:
    try:
        if not isinstance(episode, dict):
            return 0.05
        score = 0.0
        classification_correct = episode.get("classification_correct", False)
        classification_partial = episode.get("classification_partial", False)
        response_correct = episode.get("response_correct", False)
        response_partial = episode.get("response_partial", False)

        if classification_correct:
            score += 0.5
        elif classification_partial:
            score += 0.25

        if response_correct:
            score += 0.45
        elif response_partial:
            score += 0.2

        # Clamp strictly between 0 and 1
        return min(0.95, max(0.05, round(score, 4)))
    except Exception:
        return 0.05

grade = grader
