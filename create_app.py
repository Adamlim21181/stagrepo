"""Flask application factory and configuration."""

import os
from datetime import timedelta
from flask import Flask, render_template
from extensions import db
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None


def _build_database_uri() -> str:
    """Return SQLAlchemy DB URI from env, defaulting to SQLite."""
    mysql_user = os.environ.get("MYSQL_USER")
    mysql_password = os.environ.get("MYSQL_PASSWORD")
    mysql_host = os.environ.get("MYSQL_HOST")
    mysql_database = os.environ.get("MYSQL_DATABASE")

    if all([mysql_user, mysql_password, mysql_host, mysql_database]):
        uri = (
            "mysql+pymysql://"
            f"{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
        )
        return uri

    basedir = os.path.abspath(os.path.dirname(__file__))
    return f"sqlite:///{os.path.join(basedir, 'stagdata.db')}"


def create_app():
    # Load environment from .env if available
    if load_dotenv:
        load_dotenv()

    app = Flask(__name__)

    # Core configuration
    app.config.update(
        SQLALCHEMY_DATABASE_URI=_build_database_uri(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get("SECRET_KEY", "change-me-in-prod"),
        DEBUG=os.environ.get("FLASK_DEBUG", "0") in {"1", "true", "True"},
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
    )

    db.init_app(app)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(414)
    def url_too_long(e):
        return render_template("414.html"), 414

    # Template context: current user session
    @app.context_processor
    def inject_user():
        from flask import session
        role_id = session.get("role_id")
        return {
            "current_user": {
                "is_authenticated": "user_id" in session,
                "user_id": session.get("user_id"),
                "email": session.get("email"),
                "first_name": session.get("first_name"),
                "role_id": role_id,
                "is_admin": role_id == 1,
                "is_judge": role_id == 2,
                "is_judge_or_admin": role_id in [1, 2],
            }
        }

    # Blueprints
    from routes import main
    app.register_blueprint(main)

    with app.app_context():
        initialize_seasons()

    return app


def initialize_seasons():
    """Create seasons for current and future years if they don't exist."""
    from datetime import datetime
    import models

    current_year = datetime.now().year
    created_count = 0

    for year in range(current_year, current_year + 6):
        existing = models.Seasons.query.filter_by(year=year).first()
        if not existing:
            season = models.Seasons(year=year)
            db.session.add(season)
            created_count += 1

    try:
        db.session.commit()
        if created_count > 0:
            print(f"Created {created_count} seasons")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating seasons: {e}")
