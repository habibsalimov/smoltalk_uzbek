"""
SmolTalk Batch Translation - Cloud Run Job
===========================================

Bu script Cloud Run Job olarak çalışacak şekilde tasarlanmıştır.
Her job belirli bir range'deki örnekleri çevirir.
"""

import os
import json
import time
from typing import Dict, List
from google import genai
from datasets import load_dataset
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import storage
import sys

# Environment variables
PROJECT_ID = os.getenv('PROJECT_ID', 'sunlit-mantra-479913-i5')
START_INDEX = int(os.getenv('START_INDEX', '0'))
END_INDEX = int(os.getenv('END_INDEX', '1000'))
OUTPUT_BUCKET = os.getenv('OUTPUT_BUCKET', 'smoltalk-translations')
JOB_ID = os.getenv('CLOUD_RUN_JOB', 'unknown')
TASK_INDEX = os.getenv('CLOUD_RUN_TASK_INDEX', '0')
WORKERS = int(os.getenv('WORKERS', '10'))

# Job identifier
JOB_NAME = f"job-{TASK_INDEX}-{START_INDEX}-{END_INDEX}"

print(f"\n{'='*80}")
print(f"🚀 SMOLTALK BATCH TRANSLATION JOB")
print(f"{'='*80}")
print(f"Job ID: {JOB_NAME}")
print(f"Range: {START_INDEX:,} → {END_INDEX:,}")
print(f"Workers: {WORKERS}")
print(f"Output: gs://{OUTPUT_BUCKET}/translations/{JOB_NAME}.jsonl")
print(f"{'='*80}\n")

# Vertex AI client
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="global"
)

def load_samples() -> List[Dict]:
    """Dataset'ten belirtilen range'deki örnekleri yükle"""
    print(f"📖 Dataset yükleniyor (range: {START_INDEX}-{END_INDEX})...")
    
    dataset = load_dataset("HuggingFaceTB/smoltalk", "all", split="train", streaming=True)
    
    samples = []
    current_conv_idx = -1
    
    for example in dataset:
        current_conv_idx += 1
        
        # Range kontrolü
        if current_conv_idx < START_INDEX:
            continue
        if current_conv_idx >= END_INDEX:
            break
        
        conversation_id = f"smoltalk_{current_conv_idx}"
        messages = example.get('messages', [])
        
        # Her konuşmadaki user mesajlarını al
        for msg_idx, msg in enumerate(messages):
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            # Sadece user mesajları + filtreleme
            if role == 'user' and len(content) > 30 and '```' not in content and content.count('http') < 3:
                samples.append({
                    'conversation_id': conversation_id,
                    'conversation_index': current_conv_idx,
                    'message_index': msg_idx,
                    'text': content,
                    'chars': len(content)
                })
    
    print(f"✅ {len(samples)} mesaj yüklendi\n")
    return samples

def translate_message(sample: Dict) -> Dict:
    """Tek bir mesajı çevir"""
    start_time = time.time()
    
    max_retries = 3
    retry_delay = 2  # saniye
    
    for attempt in range(max_retries):
        try:
            prompt = f"""Translate the following English text to Uzbek (Latin script).
Only provide the translation, no explanations or additional text.

English text:
{sample['text']}

Uzbek translation:"""
            
            response = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=prompt
            )
            
            elapsed = time.time() - start_time
            translated = response.text.strip()
            
            # Token tahmini (maliyet hesabı için)
            input_tokens = len(prompt) / 0.75
            output_tokens = len(translated) / 0.75
            cost = (input_tokens / 1_000_000) * 0.075 + (output_tokens / 1_000_000) * 0.30
            
            return {
                'conversation_id': sample['conversation_id'],
                'conversation_index': sample['conversation_index'],
                'message_index': sample['message_index'],
                'original': sample['text'],
                'translated': translated,
                'chars': sample['chars'],
                'translation_time': elapsed,
                'cost': cost,
                'success': True,
                'error': None,
                'retries': attempt
            }
        
        except Exception as e:
            error_msg = str(e)
            
            # Rate limit hatası mı?
            if 'RESOURCE_EXHAUSTED' in error_msg or '429' in error_msg:
                if attempt < max_retries - 1:
                    # Exponential backoff ile bekle
                    wait_time = retry_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
            
            # Başka hata veya son deneme
            elapsed = time.time() - start_time
            return {
                'conversation_id': sample['conversation_id'],
                'conversation_index': sample['conversation_index'],
                'message_index': sample['message_index'],
                'original': sample['text'],
                'translated': None,
                'chars': sample['chars'],
                'translation_time': elapsed,
                'cost': 0,
                'success': False,
                'error': error_msg[:500],
                'retries': attempt + 1
            }
    
    # Tüm denemeler başarısız
    elapsed = time.time() - start_time
    return {
        'conversation_id': sample['conversation_id'],
        'conversation_index': sample['conversation_index'],
        'message_index': sample['message_index'],
        'original': sample['text'],
        'translated': None,
        'chars': sample['chars'],
        'translation_time': elapsed,
        'cost': 0,
        'success': False,
        'error': 'Max retries exceeded',
        'retries': max_retries
    }

