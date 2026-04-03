from typing import Any, Dict


TASK_NAME = "easy"
DESCRIPTION = "Classification only. Score is 1.0 if classification is correct, else 0.0."


def grade(episode: Dict[str, Any]) -> float:
    classification_correct = bool(episode.get("classification_correct", False))
    return 1.0 if classification_correct else 0.0


def grader(episode: Dict[str, Any]) -> float:
    return grade(episode)


def score(episode: Dict[str, Any]) -> float:
    return grade(episode)
