from flask import Flask
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///stagdata.db')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'secretstagkey2025!'
    app.config['DEBUG'] = True

    db.init_app(app)

    # take all the routes and add them to the main app
    from routes import main
    app.register_blueprint(main)

    return app
