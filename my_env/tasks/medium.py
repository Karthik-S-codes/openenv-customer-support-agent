from typing import Any, Dict


TASK_NAME = "medium"
DESCRIPTION = "Classification + response. Score is 0.5 + 0.5 using partial correctness."


def grade(episode: Dict[str, Any]) -> float:
    classification_correct = bool(episode.get("classification_correct", False))
    response_correct = bool(episode.get("response_correct", False))

    score_value = 0.0
    if classification_correct:
        score_value += 0.5
    if response_correct:
        score_value += 0.5

    return float(score_value)


def grader(episode: Dict[str, Any]) -> float:
    return grade(episode)


def score(episode: Dict[str, Any]) -> float:
    return grade(episode)
