# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY requirements.txt .

# Install system packages needed to build mysqlclient (or similar)
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt


COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
