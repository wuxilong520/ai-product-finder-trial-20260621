#!/usr/bin/env bash
set -euo pipefail

SERVER_USER="ubuntu"
SERVER_HOST="121.4.35.33"
SERVER_KEY="/Users/Admin/.ssh/codex_tencent"
CRON_LINE="* * * * * /usr/bin/env bash /home/ubuntu/publish_repo/scripts/auto-deploy-from-primary.sh >> /home/ubuntu/publish_repo/logs/auto-deploy.log 2>&1"

ssh -i "${SERVER_KEY}" -o StrictHostKeyChecking=yes "${SERVER_USER}@${SERVER_HOST}" <<'EOF'
set -euo pipefail

mkdir -p /home/ubuntu/publish_repo
mkdir -p /home/ubuntu/publish_repo/logs
mkdir -p /home/ubuntu/publish_repo_runtime_restore

if [ ! -d /home/ubuntu/publish_repo/.git ]; then
  cd /home/ubuntu/publish_repo
  git init
  git remote add origin git@gitee.com:westward-dragon/ai-product-finder-trial-20260621.git
  git remote add github git@github.com:wuxilong520/ai-product-finder-trial-20260621.git
fi

mkdir -p /home/ubuntu/.ssh
chmod 700 /home/ubuntu/.ssh

if ! grep -q "Host gitee.com" /home/ubuntu/.ssh/config 2>/dev/null; then
  cat >> /home/ubuntu/.ssh/config <<'CFG'

Host gitee.com
  HostName gitee.com
  User git
  IdentityFile ~/.ssh/github_push_key
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
CFG
fi

if ! grep -q "Host github.com" /home/ubuntu/.ssh/config 2>/dev/null; then
  cat >> /home/ubuntu/.ssh/config <<'CFG'

Host github.com
  HostName ssh.github.com
  Port 443
  User git
  IdentityFile ~/.ssh/github_push_key
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
CFG
fi

chmod 600 /home/ubuntu/.ssh/config

cd /home/ubuntu/publish_repo

if [ -f /home/ubuntu/publish_repo/deploy/tencent-cloud/.env.tencent ]; then
  cp /home/ubuntu/publish_repo/deploy/tencent-cloud/.env.tencent /home/ubuntu/publish_repo_runtime_restore/.env.tencent
fi

if [ -f /home/ubuntu/publish_repo/backend/product_mvp.db ]; then
  cp /home/ubuntu/publish_repo/backend/product_mvp.db /home/ubuntu/publish_repo_runtime_restore/product_mvp.db
fi

if [ -d /home/ubuntu/publish_repo/backend/db_backups ]; then
  rm -rf /home/ubuntu/publish_repo_runtime_restore/db_backups
  cp -R /home/ubuntu/publish_repo/backend/db_backups /home/ubuntu/publish_repo_runtime_restore/db_backups
fi

git fetch origin main
find /home/ubuntu/publish_repo -mindepth 1 -maxdepth 1 ! -name '.git' ! -name 'logs' -exec rm -rf {} +
git checkout -f -B main origin/main
git reset --hard origin/main

mkdir -p /home/ubuntu/publish_repo/deploy/tencent-cloud
mkdir -p /home/ubuntu/publish_repo/backend

if [ -f /home/ubuntu/publish_repo_runtime_restore/.env.tencent ]; then
  cp /home/ubuntu/publish_repo_runtime_restore/.env.tencent /home/ubuntu/publish_repo/deploy/tencent-cloud/.env.tencent
fi

if [ -f /home/ubuntu/publish_repo_runtime_restore/product_mvp.db ]; then
  cp /home/ubuntu/publish_repo_runtime_restore/product_mvp.db /home/ubuntu/publish_repo/backend/product_mvp.db
fi

if [ -d /home/ubuntu/publish_repo_runtime_restore/db_backups ]; then
  rm -rf /home/ubuntu/publish_repo/backend/db_backups
  cp -R /home/ubuntu/publish_repo_runtime_restore/db_backups /home/ubuntu/publish_repo/backend/db_backups
fi

mkdir -p /home/ubuntu/publish_repo/.deploy-state
echo "$(git rev-parse HEAD)" > /home/ubuntu/publish_repo/.deploy-state/last_deployed_commit
EOF

ssh -i "${SERVER_KEY}" -o StrictHostKeyChecking=yes "${SERVER_USER}@${SERVER_HOST}" "(
  crontab -l 2>/dev/null | grep -Fv '/home/ubuntu/publish_repo/scripts/auto-deploy-from-primary.sh' || true
  echo '${CRON_LINE}'
) | crontab -"

echo "腾讯云主仓自动部署已配置。"
