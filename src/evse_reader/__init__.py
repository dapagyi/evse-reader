import contextlib
import os

from dotenv import load_dotenv
from flask import Flask

from evse_reader.datetime_utils import convert_to_local_iso

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "db.sqlite"),
    )
    app.config.from_prefixed_env(prefix="EVSE")

    with contextlib.suppress(OSError):
        os.makedirs(app.instance_path)

    from . import db

    db.init_app(app)

    from . import charging_data

    app.register_blueprint(charging_data.bp)

    @app.route("/health")
    def health():
        _db = db.get_db()
        rows = _db.execute(
            "SELECT key, value FROM app_state WHERE key IN ('creation_time', 'last_updated')"
        ).fetchall()
        state = dict(rows)
        return {
            "status": "ok",
            "creation_time": convert_to_local_iso(state.get("creation_time")),
            "last_updated": convert_to_local_iso(state.get("last_updated"))
            if state.get("last_updated")
            else None,
            "instance_path": app.instance_path,
        }

    @app.route("/")
    def index():
        return app.redirect("/health")

    return app
