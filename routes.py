from flask import render_template, Blueprint, redirect, url_for
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

    if gymnast_form.validate_on_submit():
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

    if club_form.validate_on_submit():
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
