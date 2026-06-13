#!/bin/bash

set -e

git config --global --add safe.directory /app

cd /app

git fetch origin
git reset --hard origin/prod

chmod +x deploy.sh

docker compose up -d --build backend frontend

docker ps