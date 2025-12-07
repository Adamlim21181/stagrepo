"""Database models for gymnastics competition management."""

from extensions import db
from datetime import datetime


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

    email = db.Column(
        db.String(120), nullable=False, unique=True
    )

    email_confirmed = db.Column(
        db.Boolean, nullable=False, default=False
    )

    first_name = db.Column(
        db.String(50), nullable=True
    )

    last_name = db.Column(
        db.String(50), nullable=True
    )

    password = db.Column(
        db.String(255), nullable=False
    )

    created_at = db.Column(
            db.DateTime, nullable=False, default=db.func.current_timestamp()
        )

    role_id = db.Column(
        db.Integer, db.ForeignKey('roles.id'), nullable=False
    )

    role = db.relationship("Roles", backref="users")
    
    # Relationship to gymnast profile (if user is linked to a gymnast)
    gymnast = db.relationship("Gymnasts", backref="user", uselist=False)


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
    )

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

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True
    )

    name = db.Column(
        db.String(50), nullable=False
    )

    age = db.Column(db.Integer, nullable=True)

    goals = db.Column(db.Text, nullable=True)

    achievements = db.Column(db.Text, nullable=True)

    injuries = db.Column(db.Text, nullable=True)

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

    # Database constraint prevents duplicate entries
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

    judge_scores = db.relationship(
        'JudgeScores', backref='final_score', lazy=True
    )

    def calculate_average_e_score(self):
        """Calculate the average E-score from all judge scores."""
        if not self.judge_scores:
            return self.e_score

        # Sum all judge scores and divide by count to get average
        total_e_score = sum(js.e_score for js in self.judge_scores)
        return round(total_e_score / len(self.judge_scores), 3)

    def update_final_score(self):
        """Update the final e_score and total based on judge scores."""
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


class AthleteApplications(db.Model):
    __tablename__ = 'athlete_applications'

    id = db.Column(
        db.Integer, primary_key=True
    )

    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False
    )

    club_name = db.Column(
        db.String(100), nullable=False
    )

    gymnastics_level = db.Column(
        db.String(50), nullable=False
    )

    years_experience = db.Column(
        db.Integer, nullable=True
    )

    coach_name = db.Column(
        db.String(100), nullable=True
    )

    coach_contact = db.Column(
        db.String(100), nullable=True
    )

    achievements = db.Column(
        db.Text, nullable=True
    )

    why_join = db.Column(
        db.Text, nullable=True
    )

    status = db.Column(
        db.String(20), nullable=False, default='pending'
        # Values: 'pending', 'approved', 'rejected'
    )

    submitted_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )

    reviewed_at = db.Column(
        db.DateTime, nullable=True
    )

    reviewed_by = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True
    )

    admin_notes = db.Column(
        db.Text, nullable=True
    )

    # Relationships
    user = db.relationship("Users", foreign_keys=[user_id],
                           backref="athlete_application")
    reviewer = db.relationship("Users", foreign_keys=[reviewed_by])
