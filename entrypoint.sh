#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for PostgreSQL ..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL has been started."
fi

# Apply migrations
python manage.py migrate
python manage.py collectstatic --no-input --clear

exec "$@"
