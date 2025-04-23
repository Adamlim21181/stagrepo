class Config:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqldb://STAGNASTICS:gyM!2025_Score$NZ"
        "@STAGNASTICS.mysql.pythonanywhere-services.com/STAGNASTICS$stagdata"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
