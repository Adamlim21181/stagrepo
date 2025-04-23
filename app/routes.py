from flask import Blueprint, render_template
from app import db  # Import db from the app, not from models

import app.models as models  # Models will be used here

main = Blueprint('main', __name__)

# Your route handlers go here


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/gymnasts')
def gymnasts():
    return render_template('gymnasts.html')


@main.route('/levels')
def levels():
    return render_template('levels.html')


@main.route('/scoring')
def scoring():
    return render_template('scoring.html')


@main.route('/live')
def live():
    return render_template('live.html')


@main.route('/calendar')
def calendar():
    return render_template('calendar.html')


@main.route('/login')
def login():
    return render_template('login.html')


@main.route('/results')
def results():

    id = [i[0] for i in
          db.session.query(models.Score.score_id).distinct().all()]

    name = [n[0] for n in
            db.session.query(models.Gymnast.gymnast_name).distinct().all()]

    level = [le[0] for le in
             db.session.query(models.Gymnast.level).distinct().all()]

    club = [c[0] for c in
            db.session.query(models.Club.club_name).distinct().all()]

    competition = [comp[0] for comp in
                   db.session.query
                   (models.Competition.competition_name).distinct().all()]

    year = [y[0] for y in
            db.session.query(models.Season.year).distinct().all()]

    apparatus = [a[0] for a in
                 db.session.query(models.Apparatus.apparatus_name)
                 .distinct().all()]

    execution = [e[0] for e in
                 db.session.query(models.Score.execution).distinct().all()]

    difficulty = [d[0] for d in
                  db.session.query(models.Score.difficulty).distinct().all()]

    penalty = [p[0] for p in
               db.session.query(models.Score.penalty).distinct().all()]

    total = [t[0] for t in
             db.session.query(models.Score.execution +
                              models.Score.difficulty -
                              models.Score.penalty).distinct().all()]

    total_score = (models.Score.execution + models.Score.difficulty -
                   models.Score.penalty).label('total')

    query = (db.session.query(models.Score.score_id,
                              models.Gymnast.gymnast_name,
                              models.Gymnast.level,
                              models.Club.club_name,
                              models.Competition.competition_name,
                              models.Season.year,
                              models.Apparatus.apparatus_name,
                              models.Score.execution,
                              models.Score.difficulty,
                              models.Score.penalty,
                              total_score)
             .join(models.Entry,
                   models.Entry.entries_id == models.Score.entries_id)
             .join(models.Gymnast,
                   models.Gymnast.gymnast_id == models.Entry.gymnast_id)
             .join(models.Club,
                   models.Club.club_id == models.Gymnast.club_id)
             .join(models.Competition,
                   models.Competition.competition_id ==
                   models.Entry.competition_id)
             .join(models.Season,
                   models.Season.season_id ==
                   models.Competition.season_id)
             .join(models.Apparatus,
                   models.Apparatus.apparatus_id == models.Score.apparatus_id))

    id_filter = request.args.get('id')
    name_filter = request.args.get('name')
    level_filter = request.args.get('level')
    club_filter = request.args.get('club')
    competition_filter = request.args.get('competition')
    year_filter = request.args.get('year')
    apparatus_filter = request.args.get('apparatus')
    execution_filter = request.args.get('execution')
    difficulty_filter = request.args.get('difficulty')
    penalty_filter = request.args.get('penalty')
    total_filter = request.args.get('total')

    if id_filter:
        query = query.filter(models.Score.score_id == int(id_filter))

    if name_filter:
        query = query.filter(models.Gymnast.gymnast_name == name_filter)

    if level_filter:
        query = query.filter(models.Gymnast.level == level_filter)

    if club_filter:
        query = query.filter(models.Club.club_name == club_filter)

    if competition_filter:
        query = query.filter(models.Competition.competition_name ==
                             competition_filter)

    if year_filter:
        query = query.filter(models.Season.year == int(year_filter))

    if apparatus_filter:
        query = query.filter(models.Apparatus.apparatus_name ==
                             apparatus_filter)

    if execution_filter:
        query = query.filter(models.Score.execution ==
                             float(execution_filter))

    if difficulty_filter:
        query = query.filter(models.Score.difficulty ==
                             float(difficulty_filter))

    if penalty_filter:
        query = query.filter(models.Score.penalty ==
                             float(penalty_filter))

    if total_filter:
        query = query.filter(models.Score.execution +
                             models.Score.difficulty -
                             models.Score.penalty == float(total_filter))

    results = query.all()

    return render_template('results.html', results=results,
                           id=id, name=name, level=level, club=club,
                           competition=competition, year=year,
                           apparatus=apparatus, execution=execution,
                           difficulty=difficulty, penalty=penalty,
                           total=total)
