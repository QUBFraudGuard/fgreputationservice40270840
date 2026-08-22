# Python screening service — the only service with business logic.
# Built and run as an individual container (no docker-compose)
FROM python:3.12-slim
WORKDIR /app

# Install dependencies first so this layer caches across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# app.py runs Flask on 0.0.0.0:5000.
CMD ["python", "app.py"]
