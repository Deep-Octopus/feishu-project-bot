#!/bin/bash
set -e

echo "=== 飞书项目进度管理机器人 部署脚本 ==="

# Pull latest code
git pull origin main

# Build images
docker-compose build --no-cache

# Stop old containers
docker-compose down

# Start new containers
docker-compose up -d

# Wait for postgres to be ready
echo "Waiting for database..."
sleep 5

# Show logs
echo "=== 服务启动日志 ==="
docker-compose logs --tail=50
echo "=== 部署完成 ==="
