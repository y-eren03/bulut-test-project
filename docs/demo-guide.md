# Demo Guide and Screenshot Checklist

Use this guide before preparing `docs/slides.pdf` and `docs/final-report.pdf`.

## Required Screenshots

Save the screenshots under `docs/screenshots/` with clear names.

| File name | What to show | Where it is used |
| --- | --- | --- |
| `01-app-ui.png` | To-Do List Manager cyber operations UI with at least three tasks and one tag | slides, final report |
| `02-api-docs.png` | FastAPI Swagger page showing the REST endpoints | final report |
| `03-pytest-coverage.png` | pytest coverage result, ideally `--cov=src --cov-report=term-missing` or HTML coverage | slides, final report |
| `04-github-actions.png` | green CI workflow with lint, pytest, docker build, deploy validation, smoke test | slides |
| `05-docker-compose.png` | running API, PostgreSQL, LocalStack, Prometheus, and Grafana containers | final report |
| `06-localstack-s3.png` | S3 bucket or uploaded task attachment in LocalStack | final report |
| `07-grafana-dashboard.png` | request rate, P95 latency, and HTTP status panels | slides, final report |
| `08-k6-results.png` | terminal output with `http_req_duration` and p95 latency | slides, final report |
| `09-playwright-e2e.png` | Playwright E2E run or browser automation result | slides |
| `10-minikube.png` | `kubectl get pods` and service output | final report |

## Local Demo Flow

1. Start the stack:

```bash
docker-compose up -d --build
```

2. Open the main screens:

- App: http://localhost:8000
- API docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

3. Run verification commands:

```bash
pytest --cov=src --cov-report=term-missing
newman run postman/collection.json
k6 run perf/load-test.js
pytest tests/e2e/test_ui.py --headed
```

4. For Kubernetes demo:

```bash
minikube start
minikube docker-env | Invoke-Expression
docker build -t todo-list-manager:latest .
kubectl apply -f k8s/
kubectl get pods
kubectl get svc
```

## 7-Minute Live Demo Script

| Time | Action |
| --- | --- |
| 0:00-1:00 | Show PR or recent commit and GitHub Actions starting |
| 1:00-2:00 | Explain CI steps: Black, pytest coverage, Docker build |
| 2:00-3:00 | Show Kubernetes manifests and Minikube pod/service status |
| 3:00-4:00 | Show app UI and create a tagged security task |
| 4:00-5:00 | Run Newman smoke collection |
| 5:00-6:00 | Run k6 and show p95 latency |
| 6:00-7:00 | Show Grafana metrics and Playwright E2E result |

Keep a recorded backup demo ready in case the live environment fails.
