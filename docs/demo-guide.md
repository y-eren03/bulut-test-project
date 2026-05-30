# To-Do List Manager - Canlı Demo ve Ekran Görüntüsü Kılavuzu

Bu kılavuz, **Bulut Mimarilerinde Test Mühendisliği** dersi dönem projenizin **7 Dakikalık Canlı Demo** sunumunu başarıyla yapabilmeniz ve sunum slaytları ile final raporu için gerekli **ekran görüntülerini (screenshots)** nasıl alacağınızı adım adım açıklamaktadır.

---

## 1. Hangi Ekran Görüntüleri Gerekli ve Nasıl Alınır?

Sunum slaytlarınız ve final raporunuz için aşağıdaki ekran görüntülerini yerel (local) ortamınızda alıp `docs/` klasörüne kaydetmeniz gerekmektedir:

### A. Test Coverage Raporu (Pytest HTML)
*   **Amaç:** Test stratejisi ve "Sayılar" slaytı için test kapsama oranını göstermek.
*   **Nasıl Alınır?**
    1.  Proje dizininde terminali açın.
    2.  Şu komutu çalıştırarak HTML raporu oluşturun:
        ```bash
        python -m poetry run pytest --cov=src --cov-report=html
        ```
    3.  Oluşan `htmlcov/index.html` dosyasını tarayıcınızda açın.
    4.  Tabloyu ve **Overall Coverage (örn: %75+)** değerini net şekilde gösterecek bir ekran görüntüsü alın.

### B. Grafana Metrik Dashboard Paneli
*   **Amaç:** Monitoring & Observability slaytı ve canlı demo hazırlığı.
*   **Nasıl Alınır?**
    1.  Docker Compose ile izleme araçlarını ayağa kaldırın (Aşağıdaki Kurulum bölümüne bakın).
    2.  Tarayıcıda `http://localhost:3000` adresine gidin (Grafana).
    3.  `monitoring/grafana-dashboard.json` şablonunu import edin.
    4.  Sisteme biraz yük gönderdikten sonra (k6 çalıştırarak) Grafana üzerindeki **P95 Latency, Request Rate ve Error Rate** grafiklerinin ekran görüntüsünü alın.

### C. k6 Load Test Sonuçları (Terminal Ekranı)
*   **Amaç:** "Sayılar" ve "Performans" slaytları için p95 latency verilerini göstermek.
*   **Nasıl Alınır?**
    1.  Yerel API çalışırken terminalden k6 testini koşun:
        ```bash
        k6 run perf/load-test.js
        ```
    2.  Test bittiğinde terminale basılan özet tablonun (özellikle `http_req_duration: p(95)=...ms` satırını içerecek şekilde) ekran görüntüsünü alın.

### D. Playwright E2E UI Test Koşumu
*   **Amaç:** Canlı E2E test koşumunu ve arayüzü görselleştirmek.
*   **Nasıl Alınır?**
    1.  Playwright UI testini çalıştırın:
        ```bash
        python -m poetry run pytest tests/e2e/test_ui.py --headed
        ```
    2.  Veya tarayıcıda uygulamanın ana sayfasını (`http://localhost:8000`) açıp temiz, premium bir ekran görüntüsü alın.

---

## 2. Yerel (Local) Ortamı Canlı Demo İçin Hazırlama Adımları

Canlı demodan en az 1 saat önce yerel bilgisayarınızda şu servisleri ayağa kaldırıp her şeyin çalıştığından emin olun:

### Adım 1: Docker Compose ile Altyapıyı Çalıştırın
LocalStack (S3 için), Prometheus ve Grafana bileşenlerini başlatın:
```bash
docker-compose up -d
```
*   **Kontrol:** `docker ps` komutuyla `api`, `db`, `localstack`, `prometheus` ve `grafana` servislerinin sorunsuz çalıştığını doğrulayın.

