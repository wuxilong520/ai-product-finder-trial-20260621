#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env.tencent"
DB_FILE="${ROOT_DIR}/backend/product_mvp.db"
DB_BACKUP_DIR="${ROOT_DIR}/backend/db_backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

if [ -f "${ENV_FILE}" ]; then
  set -a
  . "${ENV_FILE}"
  set +a
fi

mkdir -p "${DB_BACKUP_DIR}"

DATABASE_URL_VALUE="${DATABASE_URL:-sqlite:///./product_mvp.db}"

if printf '%s' "${DATABASE_URL_VALUE}" | grep -q '^sqlite:///'; then
  touch "${DB_FILE}"
  if [ -s "${DB_FILE}" ]; then
    backup_file="${DB_BACKUP_DIR}/product_mvp_${TIMESTAMP}.db"
    cp "${DB_FILE}" "${backup_file}"
    echo "SQLite 备份完成：${backup_file}"
  else
    echo "SQLite 数据库当前为空，跳过实体备份"
  fi
  exit 0
fi

if printf '%s' "${DATABASE_URL_VALUE}" | grep -q 'postgres'; then
  if ! command -v pg_dump >/dev/null 2>&1; then
    echo "检测到 PostgreSQL，但服务器没有 pg_dump，当前无法执行真实备份"
    exit 1
  fi
  backup_file="${DB_BACKUP_DIR}/postgres_${TIMESTAMP}.sql"
  pg_dump "${DATABASE_URL_VALUE}" > "${backup_file}"
  echo "PostgreSQL 备份完成：${backup_file}"
  exit 0
fi

echo "未知数据库类型，未执行备份：${DATABASE_URL_VALUE}"
exit 1
