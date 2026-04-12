import os

def rewrite_grader(filepath, new_grader_code):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # We find where def grader( begins and tear everything below it
    parts = content.split('def grader(', 1)
    if len(parts) == 2:
        new_content = parts[0] + new_grader_code
        with open(filepath, 'w') as f:
            f.write(new_content)

ez = '''def grader(episode: dict) -> float:
    try:
        if not isinstance(episode, dict):
            return 0.05
        classification_correct = episode.get("classification_correct", False)
        classification_partial = episode.get("classification_partial", False)
        if classification_correct:
            return 0.95
        elif classification_partial:
            return 0.5
        else:
            return 0.05
    except Exception:
        return 0.05

# Keep the old grade name as alias so nothing else breaks
grade = grader
'''

md = '''def grader(episode: dict) -> float:
    try:
        if not isinstance(episode, dict):
            return 0.05
        score = 0.0
        classification_correct = episode.get("classification_correct", False)
        classification_partial = episode.get("classification_partial", False)
        response_correct = episode.get("response_correct", False)
        response_partial = episode.get("response_partial", False)

        if classification_correct:
            score += 0.5
        elif classification_partial:
            score += 0.25

        if response_correct:
            score += 0.45
        elif response_partial:
            score += 0.2

        # Clamp strictly between 0 and 1
        return min(0.95, max(0.05, round(score, 4)))
    except Exception:
        return 0.05

grade = grader
'''

hd = '''def grader(episode: dict) -> float:
    try:
        if not isinstance(episode, dict):
            return 0.05
        score = 0.0
        classification_correct = episode.get("classification_correct", False)
        classification_partial = episode.get("classification_partial", False)
        response_correct = episode.get("response_correct", False)
        response_partial = episode.get("response_partial", False)
        resolution_correct = episode.get("resolution_correct", False)
        resolution_partial = episode.get("resolution_partial", False)
        bonus = episode.get("bonus_awarded", False)

        if classification_correct:
            score += 0.35
        elif classification_partial:
            score += 0.15

        if response_correct:
            score += 0.35
        elif response_partial:
            score += 0.15

        if resolution_correct:
            score += 0.2
        elif resolution_partial:
            score += 0.1

        if bonus:
            score += 0.05

        # Clamp strictly between 0 and 1
        return min(0.95, max(0.05, round(score, 4)))
    except Exception:
        return 0.05

grade = grader
'''

rewrite_grader('d:/cusort/openenv-customer-support-agent/my_env/tasks/easy.py', ez)
rewrite_grader('d:/cusort/openenv-customer-support-agent/my_env/tasks/medium.py', md)
rewrite_grader('d:/cusort/openenv-customer-support-agent/my_env/tasks/hard.py', hd)
