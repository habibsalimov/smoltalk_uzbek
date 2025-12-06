#!/bin/bash

# SmolTalk Translation - Cloud Run Jobs Setup
# ============================================

set -e

PROJECT_ID="sunlit-mantra-479913-i5"
REGION="us-central1"
IMAGE_NAME="smoltalk-translator"
BUCKET_NAME="smoltalk-translations"
IMAGE_URI="gcr.io/${PROJECT_ID}/${IMAGE_NAME}"

echo "======================================================================"
echo "🚀 SMOLTALK TRANSLATION - CLOUD RUN JOBS KURULUM"
echo "======================================================================"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Image: ${IMAGE_URI}"
echo "Bucket: gs://${BUCKET_NAME}"
echo ""

# 1. GCS Bucket oluştur
echo "📦 GCS Bucket oluşturuluyor..."
if gsutil ls -b gs://${BUCKET_NAME} &>/dev/null; then
    echo "  ✅ Bucket zaten mevcut"
else
    gsutil mb -p ${PROJECT_ID} -l ${REGION} gs://${BUCKET_NAME}
    echo "  ✅ Bucket oluşturuldu: gs://${BUCKET_NAME}"
fi
echo ""

# 2. Docker image build
echo "🐳 Docker image build ediliyor..."
docker build -t ${IMAGE_URI} .
echo "  ✅ Image build tamamlandı"
echo ""

# 3. Docker image push
echo "📤 Image push ediliyor..."
docker push ${IMAGE_URI}
echo "  ✅ Image push tamamlandı: ${IMAGE_URI}"
echo ""

# 4. Cloud Run Job oluştur
echo "☁️  Cloud Run Job oluşturuluyor..."

# Job varsa sil
if gcloud run jobs describe smoltalk-translate --region=${REGION} &>/dev/null; then
    echo "  ⚠️  Job zaten mevcut, siliniyor..."
    gcloud run jobs delete smoltalk-translate --region=${REGION} --quiet
fi

gcloud run jobs create smoltalk-translate \
    --image ${IMAGE_URI} \
    --region ${REGION} \
    --set-env-vars PROJECT_ID=${PROJECT_ID},OUTPUT_BUCKET=${BUCKET_NAME},WORKERS=10 \
    --memory 2Gi \
    --cpu 2 \
    --max-retries 3 \
    --task-timeout 1h \
    --parallelism 1

echo "  ✅ Cloud Run Job oluşturuldu: smoltalk-translate"
echo ""

echo "======================================================================"
echo "✅ KURULUM TAMAMLANDI!"
echo "======================================================================"
echo ""
echo "📝 Sonraki Adımlar:"
echo ""
echo "1. TEK JOB TEST:"
echo "   ./run_job.sh 0 100"
echo ""
echo "2. PARALEL 10 JOB TEST:"
echo "   ./run_parallel_jobs.sh 10"
echo ""
echo "3. TAM DATASET (100 JOB):"
echo "   ./run_parallel_jobs.sh 100"
echo ""
echo "4. SONUÇLARI KONTROL ET:"
echo "   gsutil ls gs://${BUCKET_NAME}/translations/"
echo "   ./check_progress.sh"
echo ""
