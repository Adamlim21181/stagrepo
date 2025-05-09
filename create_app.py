from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    connection = pymysql.connect(
        host = 'STAGNASTICS.mysql.pythonanywhere-services.com',
        user = 'STAGNASTICS',
        password = 'stagweb@2025!',
        db = 'STAGNASTICS$stagdata',
        cursorclass = pymysql.cursors.DictCursor
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    return app
    