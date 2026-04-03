"""OpenEnv client entry module.

This file is required by OpenEnv structure checks.
"""

from typing import Any, Dict

from server.your_environment import CustomerSupportEnvironment


class Client:
    """Thin client wrapper around the local environment."""

    def __init__(self) -> None:
        self.env = CustomerSupportEnvironment()

    def reset(self, issue_type: str | None = None) -> Dict[str, Any]:
        return self.env.reset(issue_type=issue_type)

    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        state, reward, done, error = self.env.step(action)
        return {
            "state": state,
            "reward": reward,
            "done": done,
            "error": error,
        }
