from typing import Any

class grader:
    def __call__(self, episode: Any = None, **kwargs) -> float:
        try:
            if episode is None:
                original_score = 0.5
                safe_score = max(0.001, min(0.999, float(original_score)))
                return float(safe_score)
            if hasattr(episode, "model_dump"):
                episode = episode.model_dump()
            if not isinstance(episode, dict):
                original_score = 0.5
                safe_score = max(0.001, min(0.999, float(original_score)))
                return float(safe_score)
            
            score = 0.1
            if episode.get("classification_correct"):
                score += 0.25
            elif episode.get("classification_partial"):
                score += 0.1
            
            if episode.get("response_correct"):
                score += 0.25
            elif episode.get("response_partial"):
                score += 0.1
                
            if episode.get("resolution_correct"):
                score += 0.2
            elif episode.get("resolution_partial"):
                score += 0.1
                
            if episode.get("bonus_awarded"):
                score += 0.05
                
            original_score = score
            safe_score = max(0.001, min(0.999, float(original_score)))
            return float(safe_score)
        except Exception:
            original_score = 0.5
            safe_score = max(0.001, min(0.999, float(original_score)))
            return float(safe_score)

    def grade(self, episode: Any = None, **kwargs) -> float:
        return self.__call__(episode, **kwargs)

grader = grader()
