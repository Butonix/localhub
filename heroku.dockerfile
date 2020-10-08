# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

FROM python:3.8.3-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV DISABLE_COLLECTSTATIC=1

# dummy values for deployment purposes
#
ENV SECRET_KEY=seekrit
ENV DATABASE_URL=sqlite:///
ENV REDIS_URL=redis://redis:6379/0

ENV DJANGO_SETTINGS_MODULE=localhub.config.settings.deploy

RUN apt-get update \
    && apt-get install --no-install-recommends -y postgresql-client-11 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app

# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/
#
RUN python manage.py collectstatic --noinput

RUN useradd -m user
USER user

