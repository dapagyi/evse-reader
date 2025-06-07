#!/bin/sh
set -e

FLASK_APP=src.evse_reader
DB_PATH="./instance/db.sqlite"

mkdir -p "$(dirname "$DB_PATH")"

if [ "$FLASK_ENV" != "production" ]; then
    echo "Development mode: running DB initialization"
    uv run flask --app "$FLASK_APP" init-db
    uv run flask --app "$FLASK_APP" run --debug --host 0.0.0.0 --port 3031
else
    if [ ! -f "$DB_PATH" ]; then
        echo "Database not found at $DB_PATH. Initializing..."
        uv run flask --app "$FLASK_APP" init-db
    else
        echo "Database exists at $DB_PATH. Skipping initialization."
    fi
    uv run gunicorn -w 2 -b 0.0.0.0 "$FLASK_APP:create_app()"
fi
