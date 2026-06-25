#!/usr/bin/env sh
set -e

if [ ! -f ./.env.tencent ]; then
  echo "缺少 .env.tencent，请先从 .env.tencent.example 复制一份并填好真实值"
  exit 1
fi

docker compose --env-file ./.env.tencent up -d --build

