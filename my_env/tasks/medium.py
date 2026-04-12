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
            
            score = 0.1
            if episode.get("classification_correct"):
                score += 0.35
            elif episode.get("classification_partial"):
                score += 0.15
            
            if episode.get("response_correct"):
                score += 0.35
            elif episode.get("response_partial"):
                score += 0.15
                
            safe_score = max(0.01, min(0.99, float(score)))
            return float(safe_score)
        except Exception:
            return 0.5

    def grade(self, episode: Any = None, **kwargs) -> float:
        return self.__call__(episode, **kwargs)

grader = grader()
