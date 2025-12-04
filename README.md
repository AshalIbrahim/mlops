# Zameen MLOps

One-line pitch: A reproducible end-to-end MLOps stack for Zameen property price prediction — training, model registry (MLflow), monitoring, and a FastAPI inference service with a React frontend.

---

## Architecture (Data → Training → Inference)

```mermaid
flowchart LR
	A[Data Ingestion] -->|CSV / MySQL| B[Data Lake / DB]
	B --> C[Feature Engineering & Training]
	C --> D[MLflow Tracking & Registry]
	D --> E[Model Artifacts (mlruns/ & artifact store)]
	E --> F[Inference (FastAPI backend)]
	F --> G[Frontend (React)]
	E --> H[Monitoring: Evidently / Prometheus / Grafana]
	H --> I[Dashboards & Alerts]
```

Notes: the repo contains a `backend/` FastAPI service, `frontend/` React app (Vite), and local MLflow artifacts under `mlruns/`.

---

## Quick start (local / development)

Prerequisites

- Git
- Docker & Docker Compose (recommended)
- Python 3.10+ (if running services locally without Docker)
- Node.js 18+ (for frontend)

Clone and go to project

```powershell
git clone https://github.com/AshalIbrahim/mlops.git
cd mlops
```

Option A — Run everything with Docker Compose (recommended)

```powershell
docker-compose up --build
# This starts backend (8000), frontend (5173), and mlflow server (5000)
```

Option B — Run services locally (PowerShell examples)

# 1) Python environment
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install mlflow
```

# 2) Start MLflow server (local tracking + artifact root uses ./mlruns)
```powershell
mlflow server --backend-store-uri sqlite:///mlflow.db `
	--default-artifact-root "file:./mlruns" `
	--host 127.0.0.1 --port 5000
# If `mlflow` is not found, run `pip install mlflow` inside the activated venv
```

# 3) Backend (FastAPI)
```powershell
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

# 4) Frontend
```powershell
cd frontend
npm install
npm run dev
```

Environment variables (examples)

- MLFLOW_TRACKING_URI — default in repo: `http://127.0.0.1:5000` (or Docker: `http://mlflow:5000`)
- DATABASE_URL / MySQL connection: repo uses local MySQL settings in `backend/app.py` (host=localhost, user=root, password=1234, database=zameen)

---

## Makefile (recommended targets explained)

This repo doesn't require a Makefile to run, but here are recommended targets to add to `Makefile`:

- `make dev` — build and run services locally (docker-compose up --build)
- `make test` — run `pytest` and fail on coverage threshold
- `make lint` — run `ruff` and `black --check` for formatting and linting
- `make docker` — build docker images (`docker-compose build`)
- `make clean` — remove temp files, prune Docker images/containers used by this project

Example `Makefile` snippets (suggested)

```makefile
dev:
	docker-compose up --build

test:
	pytest -q --cov=.

lint:
	ruff check . && black --check .

docker:
	docker-compose build
```

---

## FAQ / Troubleshooting

- Problem: `mlflow : The term 'mlflow' is not recognized ...`
	- Cause: `mlflow` is not installed into the active Python environment or you are not running inside the venv.
	- Fix: Activate the venv and `pip install mlflow`, or run MLflow inside Docker (docker-compose starts mlflow automatically).

- Backend cannot load model (500 error):
	- Confirm `MLFLOW_TRACKING_URI` is reachable and the MLflow server is running at that URI.
	- Check `mlruns/` and the registry for the model name `ZameenPriceModelV2` (the backend expects that name by default).

- Database connection errors:
	- The backend assumes a local MySQL server (host=localhost, user=root, password=1234). Update `backend/app.py` or set env vars to match your DB credentials.

Windows-specific tips

- Use PowerShell with an activated venv: `python -m venv .venv; .\.venv\Scripts\Activate.bat`.
- If using WSL2, run Docker and commands inside the Linux subsystem for fewer permission issues.

---

## ML workflow & Monitoring

- MLflow Tracking URI (local): `http://127.0.0.1:5000` (or in Docker compose: `http://mlflow:5000`). The repo stores artifacts locally in `./mlruns/`.
- Registered model(s) in this repo: `ZameenPriceModel`, `ZameenPriceModelV2` (backend uses `ZameenPriceModelV2` by default).

Model registry note

The backend loads the model by models:/ URI:

```py
model_uri = "models:/ZameenPriceModelV2/Production"
```

If the models:/ registry approach fails, the backend falls back to downloading artifacts from the run and loading the model artifact directly.

Evidently (data drift)

- The project references an Evidently dashboard — run it locally and point to the stored metrics or configure it with the model's reference dataset. Example: Evidently dashboard at `http://localhost:7000`.

Prometheus + Grafana

- Suggested metrics to collect:
	- Request latencies (FastAPI middleware)
	- Prediction counts and error rates
	- Model inference time
	- Resource utilization (CPU / memory)

