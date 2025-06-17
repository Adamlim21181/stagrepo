from flask import render_template, Blueprint, redirect, url_for, request
from extensions import db
import models
import forms
main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/gymnasts', methods=['GET', 'POST'])
def gymnasts():

    gymnast_form = forms.AddGymnast()

    if gymnast_form.submit.data and gymnast_form.validate_on_submit():
        name = gymnast_form.name.data
        club_id = gymnast_form.club.data.id
        level = gymnast_form.level.data

        new_gymnast = models.Gymnasts(
            name=name,
            club_id=club_id,
            level=level
        )

        db.session.add(new_gymnast)
        db.session.commit()

        return redirect(url_for('main.gymnasts'))

    club_form = forms.AddClub()

    if club_form.submit.data and club_form.validate_on_submit():
        name = club_form.name.data

        new_club = models.Clubs(
            name=name
        )

        db.session.add(new_club)
        db.session.commit()

        return redirect(url_for('main.gymnasts'))

    gymnasts = models.Gymnasts.query.all()

    return render_template(
        'gymnasts.html',
        gymnasts=gymnasts,
        gymnast_form=gymnast_form,
        club_form=club_form
    )


@main.route('/levels')
def levels():
    return render_template('levels.html')


@main.route('/scoring', methods=['GET', 'POST'])
def scoring():

    scoring_form = forms.AddScores()

    if scoring_form.submit.data and scoring_form.validate_on_submit():
        id = scoring_form.id.data
        apparatus = scoring_form.apparatus.data
        execution = scoring_form.execution.data
        difficulty = scoring_form.difficulty.data
        penalty = scoring_form.penalty.data

        new_score = models.Scores(
            id=id,
            apparatus=apparatus,
            execution=execution,
            difficulty=difficulty,
            penalty=penalty
        )

        db.session.add(new_score)
        db.session.commit()

        return redirect(url_for('main.scoring'))

    return render_template('scoring.html', scoring_form=scoring_form)


@main.route('/live')
def live():
    scores = models.Scores.query.all()

    return render_template('live.html', scores=scores)


@main.route('/calander')
def calander():
    return render_template('calander.html')


@main.route('/login')
def login():
    return render_template('login.html')


@main.route('/results')
def results():

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    paginated_results = models.Scores.query.paginate(
        page=page,
        per_page=per_page
    )

    return render_template(
        'results.html',
        results=paginated_results,
        per_page=per_page
    )
