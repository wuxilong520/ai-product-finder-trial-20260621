#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VERSION_FILE="${ROOT_DIR}/.release-version"

commit="$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || true)"

if [ -z "${commit}" ]; then
  echo "无法读取当前 Git 版本号，未生成 .release-version"
  exit 1
fi

printf '%s\n' "${commit}" > "${VERSION_FILE}"
echo "已写入发布版本: ${commit}"
