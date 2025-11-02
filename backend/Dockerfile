# ---- Stage 1: Build ----
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies for mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Pre-download the model
RUN mkdir -p model_cache && python -c "from app import load_model; load_model()"

# ---- Stage 2: Final ----
FROM python:3.10-slim

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy app code and pre-downloaded model
COPY --from=builder /app /app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
