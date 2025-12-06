"""
Vertex AI Batch Prediction API Araştırması
==========================================

Gemini modelleri için batch prediction nasıl kullanılır?

ÖNEMLI NOT: Gemini modelleri şu anda Vertex AI Batch Prediction API'yi 
desteklemiyor. Sadece online prediction destekleniyor.

Alternatif Çözümler:
====================

1. CLOUD RUN JOBS (Önerilen)
   - Serverless, otomatik scaling
   - Her job 10-15 worker çalıştırabilir
   - Birden fazla job paralel çalışabilir
   - Maliyet: Sadece kullanıldığı süre
   
2. COMPUTE ENGINE VM CLUSTER
   - Birden fazla VM oluştur
   - Her VM'de 10 worker çalıştır
   - Daha fazla kontrol
   - Maliyet: VM çalıştığı süre boyunca

3. KUBERNETES (GKE)
   - En esnek çözüm
   - Auto-scaling
   - Job scheduling
   - Kurulum daha karmaşık

CLOUD RUN JOBS ÇÖZÜMÜ:
======================
"""

# Cloud Run Jobs için örnek script

import os
import json
from google import genai
from datasets import load_dataset
from concurrent.futures import ThreadPoolExecutor
import sys

PROJECT_ID = "sunlit-mantra-479913-i5"
WORKERS = 10

# Environment variables'dan parametreleri al
START_INDEX = int(os.getenv('START_INDEX', '0'))
END_INDEX = int(os.getenv('END_INDEX', '1000'))
OUTPUT_BUCKET = os.getenv('OUTPUT_BUCKET', 'gs://smoltalk-translations')
JOB_ID = os.getenv('CLOUD_RUN_JOB', 'job-0')

def main():
    print(f"🚀 Job başlatılıyor: {JOB_ID}")
    print(f"   Range: {START_INDEX} - {END_INDEX}")
    print(f"   Workers: {WORKERS}")
    
    # Vertex AI client
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global"
    )
    
    # Dataset yükle
    print("📖 Dataset yükleniyor...")
    dataset = load_dataset("HuggingFaceTB/smoltalk", "all", split="train", streaming=True)
    
    # İlgili range'i al
    samples = []
    for idx, example in enumerate(dataset):
        if idx < START_INDEX:
            continue
        if idx >= END_INDEX:
            break
            
        for msg in example.get('messages', []):
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if len(content) > 30 and '```' not in content:
                    samples.append({
                        'index': idx,
                        'text': content
                    })
    
    print(f"✅ {len(samples)} örnek yüklendi")
    
    # Paralel çeviri
    def translate(sample):
        try:
            prompt = f"""Translate to Uzbek (Latin script): {sample['text']}"""
            response = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=prompt
            )
            return {
                'index': sample['index'],
                'original': sample['text'],
                'translated': response.text.strip(),
                'success': True
            }
        except Exception as e:
            return {
                'index': sample['index'],
                'original': sample['text'],
                'error': str(e),
                'success': False
            }
    
    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        results = list(executor.map(translate, samples))
    
    # Sonuçları kaydet
    output_file = f'/tmp/results_{JOB_ID}.jsonl'
    with open(output_file, 'w') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    
    # GCS'ye yükle
    from google.cloud import storage
    storage_client = storage.Client()
    bucket_name = OUTPUT_BUCKET.replace('gs://', '').split('/')[0]
    blob_path = f"translations/{JOB_ID}.jsonl"
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(output_file)
    
    print(f"✅ Sonuçlar yüklendi: gs://{bucket_name}/{blob_path}")
    
    # İstatistikler
    success = sum(1 for r in results if r['success'])
    print(f"\n📊 ÖZET:")
    print(f"   Toplam: {len(results)}")
    print(f"   Başarılı: {success}")
    print(f"   Başarısız: {len(results) - success}")

if __name__ == "__main__":
    main()

"""
CLOUD RUN JOBS KULLANIMI:
==========================

1. Docker Image Hazırla:
   
   Dockerfile:
   -----------
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY translate_batch.py .
   
   CMD ["python", "translate_batch.py"]


2. Image'ı Build Et ve Push Et:
   
   docker build -t gcr.io/sunlit-mantra-479913-i5/smoltalk-translator .
   docker push gcr.io/sunlit-mantra-479913-i5/smoltalk-translator


3. Cloud Run Job Oluştur:
   
   gcloud run jobs create smoltalk-translate \\
     --image gcr.io/sunlit-mantra-479913-i5/smoltalk-translator \\
     --region us-central1 \\
     --set-env-vars PROJECT_ID=sunlit-mantra-479913-i5 \\
     --memory 2Gi \\
     --cpu 2 \\
     --max-retries 3 \\
     --parallelism 50 \\
     --tasks 100


4. Job'u Çalıştır:
   
   # Tek job
   gcloud run jobs execute smoltalk-translate \\
     --region us-central1
   
   # Parametreli (farklı range'ler için)
   gcloud run jobs execute smoltalk-translate \\
     --region us-central1 \\
     --set-env-vars START_INDEX=0,END_INDEX=1000


5. Birden Fazla Job Paralel:
   
   # 100 job, her biri 10,000 örnek işliyor
   for i in {0..99}; do
     start=$((i * 10000))
     end=$(((i + 1) * 10000))
     
     gcloud run jobs execute smoltalk-translate-${i} \\
       --region us-central1 \\
       --set-env-vars START_INDEX=$start,END_INDEX=$end,JOB_ID=job-$i &
   done
   wait


AVANTAJLAR:
===========
✅ Otomatik scaling (parallelism ayarlanabilir)
✅ Retry mekanizması built-in
✅ Sadece çalıştığı süre için ücret
✅ Her job izole çalışır
✅ 100+ job paralel çalışabilir

MALİYET:
========
- Cloud Run: ~$0.024/vCPU-hour + $0.0025/GB-hour
- Her job (2 vCPU, 2GB): ~$0.053/saat
- 100 job 10 saat çalışırsa: ~$53
- Toplam (Gemini + Cloud Run): $1,350 + $53 = $1,403


HIZLANDIRMA:
============
10 worker/job ile:
- 1 job: 336 gün
- 10 job paralel: 34 gün
- 50 job paralel: 7 gün
- 100 job paralel: 3.4 gün ✨


ÖNERİ:
======
50-100 Cloud Run job paralel çalıştırın:
- Toplam süre: 3-7 gün
- Toplam maliyet: ~$1,400
- Güvenilir, otomatik retry
- Progress tracking kolay
"""

print(__doc__)
