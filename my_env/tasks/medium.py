from typing import Any, Dict


TASK_NAME = "medium"
DESCRIPTION = "Classification + response. Score uses 0.5 for classification and up to 0.5 for response."


def grade(episode: Dict[str, Any]) -> float:
    classification_correct = bool(episode.get("classification_correct", False))
    response_correct = bool(episode.get("response_correct", False))
    response_partial = bool(episode.get("response_partial", False))

    score_value = 0.0
    if classification_correct:
        score_value += 0.5
    if response_correct:
        score_value += 0.5
    elif response_partial:
        score_value += 0.25

    return max(0.0, min(1.0, float(score_value)))


def grader(episode: Dict[str, Any]) -> float:
    return grade(episode)


def score(episode: Dict[str, Any]) -> float:
    return grade(episode)
