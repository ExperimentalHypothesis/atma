#!/bin/bash

# Simple deployment script for atma.fm on Ubuntu server
# Run this script on your Ubuntu server to deploy the latest version

set -e

echo "🚀 Deploying atma.fm..."

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin master

# Stop running containers
echo "🛑 Stopping current containers..."
docker-compose down

# Remove the override file if it exists (local dev only)
if [ -f "docker-compose.override.yaml" ]; then
    echo "🗑️  Removing local development override..."
    rm docker-compose.override.yaml
fi

# Rebuild and start
echo "🔨 Building and starting containers..."
docker-compose up -d --build

# Wait a bit for containers to start
sleep 3

# Show logs
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Container status:"
docker-compose ps

echo ""
echo "📝 Recent logs:"
docker-compose logs --tail=20

echo ""
echo "🌐 Your app should be running on http://your-server-ip:5555"
echo ""
echo "To view live logs, run: docker-compose logs -f"