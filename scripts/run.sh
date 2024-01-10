#!/bin/bash

# Any command it fails in the next commands that we add to the script it's going to fail the whole script
set -e

python manage.py wait_for_db
# Collectall of the static files that we use for the project and it will put them in the configured static files directory
python manage.py collectstatic --noinput
python manage.py migrate

# Run uwsqi service, app.wsgi file entry point
uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi