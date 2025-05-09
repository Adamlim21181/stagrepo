from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://STAGNASTICS:stagweb@2025%21%40@STAGNASTICS.mysql.pythonanywhere-services.com/STAGNASTICS%24stagdata'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    return app
    