"""
JSONL'i GitHub için Markdown Tablosuna Dönüştürme
================================================

Bu script pilot_test_results.jsonl dosyasını
GitHub'da güzel görünen markdown tablosuna çevirir.
"""

import json
import sys

def jsonl_to_markdown_table(input_file: str, output_file: str, max_rows: int = 50):
    """JSONL'i markdown tablosuna çevir"""
    
    print(f"📖 {input_file} okunuyor...")
    
    results = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx >= max_rows:
                break
            try:
                data = json.loads(line)
                results.append(data)
            except json.JSONDecodeError:
                print(f"⚠️  Satır {idx+1} atlandı (JSON hatası)")
    
    print(f"✅ {len(results)} örnek yüklendi")
    
    # Markdown tablosu oluştur
    markdown = []
    markdown.append("# SmolTalk Pilot Test Sonuçları - İngilizce → Özbek\n")
    markdown.append(f"**Toplam Örnek:** {len(results)}\n")
    markdown.append("---\n")
    
    # Her konuşma için detaylı tablo
    for idx, result in enumerate(results, 1):
        conv_id = result.get('id', f'conversation_{idx}')
        conversation = result.get('conversation', [])
        
        markdown.append(f"\n## Örnek {idx}: `{conv_id}`\n")
        
        # Tablo başlıkları
        markdown.append("| Role | Orijinal (EN) | Çeviri (UZ) | Süre | Karakter |\n")
        markdown.append("|------|---------------|-------------|------|----------|\n")
        
        for msg in conversation:
            role = msg.get('role', 'unknown')
            original = msg.get('original', '')
            translated = msg.get('translated', '-')
            skipped = msg.get('skipped', False)
            
            # Metni kısalt (GitHub tablo genişliği için)
            original_short = (original[:80] + '...') if len(original) > 80 else original
            
            if skipped:
                reason = msg.get('reason', 'unknown')
                markdown.append(f"| {role} | {original_short} | *(atlandı: {reason})* | - | - |\n")
            else:
                translated_short = (translated[:80] + '...') if len(translated) > 80 else translated
                time_str = f"{msg.get('translation_time', 0):.2f}s" if 'translation_time' in msg else '-'
                chars = msg.get('chars', len(original))
                markdown.append(f"| {role} | {original_short} | {translated_short} | {time_str} | {chars} |\n")
        
        if idx >= 10:  # İlk 10 örnek yeterli
            markdown.append(f"\n*... ve {len(results) - 10} örnek daha*\n")
            break
    
    # Dosyaya yaz
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(markdown))
    
    print(f"✅ Markdown tablosu oluşturuldu: {output_file}")
    print(f"   GitHub'da README olarak veya ayrı dosya olarak ekleyebilirsiniz")

def create_summary_table(input_file: str, output_file: str):
    """Özet tablo oluştur (daha kompakt)"""
    
    print(f"\n📊 Özet tablo oluşturuluyor...")
    
    results = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                results.append(json.loads(line))
            except:
                pass
    
    markdown = []
    markdown.append("# SmolTalk Pilot Test - Özet Tablo\n\n")
    
    # Özet istatistikler
    total_conversations = len(results)
    total_translated = 0
    total_skipped = 0
    total_time = 0
    total_chars = 0
    
    for result in results:
        for msg in result.get('conversation', []):
            if msg.get('skipped'):
                total_skipped += 1
            elif 'translated' in msg:
                total_translated += 1
                total_time += msg.get('translation_time', 0)
                total_chars += msg.get('chars', 0)
    
    markdown.append("## 📊 Genel İstatistikler\n\n")
    markdown.append("| Metrik | Değer |\n")
    markdown.append("|--------|-------|\n")
    markdown.append(f"| Toplam Konuşma | {total_conversations} |\n")
    markdown.append(f"| Çevrilen Mesaj | {total_translated} |\n")
    markdown.append(f"| Atlanan Mesaj | {total_skipped} |\n")
    markdown.append(f"| Toplam Karakter | {total_chars:,} |\n")
    markdown.append(f"| Toplam Süre | {total_time:.1f}s ({total_time/60:.1f} dk) |\n")
    markdown.append(f"| Ort. Süre/Çeviri | {total_time/max(total_translated, 1):.2f}s |\n\n")
    
    # Örnek çeviriler
    markdown.append("## 🔍 Örnek Çeviriler\n\n")
    markdown.append("| # | Orijinal (EN) | Çeviri (UZ) | Süre |\n")
    markdown.append("|---|---------------|-------------|------|\n")
    
    example_count = 0
    for result in results:
        if example_count >= 20:
            break
        for msg in result.get('conversation', []):
            if 'translated' in msg and not msg.get('skipped'):
                original = msg.get('original', '')[:100]
                translated = msg.get('translated', '')[:100]
                time_val = msg.get('translation_time', 0)
                markdown.append(f"| {example_count + 1} | {original}... | {translated}... | {time_val:.2f}s |\n")
                example_count += 1
                if example_count >= 20:
                    break
    
    # Dosyaya yaz
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(markdown))
    
    print(f"✅ Özet tablo oluşturuldu: {output_file}")

def create_csv_export(input_file: str, output_file: str):
    """CSV formatında export (Excel/Google Sheets için)"""
    
    import csv
    
    print(f"\n📊 CSV export oluşturuluyor...")
    
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                conv_id = data.get('id', '')
                for msg in data.get('conversation', []):
                    rows.append({
                        'conversation_id': conv_id,
                        'role': msg.get('role', ''),
                        'original': msg.get('original', ''),
                        'translated': msg.get('translated', ''),
                        'skipped': msg.get('skipped', False),
                        'skip_reason': msg.get('reason', ''),
                        'translation_time': msg.get('translation_time', ''),
                        'chars': msg.get('chars', '')
                    })
            except:
                pass
    
    # CSV'ye yaz
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    
    print(f"✅ CSV export oluşturuldu: {output_file}")
    print(f"   GitHub'da .csv dosyası otomatik tablo olarak görünür!")

if __name__ == "__main__":
    input_file = "pilot_test_results.jsonl"
    
    print("="*80)
    print("📋 JSONL → GITHUB TABLO DÖNÜŞTÜRÜCÜ")
    print("="*80)
    
    # 1. Detaylı markdown tablo
    create_summary_table(input_file, "PILOT_RESULTS_TABLE.md")
    
    # 2. CSV export (GitHub otomatik tablo yapacak)
    create_csv_export(input_file, "pilot_results.csv")
    
    print("\n" + "="*80)
    print("✅ TAMAMLANDI!")
    print("="*80)
    print("\nGitHub'a yükleme için:")
    print("1. PILOT_RESULTS_TABLE.md - Markdown tablo (README'ye eklenebilir)")
    print("2. pilot_results.csv - CSV dosya (GitHub otomatik tablo gösterir)")
    print("\nGitHub CSV görünümü:")
    print("   → CSV dosyasını GitHub'a push edin")
    print("   → GitHub otomatik olarak tablo view sağlar")
    print("   → Filtreleme ve sıralama yapılabilir!")
