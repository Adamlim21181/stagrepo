from create_app import db

class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    code = db.Column(db.String(50), nullable=True)
    roles = relationship("Roles", secondary="user_roles", backref="users")
    
class UserRoles(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    
class Seasons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False, unique=True)
    
class Clubs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Apparatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class Competitions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    
class Gymnasts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    
class Entries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.id'), nullable=False, unique=True)
    gymnast_id = db.Column(db.Integer, db.ForeignKey('gymnasts.id'), nullable=False, unique=True)

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entries_id = db.Column(db.Integer, db.ForeignKey('entries.id'), nullable=False)
    apparatus_id = db.Column(db.Integer, db.ForeignKey('apparatus.id'), nullable=False)
    e_score = db.Column(db.Float, nullable=False)
    d_score = db.Column(db.Float, nullable=False)
    penalty = db.Column(db.Float, nullable=False)
    
    apparatus = db.relationship('Apparatus', backref = 'scores')
    
    
