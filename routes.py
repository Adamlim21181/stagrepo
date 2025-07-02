from flask import (render_template, Blueprint,
                   redirect, url_for, request, flash, session)
from extensions import db
from sqlalchemy import or_, cast, String
import models
import forms
main = Blueprint('main', __name__)


@main.context_processor  # Ensures this is run before any other routes
def inject_user():
    return dict(
        logged_in='user_id' in session,
        user_roles=session.get('roles', []),
        is_admin='admin' in session.get('roles', []),
        is_judge='judges' in session.get('roles', []),
        user_id=session.get('user_id')
    )


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/gymnasts', methods=['GET', 'POST'])
def gymnasts():

    if 'user_id' not in session:
        return render_template('nologin.html')

    if 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return render_template('nologin.html')

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

    if 'user_id' not in session:
        return render_template('nologin.html')

    user_roles = session.get('roles', [])
    if 'admin' not in user_roles and 'judges' not in user_roles:
        flash('Access denied.', 'danger')
        return render_template('nologin.html')

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
    selected_level = request.args.get('level')
    selected_apparatus_id = request.args.get('apparatus')

    # Fetch all distinct levels for the sidebar
    levels = db.session.query(
        models.Gymnasts.level
        ).distinct().order_by(models.Gymnasts.level).all()
    levels = [lvl[0] for lvl in levels]

    # Fetch all apparatus for top buttons
    apparatus_list = models.Apparatus.query.order_by(
        models.Apparatus.name
        ).all()

    leaderboard_data = []

    if selected_level and selected_apparatus_id:
        leaderboard_data = (
            db.session.query(models.Scores, models.Gymnasts, models.Clubs)
            .join(models.Entries, models.Scores.entry_id == models.Entries.id)
            .join(models.Gymnasts,
                  models.Entries.gymnast_id == models.Gymnasts.id
                  )
            .join(models.Clubs, models.Gymnasts.club_id == models.Clubs.id)
            .filter(models.Gymnasts.level == selected_level)
            .filter(models.Scores.apparatus_id == selected_apparatus_id)
            .order_by(models.Scores.total.desc())
            .all()
        )

    return render_template(
        'live.html',
        levels=levels,
        selected_level=selected_level,
        apparatus_list=apparatus_list,
        selected_apparatus_id=selected_apparatus_id,
        leaderboard_data=leaderboard_data
    )


@main.route('/calander')
def calander():
    return render_template('calander.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        code = form.code.data
        user = models.Users.query.filter_by(username=username).first()

        if user and user.code == code:
            session['user_id'] = user.id
            session['username'] = user.username
            session['roles'] = [role.name for role in user.roles]
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or code', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html', form=form)


@main.route('/results')
def results():
    search_query = request.args.get('search', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Define pagination options
    pagination_options = [(5, '5'),
                          (10, '10'),
                          (20, '20'),
                          (50, '50'),
                          (100, '100'),
                          (1000, '1000'),
                          (-1, 'All')]

    # Start with base query including necessary joins
    query = models.Scores.query\
        .join(models.Entries)\
        .join(models.Gymnasts)\
        .join(models.Clubs)\
        .join(models.Competitions)\
        .join(models.Apparatus)

    # Add search filter if search term provided
    if search_query:
        query = query.filter(
            or_(
                # Integer fields - cast to string for searching
                cast(models.Scores.id, String).contains(search_query),
                cast(models.Scores.entry_id, String).contains(search_query),

                # Float fields - cast to string for searching
                cast(models.Scores.e_score, String).contains(search_query),
                cast(models.Scores.d_score, String).contains(search_query),
                cast(models.Scores.penalty, String).contains(search_query),
                cast(models.Scores.total, String).contains(search_query),

                # Related table fields - use proper join syntax
                models.Competitions.name.contains(search_query),
                models.Gymnasts.name.contains(search_query),
                models.Gymnasts.level.contains(search_query),
                models.Clubs.name.contains(search_query),
                models.Apparatus.name.contains(search_query)
            )
        )

    # Handle "All" option vs normal pagination
    if per_page == -1:
        # Show all results, no pagination
        all_results = query.all()

        # Create a mock pagination object with
        # all necessary attributes and methods
        class MockPagination:
            def __init__(self, items):
                self.items = items
                self.total = len(items)
                self.pages = 1
                self.page = 1
                self.per_page = len(items)
                self.has_prev = False
                self.has_next = False
                self.prev_num = None
                self.next_num = None

            def iter_pages(
                self,
                left_edge=2,
                left_current=2,
                right_current=3,
                right_edge=2
            ):
                # For "All", we only have 1 page, so just return [1]
                return [1]

        paginated_results = MockPagination(all_results)
    else:
        # Apply normal pagination
        paginated_results = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    return render_template(
        'results.html',
        results=paginated_results,
        per_page=per_page,
        search_query=search_query,
        pagination_options=pagination_options
    )


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))
