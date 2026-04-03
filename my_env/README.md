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
- `history`
- `summary` (correctness flags and cumulative reward)

Typed model: `Observation` in `models.py`.

### Action

The agent sends one action per step with one of these fields:

- `issue_type` or `classification` for step 1
- `response` for step 2
- `resolution` for step 3

Typed model: `Action` in `models.py`.

### Reward

Per-step reward rules:

- Positive reward for correct actions (`+0.4`, `+0.4`, `+0.2`, weighted by scenario)
- Negative reward for wrong actions (`-0.2`)

Typed model: `Reward` in `models.py`.

## Tasks and Difficulty

Three grader tasks are provided:

1. `easy`: classification only (score `1.0` or `0.0`)
2. `medium`: classification + response (`0.5 + 0.5`)
3. `hard`: classification + response + resolution (`0.4 + 0.4 + 0.2`)

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
cd server
uvicorn app:app --host 0.0.0.0 --port 8000
```

Available endpoints:

- `POST /reset`
- `POST /step`
- `GET /state`

## Docker

```bash
docker build -t customer-support-env .
docker run --rm -p 8000:8000 customer-support-env
```

## Baseline Scores

Sample hard-task baseline (rule-based):

- Step rewards: `0.40, 0.40, 0.20`
- Final result: success `true`

Scores are task-dependent and remain in `0.0-1.0` range through graders.
