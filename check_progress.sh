#!/bin/bash

# Cloud Run Jobs ilerleme takibi
# Kullanım: ./check_progress.sh

set -e

PROJECT_ID="sunlit-mantra-479913-i5"
REGION="us-central1"
BUCKET_NAME="smoltalk-translations"

echo "======================================================================"
echo "📊 CLOUD RUN JOBS İLERLEME TAKİBİ"
echo "======================================================================"
echo ""

# Running jobs
echo "🏃 Çalışan Job'lar:"
RUNNING=$(gcloud run jobs executions list --job smoltalk-translate --region ${REGION} --filter="status.conditions.type=Ready AND status.conditions.status=Unknown" --format="value(name)" | wc -l)
echo "  Aktif: ${RUNNING}"
echo ""

# Completed jobs
echo "✅ Tamamlanan Job'lar:"
COMPLETED=$(gcloud run jobs executions list --job smoltalk-translate --region ${REGION} --filter="status.conditions.type=Ready AND status.conditions.status=True" --format="value(name)" | wc -l)
echo "  Başarılı: ${COMPLETED}"
echo ""

# Failed jobs
echo "❌ Başarısız Job'lar:"
FAILED=$(gcloud run jobs executions list --job smoltalk-translate --region ${REGION} --filter="status.conditions.type=Ready AND status.conditions.status=False" --format="value(name)" | wc -l)
echo "  Hatalı: ${FAILED}"
echo ""

# GCS dosyaları
echo "📁 GCS Çıktıları:"
RESULT_COUNT=$(gsutil ls gs://${BUCKET_NAME}/translations/*.jsonl 2>/dev/null | wc -l)
echo "  Dosya sayısı: ${RESULT_COUNT}"
echo ""

# Toplam ilerleme
TOTAL_JOBS=$((RUNNING + COMPLETED + FAILED))
if [ ${TOTAL_JOBS} -gt 0 ]; then
    PROGRESS=$((COMPLETED * 100 / TOTAL_JOBS))
    echo "📈 Genel İlerleme: ${PROGRESS}% (${COMPLETED}/${TOTAL_JOBS})"
    echo ""
fi

# İstatistikler (metadata dosyalarından)
echo "📊 Detaylı İstatistikler:"
echo "  Hesaplanıyor..."

TOTAL_MESSAGES=0
TOTAL_SUCCESS=0
TOTAL_FAILED=0
TOTAL_COST=0

for metadata in $(gsutil ls gs://${BUCKET_NAME}/translations/*_metadata.json 2>/dev/null); do
    MESSAGES=$(gsutil cat $metadata | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_messages', 0))")
    SUCCESS=$(gsutil cat $metadata | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('success_count', 0))")
    FAILED_COUNT=$(gsutil cat $metadata | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('failed_count', 0))")
    COST=$(gsutil cat $metadata | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_cost', 0))")
    
    TOTAL_MESSAGES=$((TOTAL_MESSAGES + MESSAGES))
    TOTAL_SUCCESS=$((TOTAL_SUCCESS + SUCCESS))
    TOTAL_FAILED=$((TOTAL_FAILED + FAILED_COUNT))
    TOTAL_COST=$(python3 -c "print(${TOTAL_COST} + ${COST})")
done

echo ""
echo "  Toplam Mesaj Çevrildi: ${TOTAL_SUCCESS:,}"
echo "  Başarısız Mesaj: ${TOTAL_FAILED}"
echo "  Toplam Maliyet: \$${TOTAL_COST}"
echo ""

echo "======================================================================"
echo ""
echo "💡 Komutlar:"
echo "   Son logları gör: gcloud run jobs executions describe [EXECUTION_NAME] --region ${REGION}"
echo "   Job'ları listele: gcloud run jobs executions list --job smoltalk-translate --region ${REGION}"
echo "   Sonuçları indir: gsutil -m cp -r gs://${BUCKET_NAME}/translations/ ."
echo ""
