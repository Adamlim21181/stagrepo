from flask import render_template
from datetime import datetime
import models
from . import main


@main.route('/')
def home():
    upcoming_competitions = models.Competitions.query.filter(
        models.Competitions.competition_date >= datetime.now().date(),
        models.Competitions.status.in_(['draft', 'live'])
    ).order_by(models.Competitions.competition_date).limit(3).all()

    live_competitions = models.Competitions.query.filter(
        models.Competitions.status == 'live'
    ).all()

    recent_results = models.Competitions.query.filter(
        models.Competitions.status == 'ended'
    ).order_by(models.Competitions.ended_at.desc()).limit(3).all()

    return render_template('home.html',
                           upcoming_competitions=upcoming_competitions,
                           live_competitions=live_competitions,
                           recent_results=recent_results)
