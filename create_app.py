from flask import Flask, render_template
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///stagdata.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secretstagkey2025!'
    app.config['DEBUG'] = True

    db.init_app(app)

    # Register error handlers on the main app
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(414)
    def url_too_long(e):
        return render_template("414.html"), 414

    # Register the modular routes blueprint
    from routes import main
    app.register_blueprint(main)

    # Initialize seasons after everything is set up
    with app.app_context():
        initialize_seasons()

    return app


def initialize_seasons():
    """Create seasons for current and future years if they don't exist"""
    from datetime import datetime
    import models  # Import models the same way as in routes

    current_year = datetime.now().year
    created_count = 0

    # Current + 5 future years
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
