from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Observation(BaseModel):
    env_name: str
    step_index: int
    phase: str
    customer_query: Optional[str] = None
    done: bool
    previous_actions: List[Any] = Field(default_factory=list)
    progress: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)


class Action(BaseModel):
    issue_type: Optional[str] = None
    classification: Optional[str] = None
    response: Optional[str] = None
    resolution: Optional[str] = None
    action: Optional[str] = None


class Reward(BaseModel):
    value: float


@dataclass
class Scenario:
    issue_type: str
    customer_query: str
    expected_response: str
    expected_resolution: str


@dataclass
class StepRecord:
    step: int
    action: Any
    reward: float
    done: bool
    error: Optional[str]


@dataclass
class EpisodeResult:
    classification_correct: bool
    response_correct: bool
    resolution_correct: bool
    total_reward: float
    steps: List[StepRecord]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "classification_correct": self.classification_correct,
            "response_correct": self.response_correct,
            "resolution_correct": self.resolution_correct,
            "total_reward": self.total_reward,
            "steps": [
                {
                    "step": s.step,
                    "action": s.action,
                    "reward": s.reward,
                    "done": s.done,
                    "error": s.error,
                }
                for s in self.steps
            ],
        }
