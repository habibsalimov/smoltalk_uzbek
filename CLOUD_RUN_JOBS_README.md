# SmolTalk Batch Translation - Cloud Run Jobs

Gemini 3 Pro kullanarak HuggingFace SmolTalk dataset'ini Özbekçe'ye çeviren Cloud Run Jobs çözümü.

## 📋 Genel Bakış

**Yaklaşım:** Serverless Cloud Run Jobs ile paralel çeviri
**Model:** Gemini 3 Pro Preview (Vertex AI)
**Hedef:** 1.04M konuşma, ~894M karakter

## 💰 Maliyet & Süre

| Metrik | Değer |
|--------|-------|
| **Gemini API** | $1,350 |
| **Cloud Run** | ~$53 (100 job x 10 saat) |
| **Toplam** | **~$1,403** |
| **Süre** | **3-4 gün** (100 job paralel) |
| **Hız** | 93 kar/s per job (10 worker) |

## 🚀 Hızlı Başlangıç

### 1. Önkoşullar

```bash
# Google Cloud SDK kurulu olmalı
gcloud --version

# Docker kurulu olmalı
docker --version

# Gcloud login
gcloud auth login
gcloud auth application-default login

# Project ayarla
gcloud config set project sunlit-mantra-479913-i5
```

### 2. Kurulum

```bash
# Cloud Run Job ve GCS bucket'ı oluştur
./setup_cloud_run.sh
```

Bu script:
- ✅ GCS bucket oluşturur (`gs://smoltalk-translations`)
- ✅ Docker image build eder
- ✅ Image'ı GCR'ye push eder  
- ✅ Cloud Run Job oluşturur

### 3. Pilot Test (100 örnek)

```bash
# İlk 100 konuşmayı çevir
./run_job.sh 0 100
```

### 4. 10 Job Paralel Test

```bash
# 10 job paralel çalıştır
./run_parallel_jobs.sh 10
```

### 5. Tam Dataset (100 Job)

```bash
# Tüm dataset'i çevir (100 job paralel)
./run_parallel_jobs.sh 100
```

⚠️ **UYARI:** Bu komut ~$1,403 maliyete sebep olur!

## 📊 İlerleme Takibi

```bash
# Anlık durum
./check_progress.sh

# Cloud Console'dan takip
# https://console.cloud.google.com/run/jobs
```

## 📁 Dosya Yapısı

```
.
├── Dockerfile                 # Docker image tanımı
├── requirements.txt           # Python dependencies
├── translate_batch.py         # Ana çeviri script
├── setup_cloud_run.sh        # Kurulum script
├── run_job.sh                # Tek job çalıştır
├── run_parallel_jobs.sh      # Paralel job'lar
└── check_progress.sh         # İlerleme takibi
```

## 🔧 Teknik Detaylar

### Cloud Run Job Özellikleri

- **Image:** `gcr.io/sunlit-mantra-479913-i5/smoltalk-translator`
- **Memory:** 2Gi
- **CPU:** 2 vCPU
- **Workers:** 10 (paralel çeviri)
- **Timeout:** 1 saat
- **Max Retries:** 3
- **Parallelism:** 100 (aynı anda 100 job)

### Environment Variables

| Variable | Açıklama | Varsayılan |
|----------|----------|------------|
| `START_INDEX` | Başlangıç index | 0 |
| `END_INDEX` | Bitiş index | 1000 |
| `WORKERS` | Paralel worker sayısı | 10 |
| `PROJECT_ID` | GCP Project ID | sunlit-mantra-479913-i5 |
| `OUTPUT_BUCKET` | GCS bucket adı | smoltalk-translations |

### Çıktı Formatı

Her job 2 dosya oluşturur:

**1. Çeviri Sonuçları:** `job-{index}-{start}-{end}.jsonl`
```json
{
  "conversation_id": "smoltalk_0",
  "conversation_index": 0,
  "message_index": 0,
  "original": "How can I help you?",
  "translated": "Sizga qanday yordam bera olaman?",
  "chars": 19,
  "translation_time": 1.23,
  "cost": 0.0001,
  "success": true
}
```

**2. Metadata:** `job-{index}-{start}-{end}_metadata.json`
```json
{
  "job_name": "job-0-0-1000",
  "total_messages": 1500,
  "success_count": 1480,
  "failed_count": 20,
  "total_cost": 0.15,
  "timestamp": "2025-12-06 10:30:00"
}
```

## 📥 Sonuçları İndirme

```bash
# Tüm sonuçları indir
gsutil -m cp -r gs://smoltalk-translations/translations/ ./results/

# Tek bir dosyada birleştir
gsutil cat gs://smoltalk-translations/translations/job-*.jsonl > full_translations.jsonl
```

## 🔍 Sorun Giderme

### Job başarısız oluyor

```bash
# Log kontrol
gcloud run jobs executions list --job smoltalk-translate --region us-central1

# Detaylı log
gcloud run jobs executions describe [EXECUTION_NAME] --region us-central1
```

### Rate limit hatası

- Worker sayısını azalt (10 → 5)
- Job sayısını azalt (100 → 50)
- Joblar arası bekleme süresi ekle

### GCS upload hatası

- Bucket'ın var olduğundan emin ol
- Permissions kontrol et

## 💡 İpuçları

1. **Pilot Test:** Önce küçük test yapın (100-1000 örnek)
2. **Progress Tracking:** `check_progress.sh` düzenli çalıştırın
3. **Maliyet Kontrolü:** Her job maliyeti metadata'da
4. **Retry:** Başarısız job'ları tekrar çalıştırın
5. **Backup:** Sonuçları düzenli yedekleyin

## 📚 Kaynaklar

- [Cloud Run Jobs Docs](https://cloud.google.com/run/docs/create-jobs)
- [Gemini API Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)
- [SmolTalk Dataset](https://huggingface.co/datasets/HuggingFaceTB/smoltalk)

## 🤝 Katkı

Issues ve pull request'ler memnuniyetle karşılanır!

## 📄 Lisans

MIT License
