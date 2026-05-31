# Performans Testi Raporu

## Senaryo

k6 senaryosu `GET /tasks` endpointine 10 sanal kullanıcı ile 30 saniye boyunca istek gönderir. Amaç listeleme endpointinin temel okuma yükü altında kararlı kalmasını ve p95 yanıt süresinin proje hedefi olan 500 ms altında olmasını doğrulamaktır.

```bash
k6 run perf/load-test.js
```

## Kabul Kriteri

`perf/load-test.js` içinde aşağıdaki threshold tanımlıdır:

```javascript
http_req_duration: ['p(95)<500']
```

Bu eşik, koşumdaki isteklerin yüzde 95'inin 500 ms altında tamamlanmasını bekler. CI içinde performans testi zorunlu kapı olarak koşturulmaz; canlı demo ve raporlamada yerel ortamda çalıştırılır.

## Ölçüm ve Yorum

Yerel koşum çıktısı `docs/screenshots/08-k6-results.png` içinde belgelenmiştir. Sonuçlar, listeleme endpointinin küçük ölçekli demo yükü altında hedeflenen p95 sınırını karşıladığını göstermektedir. Daha yüksek trafik için sonraki adım olarak test süresi, sanal kullanıcı sayısı ve yazma endpointlerini de kapsayan karma senaryolar artırılabilir.
