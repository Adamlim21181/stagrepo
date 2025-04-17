from . import db


class Apparatus(db.Model):
    __tablename__ = "apparatus"
    apparatus_id = db.Column(db.Integer, primary_key=True)
    apparatus_name = db.Column(db.String(255))


class Club(db.Model):
    __tablename__ = "clubs"
    club_id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(255))


class Season(db.Model):
    __tablename__ = "seasons"
    season_id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)


class Competition(db.Model):
    __tablename__ = "competitions"
    competition_id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.season_id'))
    competition_name = db.Column(db.String(255))
    date = db.Column(db.Date)
    address = db.Column(db.String(255))

    season = db.relationship("Season", backref="competitions")


class Gymnast(db.Model):
    __tablename__ = "gymnasts"
    gymnast_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
    gymnast_name = db.Column(db.String(255))
    level = db.Column(db.String(255))

    club = db.relationship("Club", backref="gymnasts")


class Entry(db.Model):
    __tablename__ = "entries"
    entries_id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competitions.competition_id'))
    gymnast_id = db.Column(db.Integer, db.ForeignKey('gymnasts.gymnast_id'))

    competition = db.relationship("Competition", backref="entries")
    gymnast = db.relationship("Gymnast", backref="entries")


class Score(db.Model):
    __tablename__ = "score"
    score_id = db.Column(db.Integer, primary_key=True)
    entries_id = db.Column(db.Integer, db.ForeignKey('entries.entries_id'))
    apparatus_id = db.Column(db.Integer, db.ForeignKey('apparatus.apparatus_id'))
    execution = db.Column(db.Float)
    difficulty = db.Column(db.Float)
    penalty = db.Column(db.Float)

    entry = db.relationship("Entry", backref="scores")
    apparatus = db.relationship("Apparatus", backref="scores")


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255))
    password = db.Column(db.String(255))
    role = db.Column(db.String(255))

