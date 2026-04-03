import random
from typing import Any, Dict, List, Optional, Tuple


class CustomerSupportEnvironment:
    """A 3-step customer support environment.

    Step 1: classify issue (refund/payment/delivery)
    Step 2: generate response
    Step 3: resolve issue
    """

    ENV_NAME = "customer_support_agent"
    ISSUE_WEIGHT = {
        "refund": 1.00,
        "delivery": 0.95,
        "payment": 0.90,
    }

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._scenarios: List[Dict[str, str]] = [
            {
                "issue_type": "refund",
                "customer_query": "I want a refund for a damaged item I received.",
                "expected_response": "refund_policy",
                "expected_resolution": "refund_processed",
            },
            {
                "issue_type": "delivery",
                "customer_query": "My order is delayed and has not arrived yet.",
                "expected_response": "delivery_update",
                "expected_resolution": "delivery_escalated",
            },
            {
                "issue_type": "payment",
                "customer_query": "My payment failed but money was debited.",
                "expected_response": "payment_verification",
                "expected_resolution": "payment_reconciled",
            },
        ]
        self.current_scenario: Dict[str, str] = {}
        self.current_step: int = 0
        self.done: bool = False
        self.total_reward: float = 0.0
        self.classification_correct: bool = False
        self.response_correct: bool = False
        self.resolution_correct: bool = False
        self.wrong_steps: int = 0
        self.history: List[Dict[str, Any]] = []

    def reset(self, issue_type: Optional[str] = None) -> Dict[str, Any]:
        if issue_type:
            matched = [s for s in self._scenarios if s["issue_type"] == issue_type]
            self.current_scenario = matched[0] if matched else self._rng.choice(self._scenarios)
        else:
            self.current_scenario = self._rng.choice(self._scenarios)

        self.current_step = 0
        self.done = False
        self.total_reward = 0.0
        self.classification_correct = False
        self.response_correct = False
        self.resolution_correct = False
        self.wrong_steps = 0
        self.history = []
        return self.state()

    def _scenario_weight(self) -> float:
        issue = self.current_scenario.get("issue_type", "refund")
        return float(self.ISSUE_WEIGHT.get(issue, 1.0))

    def _quality_multiplier(self) -> float:
        # More mistakes in earlier steps reduce later positive rewards.
        return max(0.7, 1.0 - 0.1 * self.wrong_steps)

    def _positive_reward(self, base_reward: float) -> float:
        reward = base_reward * self._scenario_weight() * self._quality_multiplier()
        return round(reward, 2)

    def _extract_action_value(self, action: Any) -> str:
        if isinstance(action, dict):
            for key in ("issue_type", "classification", "response", "resolution", "action"):
                if key in action and isinstance(action[key], str):
                    return action[key].strip().lower()
            return ""
        if isinstance(action, str):
            return action.strip().lower()
        return ""

    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, Optional[str]]:
        if self.done:
            return self.state(), -0.2, True, "episode_finished"

        action_value = self._extract_action_value(action)
        reward = -0.2
        error: Optional[str] = None

        if self.current_step == 0:
            expected = self.current_scenario["issue_type"]
            if action_value == expected:
                self.classification_correct = True
                reward = self._positive_reward(0.4)
            else:
                self.classification_correct = False
                reward = -0.2
                error = "wrong_classification"
                self.wrong_steps += 1
            self.current_step = 1

        elif self.current_step == 1:
            expected = self.current_scenario["expected_response"]
            if action_value == expected:
                self.response_correct = True
                reward = self._positive_reward(0.4)
            else:
                self.response_correct = False
                reward = -0.2
                error = "wrong_response"
                self.wrong_steps += 1
            self.current_step = 2

        elif self.current_step == 2:
            expected = self.current_scenario["expected_resolution"]
            if action_value == expected:
                self.resolution_correct = True
                reward = self._positive_reward(0.2)
            else:
                self.resolution_correct = False
                reward = -0.2
                error = "wrong_resolution"
                self.wrong_steps += 1
            self.current_step = 3
            self.done = True

        self.total_reward += reward
        self.history.append(
            {
                "step": len(self.history) + 1,
                "action": action,
                "reward": reward,
                "done": self.done,
                "error": error,
            }
        )

        return self.state(), reward, self.done, error

    def state(self) -> Dict[str, Any]:
        phase_map = {
            0: "classify_issue",
            1: "generate_response",
            2: "resolve_issue",
            3: "completed",
        }
        return {
            "env_name": self.ENV_NAME,
            "step_index": self.current_step,
            "phase": phase_map.get(self.current_step, "completed"),
            "customer_query": self.current_scenario.get("customer_query"),
            "done": self.done,
            "history": self.history,
            "summary": {
                "classification_correct": self.classification_correct,
                "response_correct": self.response_correct,
                "resolution_correct": self.resolution_correct,
                "wrong_steps": self.wrong_steps,
                "total_reward": self.total_reward,
            },
        }

    def episode_result(self) -> Dict[str, Any]:
        return {
            "classification_correct": self.classification_correct,
            "response_correct": self.response_correct,
            "resolution_correct": self.resolution_correct,
            "total_reward": self.total_reward,
            "steps": self.history,
        }
