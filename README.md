# OpenEnv Customer Support Agent

Production-style OpenEnv environment for customer support automation.

## 1. Project Overview

This project simulates a realistic customer support workflow where an agent must handle user issues across multiple phases and return high-quality actions under constrained labels.

Supported issue families:

- refund
- delivery
- payment

Episode flow:

1. classify_issue
2. generate_response
3. resolve_issue
4. completed

## 2. Problem Description

Customer support tickets often include emotion, urgency, and mixed signals (for example payment plus delivery concerns in one message). The goal is to train/evaluate an agent that can:

- classify issue type correctly
- generate a relevant response
- choose a practical resolution outcome

while receiving meaningful per-step feedback and a final normalized task score.

## 3. Environment Design

Core environment file:

- my_env/server/your_environment.py

Design highlights:

- realistic query pool with order IDs, urgency, frustration, and mixed-condition phrasing
- randomized query selection on reset
- strict phase progression with no premature completion
- explicit error handling for invalid/missing action keys
- episode history tracking for auditability

## 4. Observation and Action Spaces

Observation fields include:

- env_name
- step_index
- phase
- customer_query
- done
- previous_actions
- progress (completed_steps, total_steps, completion_ratio)
- history (step-wise action/reward/error)
- summary (correctness, partial correctness, wrong_steps, total_reward)

Action interface by phase:

- classify_issue: issue_type or classification
- generate_response: response
- resolve_issue: resolution

## 5. Reward System

Per-step reward shaping:

- Classification:
	- correct: +0.4
	- close/related: +0.2
	- wrong: -0.2
- Response:
	- correct and label-aligned: +0.4
	- generic but acceptable / partial: +0.2
	- wrong: -0.2
- Resolution:
	- correct: +0.2
	- partial: +0.1
	- wrong: -0.2

Error handling:

- missing required keys -> negative reward and structured error string
- invalid action type -> negative reward and structured error string

## 6. Task Definitions

Task files:

- my_env/tasks/easy.py
- my_env/tasks/medium.py
- my_env/tasks/hard.py

Scoring is always bounded to [0.0, 1.0].

Easy:

- classification only
- score = 1.0 if correct else 0.0

Medium:

- classification + response
- weights: 0.5 + 0.5
- classification is checked against the scenario expected issue type
- partial correctness gives partial credit through domain-aware token rules

Hard:

- classification + response + resolution
- weights: 0.4 + 0.4 + 0.2
- classification is checked against the scenario expected issue type
- partial correctness gives partial credit through domain-aware token rules

## 7. Example Interaction Flow

Sample episode (refund case):

1. Reset:
	- query: "My order #4821 arrived damaged and I want a refund immediately."
	- phase: classify_issue
2. Step 1 action:
	- `{ "issue_type": "refund" }`
	- reward: `+0.4`
	- next phase: generate_response
3. Step 2 action:
	- `{ "response": "refund_policy" }`
	- reward: `+0.4`
	- next phase: resolve_issue
4. Step 3 action:
	- `{ "resolution": "refund_processed" }`
	- reward: `+0.2` (plus bonus when no mistakes)
	- done: true

## 8. Run Locally

From repository root:

```powershell
cd my_env
openenv validate
python inference.py --agent rule_based --task hard --max-steps 6
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Local API and docs:

- http://localhost:8000/state
- http://localhost:8000/docs

## 9. Deployment Details

Deploy target:

- Hugging Face Space: https://huggingface.co/spaces/Karthis7482/customer-support-env
- Live runtime URL: https://karthis7482-customer-support-env.hf.space

Deploy command:

```powershell
cd my_env
openenv validate
openenv push -r Karthis7482/customer-support-env
```

Post-deploy checks:

```powershell
Invoke-RestMethod -Method Get -Uri "https://karthis7482-customer-support-env.hf.space/state"
Invoke-RestMethod -Method Post -Uri "https://karthis7482-customer-support-env.hf.space/reset" -ContentType "application/json" -Body "{}"
```

## Resource and Compatibility Notes

- inference.py remains compatible and unchanged in interface
- openenv validate passes
- Docker image builds and runs on low-resource setup (2 CPU, 8 GB RAM)

## Why This Environment Is Useful

This benchmark is useful for evaluating practical agent capabilities beyond one-shot classification:

- multi-step reasoning under strict phase constraints
- handling ambiguous, emotional, and mixed customer issues
- balancing correctness, partial correctness, and robustness penalties
- producing measurable signals for RL-style optimization and agent comparison
