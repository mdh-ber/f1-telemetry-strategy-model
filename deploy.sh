#!/bin/bash

set -e

cd /opt/apps/f1-telemetry-strategy-model

git config --global --add safe.directory /opt/apps/f1-telemetry-strategy-model

git checkout prod
git pull origin prod

docker compose up -d --build

docker ps