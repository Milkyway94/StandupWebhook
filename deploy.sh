#!/bin/bash
# Quick deployment script for Daily Standup Webhook

set -e

echo "🚀 Deploying Daily Standup Webhook..."
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker found"
echo "✅ Docker Compose found: $COMPOSE_CMD"
echo ""

# Stop existing container
echo "🛑 Stopping existing container..."
$COMPOSE_CMD down 2>/dev/null || true

# Build new image
echo "🔨 Building new image..."
$COMPOSE_CMD build --no-cache

# Start container
echo "▶️  Starting container..."
$COMPOSE_CMD up -d

# Wait for container to be healthy
echo "⏳ Waiting for container to be ready..."
sleep 5

# Check status
if $COMPOSE_CMD ps | grep -q "Up"; then
    echo ""
    echo "✅ ======================================"
    echo "✅  Deployment successful!"
    echo "✅ ======================================"
    echo ""
    echo "📊 Container status:"
    $COMPOSE_CMD ps
    echo ""
    echo "📝 View logs: $COMPOSE_CMD logs -f"
    echo "🔍 Health check: curl http://localhost:8080"
    echo "🛑 Stop: $COMPOSE_CMD down"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "📋 Checking logs..."
    $COMPOSE_CMD logs
    exit 1
fi
