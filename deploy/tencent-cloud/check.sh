#!/usr/bin/env bash
set -euo pipefail

NETWORK_NAME="tencent-cloud_default"
BACKEND_CONTAINER="tencent-cloud_backend_1"
FRONTEND_CONTAINER="tencent-cloud_frontend_1"
NGINX_CONTAINER="tencent-cloud_nginx_1"
APP_LABEL="ai-product-finder-tencent"

check_container_running() {
  local name="$1"
  local actual
  actual="$(sudo docker inspect -f '{{.State.Running}}' "${name}" 2>/dev/null || true)"
  if [ "${actual}" != "true" ]; then
    echo "容器未正常运行: ${name}"
    exit 1
  fi
}

echo "检查网络..."
sudo docker network inspect "${NETWORK_NAME}" >/dev/null

echo "检查核心容器..."
check_container_running "${BACKEND_CONTAINER}"
check_container_running "${FRONTEND_CONTAINER}"
check_container_running "${NGINX_CONTAINER}"

echo "检查是否还有旧版遗留容器..."
legacy_containers="$( (sudo docker ps -a --format '{{.Names}} {{.Label "app"}}' | grep 'tencent-cloud_' || true) | grep -v "${APP_LABEL}" || true )"
if [ -n "${legacy_containers}" ]; then
  echo "发现旧版遗留容器，请先清理："
  echo "${legacy_containers}"
  exit 1
fi

echo "检查后端健康状态..."
curl -fsS http://127.0.0.1/health >/tmp/tencent-health.json
cat /tmp/tencent-health.json

echo "检查前端登录页..."
curl -fsS http://127.0.0.1/login >/tmp/tencent-login.html
if ! grep -qi "<html" /tmp/tencent-login.html; then
  echo "前端登录页返回异常"
  exit 1
fi

echo "检查当前运行版本标签..."
sudo docker ps \
  --filter "label=app=${APP_LABEL}" \
  --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Label "deploy_commit"}}'

echo "部署自检通过"
