#!/usr/bin/env bash

set -e

echo "Building assets..."
docker-compose run --rm assets yarn build

echo "Deploying assets to S3..."
docker-compose run --rm \
    -e DJANGO_SETTINGS_MODULE=localhub.config.settings.deploy \
    django ./manage.py collectstatic --noinput

echo "Deploying to Heroku..."
git push heroku master



