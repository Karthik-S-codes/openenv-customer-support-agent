# OpenEnv Customer Support Agent

Round 1 OpenEnv submission for a multi-step Customer Support Agent environment.

The environment simulates real support workflows across three issue types:

- Refund
- Delivery delay
- Payment failure

Each episode follows three phases:

1. Classify issue
2. Generate response
3. Resolve issue

## Submission Links

- GitHub Repository: https://github.com/Karthik-S-codes/openenv-customer-support-agent
- Hugging Face Space: https://huggingface.co/spaces/Karthis7482/customer-support-env
- Live Runtime URL: https://karthis7482-customer-support-env.hf.space

## Repository Structure

Main implementation lives in the my_env folder.

- my_env/openenv.yaml: OpenEnv config and task wiring
- my_env/inference.py: baseline inference runner
- my_env/server/your_environment.py: environment logic
- my_env/server/app.py: FastAPI endpoints
- my_env/tasks/easy.py: easy grader
- my_env/tasks/medium.py: medium grader
- my_env/tasks/hard.py: hard grader
- my_env/Dockerfile: deployment container

## API Endpoints

- GET /
- POST /reset
- GET /state
- POST /step
- GET /docs

## Local Run

From repository root:

1. cd my_env
2. openenv validate
3. python inference.py --agent rule_based
4. uvicorn server.app:app --host 0.0.0.0 --port 8000

## Deployment

1. cd my_env
2. openenv validate
3. openenv push -r Karthis7482/customer-support-env

## Deployment Verification

After deployment, verify:

- Space page opens and shows Running status
- /docs loads successfully
- POST /reset returns state JSON
- POST /step progresses episode state and reward

## Notes

- Inference uses OpenAI client pattern with environment variables:
	API_BASE_URL, MODEL_NAME, HF_TOKEN
- Default values are set only for API_BASE_URL and MODEL_NAME
- HF_TOKEN is never hardcoded
