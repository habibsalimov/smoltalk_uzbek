#!/bin/bash

# Tek bir Cloud Run Job çalıştır
# Kullanım: ./run_job.sh START_INDEX END_INDEX

set -e

START_INDEX=${1:-0}
END_INDEX=${2:-1000}
PROJECT_ID="sunlit-mantra-479913-i5"
REGION="us-central1"
BUCKET_NAME="smoltalk-translations"

echo "======================================================================"
echo "🚀 CLOUD RUN JOB BAŞLATILIYOR"
echo "======================================================================"
echo ""
echo "Range: ${START_INDEX} → ${END_INDEX}"
echo ""

# Job'u çalıştır
gcloud run jobs execute smoltalk-translate \
    --region ${REGION} \
    --set-env-vars START_INDEX=${START_INDEX},END_INDEX=${END_INDEX} \
    --wait

echo ""
echo "======================================================================"
echo "✅ JOB TAMAMLANDI"
echo "======================================================================"
echo ""
echo "📊 Sonuçları kontrol et:"
echo "   gsutil ls gs://${BUCKET_NAME}/translations/"
echo ""
