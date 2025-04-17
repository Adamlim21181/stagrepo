from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    # Create a new Flask app instance
    app = Flask(__name__)

    # Load configuration settings from the Config class (in config.py)
    app.config.from_object(Config)

    # Initialize the SQLAlchemy extension with this app
    db.init_app(app)

    # Import the Blueprint named 'main' from the routes module
    # This prevents circular import issues by importing inside the function
    from app.routes import main

    # Register the 'main' Blueprint with the app
    # This connects all the routes defined in app/routes.py to the app
    app.register_blueprint(main)

    # Return the fully configured Flask app instance
    return app
