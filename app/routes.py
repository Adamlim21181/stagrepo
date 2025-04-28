from flask import Blueprint, render_template


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
    return render_template('results.html')
