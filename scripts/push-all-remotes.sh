#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/Admin/Documents/商品上传/publish_repo"
GITEE_KEY="/Users/Admin/Documents/商品上传/publish_repo/.deploy-keys/github_push_key"
GITEE_REMOTE="gitee"
BRANCH="main"

cd "$REPO_DIR"

echo "1) 推送到 GitHub（origin）..."
git push origin "$BRANCH"

echo "2) 推送到 Gitee（gitee）..."
GIT_SSH_COMMAND="ssh -i ${GITEE_KEY} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  git push "$GITEE_REMOTE" "$BRANCH"

echo "完成：GitHub 和 Gitee 都已经同步。"
