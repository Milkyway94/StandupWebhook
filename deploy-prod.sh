#!/bin/bash
# Production deployment script for Daily Standup Webhook
# Uses pre-built image from registry.fourier.group

set -e

REGISTRY="registry.fourier.group"
IMAGE_NAME="bot/daily-standup-webhook"
IMAGE_TAG="latest"
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🚀 Deploying Daily Standup Webhook (Production)"
echo "================================================"
echo "Image: ${FULL_IMAGE}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Login to registry
echo "🔐 Logging in to registry..."
if ! docker login ${REGISTRY} -u digital; then
    echo "❌ Login failed. Please check credentials."
    exit 1
fi

# Pull latest image
echo "📦 Pulling latest image..."
docker pull ${FULL_IMAGE}

# Stop and remove old container
echo "🛑 Stopping old container..."
docker stop daily-standup-webhook 2>/dev/null || true
docker rm daily-standup-webhook 2>/dev/null || true

# Run new container
echo "▶️  Starting new container..."
docker run -d \
  --name daily-standup-webhook \
  --restart unless-stopped \
  -p 8080:8080 \
  ${FULL_IMAGE}

# Wait for container to start
echo "⏳ Waiting for container to be ready..."
sleep 5

# Check status
if docker ps | grep -q daily-standup-webhook; then
    echo ""
    echo "✅ ======================================"
    echo "✅  Deployment successful!"
    echo "✅ ======================================"
    echo ""
    echo "📊 Container info:"
    docker ps | grep daily-standup-webhook
    echo ""
    echo "📝 View logs: docker logs -f daily-standup-webhook"
    echo "🔍 Test: curl http://localhost:8080"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "📋 Checking logs..."
    docker logs daily-standup-webhook 2>&1
    exit 1
fi
