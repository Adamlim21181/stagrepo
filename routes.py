from flask import render_template, Blueprint
from extensions import db
import models
import forms
main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/gymnasts', methods=['GET', 'POST'])
def gymnasts():

    form = forms.AddGymnast()

    if form.validate_on_submit():
        name = form.name.data
        club_id = form.club_id.data
        level = form.level.data

        new_gymnast = models.Gymnasts(
            name=name,
            club_id=club_id,
            level=level
        )

        db.session.add(new_gymnast)
        db.session.commit()

        form = forms.AddGymnast()

    gymnasts = models.Gymnasts.query.all()

    return render_template(
        'gymnasts.html',
        gymnasts=gymnasts,
        form=form
    )


@main.route('/levels')
def levels():
    return render_template('levels.html')


@main.route('/scoring')
def scoring():
    return render_template('scoring.html')


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
    return render_template('results.html')
