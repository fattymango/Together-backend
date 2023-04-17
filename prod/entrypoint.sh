#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$CONTAINER" = "django" ]
then
    echo "----- Collect static files ------ " 
    python manage.py collectstatic --noinput

    echo "-----------Apply migration--------- "
    python manage.py makemigrations 
    python manage.py migrate
fi

exec "$@"