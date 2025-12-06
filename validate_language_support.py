"""
Google Translation API - Desteklenen Diller Listesi
===================================================

Bu script Google Translation API'nin desteklediği tüm dilleri listeler
ve Özbek dilinin desteklenip desteklenmediğini kontrol eder.
"""

from google.cloud import translate_v2 as translate

# Google Cloud Project ID
PROJECT_ID = "sunlit-mantra-479913-i5"

print("="*80)
print("🌍 GOOGLE TRANSLATION API - DESTEKLENEN DİLLER")
print("="*80)

# Translation client oluştur
print("\n📦 Translation API başlatılıyor...")
try:
    translate_client = translate.Client()
    print("✅ Translation API hazır!")
except Exception as e:
    print(f"❌ Hata: {e}")
    exit(1)

# Desteklenen dilleri al
print("\n🔍 Desteklenen diller sorgulanıyor...")
try:
    languages = translate_client.get_languages()
    print(f"✅ Toplam {len(languages)} dil destekleniyor!\n")
except Exception as e:
    print(f"❌ Hata: {e}")
    exit(1)

# Özbek dilini ara
uzbek_found = False
uzbek_info = None

print("="*80)
print("🇺🇿 ÖZBEK DİLİ KONTROLÜ")
print("="*80)

for lang in languages:
    if lang['language'] == 'uz':
        uzbek_found = True
        uzbek_info = lang
        break

if uzbek_found:
    print("\n✅ ÖZBEK DİLİ DESTEKLENİYOR!")
    print(f"   Dil Kodu: {uzbek_info['language']}")
    print(f"   Dil Adı: {uzbek_info.get('name', 'N/A')}")
else:
    print("\n❌ ÖZBEK DİLİ BULUNAMADI!")

# Türkçe ve yakın dilleri göster
print("\n" + "="*80)
print("🌐 TÜRK DİLLERİ VE YAKIN DİLLER")
print("="*80)

turkic_languages = ['uz', 'tr', 'kk', 'ky', 'az', 'tk', 'tt', 'ug']
found_turkic = []

for lang in languages:
    if lang['language'] in turkic_languages:
        found_turkic.append(lang)

if found_turkic:
    print(f"\n✅ {len(found_turkic)} Türk dili bulundu:\n")
    for lang in sorted(found_turkic, key=lambda x: x['language']):
        flag_map = {
            'uz': '🇺🇿',
            'tr': '🇹🇷', 
            'kk': '🇰🇿',
            'ky': '🇰🇬',
            'az': '🇦🇿',
            'tk': '🇹🇲',
            'tt': '🏴',
            'ug': '🏴'
        }
        flag = flag_map.get(lang['language'], '🏳️')
        print(f"   {flag} {lang['language'].upper()}: {lang.get('name', 'N/A')}")

# Tüm desteklenen dilleri grupla
print("\n" + "="*80)
print("📊 TÜM DESTEKLENEN DİLLER (Alfabetik)")
print("="*80)

# Dilleri alfabetik sırala ve grupla (her 5 dil bir satır)
sorted_langs = sorted(languages, key=lambda x: x['language'])
print("\n")
for i in range(0, len(sorted_langs), 5):
    batch = sorted_langs[i:i+5]
    line = "   ".join([f"{lang['language'].upper():3}" for lang in batch])
    print(f"   {line}")

# İstatistikler
print("\n" + "="*80)
print("📈 İSTATİSTİKLER")
print("="*80)

print(f"\n✅ Toplam desteklenen dil sayısı: {len(languages)}")
print(f"✅ Türk dilleri: {len(found_turkic)}")
print(f"✅ Özbek dili: {'DESTEKLENIYOR ✓' if uzbek_found else 'DESTEKLENMIYOR ✗'}")

# Önemli diller kontrolü
important_langs = {
    'en': 'İngilizce',
    'uz': 'Özbek', 
    'tr': 'Türkçe',
    'ru': 'Rusça',
    'ar': 'Arapça',
    'zh': 'Çince',
    'es': 'İspanyolca',
    'fr': 'Fransızca',
    'de': 'Almanca',
    'ja': 'Japonca'
}

print("\n" + "="*80)
print("🎯 ÖNEMLİ DİLLER KONTROLÜ")
print("="*80)
print("\n")

for code, name in important_langs.items():
    found = any(lang['language'] == code for lang in languages)
    status = "✅" if found else "❌"
    print(f"   {status} {code.upper()}: {name}")

# Detaylı bilgi al (İngilizce dilinde dil isimleri)
print("\n" + "="*80)
print("🔤 DETAYLI DİL BİLGİLERİ (İngilizce İsimlerle)")
print("="*80)

try:
    languages_en = translate_client.get_languages(target_language='en')
    
    # Türk dillerini göster
    print("\n🇹🇷 Türk Dilleri (İngilizce İsimler):\n")
    for lang in languages_en:
        if lang['language'] in turkic_languages:
            print(f"   {lang['language'].upper()}: {lang.get('name', 'N/A')}")
    
    # Özbek dilini detaylı göster
    if uzbek_found:
        uzbek_detail = next((l for l in languages_en if l['language'] == 'uz'), None)
        if uzbek_detail:
            print("\n🇺🇿 Özbek Dili Detayları:")
            print(f"   Kod: {uzbek_detail['language']}")
            print(f"   İngilizce İsim: {uzbek_detail.get('name', 'N/A')}")
            
except Exception as e:
    print(f"\n⚠️  Detaylı bilgi alınamadı: {e}")

print("\n" + "="*80)
print("💡 SONUÇ")
print("="*80)

if uzbek_found:
    print("""
✅ ÖZBEK DİLİ TAM OLARAK DESTEKLENİYOR!

🎯 Kullanım:
   - Dil Kodu: 'uz'
   - İngilizce ↔ Özbek: Destekleniyor
   - Türkçe ↔ Özbek: Destekleniyor (iki yönlü)
   - Rusça ↔ Özbek: Destekleniyor
   
📚 Özellikler:
   - TranslationLLM model desteği
   - Glossary (sözlük) desteği
   - Batch (toplu) çeviri
   - HTML format desteği
   
💰 Fiyatlandırma:
   - Standard: $20 per 1M karakter
   - Advanced (LLM): Kontrol gerekli
   
🔗 Dokümantasyon:
   https://cloud.google.com/translate/docs/languages
""")
else:
    print("""
❌ ÖZBEK DİLİ BULUNAMADI!

Lütfen kontrol edin:
1. API anahtarı doğru mu?
2. Project ID doğru mu?
3. Translation API aktif mi?
""")

print("✅ Kontrol tamamlandı!")
