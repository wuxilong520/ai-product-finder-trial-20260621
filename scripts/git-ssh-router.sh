#!/usr/bin/env bash
set -euo pipefail

ALL_ARGS="$*"
SSH_BIN="ssh"
REPO_KEY="/Users/Admin/Documents/商品上传/publish_repo/.deploy-keys/github_push_key"
TENCENT_KEY="/Users/Admin/.ssh/codex_tencent"

if [[ "$ALL_ARGS" == *"gitee.com"* ]]; then
  exec "$SSH_BIN" \
    -i "$REPO_KEY" \
    -o IdentitiesOnly=yes \
    -o StrictHostKeyChecking=accept-new \
    "$@"
fi

if [[ "$ALL_ARGS" == *"ssh.github.com"* ]]; then
  exec "$SSH_BIN" \
    -o ProxyCommand="ssh -i ${TENCENT_KEY} -o StrictHostKeyChecking=yes -W %h:%p ubuntu@121.4.35.33" \
    -i "$REPO_KEY" \
    -o StrictHostKeyChecking=accept-new \
    -o HostKeyAlias=ssh.github.com \
    -o IdentitiesOnly=yes \
    -p 443 \
    "$@"
fi

exec "$SSH_BIN" "$@"
