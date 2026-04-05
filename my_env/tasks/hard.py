from typing import Any, Dict


TASK_NAME = "hard"
DESCRIPTION = "Full resolution scoring with classification, response, and resolution correctness."


def grade(episode: Dict[str, Any]) -> float:
    classification_correct = bool(episode.get("classification_correct", False))
    response_correct = bool(episode.get("response_correct", False))
    response_partial = bool(episode.get("response_partial", False))
    resolution_correct = bool(episode.get("resolution_correct", False))
    resolution_partial = bool(episode.get("resolution_partial", False))

    score_value = 0.0
    if classification_correct:
        score_value += 0.4
    if response_correct:
        score_value += 0.4
    elif response_partial:
        score_value += 0.2
    if resolution_correct:
        score_value += 0.2
    elif resolution_partial:
        score_value += 0.1

    # Bound score to [0.0, 1.0] and return a stable rounded value.
    return max(0.0, min(1.0, round(score_value, 4)))


def grader(episode: Dict[str, Any]) -> float:
    return grade(episode)


def score(episode: Dict[str, Any]) -> float:
    return grade(episode)
