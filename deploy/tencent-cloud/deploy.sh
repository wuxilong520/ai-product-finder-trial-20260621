#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env.tencent"
DB_FILE="${ROOT_DIR}/backend/product_mvp.db"
DB_BACKUP_DIR="${ROOT_DIR}/backend/db_backups"
RUNTIME_DIR="${ROOT_DIR}_runtime"
STATE_DIR="${RUNTIME_DIR}/state"
LAST_DEPLOYED_FILE="${STATE_DIR}/last_deployed_commit"
LAST_ENV_HASH_FILE="${STATE_DIR}/last_env_hash"
NETWORK_NAME="tencent-cloud_default"
BACKEND_CONTAINER="tencent-cloud_backend_1"
FRONTEND_CONTAINER="tencent-cloud_frontend_1"
NGINX_CONTAINER="tencent-cloud_nginx_1"
BACKEND_IMAGE="tencent-cloud_backend"
FRONTEND_IMAGE="tencent-cloud_frontend"
NGINX_IMAGE="docker.m.daocloud.io/library/nginx:1.27-alpine"
APP_LABEL="ai-product-finder-tencent"
RELEASE_VERSION_FILE="${ROOT_DIR}/.release-version"
BUILD_BACKEND="${BUILD_BACKEND:-1}"
BUILD_FRONTEND="${BUILD_FRONTEND:-1}"
LOCK_FILE="/tmp/shanghang-ai-deploy.lock"
ENABLE_HTTPS="${ENABLE_HTTPS:-false}"
SSL_CERT_PATH="${SSL_CERT_PATH:-}"
SSL_CERT_KEY_PATH="${SSL_CERT_KEY_PATH:-}"
NGINX_PORT_ARGS=(-p 80:80)
NGINX_TEMPLATE_PATH="${SCRIPT_DIR}/nginx.http.conf"
RENDERED_NGINX_DIR="${RUNTIME_DIR}/nginx"
RENDERED_NGINX_CONF="${RENDERED_NGINX_DIR}/default.conf"
NGINX_VOLUME_ARGS=(-v "${RENDERED_NGINX_CONF}:/etc/nginx/conf.d/default.conf:ro")

configure_nginx_mode() {
  local enable_https_normalized
  enable_https_normalized="$(printf '%s' "${ENABLE_HTTPS}" | tr '[:upper:]' '[:lower:]')"

  if [ "${enable_https_normalized}" != "true" ]; then
    echo "当前使用 HTTP 网关模式（未开启 HTTPS）"
    return
  fi

  if [ -z "${SSL_CERT_PATH}" ] || [ -z "${SSL_CERT_KEY_PATH}" ]; then
    echo "ENABLE_HTTPS=true 时必须同时提供 SSL_CERT_PATH 和 SSL_CERT_KEY_PATH"
    exit 1
  fi

  if [ ! -f "${SSL_CERT_PATH}" ] || [ ! -f "${SSL_CERT_KEY_PATH}" ]; then
    echo "HTTPS 证书文件不存在，请检查 SSL_CERT_PATH 和 SSL_CERT_KEY_PATH"
    exit 1
  fi

  NGINX_PORT_ARGS=(-p 80:80 -p 443:443)
  NGINX_TEMPLATE_PATH="${SCRIPT_DIR}/nginx.conf"
  NGINX_VOLUME_ARGS=(
    -v "${RENDERED_NGINX_CONF}:/etc/nginx/conf.d/default.conf:ro"
    -v "${SSL_CERT_PATH}:${SSL_CERT_PATH}:ro"
    -v "${SSL_CERT_KEY_PATH}:${SSL_CERT_KEY_PATH}:ro"
  )
  echo "当前使用 HTTPS 网关模式"
}

render_nginx_config() {
  mkdir -p "${RENDERED_NGINX_DIR}"
  MAIN_HOST="${MAIN_HOST:-_}" \
  ADMIN_HOST="${ADMIN_HOST:-admin.local}" \
  SSL_CERT_PATH="${SSL_CERT_PATH:-}" \
  SSL_CERT_KEY_PATH="${SSL_CERT_KEY_PATH:-}" \
  NGINX_TEMPLATE_PATH="${NGINX_TEMPLATE_PATH}" \
  RENDERED_NGINX_CONF="${RENDERED_NGINX_CONF}" \
  python3 <<'PY'
from pathlib import Path
import os

template_path = Path(os.environ["NGINX_TEMPLATE_PATH"])
output_path = Path(os.environ["RENDERED_NGINX_CONF"])
content = template_path.read_text()
for key in ("MAIN_HOST", "ADMIN_HOST", "SSL_CERT_PATH", "SSL_CERT_KEY_PATH"):
    content = content.replace("${" + key + "}", os.environ.get(key, ""))
output_path.write_text(content)
PY
  echo "已生成 Nginx 配置：${RENDERED_NGINX_CONF}"
}

resolve_deploy_commit() {
  local override_commit=""
  local git_commit=""
  local file_commit=""

  override_commit="$(printf '%s' "${DEPLOY_COMMIT_OVERRIDE:-${DEPLOY_COMMIT:-}}" | tr -d '[:space:]')"
  if [ -n "${override_commit}" ]; then
    echo "${override_commit}"
    return
  fi

  git_commit="$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || true)"
  if [ -n "${git_commit}" ]; then
    echo "${git_commit}"
    return
  fi

  if [ -f "${RELEASE_VERSION_FILE}" ]; then
    file_commit="$(tr -d '[:space:]' < "${RELEASE_VERSION_FILE}")"
    if [ -n "${file_commit}" ]; then
      echo "${file_commit}"
      return
    fi
  fi

  echo "unknown"
}

