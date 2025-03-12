#!/bin/bash

set -e

# 等待 PostgreSQL 准备好
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing migrations"
python manage.py migrate

# 执行传入的命令
exec "$@" 