# To-Do List Manager

Bulut Mimarilerinde Test Mühendisliği dönem projesi için hazırlanmış küçük bir FastAPI mikroservisi. Uygulama görev oluşturma, listeleme, tamamlama ve göreve dosya eki yükleme akışlarını içerir. Dosya ekleri LocalStack üzerinde çalışan S3 servisine gönderilir.

## Kapsam

- FastAPI tabanlı mini servis: 2 entity, 6 temel endpoint
- Pytest unit, integration ve Playwright E2E testleri
- Factory Boy + Faker ile test verisi üretimi
- Postman koleksiyonu ve Newman smoke koşumu
- Multi-stage Dockerfile ve docker-compose geliştirme ortamı
- LocalStack S3 entegrasyonu
- Kubernetes Deployment, Service ve ConfigMap manifestleri
- GitHub Actions: lint, test, coverage, Docker build, deploy dry-run ve smoke
- Prometheus + Grafana monitoring
- k6 performans senaryosu
- Bonus: Helm chart, ArgoCD GitOps manifesti, OpenTelemetry + Jaeger tracing

## Proje Yapısı

```text
src/                 FastAPI uygulaması, modeller ve servisler
tests/               Unit, integration ve E2E testleri
postman/             Newman ile koşan API koleksiyonu
k8s/                 Minikube için Kubernetes manifestleri
charts/              Helm paketleme çıktısı
gitops/              ArgoCD Application manifesti
monitoring/          Prometheus ve Grafana ayarları
perf/                k6 senaryosu ve performans raporu
docs/                Final rapor, slayt, mimari diyagram ve demo dokümanları
```

## Yerel Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Uygulama: `http://localhost:8000`

API dokümantasyonu: `http://localhost:8000/docs`

## Docker Compose ile Çalıştırma

```bash
docker-compose up --build
```

Servisler:

- API: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Jaeger: `http://localhost:16686`
- LocalStack S3: `http://localhost:4566`

## Testler

```bash
pytest --cov=src --cov-fail-under=70
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

Postman/Newman:

```bash
newman run postman/collection.json --working-dir .
```

Performans testi:

```bash
k6 run perf/load-test.js
```

## Kubernetes ve Bonus Kurulumları

Minikube manifestleri:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Helm:

```bash
helm lint charts/todo-list-manager
helm install todo-list-manager charts/todo-list-manager
```

ArgoCD:

```bash
kubectl apply -n argocd -f gitops/argocd-application.yaml
```

Bonus anlatım notları: `docs/bonus-guide.md`

## Teslim Dosyaları

- `docs/final-report.pdf`
- `docs/slides.pdf`
- `docs/architecture.png`
- `docs/work-distribution.md`
- `docs/demo-guide.md`

Yedek demo videosu bağlantısı teslimden önce buraya eklenmelidir: `Drive/YouTube demo linki`

## Lisans

Bu proje MIT lisansı ile yayınlanmıştır.
