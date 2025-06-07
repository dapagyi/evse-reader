#!/bin/sh
set -e

FLASK_APP=src.evse_reader

# Path to SQLite DB  (this matches how it's defined in create_app())
DB_PATH="/app/instance/db.sqlite"

mkdir -p "$(dirname "$DB_PATH")"

# Init DB if not present
if [ ! -f "$DB_PATH" ]; then
    echo "Database not found at $DB_PATH. Initializing..."
    uv run flask --app "$FLASK_APP" init-db
else
    echo "Database already exists at $DB_PATH. Skipping initialization."
fi

exec uv run gunicorn -w 2 -b 0.0.0.0:3030 "${FLASK_APP}:create_app()"
