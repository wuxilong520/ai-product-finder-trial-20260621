#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/ubuntu/publish_repo"
LOCK_FILE="/tmp/publish_repo_auto_deploy.lock"
DEPLOY_LOCK_FILE="/tmp/shanghang-ai-deploy.lock"
RUNTIME_DIR="/home/ubuntu/publish_repo_runtime"
STATE_DIR="${RUNTIME_DIR}/state"
LAST_DEPLOYED_FILE="${STATE_DIR}/last_deployed_commit"
LAST_ENV_HASH_FILE="${STATE_DIR}/last_env_hash"
ENV_FILE="${REPO_DIR}/deploy/tencent-cloud/.env.tencent"
LOG_PREFIX="[auto-deploy]"

mkdir -p "${RUNTIME_DIR}"
mkdir -p "${STATE_DIR}"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "${LOG_PREFIX} another deploy is running, skip"
  exit 0
fi

if [ -f "${DEPLOY_LOCK_FILE}" ]; then
  DEPLOY_PID="$(cat "${DEPLOY_LOCK_FILE}" 2>/dev/null || true)"
  if [ -n "${DEPLOY_PID}" ] && kill -0 "${DEPLOY_PID}" >/dev/null 2>&1; then
    echo "${LOG_PREFIX} production deploy is running, skip"
    exit 0
  fi
fi

cd "${REPO_DIR}"

echo "${LOG_PREFIX} fetch latest from Gitee origin"
git fetch origin main

REMOTE_COMMIT="$(git rev-parse origin/main)"
LOCAL_COMMIT="$(git rev-parse HEAD)"
LAST_DEPLOYED_COMMIT=""
CURRENT_ENV_HASH="missing"
LAST_ENV_HASH=""

if [ -f "${LAST_DEPLOYED_FILE}" ]; then
  LAST_DEPLOYED_COMMIT="$(cat "${LAST_DEPLOYED_FILE}")"
fi

if [ -f "${ENV_FILE}" ]; then
  CURRENT_ENV_HASH="$(shasum -a 256 "${ENV_FILE}" | awk '{print $1}')"
fi

if [ -f "${LAST_ENV_HASH_FILE}" ]; then
  LAST_ENV_HASH="$(cat "${LAST_ENV_HASH_FILE}")"
fi

if [ "${REMOTE_COMMIT}" = "${LAST_DEPLOYED_COMMIT}" ] && [ "${CURRENT_ENV_HASH}" = "${LAST_ENV_HASH}" ]; then
  echo "${LOG_PREFIX} no code or env change, commit=${REMOTE_COMMIT} env_hash=${CURRENT_ENV_HASH}"
  exit 0
fi

if [ "${REMOTE_COMMIT}" != "${LAST_DEPLOYED_COMMIT}" ]; then
  echo "${LOG_PREFIX} detected code change: ${LAST_DEPLOYED_COMMIT} -> ${REMOTE_COMMIT}"
else
  echo "${LOG_PREFIX} detected env change: ${LAST_ENV_HASH} -> ${CURRENT_ENV_HASH}"
fi

echo "${LOG_PREFIX} update working tree to ${REMOTE_COMMIT}"
git checkout -B main origin/main
git reset --hard origin/main

if git remote get-url github >/dev/null 2>&1; then
  echo "${LOG_PREFIX} sync GitHub backup (best effort)"
  if ! git push github main; then
    echo "${LOG_PREFIX} GitHub backup sync failed, continue deploy"
  fi
fi

echo "${LOG_PREFIX} run production deploy"
/usr/bin/env bash "${REPO_DIR}/deploy/tencent-cloud/deploy.sh"
/usr/bin/env bash "${REPO_DIR}/deploy/tencent-cloud/check.sh"

echo "${REMOTE_COMMIT}" > "${LAST_DEPLOYED_FILE}"
echo "${CURRENT_ENV_HASH}" > "${LAST_ENV_HASH_FILE}"
echo "${LOG_PREFIX} done deployed=${REMOTE_COMMIT} previous_local=${LOCAL_COMMIT}"
