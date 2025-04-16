"""
============================================
FLASK APPLICATION - COMPLETE EXPLANATION
============================================

This is the main backend server file that:
1. Sets up the Flask web application
2. Configures database connections
3. Defines routes for different pages
4. Handles database queries
"""

# Import required libraries
from flask import Flask, render_template  # Flask core functionality

# Database ORM (Object-Relational Mapping)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # For writing raw SQL queries

# ============================================
# 1. FLASK APPLICATION SETUP
# ============================================

# Create the Flask application instance
# __name__ tells Flask where to look for templates/static files
app = Flask(__name__)

# ============================================
# 2. DATABASE CONFIGURATION
# ============================================

# Configure the MySQL database connection string
# Format: mysql+mysqldb://username:password@host/database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+mysqldb://STAGNASTICS:"  # Username
    "gyM!2025_Score$NZ"              # Password
    "@STAGNASTICS.mysql.pythonanywhere-services.com"  # Host
    "/STAGNASTICS$stagdata"          # Database name
)

# Additional database configuration:
# pool_recycle prevents connection timeouts
# by recycling connections after 280 seconds
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}

# Initialize SQLAlchemy database connection
# This connects our Flask app to the MySQL database
db = SQLAlchemy(app)

# ============================================
# 3. DATABASE QUERY HELPER FUNCTION
# ============================================


def db_query(query_string, params=(), single=True, commit=False):
    """
    Executes a database query safely and returns results

    Parameters:
    - query_string: SQL query to execute (as text object)
    - params: Tuple of parameters for the query (prevents SQL injection)
    - single: If True, returns only first row; if False, returns all rows
    - commit: If True, commits transaction (for INSERT/UPDATE/DELETE)

    Returns:
    - A single row if single=True, or all rows if single=False
    """

    # Execute the query using Flask-SQLAlchemy's session
    result = db.session.execute(query_string, params)

    # For SELECT queries that return data
    if single:
        # Return just the first row (for queries expecting 1 result)
        return result.fetchone()
    else:
        # Return all rows (for queries expecting multiple results)
        return result.fetchall()

    # For INSERT/UPDATE/DELETE queries that modify data
    if commit:
        # Save changes to database
        db.session.commit()

    return result

# ============================================
# 4. ROUTE DEFINITIONS
# ============================================


# Homepage route - responds to http://yoursite.com/
@app.route('/')
def home():
    """Renders the homepage template"""
    return render_template('home.html')


# Gymnasts page route - http://yoursite.com/gymnasts
@app.route('/gymnasts')
def gymnasts():
    """Renders the gymnasts listing page"""
    return render_template('gymnasts.html')


# Levels page route - http://yoursite.com/levels
@app.route('/levels')
def levels():
    """Renders the levels information page"""
    return render_template('levels.html')


# Results page route - http://yoursite.com/results
@app.route('/results', methods=['GET'])
def results():
    """
    Renders the competition results page with data from database

    1. Executes a complex SQL query joining multiple tables
    2. Calculates total scores and competition rankings
    3. Passes the results to the template for display
    """

    # Define our SQL query using text() for safety
    query = text(
        "SELECT score.score_id, gymnasts.gymnast_name, gymnasts.level, "
        "competitions.competition_name, seasons.year, clubs.club_name, "
        "apparatus.apparatus_name, score.difficulty, score.execution, "
        "score.penalty, "
        # Calculate total score (difficulty + execution - penalty)
        "ROUND(score.difficulty + score.execution - score.penalty) AS total, "
        # Calculate competition ranking using window function
        "RANK() OVER (PARTITION BY competitions.competition_id ORDER BY "
        "(score.difficulty + score.execution - score.penalty) DESC) "
        "AS rank_in_competition "
        # Join all the related tables
        "FROM score "
        "JOIN entries ON score.entries_id = entries.entries_id "
        "JOIN gymnasts ON entries.gymnast_id = gymnasts.gymnast_id "
        "JOIN competitions "
        "ON entries.competition_id = competitions.competition_id "
        "JOIN seasons ON competitions.season_id = seasons.season_id "
        "JOIN clubs ON gymnasts.club_id = clubs.club_id "
        "JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id;"
    )

    # Execute query and get all results (single=False)
    result = db_query(query, single=False)

    # Render template with the query results
    return render_template('results.html', result=result)


# Scoring system explanation page
@app.route('/scoring')
def scoring():
    """Renders the scoring system explanation page"""
    return render_template('scoring.html')


# Live competition page
@app.route('/live')
def live():
    """Renders the live competition page"""
    return render_template('live.html')


# Calendar/events page
@app.route('/calander')  # Note: Typo in "calendar"
def calander():
    """Renders the calendar/events page"""
    return render_template('calander.html')


# Login page
@app.route('/login')
def login():
    """Renders the login page"""
    return render_template('login.html')

# ============================================
# 5. APPLICATION STARTUP
# ============================================


# This ensures the app only runs when executed directly
# (not when imported as a module)
if __name__ == '__main__':
    # Start the development server
    # debug=True enables auto-reloader and debug pages
    app.run(debug=True)
