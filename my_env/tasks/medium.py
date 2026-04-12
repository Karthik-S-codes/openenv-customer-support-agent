from typing import Any, Dict


def _safe_score(original_score: Any) -> float:
    """Clamp score strictly inside (0, 1)."""
    safe_score = max(0.001, min(0.999, float(original_score)))
    return float(safe_score)


class MediumGrader:
    """Classification + response grader with strict safe score bounds."""

    def __call__(self, episode: Any = None, **kwargs: Any) -> float:
        try:
            if hasattr(episode, "model_dump"):
                episode = episode.model_dump()

            if not isinstance(episode, dict):
                return _safe_score(0.5)

            classification_correct = bool(episode.get("classification_correct", False))
            classification_partial = bool(episode.get("classification_partial", False))
            response_correct = bool(episode.get("response_correct", False))
            response_partial = bool(episode.get("response_partial", False))

            original_score = 0.1
            if classification_correct:
                original_score += 0.35
            elif classification_partial:
                original_score += 0.15

            if response_correct:
                original_score += 0.35
            elif response_partial:
                original_score += 0.15

            return _safe_score(original_score)
        except Exception:
            return _safe_score(0.5)

    def grade(self, episode: Any = None, **kwargs: Any) -> float:
        """Compatibility method for frameworks expecting `.grade(...)`."""
        return self.__call__(episode=episode, **kwargs)


grader = MediumGrader()


def grade(episode: Dict[str, Any] | None = None, **kwargs: Any) -> float:
    """Module-level compatibility alias."""
    return grader(episode=episode, **kwargs)


def score(episode: Dict[str, Any] | None = None, **kwargs: Any) -> float:
    """Module-level compatibility alias."""
    return grader(episode=episode, **kwargs)
