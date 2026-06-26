#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env.tencent"
DB_FILE="${ROOT_DIR}/backend/product_mvp.db"
DB_BACKUP_DIR="${ROOT_DIR}/backend/db_backups"
NETWORK_NAME="tencent-cloud_default"
BACKEND_CONTAINER="tencent-cloud_backend_1"
FRONTEND_CONTAINER="tencent-cloud_frontend_1"
NGINX_CONTAINER="tencent-cloud_nginx_1"
BACKEND_IMAGE="tencent-cloud_backend"
FRONTEND_IMAGE="tencent-cloud_frontend"
NGINX_IMAGE="docker.m.daocloud.io/library/nginx:1.27-alpine"

if [ ! -f "${ENV_FILE}" ]; then
  echo "缺少 ${ENV_FILE}，请先从 .env.tencent.example 复制一份并填好真实值"
  exit 1
fi

mkdir -p "${DB_BACKUP_DIR}"
touch "${DB_FILE}"

if [ -s "${DB_FILE}" ]; then
  backup_file="${DB_BACKUP_DIR}/product_mvp_$(date +%Y%m%d_%H%M%S).db"
  cp "${DB_FILE}" "${backup_file}"
  echo "已备份数据库到 ${backup_file}"
fi

set -a
. "${ENV_FILE}"
set +a

echo "开始构建后端镜像..."
sudo docker build \
  -t "${BACKEND_IMAGE}" \
  -f "${SCRIPT_DIR}/backend.Dockerfile" \
  "${ROOT_DIR}"

echo "开始构建前端镜像..."
sudo docker build \
  --build-arg NEXT_PUBLIC_API_BASE="${NEXT_PUBLIC_API_BASE:-}" \
  --build-arg NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-}" \
  --build-arg NEXT_PUBLIC_WS_URL="${NEXT_PUBLIC_WS_URL:-}" \
  -t "${FRONTEND_IMAGE}" \
  -f "${SCRIPT_DIR}/frontend.Dockerfile" \
  "${ROOT_DIR}"

sudo docker network inspect "${NETWORK_NAME}" >/dev/null 2>&1 || sudo docker network create "${NETWORK_NAME}"

echo "重启后端容器..."
sudo docker rm -f "${BACKEND_CONTAINER}" >/dev/null 2>&1 || true
sudo docker run -d \
  --name "${BACKEND_CONTAINER}" \
  --network "${NETWORK_NAME}" \
  --network-alias backend \
  --restart unless-stopped \
  --env-file "${ENV_FILE}" \
  -e PORT=8000 \
  -v "${DB_FILE}:/app/product_mvp.db" \
  "${BACKEND_IMAGE}" >/dev/null

echo "重启前端容器..."
sudo docker rm -f "${FRONTEND_CONTAINER}" >/dev/null 2>&1 || true
sudo docker run -d \
  --name "${FRONTEND_CONTAINER}" \
  --network "${NETWORK_NAME}" \
  --network-alias frontend \
  --restart unless-stopped \
  -e NODE_ENV=production \
  -e PORT=3000 \
  -e NEXT_PUBLIC_API_BASE="${NEXT_PUBLIC_API_BASE:-}" \
  -e NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-}" \
  -e NEXT_PUBLIC_WS_URL="${NEXT_PUBLIC_WS_URL:-}" \
  "${FRONTEND_IMAGE}" >/dev/null

echo "重启 Nginx 容器..."
sudo docker rm -f "${NGINX_CONTAINER}" >/dev/null 2>&1 || true
sudo docker run -d \
  --name "${NGINX_CONTAINER}" \
  --network "${NETWORK_NAME}" \
  --restart unless-stopped \
  -p 80:80 \
  -v "${SCRIPT_DIR}/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
  "${NGINX_IMAGE}" >/dev/null

echo "等待服务启动..."
sleep 5

echo "当前容器状态："
sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'

echo "健康检查："
curl -fsS http://127.0.0.1/health
