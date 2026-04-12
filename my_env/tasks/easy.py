def grader(episode):
    try:
        score = 0.5
        if isinstance(episode, dict):
            if episode.get("classification_correct"):
                score = 0.9
            elif episode.get("classification_partial"):
                score = 0.5
            else:
                score = 0.1
        return float(score)
    except Exception:
        return 0.5

