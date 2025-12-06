"""
Gemini 3 Pro - Paralel Worker Test
===================================

Amaç: Max kaç paralel worker ile çalışabileceğimizi test etmek
- Rate limiting kontrol
- Quota kontrol
- Optimal worker sayısını bul
"""

import json
import time
from typing import Dict, List
from google import genai
from datasets import load_dataset
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading

# Google Cloud ayarları
PROJECT_ID = "sunlit-mantra-479913-i5"

# Test parametreleri
SAMPLES_PER_TEST = 20  # Her worker sayısı için kaç örnek test edelim
WORKER_COUNTS = [1, 2, 5, 10, 20, 50]  # Test edilecek worker sayıları

def get_client():
    """Her işlem için fresh client oluştur"""
    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global"
    )

# Thread-safe counter
class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()
        self.success = 0
        self.failed = 0
    
    def increment(self):
        with self.lock:
            self.value += 1
    
    def add_success(self):
        with self.lock:
            self.success += 1
    
    def add_failed(self):
        with self.lock:
            self.failed += 1

def load_smoltalk_samples(num_samples: int) -> List[Dict]:
    """HuggingFace'ten SmolTalk dataset'ini yükle"""
    print(f"\n📖 SmolTalk dataset yükleniyor...")
    
    dataset = load_dataset("HuggingFaceTB/smoltalk", "all", split="train", streaming=True)
    
    samples = []
    for idx, example in enumerate(dataset):
        if len(samples) >= num_samples:
            break
        
        # Sadece user mesajlarını al
        conversation = example.get('messages', [])
        for msg in conversation:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                # Kod bloğu veya çok kısa mesajları atla
                if len(content) > 30 and '```' not in content:
                    samples.append({
                        'id': f"sample_{len(samples)}",
                        'text': content,
                        'chars': len(content)
                    })
                    if len(samples) >= num_samples:
                        break
    
    print(f"✅ {len(samples)} örnek yüklendi")
    return samples

def translate_single(text: str, sample_id: str, counter: Counter) -> Dict:
    """Tek bir metni çevir"""
    start_time = time.time()
    
    try:
        # Her işlem için fresh client
        client = get_client()
        
        prompt = f"""Translate the following English text to Uzbek (Latin script).
Only provide the translation, no explanations or additional text.

English text:
{text}

Uzbek translation:"""
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt
        )
        
        elapsed = time.time() - start_time
        translated = response.text.strip()
        
        counter.add_success()
        
        return {
            'id': sample_id,
            'success': True,
            'time': elapsed,
            'chars': len(text),
            'translated': translated[:100],  # İlk 100 karakter
            'error': None
        }
    
    except Exception as e:
        elapsed = time.time() - start_time
        counter.add_failed()
        
        error_msg = str(e)
        
        # Rate limit veya quota hatası mı kontrol et
        is_rate_limit = 'RESOURCE_EXHAUSTED' in error_msg or 'quota' in error_msg.lower()
        
        return {
            'id': sample_id,
            'success': False,
            'time': elapsed,
            'chars': len(text),
            'translated': None,
            'error': error_msg[:200],
            'is_rate_limit': is_rate_limit
        }

