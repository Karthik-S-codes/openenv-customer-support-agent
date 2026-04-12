def safe_grader(output, expected):
    score = 0.5

    try:
        text = str(output).lower()

        if isinstance(output, dict):
            score += 0.1
        if "refund" in text:
            score += 0.1
        if "delay" in text:
            score += 0.1
        if "payment" in text:
            score += 0.1

    except:
        score = 0.3

    if score <= 0.0:
        score = 0.01
    elif score >= 1.0:
        score = 0.99

    return float(score)
