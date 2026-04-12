from typing import Any, Dict


TASK_NAME = "hard"
DESCRIPTION = "Full resolution scoring with classification, response, and resolution correctness."


VALID_ISSUES = {"refund", "delivery", "payment"}
EXPECTED_RESPONSES = {"refund_policy", "delivery_update", "payment_verification"}
EXPECTED_RESOLUTIONS = {"refund_processed", "delivery_escalated", "payment_reconciled"}
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
PARTIAL_RESOLUTION_TOKENS = (
    "refund",
    "processed",
    "request",
    "delivery",
    "escalate",
    "investigate",
    "payment",
    "reconcile",
    "verify",
)


def _fallback_flags(episode: Dict[str, Any]) -> Dict[str, bool]:
    steps = episode.get("steps", [])
    if not isinstance(steps, list):
        steps = []

    classification_value = ""
    response_value = ""
    resolution_value = ""

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

    if len(steps) > 2 and isinstance(steps[2], dict):
        action = steps[2].get("action", {})
        if isinstance(action, dict):
            value = action.get("resolution")
            if isinstance(value, str):
                resolution_value = value.strip().lower()

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
        "resolution_correct": resolution_value in EXPECTED_RESOLUTIONS,
        "resolution_partial": any(token in resolution_value for token in PARTIAL_RESOLUTION_TOKENS),
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
        resolution_correct = episode.get("resolution_correct", False)
        resolution_partial = episode.get("resolution_partial", False)
        bonus = episode.get("bonus_awarded", False)

        if classification_correct:
            score += 0.35
        elif classification_partial:
            score += 0.15

        if response_correct:
            score += 0.35
        elif response_partial:
            score += 0.15

        if resolution_correct:
            score += 0.2
        elif resolution_partial:
            score += 0.1

        if bonus:
            score += 0.05

        # Clamp strictly between 0 and 1
        return min(0.95, max(0.05, round(score, 4)))
    except Exception:
        return 0.05

grade = grader
