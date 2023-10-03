#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py makemigrations account
python manage.py makemigrations authenticate
python manage.py makemigrations chat
python manage.py makemigrations notification

python manage.py migrate --no-input

# python manage.py runserver 0.0.0.0:8000
# daphne -b 0.0.0.0 -p 8000 watsapp_backend.asgi:application
# uvicorn watsapp_backend.asgi:application --host 0.0.0.0 --port 8080
gunicorn --bind 0.0.0.0:8000 watsapp_backend.asgi -w 1 -k uvicorn.workers.UvicornWorker