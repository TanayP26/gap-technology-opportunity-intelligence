FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN python -m pip install --no-cache-dir .

CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8050}"]