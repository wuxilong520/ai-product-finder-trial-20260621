#!/usr/bin/env bash
set -euo pipefail

SERVER_USER="ubuntu"
SERVER_HOST="121.4.35.33"
SERVER_PATH="/home/ubuntu/publish_repo"
SSH_KEY="/Users/Admin/.ssh/codex_tencent"
LOCAL_REPO="/Users/Admin/Documents/商品上传/publish_repo"

if ! command -v rsync >/dev/null 2>&1; then
  echo "缺少 rsync，先安装后再执行。"
  exit 1
fi

echo "1) 同步本地代码到腾讯云服务器..."
rsync -az \
  -e "ssh -i ${SSH_KEY} -o StrictHostKeyChecking=yes" \
  --exclude '.git' \
  --exclude '.deploy-keys' \
  --exclude 'frontend/.next' \
  --exclude 'frontend/node_modules' \
  --exclude 'backend/__pycache__' \
  --exclude 'backend/.pytest_cache' \
  --exclude '*.pyc' \
  --exclude 'backend/product_mvp.db' \
  --exclude 'deploy/tencent-cloud/.env.tencent' \
  "${LOCAL_REPO}/" \
  "${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/"

echo "2) 同步 Git 仓库元信息到腾讯云服务器..."
rsync -az \
  -e "ssh -i ${SSH_KEY} -o StrictHostKeyChecking=yes" \
  "${LOCAL_REPO}/.git/" \
  "${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/.git/"

echo "3) 由腾讯云服务器推送到 GitHub..."
ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=yes "${SERVER_USER}@${SERVER_HOST}" \
  "cd ${SERVER_PATH} && git push origin main"

echo "完成：本地 -> 腾讯云 -> GitHub 已同步。"
