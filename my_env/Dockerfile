FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV API_BASE_URL=""
ENV MODEL_NAME="gpt-4o-mini"

RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir fastapi uvicorn openai openenv-core

COPY . /app

EXPOSE 7860

CMD ["sh", "-c", "uvicorn server.app:app --host 0.0.0.0 --port ${PORT:-7860}"]