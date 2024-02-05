#!/bin/sh
python /app/manage.py migrate
python /app/manage.py runserver 0.0.0.0:5001 & celery -A cyberbot beat & celery -A cyberbot worker