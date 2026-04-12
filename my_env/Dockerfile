FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --retries 5 --timeout 100 -r requirements.txt

COPY . /app

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]