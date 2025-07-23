from extensions import db


class Roles(db.Model):

    __tablename__ = 'roles'

    id = db.Column(
        db.Integer, primary_key=True
    )

    name = db.Column(
        db.String(50), nullable=False, unique=True
    )


class Users(db.Model):

    __tablename__ = 'users'

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

    __tablename__ = 'user_roles'

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True
    )

    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id'), primary_key=True
    )


class Seasons(db.Model):

    __tablename__ = 'seasons'

    id = db.Column(
        db.Integer, primary_key=True
    )

    year = db.Column(
        db.Integer, nullable=False, unique=True
    )


class Clubs(db.Model):

    __tablename__ = 'clubs'

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

    __tablename__ = 'apparatus'

    id = db.Column(
        db.Integer, primary_key=True
    )

    name = db.Column(
        db.String(50), nullable=False, unique=True
    )

    scores = db.relationship(
        'Scores', backref='apparatus'
    )


# Add this to your existing Competitions model in models.py

class Competitions(db.Model):
    __tablename__ = 'competitions'

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

    competition_date = db.Column(
        db.Date, nullable=True
    )

    status = db.Column(
        db.String(20), nullable=False, default='draft'
    )  # Options: 'draft', 'live', 'ended'

    started_at = db.Column(
        db.DateTime, nullable=True
    )

    ended_at = db.Column(
        db.DateTime, nullable=True
    )

    entries = db.relationship(
        'Entries', backref='competitions'
    )

    season = db.relationship(
        'Seasons', backref='competitions'
    )


class Gymnasts(db.Model):

    __tablename__ = 'gymnasts'

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

    entries = db.relationship(
        'Entries', backref='gymnasts',
    )


class Entries(db.Model):

    __tablename__ = 'entries'

    id = db.Column(
        db.Integer, primary_key=True
    )

    competition_id = db.Column(
        db.Integer, db.ForeignKey('competitions.id'), nullable=False
    )

    gymnast_id = db.Column(
        db.Integer, db.ForeignKey('gymnasts.id'), nullable=False
    )

    scores = db.relationship(
        'Scores', backref='entry'
    )

    # __table_args is how to define additional configurations
    # so for this case, I am defining a unique constraint
    __table_args__ = (
        db.UniqueConstraint('competition_id', 'gymnast_id',
                            name='_competition_gymnast_uc'),
        )


class Scores(db.Model):

    __tablename__ = 'scores'

    id = db.Column(
        db.Integer, primary_key=True
    )

    entry_id = db.Column(
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

    # Relationship to individual judge scores
    judge_scores = db.relationship(
        'JudgeScores', backref='final_score', lazy=True
    )

    def calculate_average_e_score(self):
        """Calculate the average E-score from all judge scores"""
        if not self.judge_scores:
            # Fallback to stored e_score if no judge scores
            return self.e_score
        
        total_e_score = sum(js.e_score for js in self.judge_scores)
        return round(total_e_score / len(self.judge_scores), 3)

    def update_final_score(self):
        """Update the final e_score and total based on judge scores"""
        if self.judge_scores:
            self.e_score = self.calculate_average_e_score()
            self.total = self.e_score + self.d_score - self.penalty


class JudgeScores(db.Model):

    __tablename__ = 'judge_scores'

    id = db.Column(
        db.Integer, primary_key=True
    )

    score_id = db.Column(
        db.Integer, db.ForeignKey('scores.id'), nullable=False
    )

    judge_number = db.Column(
        db.Integer, nullable=False
    )

    e_score = db.Column(
        db.Float, nullable=False
    )

    # Timestamp for when the score was submitted
    submitted_at = db.Column(
        db.DateTime, default=db.func.current_timestamp()
    )
