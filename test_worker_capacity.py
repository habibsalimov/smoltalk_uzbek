"""
Gemini 3 Pro - Paralel Worker Sayısını Artırarak Test
=======================================================

Önceki başarılı yaklaşımı kullanarak worker sayısını artıracağız.
"""

import json
import time
from typing import Dict, List
from google import genai
from datasets import load_dataset
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

PROJECT_ID = "sunlit-mantra-479913-i5"

# Global client - tekrar tekrar oluşturmayalım
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="global"
)

def load_samples(n: int) -> List[Dict]:
    """Dataset'ten örnek yükle"""
    print(f"📖 {n} örnek yükleniyor...")
    dataset = load_dataset("HuggingFaceTB/smoltalk", "all", split="train", streaming=True)
    
    samples = []
    for ex in dataset:
        for msg in ex.get('messages', []):
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                if len(content) > 30 and '```' not in content:
                    samples.append({'text': content, 'id': len(samples)})
                    if len(samples) >= n:
                        return samples
    return samples

def translate_one(sample: Dict) -> Dict:
    """Tek çeviri"""
    start = time.time()
    try:
        prompt = f"""Translate the following English text to Uzbek (Latin script).
Only provide the translation, no explanations.

English: {sample['text']}

Uzbek:"""
        
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt
        )
        
        return {
            'id': sample['id'],
            'success': True,
            'time': time.time() - start,
            'chars': len(sample['text'])
        }
    except Exception as e:
        return {
            'id': sample['id'],
            'success': False,
            'time': time.time() - start,
            'chars': len(sample['text']),
            'error': str(e)[:100]
        }

def test_workers(num_workers: int, samples: List[Dict]):
    """Belirli worker sayısı ile test"""
    print(f"\n{'='*60}")
    print(f"🧪 {num_workers} WORKER TESTİ")
    print(f"{'='*60}")
    
    start = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(translate_one, s): s for s in samples}
        
        for future in tqdm(as_completed(futures), total=len(samples), desc=f"{num_workers} worker"):
            results.append(future.result())
    
    elapsed = time.time() - start
    
    success = sum(1 for r in results if r['success'])
    total_chars = sum(r['chars'] for r in results if r['success'])
    
    print(f"\n📊 SONUÇLAR:")
    print(f"   ✅ Başarılı: {success}/{len(samples)}")
    print(f"   ⏱️  Süre: {elapsed:.1f}s")
    print(f"   📈 Hız: {total_chars/elapsed:.0f} kar/s")
    print(f"   🔄 Throughput: {len(samples)/elapsed:.2f} istek/s")
    
    if success == 0 and results:
        print(f"   ❌ Hata örneği: {results[0].get('error', 'Unknown')}")
    
    return {
        'workers': num_workers,
        'success': success,
        'total': len(samples),
        'time': elapsed,
        'chars_per_sec': total_chars/elapsed if elapsed > 0 else 0,
        'requests_per_sec': len(samples)/elapsed if elapsed > 0 else 0
    }

def main():
    print("\n" + "="*60)
    print("🚀 GEMINI 3 PRO - WORKER KAPASİTE TESTİ")
    print("="*60)
    
    # 30 örnek yükle
    samples = load_samples(30)
    print(f"✅ {len(samples)} örnek hazır\n")
    
    # Farklı worker sayılarını test et
    worker_counts = [15]  # 15 worker test
    all_results = []
    
    for workers in worker_counts:
        result = test_workers(workers, samples[:20])  # 20 örnek test edelim
        all_results.append(result)
        
        # Başarısızsa dur
        if result['success'] == 0:
            print("\n🛑 Testler durduruluyor (başarısız istekler)")
            break
        
        # Sonraki test için bekle
        if workers < worker_counts[-1]:
            print("\n⏸️  3 saniye bekleniyor...")
            time.sleep(3)
    
    # Özet
    print("\n" + "="*60)
    print("📊 ÖZET")
    print("="*60)
    print(f"\n{'Workers':<10} {'Başarı':<12} {'Süre':<10} {'Hız (kar/s)':<15}")
    print("-" * 60)
    
    for r in all_results:
        print(f"{r['workers']:<10} {r['success']}/{r['total']:<9} {r['time']:<9.1f}s {r['chars_per_sec']:<15.0f}")
    
    # En iyi sonuç
    if all_results:
        best = max([r for r in all_results if r['success'] > 0], 
                   key=lambda x: x['chars_per_sec'], default=None)
        if best:
            print(f"\n✨ EN İYİ: {best['workers']} worker → {best['chars_per_sec']:.0f} kar/s")

if __name__ == "__main__":
    main()
