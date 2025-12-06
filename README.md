# SmolTalk Uzbek Translation - Pilot Test

İngilizce-Özbek çeviri projesi için Google Cloud Translation API kullanılarak yapılan pilot test sonuçları.

[![Translation](https://img.shields.io/badge/Translation-EN%20%E2%86%92%20UZ-blue)](https://cloud.google.com/translate)
[![Dataset](https://img.shields.io/badge/Dataset-SmolTalk-orange)](https://huggingface.co/datasets/HuggingFaceTB/smoltalk)
[![API](https://img.shields.io/badge/API-TranslationLLM-green)](https://cloud.google.com/translate/docs)

## 📊 Pilot Test Özeti

- **Test Tarihi:** 6 Aralık 2025
- **Örnek Sayısı:** 100 konuşma
- **Çevrilen Mesaj:** 146
- **Başarı Oranı:** %100
- **Toplam Maliyet:** $1.69 (₺57.42)

## 📁 Dosyalar

| Dosya | Açıklama | Format |
|-------|----------|--------|
| [`pilot_results.csv`](pilot_results.csv) | Tüm çeviri sonuçları (GitHub'da tablo olarak görünür) | CSV |
| [`PILOT_RESULTS_TABLE.md`](PILOT_RESULTS_TABLE.md) | Özet tablo ve örnekler | Markdown |
| [`PILOT_TEST_REPORT.md`](PILOT_TEST_REPORT.md) | Detaylı analiz raporu | Markdown |
| [`pilot_test_results.jsonl`](pilot_test_results.jsonl) | Ham çeviri verileri | JSONL |
| [`pilot_test_stats.json`](pilot_test_stats.json) | İstatistik metrikleri | JSON |

## 🔍 Sonuçları Görüntüleme

### GitHub'da CSV Görünümü (Önerilen)

1. [`pilot_results.csv`](pilot_results.csv) dosyasına tıklayın
2. GitHub otomatik olarak tablo görünümü sağlar
3. Filtreleme ve sıralama yapabilirsiniz

### Markdown Tablosu

Kısaltılmış örnekler için [`PILOT_RESULTS_TABLE.md`](PILOT_RESULTS_TABLE.md) dosyasına bakın.

## 📈 Önemli Bulgular

✅ **Başarılar:**
- %100 çeviri başarı oranı
- Ortalama 0.98 saniye/çeviri
- Teknik terimler ve matematik formülleri korunuyor
- Filtering ile %43 maliyet tasarrufu

📊 **Tam Dataset Projeksiyonu (1.04M örnek):**
- Tahmini Maliyet: $17,563 (₺597,146)
- Tahmini Süre: ~4.1 saat (100 paralel worker ile)

## 🚀 Kullanılan Teknolojiler

- **Dataset:** [HuggingFace SmolTalk](https://huggingface.co/datasets/HuggingFaceTB/smoltalk)
- **Çeviri API:** Google Cloud Translation API
- **Model:** TranslationLLM (general/translation-llm)
- **Diller:** İngilizce → Özbek

## 📝 Örnek Çeviri

**İngilizce:**
> The function g(x) satisfies the functional equation g(x + y) = g(x) + g(y) for all real numbers x and y...

**Özbekçe:**
> Funksiya g(x) barcha haqiqiy sonlar x va y uchun funksional tenglamani qanoatlantiradi...

⏱️ **Süre:** 1.23s | 📊 **Karakter:** 183

## 📖 Detaylı Dökümanlar

- [Pilot Test Raporu](PILOT_TEST_REPORT.md) - Detaylı analiz ve bulgular
- [Maliyet Analizi](SMOLTALK_TRANSLATION_ANALYSIS.md) - Tam dataset için tahminler

## 🛠️ Scriptler

- `pilot_test_smoltalk.py` - Ana test scripti
- `convert_jsonl_to_table.py` - JSONL → Markdown/CSV dönüştürücü
- `test_uzbek_translation.py` - Özbek dili test scripti
- `validate_language_support.py` - Dil desteği doğrulama

## 📞 İletişim

**Repository:** [habibsalimov/smoltalk_uzbek](https://github.com/habibsalimov/smoltalk_uzbek)

---

*Son güncelleme: 6 Aralık 2025*
