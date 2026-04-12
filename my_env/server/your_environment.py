import random
from typing import Any, Dict, Optional, Tuple


class CustomerSupportEnvironment:
    ENV_NAME = "customer_support_agent"

    def __init__(self, seed: Optional[int] = None) -> None:
        self.seed = seed
        self._rng = random.Random(seed)
        self.tasks = ["task_easy", "task_medium", "task_hard"]
        self.current_task = self.tasks[0]
        self.done = False
        self.step_count = 0
        self._last_action: Any = None

    def _clamp_reward(self, score: float) -> float:
        score = max(0.01, min(float(score), 0.99))
        return float(score)

    def reset(self, issue_type: Optional[str] = None) -> Dict[str, Any]:
        _ = issue_type
        self.current_task = self._rng.choice(self.tasks)
        self.done = False
        self.step_count = 0
        self._last_action = None
        return {
            "env_name": self.ENV_NAME,
            "task": self.current_task,
            "done": self.done,
            "step": self.step_count,
        }

    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        self.step_count += 1
        self._last_action = action

        reward = 0.3
        text = str(action).lower()
        if isinstance(action, dict):
            reward += 0.2
        if "response" in text:
            reward += 0.2
        if "category" in text:
            reward += 0.2
        reward = self._clamp_reward(reward)

        self.done = True
        observation = {
            "env_name": self.ENV_NAME,
            "task": self.current_task,
            "done": self.done,
            "step": self.step_count,
        }
        info = {
            "task_id": self.current_task,
            "last_action": self._last_action,
        }
        return observation, float(reward), self.done, info

    def state(self) -> Dict[str, Any]:
        return {
            "env_name": self.ENV_NAME,
            "task": self.current_task,
            "done": self.done,
            "step": self.step_count,
        }

    def episode_result(self) -> Dict[str, Any]:
        return {
            "task_id": self.current_task,
            "output": self._last_action,
            "response": str(self._last_action),
            "category": self.current_task,
            "steps": self.step_count,
        }
