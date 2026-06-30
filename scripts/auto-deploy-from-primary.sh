#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/ubuntu/publish_repo"
LOCK_FILE="/tmp/publish_repo_auto_deploy.lock"
RUNTIME_DIR="/home/ubuntu/publish_repo_runtime"
STATE_DIR="${RUNTIME_DIR}/state"
LAST_DEPLOYED_FILE="${STATE_DIR}/last_deployed_commit"
LOG_PREFIX="[auto-deploy]"

mkdir -p "${RUNTIME_DIR}"
mkdir -p "${STATE_DIR}"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "${LOG_PREFIX} another deploy is running, skip"
  exit 0
fi

cd "${REPO_DIR}"

echo "${LOG_PREFIX} fetch latest from Gitee origin"
git fetch origin main

REMOTE_COMMIT="$(git rev-parse origin/main)"
LOCAL_COMMIT="$(git rev-parse HEAD)"
LAST_DEPLOYED_COMMIT=""

if [ -f "${LAST_DEPLOYED_FILE}" ]; then
  LAST_DEPLOYED_COMMIT="$(cat "${LAST_DEPLOYED_FILE}")"
fi

if [ "${REMOTE_COMMIT}" = "${LAST_DEPLOYED_COMMIT}" ]; then
  echo "${LOG_PREFIX} no new commit, current=${REMOTE_COMMIT}"
  exit 0
fi

echo "${LOG_PREFIX} update working tree to ${REMOTE_COMMIT}"
git checkout -B main origin/main
git reset --hard origin/main

echo "${LOG_PREFIX} sync GitHub backup"
git push github main

echo "${LOG_PREFIX} run production deploy"
/usr/bin/env bash "${REPO_DIR}/deploy/tencent-cloud/deploy.sh"

echo "${REMOTE_COMMIT}" > "${LAST_DEPLOYED_FILE}"
echo "${LOG_PREFIX} done deployed=${REMOTE_COMMIT} previous_local=${LOCAL_COMMIT}"
