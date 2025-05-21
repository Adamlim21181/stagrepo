from extensions import db


class Roles(db.Model):
    
    __table_name__ = 'roles'
    
    id = db.Column(
        db.Integer, primary_key=True
    )

    name = db.Column(
        db.String(50), nullable=False, unique=True
    )


class Users(db.Model):
    
    __table_name__ = 'users'
    
    id = db.Column(
        db.Integer, primary_key=True
    )

    username = db.Column(
        db.String(50), nullable=False, unique=True
    )

    code = db.Column(
        db.String(50), nullable=True
    )

    roles = db.relationship(
        "Roles", secondary="user_roles", backref="users"
    )


class UserRoles(db.Model):
    
    __table_name__ = 'user_roles'
    
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True
    )

    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id'), primary_key=True
    )


class Seasons(db.Model):
    
    __table_name__ = 'seasons'
    
    id = db.Column(
        db.Integer, primary_key=True
    )

    year = db.Column(
        db.Integer, nullable=False, unique=True
    )


class Clubs(db.Model):
    
    __table_name__ = 'clubs'
    
    id = db.Column(
        db.Integer, primary_key=True
        )

    name = db.Column(
        db.String(50), nullable=False
    )

    gymnasts = db.relationship(
        'Gymnasts', backref='clubs'
    )


class Apparatus(db.Model):

    __table_name__ = 'apparatus'

    id = db.Column(
        db.Integer, primary_key=True
    )

    name = db.Column(
        db.String(50), nullable=False, unique=True
    )


class Competitions(db.Model):
    
    __table_name__ = 'competitions'    
    
    id = db.Column(
        db.Integer, primary_key=True
    )

    season_id = db.Column(
        db.Integer, db.ForeignKey('seasons.id'), nullable=False
    )

    name = db.Column(
        db.String(50), nullable=False
    )

    address = db.Column(
        db.String(100), nullable=False
    )


class Gymnasts(db.Model):
    
    __table_name__ = 'gymnasts'
    
    id = db.Column(
        db.Integer, primary_key=True
    )

    club_id = db.Column(
        db.Integer, db.ForeignKey('clubs.id'), nullable=False
    )

    name = db.Column(
        db.String(50), nullable=False
    )

    level = db.Column(
        db.String(50), nullable=False
    )


class Entries(db.Model):
    
    __table_name__ = 'entries'
    
    id = db.Column(
        db.Integer, primary_key=True
    )

    competition_id = db.Column(
        db.Integer, db.ForeignKey('competitions.id'), nullable=False
    )

    gymnast_id = db.Column(
        db.Integer, db.ForeignKey('gymnasts.id'), nullable=False
    )

    # __table_args is how to define additional configurations
    # so for this case, I am defining a unique constraint
    __table_args__ = (
        db.UniqueConstraint('competition_id', 'gymnast_id',
                            name='_competition_gymnast_uc'),
        )


class Scores(db.Model):
    
    __table_name__ = 'scores'
    
    id = db.Column(
        db.Integer, primary_key=True
    )

    entries_id = db.Column(
        db.Integer, db.ForeignKey('entries.id'), nullable=False
    )

    apparatus_id = db.Column(
        db.Integer, db.ForeignKey('apparatus.id'), nullable=False
    )

    e_score = db.Column(
        db.Float, nullable=False
    )

    d_score = db.Column(
        db.Float, nullable=False
    )

    penalty = db.Column(
        db.Float, nullable=False
    )

    total = db.Column(
        db.Float, nullable=False
    )

    apparatus = db.relationship('Apparatus', backref='scores')
