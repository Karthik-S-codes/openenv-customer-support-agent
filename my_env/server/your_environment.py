import random
from typing import Any, Dict, List, Optional, Tuple


class CustomerSupportEnvironment:
    """A 3-step customer support environment.

    Step 1: classify issue (refund/payment/delivery)
    Step 2: generate response
    Step 3: resolve issue
    """

    ENV_NAME = "customer_support_agent"
    TOTAL_PHASES = 3

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._scenarios: List[Dict[str, str]] = [
            {
                "issue_type": "refund",
                "queries": [
                    "My order #1234 arrived damaged and I need a refund.",
                    "The item in order #4581 is broken, please help with refund.",
                    "I received a damaged product and want my refund processed.",
                ],
                "expected_response": "refund_policy",
                "expected_resolution": "refund_processed",
            },
            {
                "issue_type": "delivery",
                "queries": [
                    "My delivery is delayed by 5 days, what is the status?",
                    "Order #9421 has not arrived and tracking stopped updating.",
                    "Delivery is late and I need an updated ETA right away.",
                ],
                "expected_response": "delivery_update",
                "expected_resolution": "delivery_escalated",
            },
            {
                "issue_type": "payment",
                "queries": [
                    "Payment failed but amount was deducted from my account.",
                    "Checkout showed failed payment, but my bank was charged.",
                    "My transaction did not complete, yet money got debited.",
                ],
                "expected_response": "payment_verification",
                "expected_resolution": "payment_reconciled",
            },
        ]
        self.current_scenario: Dict[str, str] = {}
        self.current_query: str = ""
        self.current_step: int = 0
        self.done: bool = False
        self.total_reward: float = 0.0
        self.classification_correct: bool = False
        self.response_correct: bool = False
        self.response_partial: bool = False
        self.resolution_correct: bool = False
        self.resolution_partial: bool = False
        self.wrong_steps: int = 0
        self.history: List[Dict[str, Any]] = []

    def reset(self, issue_type: Optional[str] = None) -> Dict[str, Any]:
        if issue_type:
            matched = [s for s in self._scenarios if s["issue_type"] == issue_type]
            self.current_scenario = matched[0] if matched else self._rng.choice(self._scenarios)
        else:
            self.current_scenario = self._rng.choice(self._scenarios)

        queries = self.current_scenario.get("queries", [])
        self.current_query = self._rng.choice(queries) if queries else ""

        self.current_step = 0
        self.done = False
        self.total_reward = 0.0
        self.classification_correct = False
        self.response_correct = False
        self.response_partial = False
        self.resolution_correct = False
        self.resolution_partial = False
        self.wrong_steps = 0
        self.history = []
        return self.state()

    def _extract_action_value(self, action: Any) -> str:
        if isinstance(action, dict):
            for key in ("issue_type", "classification", "response", "resolution", "action"):
                if key in action and isinstance(action[key], str):
                    return action[key].strip().lower()
            return ""
        if isinstance(action, str):
            return action.strip().lower()
        return ""

    def _validate_action(self, action: Any, required_keys: Tuple[str, ...]) -> Optional[str]:
        if not isinstance(action, dict):
            return "invalid_action_type"

        for key in required_keys:
            value = action.get(key)
            if isinstance(value, str) and value.strip():
                return None

        return f"missing_keys:{','.join(required_keys)}"

    def _is_partial_response(self, action_value: str) -> bool:
        issue = self.current_scenario.get("issue_type", "")
        partial_tokens = {
            "refund": ["refund", "return", "policy"],
            "delivery": ["delivery", "delay", "eta", "tracking"],
            "payment": ["payment", "verify", "charge", "bank"],
        }
        return any(token in action_value for token in partial_tokens.get(issue, []))

    def _is_partial_resolution(self, action_value: str) -> bool:
        issue = self.current_scenario.get("issue_type", "")
        partial_tokens = {
            "refund": ["refund", "escalate", "request"],
            "delivery": ["delivery", "escalate", "investigate", "status"],
            "payment": ["payment", "reconcile", "escalate", "verify"],
        }
        return any(token in action_value for token in partial_tokens.get(issue, []))

    def _record_step(self, action: Any, reward: float, error: Optional[str]) -> None:
        self.total_reward += reward
        self.history.append(
            {
                "step": len(self.history) + 1,
                "phase": self.state().get("phase"),
                "action": action,
                "reward": reward,
                "done": self.done,
                "error": error,
            }
        )

    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, Optional[str]]:
        if self.done:
            return self.state(), -0.2, True, "episode_finished"

        if self.current_step == 0:
            validation_error = self._validate_action(action, ("issue_type", "classification"))
        elif self.current_step == 1:
            validation_error = self._validate_action(action, ("response",))
        else:
            validation_error = self._validate_action(action, ("resolution",))

        if validation_error is not None:
            self.wrong_steps += 1
            reward = -0.2
            self._record_step(action=action, reward=reward, error=validation_error)
            return self.state(), reward, self.done, validation_error

        action_value = self._extract_action_value(action)
        reward = -0.2
        error: Optional[str] = None

        if self.current_step == 0:
            expected = self.current_scenario["issue_type"]
            if action_value == expected:
                self.classification_correct = True
                reward = 0.4
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
                self.response_partial = False
                reward = 0.4
            elif self._is_partial_response(action_value):
                self.response_correct = False
                self.response_partial = True
                reward = 0.2
                error = "partial_response"
            else:
                self.response_correct = False
                self.response_partial = False
                reward = -0.2
                error = "wrong_response"
                self.wrong_steps += 1
            self.current_step = 2

        elif self.current_step == 2:
            expected = self.current_scenario["expected_resolution"]
            if action_value == expected:
                self.resolution_correct = True
                self.resolution_partial = False
                reward = 0.2
            elif self._is_partial_resolution(action_value):
                self.resolution_correct = False
                self.resolution_partial = True
                reward = 0.1
                error = "partial_resolution"
            else:
                self.resolution_correct = False
                self.resolution_partial = False
                reward = -0.2
                error = "wrong_resolution"
                self.wrong_steps += 1
            self.current_step = 3
            self.done = True

        self._record_step(action=action, reward=reward, error=error)

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
            "customer_query": self.current_query,
            "done": self.done,
            "progress": {
                "completed_steps": len(self.history),
                "total_steps": self.TOTAL_PHASES,
                "completion_ratio": round(len(self.history) / self.TOTAL_PHASES, 2),
            },
            "history": self.history,
            "summary": {
                "classification_correct": self.classification_correct,
                "response_correct": self.response_correct,
                "response_partial": self.response_partial,
                "resolution_correct": self.resolution_correct,
                "resolution_partial": self.resolution_partial,
                "wrong_steps": self.wrong_steps,
                "total_reward": self.total_reward,
            },
        }

    def episode_result(self) -> Dict[str, Any]:
        return {
            "classification_correct": self.classification_correct,
            "response_correct": self.response_correct,
            "response_partial": self.response_partial,
            "resolution_correct": self.resolution_correct,
            "resolution_partial": self.resolution_partial,
            "total_reward": self.total_reward,
            "steps": self.history,
        }
