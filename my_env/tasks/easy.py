def grader(episode: dict = None, **kwargs) -> float:
    try:
        if episode is None:
            return 0.5
        if hasattr(episode, "model_dump"):
            episode = episode.model_dump()
        if not isinstance(episode, dict):
            return 0.5
        
        score = 0.1
        if episode.get("classification_correct"):
            score = 0.9
        elif episode.get("classification_partial"):
            score = 0.5
        
        safe_score = max(0.01, min(0.99, float(score)))
        return float(safe_score)
    except Exception:
        return 0.5

grade = grader
