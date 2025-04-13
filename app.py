from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Configure the MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = ("mysql+mysqldb://STAGNASTICS:"
                                         "gyM!2025_Score$NZ"
                                         "@STAGNASTICS.mysql.pythonanywhere-"
                                         "services.com/STAGNASTICS$stagdata")

# Set pool_recycle to prevent connection timeouts
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}

# Initialize the database
db = SQLAlchemy(app)


# Connecting to databse and executing queries
def db_query(query_string, params=(), single=True, commit=False):

    result = db.session.execute(query_string, params)

    if single:
        return result.fetchone()

    else:
        return result.fetchall()

    if commit:
        db.session.commit()

    return result


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/gymnasts')
def gymnasts():
    return render_template('gymnasts.html')


@app.route('/levels')
def levels():
    return render_template('levels.html')


@app.route('/results', methods=['GET'])
def results():
    query = text(
        "SELECT score.score_id, gymnasts.gymnast_name, gymnasts.level, "
        "competitions.competition_name, seasons.year, clubs.club_name, "
        "apparatus.apparatus_name, score.difficulty, score.execution, "
        "score.penalty, "
        "ROUND(score.difficulty + score.execution - score.penalty) "
        "AS total, "
        "RANK() OVER (PARTITION BY competitions.competition_id ORDER BY "
        "(score.difficulty + score.execution - score.penalty) DESC) "
        "AS rank_in_competition "
        "FROM score "
        "JOIN entries ON score.entries_id = entries.entries_id "
        "JOIN gymnasts ON entries.gymnast_id = gymnasts.gymnast_id "
        "JOIN competitions "
        "ON entries.competition_id = competitions.competition_id "
        "JOIN seasons ON competitions.season_id = seasons.season_id "
        "JOIN clubs ON gymnasts.club_id = clubs.club_id "
        "JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id;")
    
    result = db_query(query, single=False)

    return render_template('results.html', result=result)


@app.route('/scoring')
def scoring():
    return render_template('scoring.html')


@app.route('/live')
def live():
    return render_template('live.html')


@app.route('/calander')
def calander():
    return render_template('calander.html')


@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
