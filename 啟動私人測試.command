#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v docker >/dev/null 2>&1; then
  echo "尚未安裝 Docker Desktop：https://www.docker.com/products/docker-desktop/"
  read -r -p '按 Enter 結束...' _; exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "請先啟動 Docker Desktop"
  read -r -p '按 Enter 結束...' _; exit 1
fi
docker compose up -d
open http://localhost:8088/install
