#!/bin/bash
apt install python3-pip
pip install watchdog celery
watchmedo auto-restart --directory=. --pattern='*.py' --recursive -- celery -A ServerDemo worker -l info
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
