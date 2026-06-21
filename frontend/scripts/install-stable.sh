#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

export CI=true

run_install() {
  pnpm install --config.confirmModulesPurge=false --prefer-offline
}

if [ ! -f pnpm-lock.yaml ]; then
  echo "pnpm-lock.yaml 不存在，正在重建..."
  pnpm install --lockfile-only --config.confirmModulesPurge=false --prefer-offline || true
fi

for attempt in 1 2 3; do
  echo "安装依赖，第 ${attempt} 次尝试..."
  if run_install; then
    echo "依赖安装成功"
    exit 0
  fi
  echo "第 ${attempt} 次失败，准备重试..."
  sleep $((attempt * 2))
done

echo "连续重试后仍失败，请检查当前网络或镜像源连通性。"
exit 1
