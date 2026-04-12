def safe_grader(output, expected=None):
    score = 0.3

    try:
        if isinstance(output, dict):
            score += 0.2
        if "response" in str(output).lower():
            score += 0.2
        if "category" in str(output).lower():
            score += 0.2
    except Exception:
        score = 0.2

    score = max(0.01, min(score, 0.99))
    return float(score)


def grader(output=None, expected=None):
    return safe_grader(output, expected)
