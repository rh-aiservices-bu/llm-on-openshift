#!/usr/bin/env bash

# Load bash libraries
SCRIPT_DIR=$(dirname -- "$0")
source ${SCRIPT_DIR}/utils/*.sh

# Initilize access logs for culling
echo '[{"id":"anythingllm","name":"anythingllm","last_activity":"'$(date -Iseconds)'","execution_state":"running","connections":1}]' >/var/log/nginx/anythingllm.access.log

# Start nginx and supervisord
run-nginx.sh &
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf &

# Add storage directories if not present
if [ ! -d "/opt/app-root/src/anythingllm/storage" ]; then
  mkdir -p /opt/app-root/src/anythingllm/storage
  mkdir -p /opt/app-root/src/anythingllm/storage/documents
  mkdir -p /opt/app-root/src/anythingllm/storage/vector-cache
  mkdir -p /opt/app-root/src/anythingllm/storage/lancedb
  mkdir -p /opt/app-root/src/anythingllm/storage/plugins/agent-skills
  touch /opt/app-root/src/anythingllm/storage/anythingllm.db
fi

# Link storage directory
if [ ! -L "/app/server/storage" ]; then
  rm -rf /app/server/storage
  ln -s /opt/app-root/src/anythingllm/storage /app/server/storage
fi

# Add collector hotdir if not present
if [ ! -d "/opt/app-root/src/anythingllm/collector/hotdir" ]; then
  mkdir -p /opt/app-root/src/anythingllm/collector/hotdir
fi

# Link collector hotdir
if [ ! -L "/app/collector/hotdir" ]; then
  rm -rf /app/collector/hotdir
  ln -s /opt/app-root/src/anythingllm/collector/hotdir /app/collector/hotdir
fi

# Add collector outputs if not present
if [ ! -d "/opt/app-root/src/anythingllm/collector/outputs" ]; then
  mkdir -p /opt/app-root/src/anythingllm/collector/outputs
fi

# Link collector outputs
if [ ! -L "/app/collector/outputs" ]; then
  rm -rf /app/collector/outputs
  ln -s /opt/app-root/src/anythingllm/collector/outputs /app/collector/outputs
fi

# Add .env if not present
if [ ! -f "/opt/app-root/src/anythingllm/.env" ]; then
  mkdir -p /opt/app-root/src/anythingllm
  echo 'DISABLE_TELEMETRY="false"' >/opt/app-root/src/anythingllm/.env
fi

# Link .env file
if [ ! -L "/app/server/.env" ]; then
  rm -rf /app/server/.env
  ln -s /opt/app-root/src/anythingllm/.env /app/server/.env
fi

# Link Chromium binary for Puppeteer
mkdir -p /opt/app-root/src/.cache
ln -s /app/collector/node_modules/puppeteer/.local-chromium /opt/app-root/src/.cache/puppeteer

export USER=$(whoami)

# Set the storage directory
export STORAGE_DIR=/app/server/storage

# Modify the collector port
export COLLECTOR_PORT=8889

# Start the AnythingLLM server
cd /app/server/ &&
rm /app/server/node_modules/.prisma/client/schema.prisma
npx prisma generate --schema=./prisma/schema.prisma &&
npx prisma migrate deploy --schema=./prisma/schema.prisma

#start_process start_anythingllm
node /app/collector/index.js &
start_process node /app/server/index.js
