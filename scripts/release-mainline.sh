#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/Admin/Documents/商品上传/publish_repo"
PRIMARY_REMOTE="origin"
BRANCH="main"
WRITE_VERSION_SCRIPT="${REPO_DIR}/scripts/write-release-version.sh"

cd "${REPO_DIR}"

echo "1) 生成本次发布版本标记..."
"${WRITE_VERSION_SCRIPT}"

echo "2) 推送到主仓（Gitee / origin）..."
git push "${PRIMARY_REMOTE}" "${BRANCH}"

echo "3) 主仓已更新。"
echo "   后续标准链路是：Gitee -> 腾讯云公网 -> GitHub 备份。"
echo "   如果腾讯云已配置自动部署，这次提交会由服务器继续完成公网与 GitHub 同步。"
