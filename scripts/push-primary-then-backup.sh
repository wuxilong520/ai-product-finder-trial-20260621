#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/Admin/Documents/商品上传/publish_repo"

cd "$REPO_DIR"

./scripts/release-mainline.sh
