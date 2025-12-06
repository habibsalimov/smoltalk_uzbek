"""
Google Translation API vs Gemini 3 Pro Karşılaştırma Testi
==========================================================

Bu script:
1. Google Translation LLM kullanarak çeviri yapar
2. Gemini 3 Pro Preview ile aynı metni çevirir
3. Sonuçları karşılaştırır
4. Performans ve kalite analizi yapar
"""

from google.cloud import translate_v2 as translate
from google.cloud import translate as translate_advanced
from google import genai
from google.genai import types
import time

# Google Cloud Project ID
PROJECT_ID = "sunlit-mantra-479913-i5"
LOCATION = "us-central1"

# Test metinleri (Türkçe -> İngilizce)
test_texts = [
    {
        "source": "tr",
        "target": "en",
        "text": "Merhaba! Ben bir yapay zeka asistanıyım. Size nasıl yardımcı olabilirim?"
    },
    {
        "source": "tr",
        "target": "en", 
        "text": "Google Cloud Platform üzerinde makine öğrenmesi modelleri geliştiriyoruz. Bu proje çok heyecan verici!"
    },
    {
        "source": "en",
        "target": "tr",
        "text": "Artificial intelligence is transforming how we build applications. Machine learning models are becoming more powerful every day."
    },
    {
        "source": "tr",
        "target": "en",
        "text": "Bugün hava çok güzel. Parkta yürüyüş yapmayı planlıyorum. Sen ne yapıyorsun?"
    }
]

print("="*80)
print("🔬 GOOGLE TRANSLATION API vs GEMINI 3 PRO KARŞILAŞTIRMASI")
print("="*80)

# Translation API Client (Advanced)
print("\n📦 Translation API Client başlatılıyor...")
try:
    translation_client = translate_advanced.TranslationServiceClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    print("✅ Translation API hazır!")
except Exception as e:
    print(f"❌ Translation API hatası: {e}")
    translation_client = None

# Gemini Client
print("\n📦 Gemini Client başlatılıyor...")
try:
    gemini_client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global"  # Gemini için global location kullan
    )
    print("✅ Gemini hazır!")
except Exception as e:
    print(f"❌ Gemini hatası: {e}")
    gemini_client = None

print("\n" + "="*80)
print("🧪 TEST SONUÇLARI")
print("="*80)

results = []

for idx, test in enumerate(test_texts, 1):
    print(f"\n{'='*80}")
    print(f"📝 TEST {idx}/{len(test_texts)}")
    print(f"{'='*80}")
    print(f"🌍 Dil: {test['source'].upper()} → {test['target'].upper()}")
    print(f"📄 Orijinal: {test['text']}")
    print("-"*80)
    
    result = {
        "original": test['text'],
        "source": test['source'],
        "target": test['target']
    }
    
    # 1. TRANSLATION API TEST
    if translation_client:
        print("\n🔵 Translation API (TranslationLLM):")
        try:
            start_time = time.time()
            
            # TranslationLLM modeli ile çeviri
            model_path = f"{parent}/models/general/translation-llm"
            
            response = translation_client.translate_text(
                request={
                    "contents": [test['text']],
                    "target_language_code": test['target'],
                    "source_language_code": test['source'],
                    "parent": parent,
                    "model": model_path,
                    "mime_type": "text/plain",
                }
            )
            
            translation_time = time.time() - start_time
            translated = response.translations[0].translated_text
            
            print(f"   ✅ Çeviri: {translated}")
            print(f"   ⏱️  Süre: {translation_time:.2f} saniye")
            
            result["translation_api"] = {
                "text": translated,
                "time": translation_time,
                "status": "success"
            }
            
        except Exception as e:
            print(f"   ❌ Hata: {str(e)[:200]}")
            result["translation_api"] = {
                "error": str(e),
                "status": "failed"
            }
    
    # 2. GEMINI TEST
    if gemini_client:
        print("\n🟢 Gemini 3 Pro Preview:")
        try:
            start_time = time.time()
            
            prompt = f"""Translate the following text from {test['source'].upper()} to {test['target'].upper()}.
Only provide the translation, nothing else.

Text to translate:
{test['text']}

Translation:"""
            
            response = gemini_client.models.generate_content(
                model="gemini-3-pro-preview",  # En yeni Gemini 3 Pro modeli
                contents=prompt
            )
            
            gemini_time = time.time() - start_time
            translated = response.text.strip()
            
            print(f"   ✅ Çeviri: {translated}")
            print(f"   ⏱️  Süre: {gemini_time:.2f} saniye")
            
            result["gemini"] = {
                "text": translated,
                "time": gemini_time,
                "status": "success"
            }
            
        except Exception as e:
            print(f"   ❌ Hata: {str(e)[:200]}")
            result["gemini"] = {
                "error": str(e),
                "status": "failed"
            }
    
    results.append(result)
    time.sleep(1)  # API rate limit için bekleme

# ÖZET RAPOR
print("\n\n" + "="*80)
print("📊 ÖZET RAPOR")
print("="*80)

successful_translation = sum(1 for r in results if r.get("translation_api", {}).get("status") == "success")
successful_gemini = sum(1 for r in results if r.get("gemini", {}).get("status") == "success")

print(f"\n✅ Başarılı Çeviriler:")
print(f"   Translation API: {successful_translation}/{len(results)}")
print(f"   Gemini: {successful_gemini}/{len(results)}")

if successful_translation > 0:
    avg_translation_time = sum(r["translation_api"]["time"] for r in results if r.get("translation_api", {}).get("status") == "success") / successful_translation
    print(f"\n⏱️  Ortalama Süre:")
    print(f"   Translation API: {avg_translation_time:.2f} saniye")

if successful_gemini > 0:
    avg_gemini_time = sum(r["gemini"]["time"] for r in results if r.get("gemini", {}).get("status") == "success") / successful_gemini
    print(f"   Gemini: {avg_gemini_time:.2f} saniye")

print("\n" + "="*80)
print("💡 ÖNERİLER")
print("="*80)
print("""
1. 🎯 TRANSLATION API (TranslationLLM):
   ✅ Özel çeviri modeli - daha doğru
   ✅ Glossary desteği (terminoloji kontrolü)
   ✅ Adaptive Translation (özelleştirme)
   ⚠️  Sadece çeviri için optimize edilmiş
   
2. 🤖 GEMINI:
   ✅ Genel amaçlı LLM
   ✅ Context anlayışı daha iyi
   ✅ Yaratıcı çeviriler yapabilir
   ⚠️  Çeviri için özel değil
   ⚠️  Daha pahalı olabilir

💰 FİYATLANDIRMA ÖNERİSİ:
   - Yüksek hacimli, standart çeviriler: Translation API
   - Context-aware, yaratıcı çeviriler: Gemini
   - Özel terminoloji gereken projeler: Translation API + Glossary
""")

print("\n✅ Test tamamlandı!")
