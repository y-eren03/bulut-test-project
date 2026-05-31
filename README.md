# To-Do List Manager

Security operations themed To-Do List Manager built for the Bulut Mimarilerinde Test Muhendisligi term project. The app keeps the domain intentionally small while demonstrating an end-to-end cloud testing pipeline: API, database, LocalStack S3, tests, CI/CD, containerization, Kubernetes, monitoring, performance testing, and E2E UI automation.

## Project Scope

- Mini service: FastAPI application with Task and Tag entities.
- REST API: health, list/create/read/complete/delete task, attach tag, upload S3 attachment, and stats endpoints.
- Database: SQLite locally by default, PostgreSQL in Docker/CI integration flows.
- AWS emulation: LocalStack S3 stores task attachments.
- Test stack: pytest, Factory Boy, Testcontainers, Playwright, Postman/Newman, and k6.
- Observability: Prometheus exporter and Grafana dashboard with request rate, P95 latency, and status code panels.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Open:

- App UI: http://localhost:8000
- API docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## Docker Compose Demo

```bash
docker-compose up -d --build
```

Services:

- API: http://localhost:8000
- LocalStack S3: http://localhost:4566
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana credentials are the default `admin` / `admin` unless changed locally.

## Tests

```bash
pytest --cov=src --cov-report=term-missing
pytest tests/unit
pytest tests/e2e/test_ui.py
newman run postman/collection.json
k6 run perf/load-test.js
```

The full integration test suite uses Testcontainers and requires Docker.

## Kubernetes

For Minikube:

```bash
minikube start
eval $(minikube docker-env)
docker build -t todo-list-manager:latest .
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods
minikube service todo-list-manager-service
```

On Windows PowerShell, use:

```powershell
minikube docker-env | Invoke-Expression
```

## API Summary

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Health check |
| GET | `/tasks` | List tasks |
| POST | `/tasks` | Create task with `title` and optional `description` |
| GET | `/tasks/{task_id}` | Read one task |
| PUT | `/tasks/{task_id}/complete` | Mark task as completed |
| DELETE | `/tasks/{task_id}` | Delete task |
| POST | `/tasks/{task_id}/tags` | Attach a tag with `name` |
| POST | `/tasks/{task_id}/attachment` | Upload attachment to LocalStack S3 |
| GET | `/tasks/stats/overview` | Dashboard statistics |

## Final Deliverables

- `docs/architecture.png`: architecture diagram
- `docs/final-report.pdf`: final report, 4-6 pages
- `docs/slides.pdf`: 7-8 presentation slides
- `docs/demo-guide.md`: demo and screenshot guide
- `perf/report.md`: performance test notes

The PDF report and slides should include real screenshots from the local run: coverage, GitHub Actions, app UI, Grafana, k6, Playwright, Docker/Minikube, and LocalStack S3.
