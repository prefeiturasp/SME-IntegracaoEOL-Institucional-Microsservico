#!/usr/bin/env bash

docker compose -f ./docker-compose-dev.yml build institucional

docker compose -f ./docker-compose-dev.yml run --rm institucional pre-commit run --all-files