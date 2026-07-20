#!/usr/bin/env bash
set -euo pipefail

echo "这个脚本已经降级为旧方案入口，不再作为默认发布链路。"
echo "原因：当前唯一主链路已经统一为：本地 -> Gitee -> 腾讯云公网 -> GitHub 备份。"
echo
echo "请改用："
echo "  ./scripts/release-mainline.sh"
echo
echo "如果你确实要手动双推两个仓库，再用："
echo "  ./scripts/push-all-remotes.sh"
exit 1
