from flask import render_template
from create_app import app


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/gymnasts')
def gymnasts():
    return render_template('gymnasts.html')


@app.route('/levels')
def levels():
    return render_template('levels.html')


@app.route('/scoring')
def scoring():
    return render_template('scoring.html')


@app.route('/live')
def live():
    return render_template('live.html')


@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

    
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/results')
def results():
    return render_template('results.html')
