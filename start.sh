#!/bin/bash

# python manage.py makemigrations account
# python manage.py makemigrations authenticate
# python manage.py makemigrations chat
# python manage.py makemigrations notification

# python manage.py migrate --no-input

# python manage.py runserver 0.0.0.0:8000
python manage.py check

daphne -b 0.0.0.0 -p 8000 watsapp_backend.asgi:application
