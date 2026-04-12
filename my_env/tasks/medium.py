def grader(episode):
    try:
        score = 0.1
        if isinstance(episode, dict):
            if episode.get("classification_correct"):
                score += 0.4
            elif episode.get("classification_partial"):
                score += 0.2
            if episode.get("response_correct"):
                score += 0.4
            elif episode.get("response_partial"):
                score += 0.2
        if score >= 0.9:
            score = 0.85
        if score <= 0.0:
            score = 0.1
        return float(round(score, 2))
    except Exception:
        return 0.5

