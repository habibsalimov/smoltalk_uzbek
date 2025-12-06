"""
Google Translation API - İngilizce ↔ Özbek Çeviri Testi
======================================================

Bu script İngilizce ve Özbek arasında çeviri testleri yapar.
"""

from google.cloud import translate as translate_advanced
import time

# Google Cloud Project ID
PROJECT_ID = "sunlit-mantra-479913-i5"
LOCATION = "us-central1"

# Test metinleri
test_texts = [
    {
        "source": "en",
        "target": "uz",
        "text": "Hello! How are you today?",
        "context": "Basit selamlaşma"
    },
    {
        "source": "en",
        "target": "uz",
        "text": "Welcome to our platform. We are developing artificial intelligence solutions for businesses.",
        "context": "İş dünyası tanıtım"
    },
    {
        "source": "en",
        "target": "uz",
        "text": "Machine learning is transforming the way we solve complex problems. Our models are trained on large datasets.",
        "context": "Teknik açıklama"
    },
    {
        "source": "uz",
        "target": "en",
        "text": "Salom! Men sun'iy intellekt yordamchisiman.",
        "context": "Özbek tanıtım"
    },
    {
        "source": "uz",
        "target": "en",
        "text": "Biz Google Cloud platformasida mashinali o'rganish modellarini ishlab chiqamiz.",
        "context": "Teknik Özbek"
    },
    {
        "source": "en",
        "target": "uz",
        "text": "Thank you for your attention. Please contact us if you have any questions.",
        "context": "Kapanış mesajı"
    },
    {
        "source": "en",
        "target": "uz",
        "text": "Our team consists of experienced developers and data scientists who are passionate about innovation.",
        "context": "Ekip tanıtımı"
    },
    {
        "source": "uz",
        "target": "en",
        "text": "Bizning xizmatlarimiz yuqori sifatli va ishonchli.",
        "context": "Hizmet kalitesi"
    }
]

print("="*80)
print("🇺🇿 GOOGLE TRANSLATION API - İNGİLİZCE ↔ ÖZBEK ÇEVİRİ TESTİ")
print("="*80)

# Translation API Client
print("\n📦 Translation API başlatılıyor...")
try:
    translation_client = translate_advanced.TranslationServiceClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    model_path = f"{parent}/models/general/translation-llm"
    print("✅ Translation API hazır!")
except Exception as e:
    print(f"❌ Hata: {e}")
    exit(1)

print("\n" + "="*80)
print("🧪 TEST SONUÇLARI")
print("="*80)

results = []
total_chars_translated = 0

for idx, test in enumerate(test_texts, 1):
    print(f"\n{'='*80}")
    print(f"📝 TEST {idx}/{len(test_texts)}")
    print(f"{'='*80}")
    
    # Dil yönü emoji
    if test['source'] == 'en' and test['target'] == 'uz':
        direction_emoji = "🇬🇧 → 🇺🇿"
        direction_text = "İngilizce → Özbek"
    else:
        direction_emoji = "🇺🇿 → 🇬🇧"
        direction_text = "Özbek → İngilizce"
    
    print(f"{direction_emoji} {direction_text}")
    print(f"📂 Bağlam: {test['context']}")
    print(f"📄 Orijinal: {test['text']}")
    print("-"*80)
    
    try:
        start_time = time.time()
        
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
        char_count = len(test['text'])
        total_chars_translated += char_count
        
        print(f"✅ Çeviri: {translated}")
        print(f"⏱️  Süre: {translation_time:.2f} saniye")
        print(f"📊 Karakter: {char_count}")
        
        results.append({
            "direction": direction_text,
            "original": test['text'],
            "translated": translated,
            "time": translation_time,
            "chars": char_count,
            "status": "success"
        })
        
    except Exception as e:
        print(f"❌ Hata: {str(e)[:200]}")
        results.append({
            "direction": direction_text,
            "error": str(e),
            "status": "failed"
        })
    
    time.sleep(0.5)  # API rate limit

# ÖZET RAPOR
print("\n\n" + "="*80)
print("📊 ÖZET RAPOR")
print("="*80)

successful = sum(1 for r in results if r.get("status") == "success")
failed = len(results) - successful

print(f"\n✅ Başarılı Çeviriler: {successful}/{len(results)}")
print(f"❌ Başarısız: {failed}/{len(results)}")

if successful > 0:
    avg_time = sum(r["time"] for r in results if r.get("status") == "success") / successful
    total_time = sum(r["time"] for r in results if r.get("status") == "success")
    
    print(f"\n⏱️  Performans:")
    print(f"   Ortalama süre: {avg_time:.2f} saniye/çeviri")
    print(f"   Toplam süre: {total_time:.2f} saniye")
    print(f"   Toplam karakter: {total_chars_translated:,}")
    print(f"   Hız: {total_chars_translated/total_time:.0f} karakter/saniye")
    
    # Yön bazlı analiz
    en_to_uz = [r for r in results if r.get("status") == "success" and "İngilizce → Özbek" in r["direction"]]
    uz_to_en = [r for r in results if r.get("status") == "success" and "Özbek → İngilizce" in r["direction"]]
    
    print(f"\n📈 Yön Bazlı İstatistikler:")
    if en_to_uz:
        avg_en_uz = sum(r["time"] for r in en_to_uz) / len(en_to_uz)
        print(f"   🇬🇧 → 🇺🇿: {len(en_to_uz)} çeviri, ort. {avg_en_uz:.2f}s")
    if uz_to_en:
        avg_uz_en = sum(r["time"] for r in uz_to_en) / len(uz_to_en)
        print(f"   🇺🇿 → 🇬🇧: {len(uz_to_en)} çeviri, ort. {avg_uz_en:.2f}s")

print("\n" + "="*80)
print("💡 ÇEVİRİ KALİTESİ DEĞERLENDİRMESİ")
print("="*80)

# Başarılı çevirileri göster
print("\n📋 Başarılı Çeviri Örnekleri:")
for idx, result in enumerate([r for r in results if r.get("status") == "success"][:3], 1):
    print(f"\n{idx}. {result['direction']}")
    print(f"   Orijinal: {result['original'][:80]}...")
    print(f"   Çeviri: {result['translated'][:80]}...")

print("\n" + "="*80)
print("🎯 ÖNERİLER")
print("="*80)
print("""
✅ Translation API Özbek Dili Desteği:
   • İngilizce ↔ Özbek çevirisi destekleniyor
   • TranslationLLM modeli kullanıldı
   • Hızlı ve güvenilir sonuçlar
   
💡 Gelişmiş Özellikler:
   • Glossary: Özel terminoloji için sözlük oluşturabilirsiniz
   • Batch Translation: Toplu çeviri desteği
   • HTML Format: HTML içeriği çevirebilir
   
📚 Sonraki Adımlar:
   1. Özel terminoloji için Glossary oluşturun
   2. Daha uzun metinler için batch translation kullanın
   3. Profesyonel çeviri için human review ekleyin
""")

print("\n✅ Test tamamlandı!")