- You can run Prometheus + Grafana in Docker and import panels that query the FastAPI /metrics endpoint (or use an exporter).

Screenshot / dashboard links

- Local dashboards are available after you run the monitoring stack. (Include screenshots in this repo under `docs/` if available.)

---

## API documentation (FastAPI)

- The backend is a FastAPI app (see `backend/app.py`) and exposes auto-generated docs at `http://localhost:8000/docs`.

Endpoints (selected)

- GET `/` — health
- GET `/listings` — sample property listings (query `limit`)
- GET `/locations` — available locations (used by frontend)
- POST `/predict` — predict property price

Prediction JSON schema (request)

```json
{
	"coveredArea": 1200.0,
	"beds": 3,
	"bathrooms": 2,
	"location": "Gulberg",
	"propType": "House",
	"purpose": "sale"
}
```

Example cURL (PowerShell / curl)

```powershell
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"coveredArea":1200,"beds":3,"bathrooms":2,"location":"Gulberg","propType":"House","purpose":"sale"}'
```

Example response

```json
{
	"prediction": 12500000.0,
	"formatted_price": "PKR 12,500,000.00"
}
```

Notes: field names follow the `PredictionInput` Pydantic model in `backend/app.py`.

---

## Cloud Integration — ☁️ Cloud Deployment

Recommended minimal cloud setup (two examples):

1) AWS: EC2 (for app) + S3 (artifact storage)

- Why: EC2 gives a simple VM to run containers or services; S3 is inexpensive, durable, and MLflow supports S3 as artifact store.
- How to reproduce (high level):
	- Create an S3 bucket, grant access via IAM role/user.
	- Launch an EC2 instance (t3.medium), install Docker, clone repo, run `docker-compose` after setting `MLFLOW_S3_ENDPOINT` and AWS credentials.
	- Configure MLflow server with `--default-artifact-root s3://<bucket>/artifacts` and `--backend-store-uri mysql+pymysql://user:pass@dbhost/mlflow` (or use sqlite for small setups).
	- Update backend env `MLFLOW_TRACKING_URI` to the public EC2 URL (or internal load balancer).

2) Azure: VM (or Azure App Service) + Azure Blob Storage

- Why: Blob Storage integrates well with Azure services and is supported by MLflow as an artifact store.
- How to reproduce (high level):
	- Create a Storage account & container.
	- Deploy backend as a container or VM and configure MLflow to use the Blob container as artifact storage.

How ML workflow interacts with cloud services

- Data lands in object storage (S3/Blob) or a cloud DB. Training jobs (on EC2/VM/container or a managed service) write metrics and artifacts to MLflow (backend registered in RDS or Cloud SQL). The inference service pulls the model from the MLflow registry/artifact store and serves predictions.

Annotated screenshots

- Add cloud console screenshots to `docs/cloud-screenshots/` for reproducibility (not included in repo by default).

---

## Security & Compliance

- LICENSE: this repository currently does not include a `LICENSE` file. Add a license (MIT / Apache-2.0) at the repo root. Example: `LICENSE (MIT)`.
- CODE_OF_CONDUCT.md: not found — consider adding one to clarify community expectations.

Dependency scanning

- Recommended: run `pip-audit` in CI. Example:

```powershell
pip install pip-audit
pip-audit
```

- Configure CI to fail on Critical CVEs (example in CI script).

---

## Monitoring / Testing Proofs (CI)

- CI expectations (recommended CI `.github/workflows/ci.yml`):
	- Lint: `ruff` + `black --check`
	- Tests: `pytest` with coverage goal >= 80%
	- Docker build: `docker-compose build`
	- Optional: Canary deploy + acceptance tests (integration against staging endpoint)

- This repo currently does not contain `.github/workflows/ci.yml`. Add a CI config that runs the above checks.

---

## Files of interest

- `backend/app.py` — FastAPI service and MLflow model loader (uses model `ZameenPriceModelV2` by default)
- `frontend/` — React app (Vite)
- `docker-compose.yml` — starts backend, frontend, and mlflow services
- `mlruns/` — local MLflow artifacts and registered models

---

## Try it (quick)

1) Start docker-compose:

```powershell
docker-compose up --build
```

2) Visit:

- FastAPI docs: http://localhost:8000/docs
- MLflow UI: http://localhost:5000
- Frontend: http://localhost:5173

---

## Next steps / PR checklist

- Add `LICENSE` (MIT) and `CODE_OF_CONDUCT.md`
- Add CI workflow at `.github/workflows/ci.yml` that runs lint, tests, coverage, and docker build
- (Optional) Add monitoring stack `docker-compose.monitor.yml` for Prometheus/Grafana/Evidently

---

If you'd like, I can: (1) create a `LICENSE` file (MIT), (2) add a starter `.github/workflows/ci.yml`, or (3) add a `Makefile` with the recommended targets. Tell me which and I'll add them.

