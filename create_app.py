from flask import Flask
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql+pymysql://STAGNASTICS:stagweb2025_secure'
        '@STAGNASTICS.mysql.pythonanywhere-services.com/STAGNASTICS$stagdata')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # take all the routes and add them to the main app
    from routes import main
    app.register_blueprint(main)

    return app
