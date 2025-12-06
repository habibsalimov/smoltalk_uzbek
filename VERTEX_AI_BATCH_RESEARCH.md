# Vertex AI Batch API Araştırması - SmolTalk Çeviri Projesi

## 🔍 ARAŞTIRMA SONUCU

**ÖNEMLİ:** Gemini modelleri şu anda **Vertex AI Batch Prediction API'yi desteklemiyor**. Sadece online (real-time) prediction mevcut.

---

## 🎯 ÖNERİLEN ÇÖZÜMLER

### 1. **CLOUD RUN JOBS** (⭐ En İyi Seçenek)

**Avantajları:**
- ✅ Serverless - altyapı yönetimi yok
- ✅ Otomatik scaling
- ✅ Built-in retry mekanizması
- ✅ Sadece kullanım süresine göre ücret
- ✅ 100+ job paralel çalışabilir
- ✅ Her job izole ortamda çalışır

**Nasıl Çalışır:**
```bash
# 1. Docker image oluştur
docker build -t gcr.io/PROJECT_ID/smoltalk-translator .
docker push gcr.io/PROJECT_ID/smoltalk-translator

# 2. Cloud Run Job oluştur
gcloud run jobs create smoltalk-translate \
  --image gcr.io/PROJECT_ID/smoltalk-translator \
  --region us-central1 \
  --parallelism 50 \
  --tasks 100 \
  --max-retries 3

# 3. Job'u çalıştır
gcloud run jobs execute smoltalk-translate
```

**Maliyet:**
- Cloud Run: ~$0.053/saat per job (2 vCPU, 2GB)
- 100 job x 10 saat = **$53**
- **Toplam: $1,350 (Gemini) + $53 (Cloud Run) = $1,403**

**Süre:**
- 100 job paralel → **3-4 gün** ✨

---

### 2. **COMPUTE ENGINE VM CLUSTER**

**Avantajları:**
- ✅ Tam kontrol
- ✅ Daha ucuz (sustained use discount)
- ✅ Daha fazla CPU/RAM ayarlanabilir

**Nasıl Çalışır:**
```bash
# 1. VM template oluştur
gcloud compute instance-templates create smoltalk-worker \
  --machine-type n1-standard-4 \
  --image-family ubuntu-2004-lts \
  --scopes cloud-platform

# 2. Instance group oluştur
gcloud compute instance-groups managed create smoltalk-workers \
  --size 50 \
  --template smoltalk-worker \
  --region us-central1

# 3. Her VM'de translation script çalıştır
```

**Maliyet:**
- n1-standard-4: ~$0.19/saat
- 50 VM x 10 saat = **$95**
- **Toplam: $1,350 + $95 = $1,445**

**Süre:**
- 50 VM x 10 worker = **~7 gün**

---

### 3. **KUBERNETES (GKE)**

**Avantajları:**
- ✅ En esnek çözüm
- ✅ Auto-scaling
- ✅ Job scheduling (Kubernetes Jobs)
- ✅ Resource management

**Dezavantajları:**
- ❌ Kurulum karmaşık
- ❌ Kubernetes bilgisi gerekli
- ❌ Cluster maliyeti ekstra

**Maliyet:**
- GKE cluster: ~$0.10/saat (management fee)
- Nodes: ~$100-150 (50 node x 10 saat)
- **Toplam: $1,350 + $150 = $1,500**

---

## 📊 ÇÖZÜM KARŞILAŞTIRMASI

| Çözüm          | Kurulum | Maliyet | Süre    | Yönetim | Tavsiye |
|----------------|---------|---------|---------|---------|---------|
| Cloud Run Jobs | Kolay   | $1,403  | 3-4 gün | Kolay   | ⭐⭐⭐⭐⭐ |
| Compute Engine | Orta    | $1,445  | 7 gün   | Orta    | ⭐⭐⭐⭐   |
| GKE           | Zor     | $1,500  | 5-7 gün | Zor     | ⭐⭐⭐     |

---

## 🚀 ÖNERİLEN YAKLASHIM: CLOUD RUN JOBS

### Adım 1: Gerekli Dosyaları Hazırla

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Gerekli paketler
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Translation script
COPY translate_batch.py .

CMD ["python", "translate_batch.py"]
```

**requirements.txt:**
```
google-genai
datasets
google-cloud-storage
```

**translate_batch.py:**
- 10 worker ile paralel çeviri
- START_INDEX ve END_INDEX environment variables
- Sonuçları GCS'ye kaydet
- Retry mekanizması

### Adım 2: GCS Bucket Oluştur

```bash
gsutil mb -p sunlit-mantra-479913-i5 gs://smoltalk-translations
```

### Adım 3: 100 Job Paralel Çalıştır

```bash
# Her job 10,000 örnek işler
for i in {0..99}; do
  start=$((i * 10000))
  end=$(((i + 1) * 10000))
  
  gcloud run jobs execute smoltalk-translate \
    --region us-central1 \
    --set-env-vars START_INDEX=$start,END_INDEX=$end,JOB_ID=job-$i &
done
wait
```

### Adım 4: Sonuçları Birleştir

```bash
gsutil cat gs://smoltalk-translations/translations/job-*.jsonl > full_translations.jsonl
```

---

## 💡 SONUÇ

**En iyi çözüm: Cloud Run Jobs**

1. ✅ Kurulumu basit
2. ✅ Maliyet optimal ($1,403)
3. ✅ Hız mükemmel (3-4 gün)
4. ✅ Yönetimi kolay
5. ✅ Otomatik retry
6. ✅ Progress tracking kolay

**Alternatif:**
- Eğer daha fazla kontrol istiyorsanız → Compute Engine
- Eğer Kubernetes bilginiz varsa → GKE

---

## 📝 SONRAKİ ADIMLAR

1. ✅ Worker kapasitesi test edildi (15 worker optimal)
2. 📋 Cloud Run Jobs için script hazırla
3. 🐳 Docker image oluştur
4. 🪣 GCS bucket oluştur
5. 🚀 İlk 10 job ile pilot test
6. 📊 Sonuçları kontrol et
7. 🎯 100 job ile full-scale çeviri başlat

Devam edelim mi?
