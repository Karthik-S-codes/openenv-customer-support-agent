import random
from typing import Any, Dict, List, Optional, Tuple


class CustomerSupportEnvironment:
    """A 3-step customer support environment.

    Flow:
    1) classify_issue
    2) generate_response
    3) resolve_issue
    """

    ENV_NAME = "customer_support_agent"
    TOTAL_PHASES = 3
    VALID_ISSUES = ("refund", "delivery", "payment")

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._scenarios: List[Dict[str, Any]] = [
            {
                "issue_type": "refund",
                "customer_query": "My order #4821 arrived damaged and I want a refund immediately.",
                "related_issue_types": ["delivery"],
                "expected_response": "refund_policy",
                "expected_resolution": "refund_processed",
            },
            {
                "issue_type": "refund",
                "customer_query": "Order #9001 is delayed and the item looks damaged in photos. Should I wait or request refund?",
                "related_issue_types": ["delivery"],
                "expected_response": "refund_policy",
                "expected_resolution": "refund_processed",
            },
            {
                "issue_type": "refund",
                "customer_query": "I am frustrated, order #1733 came broken and replacement is too slow. I need money back.",
                "related_issue_types": ["delivery"],
                "expected_response": "refund_policy",
                "expected_resolution": "refund_processed",
            },
            {
                "issue_type": "delivery",
                "customer_query": "My delivery is delayed by 4 days, I need an update urgently.",
                "related_issue_types": ["refund"],
                "expected_response": "delivery_update",
                "expected_resolution": "delivery_escalated",
            },
            {
                "issue_type": "delivery",
                "customer_query": "Order #2209 still not delivered and tracking froze yesterday. I am really upset.",
                "related_issue_types": ["payment"],
                "expected_response": "delivery_update",
                "expected_resolution": "delivery_escalated",
            },
            {
                "issue_type": "delivery",
                "customer_query": "Shipment #3008 says out for delivery, but I got nothing. Should I escalate or ask refund?",
                "related_issue_types": ["refund"],
                "expected_response": "delivery_update",
                "expected_resolution": "delivery_escalated",
            },
            {
                "issue_type": "payment",
                "customer_query": "Payment failed but amount was deducted from my account.",
                "related_issue_types": ["delivery"],
                "expected_response": "payment_verification",
                "expected_resolution": "payment_reconciled",
            },
            {
                "issue_type": "payment",
                "customer_query": "Checkout for order #8801 failed, but bank statement shows a charge.",
                "related_issue_types": ["delivery"],
                "expected_response": "payment_verification",
                "expected_resolution": "payment_reconciled",
            },
            {
                "issue_type": "payment",
                "customer_query": "Transaction #TX992 is pending after deduction and my delivery has not started.",
                "related_issue_types": ["delivery"],
                "expected_response": "payment_verification",
                "expected_resolution": "payment_reconciled",
            },
            {
                "issue_type": "payment",
                "customer_query": "Order #7023 shows payment error and delayed dispatch. Please check both urgently.",
                "related_issue_types": ["delivery"],
                "expected_response": "payment_verification",
                "expected_resolution": "payment_reconciled",
            },
        ]

        self.current_scenario: Dict[str, Any] = {}
        self.current_query: str = ""
        self.current_step: int = 0
        self.done: bool = False

        self.total_reward: float = 0.0
        self.wrong_steps: int = 0
        self.repeated_wrong_penalties: int = 0
        self.bonus_awarded: bool = False

        self.classification_correct: bool = False
        self.classification_partial: bool = False
        self.response_correct: bool = False
        self.response_partial: bool = False
        self.resolution_correct: bool = False
        self.resolution_partial: bool = False

        self.history: List[Dict[str, Any]] = []
        self.wrong_action_counts: Dict[str, int] = {}

    def reset(self, issue_type: Optional[str] = None) -> Dict[str, Any]:
        if issue_type and issue_type in self.VALID_ISSUES:
            candidates = [s for s in self._scenarios if s["issue_type"] == issue_type]
            self.current_scenario = self._rng.choice(candidates) if candidates else self._rng.choice(self._scenarios)
        else:
            self.current_scenario = self._rng.choice(self._scenarios)

        self.current_query = str(self.current_scenario.get("customer_query", ""))
        self.current_step = 0
        self.done = False

        self.total_reward = 0.0
        self.wrong_steps = 0
        self.repeated_wrong_penalties = 0
        self.bonus_awarded = False

        self.classification_correct = False
        self.classification_partial = False
        self.response_correct = False
        self.response_partial = False
        self.resolution_correct = False
        self.resolution_partial = False

        self.history = []
        self.wrong_action_counts = {}
        return self.state()

    def _extract_action_value(self, action: Any) -> str:
        if isinstance(action, dict):
            for key in ("issue_type", "classification", "response", "resolution", "action"):
                value = action.get(key)
                if isinstance(value, str):
                    return value.strip().lower()
            return ""
        if isinstance(action, str):
            return action.strip().lower()
        return ""

    def _extract_phase_value(self, action: Dict[str, Any], phase: int) -> str:
        if phase == 0:
            value = action.get("issue_type") or action.get("classification") or action.get("action")
        elif phase == 1:
            value = action.get("response") or action.get("action")
        else:
            value = action.get("resolution") or action.get("action")
        return value.strip().lower() if isinstance(value, str) else ""

    def _validate_action(self, action: Any, required_keys: Tuple[str, ...]) -> Optional[str]:
        if not isinstance(action, dict):
            return "invalid_action_type"

        for key in required_keys:
            value = action.get(key)
            if isinstance(value, str) and value.strip():
                return None

        return f"missing_keys:{','.join(required_keys)}"

    def _is_related_classification(self, action_value: str) -> bool:
        if action_value not in self.VALID_ISSUES:
            return False
        related = self.current_scenario.get("related_issue_types", [])
        return action_value in related

    def _is_generic_response(self, action_value: str) -> bool:
        generic_tokens = ["sorry", "apologize", "understand", "assist", "checking", "please wait"]
        return any(token in action_value for token in generic_tokens)

    def _is_partial_response(self, action_value: str) -> bool:
        issue = str(self.current_scenario.get("issue_type", ""))
        partial_tokens = {
            "refund": ["refund", "return", "policy"],
            "delivery": ["delivery", "delay", "eta", "tracking", "status"],
            "payment": ["payment", "verify", "charge", "bank"],
        }
        return any(token in action_value for token in partial_tokens.get(issue, []))

    def _is_partial_resolution(self, action_value: str) -> bool:
        issue = str(self.current_scenario.get("issue_type", ""))
        partial_tokens = {
            "refund": ["refund", "request", "escalate"],
            "delivery": ["delivery", "escalate", "investigate", "status"],
            "payment": ["payment", "reconcile", "verify", "escalate"],
        }
        return any(token in action_value for token in partial_tokens.get(issue, []))

    def _apply_repeated_wrong_penalty(self, action_value: str, reward: float) -> float:
        if action_value:
            previous_count = self.wrong_action_counts.get(action_value, 0)
            if previous_count > 0:
                reward -= 0.1
                self.repeated_wrong_penalties += 1
            self.wrong_action_counts[action_value] = previous_count + 1
        return reward

    def _record_step(self, action: Any, reward: float, error: Optional[str]) -> None:
        self.total_reward += reward
        self.history.append(
            {
                "step": len(self.history) + 1,
                "phase": self._phase_name(self.current_step),
                "action": action,
                "reward": reward,
                "done": self.done,
                "error": error,
            }
        )

    def _phase_name(self, step_index: int) -> str:
        phase_map = {
            0: "classify_issue",
            1: "generate_response",
            2: "resolve_issue",
            3: "completed",
        }
        return phase_map.get(step_index, "completed")

    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, Optional[str]]:
        if self.done:
            return self.state(), -0.2, True, "episode_finished"

        required = ("issue_type", "classification") if self.current_step == 0 else ("response",) if self.current_step == 1 else ("resolution",)
        validation_error = self._validate_action(action, required)
        action_value = self._extract_action_value(action)

        if validation_error is not None:
            self.wrong_steps += 1
            reward = self._apply_repeated_wrong_penalty(action_value, -0.2)
            reward = round(reward, 2)
            self._record_step(action=action, reward=reward, error=validation_error)
            return self.state(), reward, self.done, validation_error

        # Use phase-specific key first, then fallback.
        if isinstance(action, dict):
            phase_value = self._extract_phase_value(action=action, phase=self.current_step)
            if phase_value:
                action_value = phase_value

        reward = -0.2
        error: Optional[str] = None

        if self.current_step == 0:
            expected = str(self.current_scenario["issue_type"])
            if action_value == expected:
                self.classification_correct = True
                self.classification_partial = False
                reward = 0.4
            elif self._is_related_classification(action_value):
                self.classification_correct = False
                self.classification_partial = True
                reward = 0.2
                error = "partial_classification"
            else:
                self.classification_correct = False
                self.classification_partial = False
                self.wrong_steps += 1
                reward = self._apply_repeated_wrong_penalty(action_value, -0.2)
                error = "wrong_classification"
            self.current_step = 1

        elif self.current_step == 1:
            expected = str(self.current_scenario["expected_response"])
            if action_value == expected:
                self.response_correct = True
                self.response_partial = False
                reward = 0.4
            elif self._is_partial_response(action_value) or self._is_generic_response(action_value):
                self.response_correct = False
                self.response_partial = True
                reward = 0.2
                error = "partial_response"
            else:
                self.response_correct = False
                self.response_partial = False
                self.wrong_steps += 1
                reward = self._apply_repeated_wrong_penalty(action_value, -0.2)
                error = "wrong_response"
            self.current_step = 2

        else:
            expected = str(self.current_scenario["expected_resolution"])
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
                self.wrong_steps += 1
                reward = self._apply_repeated_wrong_penalty(action_value, -0.2)
                error = "wrong_resolution"

            # No-mistake bonus is granted only for a fully correct episode.
            if (
                self.classification_correct
                and self.response_correct
                and self.resolution_correct
                and self.wrong_steps == 0
            ):
                reward += 0.1
                self.bonus_awarded = True

            self.current_step = 3
            self.done = True

        reward = round(reward, 2)
        self._record_step(action=action, reward=reward, error=error)
        return self.state(), reward, self.done, error

    def state(self) -> Dict[str, Any]:
        return {
            "env_name": self.ENV_NAME,
            "step_index": self.current_step,
            "phase": self._phase_name(self.current_step),
            "customer_query": self.current_query,
            "expected_issue_type": self.current_scenario.get("issue_type"),
            "done": self.done,
            "previous_actions": [h.get("action") for h in self.history],
            "progress": {
                "completed_steps": len(self.history),
                "total_steps": self.TOTAL_PHASES,
                "completion_ratio": round(len(self.history) / self.TOTAL_PHASES, 2),
            },
            "history": self.history,
            "summary": {
                "classification_correct": self.classification_correct,
                "classification_partial": self.classification_partial,
                "response_correct": self.response_correct,
                "response_partial": self.response_partial,
                "resolution_correct": self.resolution_correct,
                "resolution_partial": self.resolution_partial,
                "wrong_steps": self.wrong_steps,
                "repeated_wrong_penalties": self.repeated_wrong_penalties,
                "bonus_awarded": self.bonus_awarded,
                "total_reward": round(self.total_reward, 2),
            },
        }

    def episode_result(self) -> Dict[str, Any]:
        return {
            "expected_issue_type": self.current_scenario.get("issue_type"),
            "related_issue_types": self.current_scenario.get("related_issue_types", []),
            "classification_correct": self.classification_correct,
            "classification_partial": self.classification_partial,
            "response_correct": self.response_correct,
            "response_partial": self.response_partial,
            "resolution_correct": self.resolution_correct,
            "resolution_partial": self.resolution_partial,
            "wrong_steps": self.wrong_steps,
            "repeated_wrong_penalties": self.repeated_wrong_penalties,
            "bonus_awarded": self.bonus_awarded,
            "total_reward": round(self.total_reward, 2),
            "steps": self.history,
        }
