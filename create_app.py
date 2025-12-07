"""Flask application factory and configuration."""

from flask import Flask, render_template
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///stagdata.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secretstagkey2025!'
    app.config['DEBUG'] = True
    
    # Session configuration for "Remember Me" functionality
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 days in seconds
    
    db.init_app(app)

    # Error handler for 404 (Not Found),
    # reroutes the user to a 404 page when an error occurs with the URL
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # Error handler for 414 (Request-URI Too Long),
    # reroutes the user to a 414 page when the URL is too long
    @app.errorhandler(414)
    def url_too_long(e):
        return render_template("414.html"), 414

    # Make session available in all templates
    @app.context_processor
    def inject_user():
        from flask import session
        return {
            'current_user': {
                'is_authenticated': 'user_id' in session,
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'first_name': session.get('first_name'),
                'role_id': session.get('role_id'),
                'is_admin': session.get('role_id') == 1,
                'is_judge': session.get('role_id') == 2,
                'is_judge_or_admin': session.get('role_id') in [1, 2]
            }
        }

    # Register routes. The Blueprint system keeps routes
    # organized in separate modules
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

    # Loop through current year + 5 future years
    # This is to pre-create seasons so competitions can be assigned to them
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
