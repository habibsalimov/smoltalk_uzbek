#!/bin/bash

# Birden fazla Cloud Run Job'u paralel çalıştır
# Kullanım: ./run_parallel_jobs.sh NUM_JOBS

set -e

NUM_JOBS=${1:-10}
TOTAL_CONVERSATIONS=1040000  # SmolTalk toplam konuşma sayısı (yaklaşık)
SAMPLES_PER_JOB=$((TOTAL_CONVERSATIONS / NUM_JOBS))

PROJECT_ID="sunlit-mantra-479913-i5"
REGION="us-central1"

echo "======================================================================"
echo "🚀 PARALEL CLOUD RUN JOBS BAŞLATILIYOR"
echo "======================================================================"
echo ""
echo "Toplam Job Sayısı: ${NUM_JOBS}"
echo "Job Başına Örnek: ${SAMPLES_PER_JOB}"
echo ""
echo "⚠️  UYARI: ${NUM_JOBS} job paralel başlatılacak!"
echo "   Maliyet tahmini: ~$${NUM_JOBS} (Cloud Run) + ~$1,350 (Gemini)"
echo ""
read -p "Devam etmek istiyor musunuz? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ İptal edildi"
    exit 1
fi
echo ""

# Her job için START ve END indexleri hesapla
echo "📋 Job'lar oluşturuluyor..."
for ((i=0; i<NUM_JOBS; i++)); do
    START_INDEX=$((i * SAMPLES_PER_JOB))
    END_INDEX=$(((i + 1) * SAMPLES_PER_JOB))
    
    echo "  Job $((i+1))/${NUM_JOBS}: Range ${START_INDEX} → ${END_INDEX}"
    
    # Job'u background'da başlat
    (
        gcloud run jobs execute smoltalk-translate \
            --region ${REGION} \
            --set-env-vars START_INDEX=${START_INDEX},END_INDEX=${END_INDEX},TASK_INDEX=${i} \
            --async \
            --quiet
    ) &
    
    # Rate limiting - her 5 job'da bir 2 saniye bekle
    if [ $((i % 5)) -eq 4 ]; then
        sleep 2
    fi
done

echo ""
echo "======================================================================"
echo "✅ TÜM JOB'LAR BAŞLATILDI"
echo "======================================================================"
echo ""
echo "📊 İleremeyi takip et:"
echo "   ./check_progress.sh"
echo ""
echo "📋 Job loglarını görüntüle:"
echo "   gcloud run jobs executions list --job smoltalk-translate --region ${REGION}"
echo ""
echo "⏱️  Tahmini tamamlanma süresi: 3-4 gün"
echo ""
