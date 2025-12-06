"""
SmolTalk Pilot Test - 10K Örnek Çevirisi
=========================================

Bu script:
1. HuggingFace'den SmolTalk dataset'ini indirir
2. Rastgele 10,000 örnek seçer
3. Filtering uygular (kod blokları, kısa mesajlar vb.)
4. İngilizce → Özbek çevirisini yapar
5. Maliyet ve kalite metriklerini toplar
"""

import json
import re
import time
from typing import List, Dict
from google.cloud import translate as translate_advanced
from collections import defaultdict

# Google Cloud Project
PROJECT_ID = "sunlit-mantra-479913-i5"
LOCATION = "us-central1"

# Pilot test parametreleri
TOTAL_SAMPLES = 100  # Önce küçük test, sonra 10_000'e çıkarırız
OUTPUT_FILE = "pilot_test_results.jsonl"
STATS_FILE = "pilot_test_stats.json"

print("="*80)
print("🧪 SMOLTALK PILOT TEST - İNGİLİZCE → ÖZBEK")
print("="*80)

# ============================================================================
# FILTERING FONKSİYONLARI
# ============================================================================

def contains_code_block(text: str) -> bool:
    """Kod bloğu içeriyor mu kontrol et"""
    code_patterns = [
        r'```',  # Markdown code blocks
        r'^\s*(def |class |import |from |function |const |let |var )',  # Programming keywords
        r'\{.*\}.*\{.*\}',  # Multiple braces (likely code)
    ]
    for pattern in code_patterns:
        if re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
            return True
    return False

def is_too_short(text: str, min_length: int = 50) -> bool:
    """Çok kısa mı?"""
    return len(text.strip()) < min_length

def has_too_many_urls(text: str) -> bool:
    """Çok fazla URL var mı?"""
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return len(urls) > 2

def should_skip_message(content: str) -> bool:
    """Bu mesaj çevrilmemeli mi?"""
    if is_too_short(content, min_length=30):
        return True
    if contains_code_block(content):
        return True
    if has_too_many_urls(content):
        return True
    return False

def extract_translatable_text(conversation: List[Dict]) -> List[Dict]:
    """Konuşmadan çevrilecek mesajları çıkar"""
    translatable = []
    
    for msg in conversation:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        # System mesajlarını atla
        if role == 'system':
            continue
            
        # Sadece user mesajlarını çevir (cost optimization)
        if role == 'user':
            if not should_skip_message(content):
                translatable.append({
                    'role': role,
                    'original': content,
                    'translatable': True
                })
            else:
                translatable.append({
                    'role': role,
                    'original': content,
                    'translatable': False,
                    'skip_reason': 'filtered'
                })
        else:
            # Assistant mesajlarını çevirme (İngilizce bırak)
            translatable.append({
                'role': role,
                'original': content,
                'translatable': False,
                'skip_reason': 'assistant_message'
            })
    
    return translatable

# ============================================================================
# ÇEVİRİ FONKSİYONLARI
# ============================================================================

def translate_text(text: str, client, parent: str, model_path: str) -> Dict:
    """Tek bir metni çevir ve metrikleri döndür"""
    try:
        start_time = time.time()
        
        response = client.translate_text(
            request={
                "contents": [text],
                "target_language_code": "uz",
                "source_language_code": "en",
                "parent": parent,
                "model": model_path,
                "mime_type": "text/plain",
            }
        )
        
        translation_time = time.time() - start_time
        translated = response.translations[0].translated_text
        
        return {
            'translated': translated,
            'time': translation_time,
            'chars': len(text),
            'status': 'success'
        }
    except Exception as e:
        return {
            'error': str(e),
            'time': 0,
            'chars': len(text),
            'status': 'failed'
        }

# ============================================================================
# DATASET LOADING
# ============================================================================

def load_smoltalk_dataset(num_samples: int = 100, use_real_data: bool = True) -> List[Dict]:
    """SmolTalk dataset'ini yükle"""
    
    if not use_real_data:
        # Mock data kullan
        return generate_sample_data(num_samples)
    
    try:
        from datasets import load_dataset
        
        print(f"   • HuggingFace'den SmolTalk yükleniyor...")
        
        # SmolTalk dataset'ini yükle
        dataset = load_dataset(
            "HuggingFaceTB/smoltalk",
            "all",
            split="train",
            streaming=True  # Tüm dataset'i indirmeden stream et
        )
        
        # İlk num_samples örneği al
        samples = []
        for idx, item in enumerate(dataset):
            if idx >= num_samples:
                break
            
            # Dataset formatı: {'messages': [...]}
            samples.append({
                'messages': item.get('messages', []),
                'id': f'smoltalk_{idx}'
            })
            
            if (idx + 1) % 1000 == 0:
                print(f"      {idx + 1} örnek yüklendi...")
        
        return samples
        
    except Exception as e:
        print(f"   ⚠️  Gerçek dataset yüklenemedi: {e}")
        print(f"   ℹ️  Mock data kullanılıyor...")
        return generate_sample_data(num_samples)

