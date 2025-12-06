"""
Basit Paralel Test - Gemini 3 Pro
==================================
"""

from google import genai
from datasets import load_dataset
from concurrent.futures import ThreadPoolExecutor
import time

PROJECT_ID = "sunlit-mantra-479913-i5"

# Global client
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="global"
)

def translate(text):
    """Basit çeviri"""
    try:
        prompt = f"""Translate to Uzbek: {text[:200]}"""
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt
        )
        return {"success": True, "result": response.text[:50]}
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}

# 5 örnek yükle
print("Dataset yükleniyor...")
dataset = load_dataset("HuggingFaceTB/smoltalk", "all", split="train", streaming=True)

samples = []
for ex in dataset:
    for msg in ex.get('messages', []):
        if msg.get('role') == 'user' and len(msg.get('content', '')) > 30:
            samples.append(msg['content'])
            if len(samples) >= 5:
                break
    if len(samples) >= 5:
        break

print(f"✅ {len(samples)} örnek yüklendi\n")

# Farklı worker sayıları test et
for workers in [1, 2, 5]:
    print(f"🧪 Test: {workers} worker")
    start = time.time()
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(translate, samples))
    
    elapsed = time.time() - start
    success = sum(1 for r in results if r['success'])
    
    print(f"   ✅ Başarılı: {success}/{len(samples)}")
    print(f"   ⏱️  Süre: {elapsed:.1f}s")
    print(f"   📈 Hız: {len(samples)/elapsed:.2f} istek/s\n")
    
    if success == 0:
        print(f"   ❌ Hata: {results[0]['error']}\n")
        break
    
    time.sleep(2)

print("✅ Test tamamlandı!")
