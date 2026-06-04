# To-Do List Manager

Bulut Mimarilerinde Test Mühendisliği dersi için geliştirilmiş, test odaklı ve bulut tabanlı bir mikroservis projesidir. Bu proje, uçtan uca test süreçlerini (Unit, Integration, E2E), CI/CD pipeline'ını ve performans izleme (Monitoring) altyapısını içerir.

## Üye listesi
- Yusuf Eren ÇELEBİ (170424826)
- MHD DIAA ALSEBAI (170423954)

## Teknolojiler ve Araçlar

- **Backend:** FastAPI (Python), SQLAlchemy
- **Veritabanı:** PostgreSQL, SQLite (Testler için)
- **AWS Emülasyonu:** LocalStack (S3 - Dosya yükleme)
- **Test Araçları:** Pytest, Playwright (E2E), Testcontainers, Factory-Boy, Faker
- **API Testleri:** Postman & Newman
- **Performans Testi:** k6
- **Monitoring & Tracing:** Prometheus, Grafana, OpenTelemetry, Jaeger
- **Dağıtım, Konteyner & GitOps:** Docker, Docker Compose, Kubernetes (Minikube), Helm, ArgoCD
- **CI/CD:** GitHub Actions

## Kurulum ve Çalıştırma

### Gereksinimler
- Docker & Docker Compose
- Minikube & kubectl
- Python 3.11+ & Poetry

### Lokal Geliştirme (Docker Compose)
Tüm sistemi (Uygulama, Veritabanı, LocalStack, Prometheus, Grafana) tek komutla ayağa kaldırmak için:
```bash
docker-compose up -d
```
- Uygulama: `http://localhost:8000`
- API Dokümantasyonu (Swagger): `http://localhost:8000/docs`
- Grafana Dashboard: `http://localhost:3000`

### Bağımlılıkların Kurulması
```bash
poetry install
```

## Canlı Demo / Sunum İçin Hızlı Başlangıç

Sunum veya demo esnasında tüm sistemi ve ArgoCD arayüzünü hızlıca ayağa kaldırmak için sırasıyla şu komutları çalıştırın:

```bash
# 1. Uygulama ve metrik servislerini arka planda başlat
docker-compose up -d

# 2. (Gerekliyse) ArgoCD namespace'ini oluştur
kubectl create namespace argocd

# 3. ArgoCD arayüzüne erişim için port yönlendirmesini başlat
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
*Bu komutları çalıştırdıktan sonra uygulamanıza `http://localhost:8000`, ArgoCD arayüzüne ise `https://localhost:8080` adreslerinden erişebilirsiniz.*

## Testlerin Çalıştırılması

Proje %80 üzerinde test coverage oranına sahiptir. Testleri çalıştırmak için aşağıdaki komutları kullanabilirsiniz:

**Birim (Unit) Testleri:**
```bash
python -m poetry run pytest tests/unit --cov=src
```

**Entegrasyon (Integration) Testleri:**
```bash
python -m poetry run pytest tests/integration
```

**Uçtan Uca (E2E) Testleri (Playwright):**
```bash
# İlk çalıştırmada tarayıcıların indirilmesi gerekebilir:
# python -m playwright install chromium
python -m poetry run pytest tests/e2e -v
```

**Yük ve Performans Testi (k6):**
```bash
k6 run perf/load-test.js
```

## Kubernetes (Minikube) Dağıtımı

Uygulamayı Minikube üzerinde çalıştırmak için:
```bash
# Minikube'ü başlatın
minikube start

# İmajı Minikube içerisine derleyin
minikube image build -t todo-list-manager:latest .

# Manifestleri uygulayın
kubectl apply -f k8s/

# Pod'ların durumunu kontrol edin
kubectl get pods
```

## CI/CD (GitHub Actions)
Projeye yapılan her `push` ve `pull_request` işlemi GitHub Actions tarafından otomatik olarak test edilir.
Adımlar:
1. `black` ile kod formatlama kontrolü
2. Pytest ile unit/integration testleri ve %70 coverage zorunluluğu
3. Newman ile Postman API testleri
4. Docker imajının build edilmesi

## Canlı Demo Videosu
Sunum yedek videosu eklenecektir: https://drive.google.com/file/d/1OspPplRVJ4-kCvRXSKRqPPkU2-JREnUF/view?usp=sharing

---
*Marmara Üniversitesi - Bulut Mimarilerinde Test Mühendisliği Dönem Projesi*
