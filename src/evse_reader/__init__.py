import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "db.sqlite"),
    )
    app.config.from_prefixed_env(prefix="EVSE")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        name = os.getenv("USERNAME", "World")
        return f"Hello, {name}!"

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
        state = {key: value for key, value in rows}
        return {
            "status": "ok",
            "creation_time": state.get("creation_time"),
            "last_updated": state.get("last_updated"),
            "instance_path": app.instance_path,
        }

    @app.route("/")
    def index():
        return app.redirect("/health")

    return app
