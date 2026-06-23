#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

docker compose -f ../docker-compose-dev.yml build institucional

docker compose -f ../docker-compose-dev.yml run --rm institucional \
  python -m coverage run --source=apps -m pytest

docker compose -f ../docker-compose-dev.yml run --rm institucional \
  python -m coverage report --show-missing --fail-under=80