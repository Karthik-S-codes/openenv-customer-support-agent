from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

try:
    from .your_environment import CustomerSupportEnvironment
except ImportError:
    from your_environment import CustomerSupportEnvironment

try:
    from ..models import Action, Observation, Reward
except ImportError:
    from models import Action, Observation, Reward


app = FastAPI(title="Customer Support Agent Environment", root_path="/web")
env = CustomerSupportEnvironment()


@app.get("/")
def root() -> Dict[str, Any]:
    return {"env": "customer_support_agent", "status": "ok"}


class ResetRequest(BaseModel):
    issue_type: Optional[str] = None


class StepRequest(BaseModel):
    action: Action


class StepResponse(BaseModel):
    state: Observation
    reward: Reward
    done: bool
    error: Optional[str] = None


@app.post("/reset")
def reset_environment(request: ResetRequest) -> Dict[str, Any]:
    state = env.reset(issue_type=request.issue_type)
    return {"state": state.model_dump()}


@app.get("/state")
def get_state() -> Dict[str, Any]:
    return {"state": env.state().model_dump()}


@app.post("/step")
def step_environment(request: StepRequest) -> StepResponse:
    state, reward, done, error = env.step(request.action.model_dump(exclude_none=True))
    return {
        "state": state,
        "reward": reward,
        "done": done,
        "error": error,
    }


def main() -> None:
    uvicorn.run("app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
