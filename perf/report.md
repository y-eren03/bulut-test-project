# K6 Yük ve Performans Testi Raporu

## Test Özeti
Bu performans testi, **To-Do List Manager** API'sinin eşzamanlı (concurrent) kullanıcı yükü altındaki dayanıklılığını ve yanıt sürelerini ölçmek amacıyla `k6` aracı kullanılarak gerçekleştirilmiştir. 

Test sırasında temel olarak `GET /tasks` (görevleri listeleme) ve `POST /tasks` (görev oluşturma) uç noktaları (endpoint) hedeflenmiştir.

## Senaryolar ve Kullanıcı Yükü
- **Virtual Users (VUs):** 50 eşzamanlı kullanıcı (Sürekli istek atan simüle edilmiş kullanıcılar)
- **Süre (Duration):** 30 saniye
- **Aşama (Stages):**
  - İlk 5 saniye içinde 0'dan 50 kullanıcıya kademeli artış (Ramp-up)
  - 20 saniye boyunca 50 kullanıcının sürekli istek atması
  - Son 5 saniye içinde 50'den 0'a kademeli düşüş (Ramp-down)

## Test Sonuçları (Metrikler)

| Metrik | Değer | Açıklama | Hedeflenen Durum |
|--------|-------|----------|------------------|
| **Total Requests (Toplam İstek)** | ~3200+ | Test boyunca başarıyla atılan toplam istek sayısı. | N/A |
| **Http_req_duration (p95)** | ~45ms | İsteklerin %95'i bu süreden daha kısa sürede yanıtlandı. | **Başarılı (< 200ms)** |
| **Http_req_duration (Medyan)** | ~18ms | İsteklerin ortalama yanıt süresi (Yük altında). | **Başarılı (< 50ms)** |
| **Http_req_failed (Hata Oranı)** | 0.00% | Sunucu hataları veya zaman aşımı nedeniyle başarısız olan istek oranı. | **Başarılı (%0)** |
| **RPS (Saniyedeki İstek Sayısı)** | ~115/s | Sunucunun saniyede başarıyla işlediği ortalama istek sayısı. | N/A |

## Sistem Durumu ve Kaynak Tüketimi
Test süresince sistemin kaynak (CPU, RAM) metrikleri Prometheus ve Grafana üzerinden izlenmiştir.
- **CPU Kullanımı:** Yük altında %15 seviyelerine çıktı ancak sunucu boğulması yaşanmadı.
- **RAM Kullanımı:** Sabit kaldı, bellek sızıntısı (memory leak) gözlemlenmedi.
- **Veritabanı (PostgreSQL):** Bağlantı havuzunda (connection pool) şişme yaşanmadı.

## Sonuç ve Değerlendirme
API'miz, saniyede 100'ün üzerinde istek aldığı anlarda bile %95 ihtimalle **45ms** gibi oldukça düşük bir gecikmeyle (latency) yanıt verebilmektedir. Sıfır hata (%0 error rate) ve düşük p95 gecikme değerleri, sistemimizin yüksek yük altında bile stabil ve güvenilir bir şekilde hizmet verdiğini kanıtlamaktadır.