### Adım 2: Minikube'ü Başlatın (K8s Sunumu İçin)
Demoda Kubernetes deployment'ı gösterebilmek için:
```bash
minikube start
```
Kubernetes manifestlerinizi uygulayın:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```
*   **Kontrol:** `kubectl get pods` komutuyla pod'ların `Running` durumunda olduğunu görün.

---

## 3. Canlı Demo Akış Planı (7 Dakika - Dakika Dakika)

Jüri karşısında heyecanlanmamak ve 7 dakikayı tam doldurmak için bu akışı takip edin. **(Önemli: Ekranınızda tarayıcı sekmelerini önceden sırayla dizin!)**

| Süre | Adım | Ne Yapacaksınız? | Ne Söyleyeceksiniz? |
| :--- | :--- | :--- | :--- |
| **0:00 - 1:00** (1 dk) | **PR Açma & CI** | GitHub üzerinde küçük bir kod değişikliği yapıp (örn: `src/main.py` içerisine küçük bir açıklama satırı ekleyip) yeni bir dalda (branch) Pull Request (PR) açın. GitHub Actions'ın hemen tetiklendiğini jüriye gösterin. | *"Şimdi canlı olarak yeni bir geliştirme için PR açıyorum. Arka planda GitHub Actions hemen tetiklendi; kod standartları için Black linting yapıyor ve ardından pytest ile testleri koşturuyor."* |
| **1:00 - 2:00** (1 dk) | **PR Merge & CD** | PR'ı merge edin. GitHub Actions üzerinde CD (Continuous Deployment) adımının tetiklendiğini, yeni Docker imajının build edilip push edildiğini gösterin. | *"Testlerimiz başarıyla tamamlandı. PR'ı ana dala (main) merge ediyorum. Şimdi CD pipeline tetiklendi, yeni Docker imajı otomatik olarak derleniyor."* |
| **2:00 - 3:00** (1 dk) | **K8s / Minikube** | Terminali veya Minikube Dashboard'ı açın. `kubectl get pods -w` ile eski pod'ların sonlanıp yeni pod'ların (Rolling Update) ayağa kalktığını canlı gösterin. | *"Kubernetes kümemiz üzerinde Minikube kullanarak rolling update stratejisiyle sıfır kesinti (zero-downtime) ile yeni sürümü deploy ediyoruz. Gördüğünüz gibi yeni pod'lar sırayla ayağa kalkıyor."* |
| **3:00 - 4:00** (1 dk) | **Grafana & Metrikler** | Tarayıcıda Grafana sekmesine geçin. | *"Prometheus ve Grafana entegrasyonumuz sayesinde uygulamamızın CPU, RAM, API yanıt sürelerini (latency) ve gelen istek sayılarını anlık olarak izleyebiliyoruz."* |
| **4:00 - 5:00** (1 dk) | **k6 Load Test** | Terminalde `k6 run perf/load-test.js` komutunu çalıştırın. Koşarken Grafana'da metriklerin anlık yükselişini gösterin. | *"Şimdi k6 ile sisteme 10 eşzamanlı kullanıcıyla yük testi gönderiyorum. Grafana ekranımızda istek oranının (RPS) arttığını ve P95 latency'nin hedeflediğimiz 500ms sınırının altında kaldığını canlı görebiliriz."* |
| **5:00 - 6:30** (1.5 dk) | **Playwright E2E** | Terminalden `python -m poetry run pytest tests/e2e/test_ui.py --headed` çalıştırın. Tarayıcının otomatik açılıp görev eklemesini, tamamlamasını izletin. | *"Son olarak, kullanıcı deneyimini test etmek için Playwright ile E2E (uçtan uca) testlerimizi koşturuyorum. Gördüğünüz gibi tarayıcı otomatik açıldı, forma görev bilgilerini girdi, ekleme ve tamamlama senaryolarını başarıyla simüle etti."* |
| **6:30 - 7:00** (0.5 dk) | **Kapanış / Buffer** | Sorulara geçiş yapın. | *"Canlı demomuz bu kadar. Sorularınızı alabilirim."* |

---

## 4. Hayat Kurtaran Demo İpuçları (B Planı)

*   **Yedek Ekran Kaydı Alın (ZORUNLU B PLANI):**
    *   Demoyu yapmadan önce, yerelinizde her şey kusursuz çalışırken yukarıdaki 7 dakikalık akışı baştan sona kaydedin (OBS Studio veya Windows Game Bar `Win + Alt + R` ile).
    *   Bu videoyu slaytların hemen sonrasına yedek olarak koyun. Canlıda hata alırsanız hiç vakit kaybetmeden: *"Küçük bir yerel bağlantı sorunu yaşıyorum, o yüzden izninizle sistemin birebir çalışmasını kaydettiğim yedek demom üzerinden devam edeceğim"* diyerek videoyu oynatın. Jüri bu profesyonelliğe bayılacaktır.
*   **Sekmeleri Hazırlayın:** Tarayıcınızda sırasıyla; GitHub PR sayfası, GitHub Actions akışı, API arayüzü (`localhost:8000`), Grafana (`localhost:3000`) sekmelerini açık tutun.
*   **Terminal Geçmişini Temizleyin:** Terminalinizde daha önceki hata logları veya gereksiz karmaşalar olmasın. Temiz bir `clear` çekin.
