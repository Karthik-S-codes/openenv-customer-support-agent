from typing import Any

class grader:
    def __call__(self, episode: Any = None, **kwargs) -> float:
        try:
            if episode is None:
                return 0.5
            if hasattr(episode, "model_dump"):
                episode = episode.model_dump()
            if not isinstance(episode, dict):
                return 0.5
            if episode.get("classification_correct"):
                return 0.9
            if episode.get("classification_partial"):
                return 0.5
            return 0.1
        except Exception:
            return 0.5

    def grade(self, episode: Any = None, **kwargs) -> float:
        return self.__call__(episode, **kwargs)

grader = grader()
