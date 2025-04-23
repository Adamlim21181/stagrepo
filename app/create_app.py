from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize db here
db = SQLAlchemy()


def create_app():
    # Create Flask app instance
    app = Flask(__name__)

    # Set up app configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your-database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db with app
    db.init_app(app)

    # Import and register routes (blueprints)
    from app.routes import main
    app.register_blueprint(main)

    return app