def test_worker_count(worker_count: int, samples: List[Dict]) -> Dict:
    """Belirli worker sayısı ile test et"""
    
    print(f"\n{'='*80}")
    print(f"🧪 Test: {worker_count} PARALEL WORKER")
    print(f"{'='*80}")
    
    counter = Counter()
    results = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        # Tüm görevleri submit et
        futures = {
            executor.submit(translate_single, sample['text'], sample['id'], counter): sample
            for sample in samples
        }
        
        # Progress bar ile takip et
        with tqdm(total=len(samples), desc=f"  {worker_count} worker") as pbar:
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                pbar.update(1)
                
                # Rate limit hatası varsa hemen durdur
                if result.get('is_rate_limit'):
                    print(f"\n⚠️  RATE LIMIT ALGILANDI! Test durduruluyor...")
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
    
    elapsed = time.time() - start_time
    
    # İstatistikler
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    total_chars = sum(r['chars'] for r in results if r['success'])
    avg_time = sum(r['time'] for r in results if r['success']) / max(success_count, 1)
    
    rate_limit_hit = any(r.get('is_rate_limit') for r in results)
    
    summary = {
        'worker_count': worker_count,
        'total_samples': len(samples),
        'completed': len(results),
        'success': success_count,
        'failed': failed_count,
        'rate_limit_hit': rate_limit_hit,
        'total_time': elapsed,
        'avg_time_per_request': avg_time,
        'total_chars': total_chars,
        'chars_per_sec': total_chars / elapsed if elapsed > 0 else 0,
        'throughput': len(results) / elapsed if elapsed > 0 else 0,
        'results': results
    }
    
    # Sonuçları göster
    print(f"\n📊 SONUÇLAR:")
    print(f"  ✅ Başarılı:        {success_count}/{len(samples)}")
    print(f"  ❌ Başarısız:       {failed_count}")
    print(f"  ⏱️  Toplam Süre:     {elapsed:.1f}s")
    print(f"  📈 Hız:             {summary['chars_per_sec']:.0f} karakter/saniye")
    print(f"  🔄 Throughput:      {summary['throughput']:.2f} istek/saniye")
    
    if rate_limit_hit:
        print(f"  ⚠️  UYARI: RATE LIMIT alındı - Bu worker sayısı çok yüksek!")
    
    return summary

def main():
    print("\n" + "="*80)
    print("🚀 GEMINI 3 PRO - PARALEL WORKER KAPASİTE TESTİ")
    print("="*80)
    print("\nAmaç: Maksimum paralel worker sayısını bul")
    print(f"Test edilecek worker sayıları: {WORKER_COUNTS}")
    print(f"Her test için örnek sayısı: {SAMPLES_PER_TEST}")
    
    # Dataset yükle
    samples = load_smoltalk_samples(SAMPLES_PER_TEST * len(WORKER_COUNTS))
    
    # Her worker sayısı için test et
    all_results = []
    
    for worker_count in WORKER_COUNTS:
        # Bu test için örnekleri al
        test_samples = samples[:SAMPLES_PER_TEST]
        
        # Test et
        summary = test_worker_count(worker_count, test_samples)
        all_results.append(summary)
        
        # Rate limit alındıysa dur
        if summary['rate_limit_hit']:
            print(f"\n🛑 Rate limit alındı! {worker_count} worker çok fazla.")
            print(f"   Önerilen maksimum: {worker_count // 2} worker")
            break
        
        # Bir sonraki test için kısa bekleme
        if worker_count < WORKER_COUNTS[-1]:
            print(f"\n⏸️  Sonraki test için 5 saniye bekleniyor...")
            time.sleep(5)
    
    # Özet rapor
    print("\n" + "="*80)
    print("📊 ÖZET RAPOR")
    print("="*80)
    print(f"\n{'Workers':<10} {'Başarı':<10} {'Süre':<12} {'Hız (kar/s)':<15} {'Throughput':<15} {'Rate Limit'}")
    print(f"{'-'*10} {'-'*10} {'-'*12} {'-'*15} {'-'*15} {'-'*11}")
    
    for r in all_results:
        rate_status = "❌ EVET" if r['rate_limit_hit'] else "✅ Hayır"
        print(f"{r['worker_count']:<10} {r['success']}/{r['total_samples']:<7} "
              f"{r['total_time']:<11.1f}s {r['chars_per_sec']:<15.0f} "
              f"{r['throughput']:<15.2f} {rate_status}")
    
    # En iyi worker sayısını bul
    successful_tests = [r for r in all_results if not r['rate_limit_hit'] and r['success'] > 0]
    
    if successful_tests:
        best = max(successful_tests, key=lambda x: x['chars_per_sec'])
        print(f"\n✨ ÖNERİLEN WORKER SAYISI: {best['worker_count']}")
        print(f"   → Hız: {best['chars_per_sec']:.0f} karakter/saniye")
        print(f"   → Throughput: {best['throughput']:.2f} istek/saniye")
    
    # JSON export
    output_file = 'worker_capacity_test_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_config': {
                'samples_per_test': SAMPLES_PER_TEST,
                'worker_counts_tested': WORKER_COUNTS,
                'model': 'gemini-3-pro-preview'
            },
            'results': all_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Detaylı sonuçlar kaydedildi: {output_file}")
    print()

if __name__ == "__main__":
    main()
