#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/Admin/Documents/商品上传/publish_repo"
PRIMARY_REMOTE="origin"
BACKUP_REMOTE="github"
BRANCH="main"

cd "$REPO_DIR"

echo "1) 推送到国内主仓（Gitee / origin）..."
git push "$PRIMARY_REMOTE" "$BRANCH"

echo "2) 推送到国外备份仓（GitHub / github）..."
git push "$BACKUP_REMOTE" "$BRANCH"

echo "完成：国内主仓已更新，国外备份仓也已同步。"