def generate_sample_data(num_samples: int = 100) -> List[Dict]:
    """Test için örnek veri üret (gerçek dataset yerine)"""
    
    sample_conversations = [
        [
            {"role": "user", "content": "Hello! How can machine learning help in healthcare?"},
            {"role": "assistant", "content": "Machine learning can revolutionize healthcare in several ways..."}
        ],
        [
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."}
        ],
        [
            {"role": "user", "content": "Explain quantum computing in simple terms."},
            {"role": "assistant", "content": "Quantum computing uses quantum mechanics principles..."}
        ],
        [
            {"role": "user", "content": "Write a Python function to reverse a string."},
            {"role": "assistant", "content": "```python\ndef reverse_string(s):\n    return s[::-1]\n```"}
        ],
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about climate change and its effects on the environment."},
            {"role": "assistant", "content": "Climate change is one of the most pressing issues..."}
        ],
    ]
    
    # Örnekleri tekrarla
    samples = []
    for i in range(num_samples):
        conv = sample_conversations[i % len(sample_conversations)]
        samples.append({
            'messages': conv,
            'id': f'sample_{i}'
        })
    
    return samples

# ============================================================================
# ANA PROGRAM
# ============================================================================

def main():
    print("\n📦 1. HAZIRLIK")
    print("-" * 80)
    
    # Translation API Client
    print("   • Translation API başlatılıyor...")
    try:
        translation_client = translate_advanced.TranslationServiceClient()
        parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
        model_path = f"{parent}/models/general/translation-llm"
        print("   ✅ Translation API hazır!")
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return
    
    # Dataset yükle (mock data)
    print(f"   • {TOTAL_SAMPLES} örnek yükleniyor...")
    USE_REAL_DATA = True  # False yaparak mock data kullanabilirsiniz
    dataset = load_smoltalk_dataset(TOTAL_SAMPLES, use_real_data=USE_REAL_DATA)
    print(f"   ✅ {len(dataset)} örnek yüklendi")
    
    # İstatistikler
    stats = {
        'total_samples': len(dataset),
        'total_messages': 0,
        'translatable_messages': 0,
        'skipped_messages': 0,
        'skip_reasons': defaultdict(int),
        'successful_translations': 0,
        'failed_translations': 0,
        'total_chars_original': 0,
        'total_chars_translated': 0,
        'total_time': 0,
        'total_cost_usd': 0,
    }
    
    # ============================================================================
    # 2. FİLTRELEME VE ÇEVİRİ
    # ============================================================================
    
    print(f"\n📝 2. FİLTRELEME VE ÇEVİRİ")
    print("-" * 80)
    
    results = []
    
    for idx, sample in enumerate(dataset, 1):
        if idx % 100 == 0:
            print(f"   İşleniyor: {idx}/{len(dataset)} ({idx/len(dataset)*100:.1f}%)")
        
        conversation = sample.get('messages', [])
        sample_id = sample.get('id', f'sample_{idx}')
        
        # Filtering uygula
        translatable_msgs = extract_translatable_text(conversation)
        
        # Her mesaj için istatistik
        stats['total_messages'] += len(translatable_msgs)
        
        # Çeviriyi yap
        translated_conversation = []
        
        for msg in translatable_msgs:
            if msg['translatable']:
                stats['translatable_messages'] += 1
                stats['total_chars_original'] += msg.get('chars', len(msg['original']))
                
                # Çevir
                result = translate_text(
                    msg['original'],
                    translation_client,
                    parent,
                    model_path
                )
                
                if result['status'] == 'success':
                    stats['successful_translations'] += 1
                    stats['total_chars_translated'] += len(result['translated'])
                    stats['total_time'] += result['time']
                    
                    translated_conversation.append({
                        'role': msg['role'],
                        'original': msg['original'],
                        'translated': result['translated'],
                        'translation_time': result['time'],
                        'chars': result['chars']
                    })
                else:
                    stats['failed_translations'] += 1
                    translated_conversation.append({
                        'role': msg['role'],
                        'original': msg['original'],
                        'error': result.get('error'),
                    })
                
                # Rate limiting
                time.sleep(0.1)
            else:
                stats['skipped_messages'] += 1
                stats['skip_reasons'][msg.get('skip_reason', 'unknown')] += 1
                
                translated_conversation.append({
                    'role': msg['role'],
                    'original': msg['original'],
                    'skipped': True,
                    'reason': msg.get('skip_reason')
                })
        
        # Sonucu kaydet
        results.append({
            'id': sample_id,
            'conversation': translated_conversation
        })
    
    # ============================================================================
    # 3. SONUÇLARI KAYDET
    # ============================================================================
    
    print(f"\n💾 3. SONUÇLARI KAYDET")
    print("-" * 80)
    
    # JSONL formatında kaydet
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    print(f"   ✅ Çeviri sonuçları kaydedildi: {OUTPUT_FILE}")
    
    # Maliyet hesapla
    stats['total_cost_usd'] = (stats['total_chars_original'] / 1_000_000) * 20
    stats['total_cost_try'] = stats['total_cost_usd'] * 34
    stats['avg_time_per_translation'] = stats['total_time'] / max(stats['successful_translations'], 1)
    stats['avg_chars_per_message'] = stats['total_chars_original'] / max(stats['translatable_messages'], 1)
    
    # İstatistikleri kaydet
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"   ✅ İstatistikler kaydedildi: {STATS_FILE}")
    
    # ============================================================================
    # 4. ÖZET RAPOR
    # ============================================================================
    
    print(f"\n" + "="*80)
    print("📊 PILOT TEST SONUÇLARI")
    print("="*80)
    
    print(f"\n📈 Dataset İstatistikleri:")
    print(f"   Toplam Örnek: {stats['total_samples']:,}")
    print(f"   Toplam Mesaj: {stats['total_messages']:,}")
    print(f"   Çevrilen Mesaj: {stats['translatable_messages']:,}")
    print(f"   Atlanan Mesaj: {stats['skipped_messages']:,}")
    
    print(f"\n🎯 Atlama Nedenleri:")
    for reason, count in stats['skip_reasons'].items():
        print(f"   {reason}: {count:,}")
    
    print(f"\n✅ Çeviri Başarısı:")
    print(f"   Başarılı: {stats['successful_translations']:,}")
    print(f"   Başarısız: {stats['failed_translations']:,}")
    print(f"   Başarı Oranı: {stats['successful_translations']/max(stats['translatable_messages'],1)*100:.1f}%")
    
    print(f"\n📊 Karakter İstatistikleri:")
    print(f"   Toplam Karakter (Orijinal): {stats['total_chars_original']:,}")
    print(f"   Toplam Karakter (Çeviri): {stats['total_chars_translated']:,}")
    print(f"   Ortalama Karakter/Mesaj: {stats['avg_chars_per_message']:.0f}")
    
    print(f"\n⏱️  Performans:")
    print(f"   Toplam Süre: {stats['total_time']:.1f} saniye ({stats['total_time']/60:.1f} dakika)")
    print(f"   Ortalama Süre/Çeviri: {stats['avg_time_per_translation']:.2f} saniye")
    
    print(f"\n💰 Maliyet:")
    print(f"   Toplam (USD): ${stats['total_cost_usd']:.2f}")
    print(f"   Toplam (TRY): ₺{stats['total_cost_try']:.2f}")
    
    # Tam dataset projeksiyonu
    if stats['total_samples'] > 0:
        scale_factor = 1_040_000 / stats['total_samples']
        projected_cost = stats['total_cost_usd'] * scale_factor
        projected_chars = stats['total_chars_original'] * scale_factor
        projected_time = stats['total_time'] * scale_factor
        
        print(f"\n📈 TAM DATASET PROJEKSİYONU (1.04M örnek):")
        print(f"   Tahmini Karakter: {projected_chars:,.0f}")
        print(f"   Tahmini Maliyet (USD): ${projected_cost:,.2f}")
        print(f"   Tahmini Maliyet (TRY): ₺{projected_cost * 34:,.2f}")
        print(f"   Tahmini Süre (tek thread): {projected_time/3600:.1f} saat")
        print(f"   Tahmini Süre (100 worker): {projected_time/3600/100:.1f} saat")
    
    print(f"\n✅ Pilot test tamamlandı!")
    print(f"\n📁 Çıktı Dosyaları:")
    print(f"   • {OUTPUT_FILE}")
    print(f"   • {STATS_FILE}")

if __name__ == "__main__":
    main()
