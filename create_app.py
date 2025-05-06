from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://STAGNASTICS:stagweb@2025!@STAGNASTICS.mysql.pythonanywhere-services.com/stagnastics$stagdata'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    