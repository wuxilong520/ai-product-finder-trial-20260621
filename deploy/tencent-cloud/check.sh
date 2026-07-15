#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env.tencent"
NETWORK_NAME="tencent-cloud_default"
BACKEND_CONTAINER="tencent-cloud_backend_1"
FRONTEND_CONTAINER="tencent-cloud_frontend_1"
NGINX_CONTAINER="tencent-cloud_nginx_1"
APP_LABEL="ai-product-finder-tencent"

if [ -f "${ENV_FILE}" ]; then
  set -a
  . "${ENV_FILE}"
  set +a
fi

check_container_running() {
  local name="$1"
  local actual
  actual="$(sudo docker inspect -f '{{.State.Running}}' "${name}" 2>/dev/null || true)"
  if [ "${actual}" != "true" ]; then
    echo "容器未正常运行: ${name}"
    exit 1
  fi
}

check_container_health() {
  local name="$1"
  local health
  health="$(sudo docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${name}" 2>/dev/null || true)"
  if [ "${health}" != "healthy" ] && [ "${health}" != "none" ]; then
    echo "容器健康检查未通过: ${name} -> ${health}"
    exit 1
  fi
}

echo "检查网络..."
sudo docker network inspect "${NETWORK_NAME}" >/dev/null

echo "检查核心容器..."
check_container_running "${BACKEND_CONTAINER}"
check_container_running "${FRONTEND_CONTAINER}"
check_container_running "${NGINX_CONTAINER}"
check_container_health "${BACKEND_CONTAINER}"
check_container_health "${FRONTEND_CONTAINER}"
check_container_health "${NGINX_CONTAINER}"

echo "检查是否还有旧版遗留容器..."
legacy_containers="$( (sudo docker ps -a --format '{{.Names}} {{.Label "app"}}' | grep 'tencent-cloud_' || true) | grep -v "${APP_LABEL}" || true )"
if [ -n "${legacy_containers}" ]; then
  echo "发现旧版遗留容器，请先清理："
  echo "${legacy_containers}"
  exit 1
fi

echo "检查后端健康状态..."
health_tmp="$(mktemp /tmp/tencent-health.XXXXXX.json)"
health_status="$(curl -sS -o "${health_tmp}" -w '%{http_code}' http://127.0.0.1/health)"
if [ "${health_status}" != "200" ]; then
  echo "后端健康检查失败，HTTP 状态码：${health_status}"
  cat "${health_tmp}" || true
  exit 1
fi
cat "${health_tmp}"

echo "检查 request id 回传..."
request_headers="$(mktemp /tmp/tencent-health-headers.XXXXXX.txt)"
curl -sS -D "${request_headers}" -o /dev/null http://127.0.0.1/health
if ! grep -qi '^X-Request-ID:' "${request_headers}"; then
  echo "后端未返回 X-Request-ID"
  exit 1
fi

echo "检查前端登录页..."
login_tmp="$(mktemp /tmp/tencent-login.XXXXXX.html)"
login_status="$(curl -sS -o "${login_tmp}" -w '%{http_code}' http://127.0.0.1/login)"
if [ "${login_status}" != "200" ]; then
  echo "前端登录页状态异常，HTTP 状态码：${login_status}"
  cat "${login_tmp}" || true
  exit 1
fi
if ! grep -qi "商航AI\\|登录你的选品工作台" "${login_tmp}"; then
  echo "前端登录页返回异常"
  exit 1
fi

echo "检查当前运行版本标签..."
sudo docker ps \
  --filter "label=app=${APP_LABEL}" \
  --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Label "deploy_commit"}}'

if [ "${ENABLE_HTTPS:-false}" = "true" ]; then
  echo "检查 HTTPS 端口..."
  curl -kfsS https://127.0.0.1/health >/dev/null
fi

echo "部署自检通过"
