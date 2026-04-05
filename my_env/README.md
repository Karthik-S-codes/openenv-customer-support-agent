---
title: Customer Support Agent OpenEnv
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Customer Support Agent OpenEnv

## Environment Motivation

This project simulates real customer support workflows where an agent must:

1. Classify the user issue
2. Generate an appropriate response
3. Resolve the case

It models practical support tasks for refund requests, delivery delays, and payment issues.

## Observation, Action, and Reward Spaces

### Observation

The environment state includes:

- `env_name`
- `step_index`
- `phase` (`classify_issue`, `generate_response`, `resolve_issue`, `completed`)
- `customer_query`
- `done`
- `progress` (`completed_steps`, `total_steps`, `completion_ratio`)
- `history`
- `summary` (correct/partial flags and cumulative reward)

Typed model: `Observation` in `models.py`.

### Action

The agent sends one action per step with one of these fields:

- `issue_type` or `classification` for step 1
- `response` for step 2
- `resolution` for step 3

Typed model: `Action` in `models.py`.

### Reward

Per-step reward rules:

- Classification:
	- correct: `+0.4`
	- wrong: `-0.2`
- Response:
	- correct: `+0.4`
	- partial: `+0.2`
	- wrong: `-0.2`
- Resolution:
	- correct: `+0.2`
	- partial: `+0.1`
	- wrong: `-0.2`

Invalid or missing action keys return a negative reward and an explicit error message.

Typed model: `Reward` in `models.py`.

## Tasks and Difficulty

Three grader tasks are provided:

1. `easy`: classification only (score `1.0` or `0.0`)
2. `medium`: classification + response (`0.5 + 0.5`, with `0.25` for partial response)
3. `hard`: classification + response + resolution (`0.4 + 0.4 + 0.2`, with partial credits)

Task files are under `tasks/`.

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install openenv-core fastapi uvicorn openai
```

## Usage

Validate project:

```bash
openenv validate
```

Run inference (rule-based baseline):

```bash
python inference.py --agent rule_based
```

Run inference (OpenAI-compatible endpoint):

Required environment variables:

- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`

Then run:

```bash
python inference.py --agent openai
```

Run local API:

```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Available endpoints:

- `GET /`
- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /docs`

## Docker

```bash
docker build -t customer-support-env .
docker run --rm -p 7860:7860 customer-support-env
```

## Deployment

```bash
openenv push -r Karthis7482/customer-support-env
```

Deployed Space:

- Space page: `https://huggingface.co/spaces/Karthis7482/customer-support-env`
- Live API: `https://karthis7482-customer-support-env.hf.space`

## Baseline Scores

Sample hard-task baseline (rule-based):

- Step rewards: `0.40, 0.40, 0.20`
- Final result: success `true`

Scores are task-dependent, non-constant, and remain in `0.0-1.0` range through graders.