DEPLOY_COMMIT="$(resolve_deploy_commit)"

release_lock() {
  if command -v flock >/dev/null 2>&1; then
    flock -u 9 >/dev/null 2>&1 || true
  fi
  rm -f "${LOCK_FILE}" >/dev/null 2>&1 || true
}

acquire_lock() {
  if command -v flock >/dev/null 2>&1; then
    exec 9>"${LOCK_FILE}"
    if ! flock -n 9; then
      echo "已有部署任务在运行，请等待上一轮完成后再重试"
      exit 1
    fi
    printf '%s\n' "$$" 1>&9
    trap release_lock EXIT
    return
  fi

  if [ -f "${LOCK_FILE}" ]; then
    existing_pid="$(cat "${LOCK_FILE}" 2>/dev/null || true)"
    if [ -n "${existing_pid}" ] && kill -0 "${existing_pid}" >/dev/null 2>&1; then
      echo "已有部署任务在运行，请等待上一轮完成后再重试"
      exit 1
    fi
  fi

  echo "$$" > "${LOCK_FILE}"
  trap release_lock EXIT
}

if [ ! -f "${ENV_FILE}" ]; then
  echo "缺少 ${ENV_FILE}，请先从 .env.tencent.example 复制一份并填好真实值"
  exit 1
fi

acquire_lock

cleanup_legacy_runtime() {
  echo "清理旧容器和脏状态..."
  (sudo docker ps -a --format '{{.Names}}' | grep -E 'tencent-cloud_.*_1$|.*_tencent-cloud_.*_1$' || true) | while read -r name; do
    if [ -n "${name}" ] && [ "${name}" != "${BACKEND_CONTAINER}" ] && [ "${name}" != "${FRONTEND_CONTAINER}" ] && [ "${name}" != "${NGINX_CONTAINER}" ]; then
      echo "删除遗留容器 ${name}"
      sudo docker rm -f "${name}" >/dev/null 2>&1 || true
    fi
  done

  sudo docker image prune -f >/dev/null 2>&1 || true
}

update_deploy_state() {
  mkdir -p "${STATE_DIR}"
  echo "${DEPLOY_COMMIT}" > "${LAST_DEPLOYED_FILE}"
  if [ -f "${ENV_FILE}" ]; then
    shasum -a 256 "${ENV_FILE}" | awk '{print $1}' > "${LAST_ENV_HASH_FILE}"
  fi
}

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

configure_nginx_mode
render_nginx_config

cleanup_legacy_runtime

if [ "${BUILD_BACKEND}" = "1" ]; then
  echo "开始构建后端镜像..."
  sudo docker build \
    --label "app=${APP_LABEL}" \
    --label "role=backend" \
    --label "deploy_commit=${DEPLOY_COMMIT}" \
    -t "${BACKEND_IMAGE}" \
    -f "${SCRIPT_DIR}/backend.Dockerfile" \
    "${ROOT_DIR}"
else
  echo "跳过后端镜像重建，继续复用当前后端镜像"
fi

if [ "${BUILD_FRONTEND}" = "1" ]; then
  echo "开始构建前端镜像..."
  sudo docker build \
    --label "app=${APP_LABEL}" \
    --label "role=frontend" \
    --label "deploy_commit=${DEPLOY_COMMIT}" \
    --build-arg NEXT_PUBLIC_API_BASE="${NEXT_PUBLIC_API_BASE:-}" \
    --build-arg NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-}" \
    --build-arg NEXT_PUBLIC_WS_URL="${NEXT_PUBLIC_WS_URL:-}" \
    -t "${FRONTEND_IMAGE}" \
    -f "${SCRIPT_DIR}/frontend.Dockerfile" \
    "${ROOT_DIR}"
else
  echo "跳过前端镜像重建，继续复用当前前端镜像"
fi

sudo docker network inspect "${NETWORK_NAME}" >/dev/null 2>&1 || sudo docker network create "${NETWORK_NAME}"

echo "重启后端容器..."
sudo docker rm -f "${BACKEND_CONTAINER}" >/dev/null 2>&1 || true
sudo docker run -d \
  --name "${BACKEND_CONTAINER}" \
  --network "${NETWORK_NAME}" \
  --network-alias backend \
  --restart unless-stopped \
  --label "app=${APP_LABEL}" \
  --label "role=backend" \
  --label "deploy_commit=${DEPLOY_COMMIT}" \
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
  --label "app=${APP_LABEL}" \
  --label "role=frontend" \
  --label "deploy_commit=${DEPLOY_COMMIT}" \
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
  --label "app=${APP_LABEL}" \
  --label "role=nginx" \
  --label "deploy_commit=${DEPLOY_COMMIT}" \
  -e MAIN_HOST="${MAIN_HOST:-_}" \
  -e ADMIN_HOST="${ADMIN_HOST:-admin.local}" \
  -e SSL_CERT_PATH="${SSL_CERT_PATH:-}" \
  -e SSL_CERT_KEY_PATH="${SSL_CERT_KEY_PATH:-}" \
  "${NGINX_PORT_ARGS[@]}" \
  "${NGINX_VOLUME_ARGS[@]}" \
  "${NGINX_IMAGE}" >/dev/null

echo "等待服务启动..."
sleep 5

echo "执行部署后自检..."
bash "${SCRIPT_DIR}/check.sh"
update_deploy_state
echo "部署完成，当前版本提交：${DEPLOY_COMMIT}"