def process_batch(samples: List[Dict]) -> List[Dict]:
    """Batch'i paralel olarak işle"""
    print(f"🔄 {len(samples)} mesaj çevriliyor ({WORKERS} worker)...\n")
    
    results = []
    success_count = 0
    failed_count = 0
    total_chars = 0
    total_cost = 0
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        # Tüm işleri submit et
        futures = {executor.submit(translate_message, sample): sample for sample in samples}
        
        # Progress tracking
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            
            if result['success']:
                success_count += 1
                total_chars += result['chars']
                total_cost += result['cost']
            else:
                failed_count += 1
            
            # Her 10 işte bir progress göster
            if completed % 10 == 0 or completed == len(samples):
                elapsed = time.time() - start_time
                progress = (completed / len(samples)) * 100
                speed = total_chars / elapsed if elapsed > 0 else 0
                print(f"  Progress: {completed}/{len(samples)} ({progress:.1f}%) | "
                      f"Success: {success_count} | Failed: {failed_count} | "
                      f"Speed: {speed:.0f} char/s")
    
    total_time = time.time() - start_time
    
    # Özet istatistikler
    print(f"\n{'='*80}")
    print(f"📊 JOB SONUÇLARI")
    print(f"{'='*80}")
    print(f"Toplam Mesaj:      {len(samples)}")
    print(f"✅ Başarılı:       {success_count} ({success_count/len(samples)*100:.1f}%)")
    print(f"❌ Başarısız:      {failed_count} ({failed_count/len(samples)*100:.1f}%)")
    print(f"⏱️  Toplam Süre:    {total_time:.1f}s ({total_time/60:.1f} dakika)")
    print(f"📈 Hız:            {total_chars/total_time:.0f} karakter/saniye")
    print(f"💰 Maliyet:        ${total_cost:.4f}")
    print(f"{'='*80}\n")
    
    return results

def save_results(results: List[Dict]) -> str:
    """Sonuçları GCS'ye kaydet"""
    print(f"💾 Sonuçlar kaydediliyor...")
    
    # Önce local'e kaydet
    local_file = f'/tmp/{JOB_NAME}.jsonl'
    with open(local_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    print(f"  ✅ Local dosya: {local_file}")
    
    # GCS'ye yükle
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(OUTPUT_BUCKET)
        blob = bucket.blob(f'translations/{JOB_NAME}.jsonl')
        blob.upload_from_filename(local_file)
        
        gcs_path = f'gs://{OUTPUT_BUCKET}/translations/{JOB_NAME}.jsonl'
        print(f"  ✅ GCS: {gcs_path}")
        
        # Metadata da kaydet
        metadata = {
            'job_name': JOB_NAME,
            'start_index': START_INDEX,
            'end_index': END_INDEX,
            'total_messages': len(results),
            'success_count': sum(1 for r in results if r['success']),
            'failed_count': sum(1 for r in results if not r['success']),
            'total_chars': sum(r['chars'] for r in results if r['success']),
            'total_cost': sum(r['cost'] for r in results if r['success']),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        metadata_blob = bucket.blob(f'translations/{JOB_NAME}_metadata.json')
        metadata_blob.upload_from_string(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            content_type='application/json'
        )
        
        print(f"  ✅ Metadata: gs://{OUTPUT_BUCKET}/translations/{JOB_NAME}_metadata.json")
        
        return gcs_path
    
    except Exception as e:
        print(f"  ⚠️  GCS upload hatası: {e}")
        print(f"  📁 Sonuçlar local'de: {local_file}")
        return local_file

def main():
    """Ana iş akışı"""
    try:
        # 1. Dataset yükle
        samples = load_samples()
        
        if not samples:
            print("⚠️  Hiç örnek bulunamadı!")
            sys.exit(1)
        
        # 2. Çevirileri yap
        results = process_batch(samples)
        
        # 3. Sonuçları kaydet
        output_path = save_results(results)
        
        print(f"\n🎉 JOB TAMAMLANDI!")
        print(f"📁 Çıktı: {output_path}\n")
        
        # Başarı oranı düşükse uyar
        success_rate = sum(1 for r in results if r['success']) / len(results)
        if success_rate < 0.9:
            print(f"⚠️  UYARI: Başarı oranı düşük (%{success_rate*100:.1f})")
            print(f"   Bazı mesajlar çevrilemedi. Retry gerekebilir.\n")
            sys.exit(1)  # Cloud Run job'u failed olarak işaretle
        
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
