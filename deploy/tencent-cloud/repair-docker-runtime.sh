#!/usr/bin/env bash
set -euo pipefail

APP_LABEL="ai-product-finder-tencent"

echo "开始修复 Docker 运行时脏状态..."

echo "1) 删除异常退出的临时构建容器"
sudo docker ps -a --format '{{.Names}} {{.Status}} {{.Label "app"}}' | while read -r name status1 status2 rest; do
  if [ -z "${name}" ]; then
    continue
  fi
  if [[ "${status1}" = Exited || "${status1}" = Created ]] && [[ "${name}" != tencent-cloud_* ]]; then
    sudo docker rm -f "${name}" >/dev/null 2>&1 || true
  fi
done

echo "2) 清理无用容器缓存"
sudo docker container prune -f >/dev/null 2>&1 || true
sudo docker image prune -f >/dev/null 2>&1 || true
sudo docker builder prune -af >/dev/null 2>&1 || true

echo "3) 清理 containerd 临时挂载目录"
sudo find /var/lib/containerd/tmpmounts -mindepth 1 -maxdepth 1 -exec rm -rf {} + >/dev/null 2>&1 || true

echo "4) 尝试安装更稳定的 buildx 插件"
if ! sudo docker buildx version >/dev/null 2>&1; then
  sudo apt-get update >/dev/null
  sudo apt-get install -y docker-buildx-plugin >/dev/null
fi

echo "5) 输出当前 Docker 能力"
sudo docker version
sudo docker buildx version || true

echo "Docker 运行时修复完成"
