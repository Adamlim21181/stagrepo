from flask import (render_template, Blueprint,
                   redirect, url_for, request, flash, session)
from extensions import db
from sqlalchemy import or_, cast, String
from datetime import datetime, timedelta
import calendar
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


@main.route('/scoring', methods=['GET', 'POST'])
def scoring():
    if 'user_id' not in session:
        return render_template('nologin.html')

    user_roles = session.get('roles', [])
    if 'admin' not in user_roles and 'judges' not in user_roles:
        flash('Access denied.', 'danger')
        return render_template('nologin.html')

    # Get the live competition
    live_competition = models.Competitions.query.filter_by(
        status='live'
        ).first()

    if not live_competition:
        flash('No live competition is currently running. '
              'Please contact an admin.', 'warning')
        return render_template('scoring.html', no_live_competition=True)

    # Get all entries for the live competition (gymnasts who are competing)
    entries = db.session.query(models.Entries, models.Gymnasts, models.Clubs)\
        .join(models.Gymnasts,
              models.Entries.gymnast_id == models.Gymnasts.id)\
        .join(models.Clubs,
              models.Gymnasts.club_id == models.Clubs.id)\
        .filter(models.Entries.competition_id == live_competition.id)\
        .all()

    # Get all apparatus
    apparatus_list = models.Apparatus.query.all()

    # Calculate scoring progress for each gymnast
    scoring_progress = {}
    total_gymnasts = len(entries)
    fully_scored_gymnasts = 0

    for entry, gymnast, club in entries:
        scored_apparatus = set()
        for score in entry.scores:
            scored_apparatus.add(score.apparatus_id)

        total_apparatus = len(apparatus_list)
        scored_count = len(scored_apparatus)
        is_complete = scored_count == total_apparatus

        if is_complete:
            fully_scored_gymnasts += 1

        scoring_progress[entry.id] = {
            'scored_count': scored_count,
            'total_count': total_apparatus,
            'is_complete': is_complete,
            'percentage': (
                (scored_count / total_apparatus * 100)
                if total_apparatus > 0 else 0
            )
        }

    # Overall competition progress
    overall_progress = {
        'total_gymnasts': total_gymnasts,
        'fully_scored': fully_scored_gymnasts,
        'percentage': (
            (fully_scored_gymnasts / total_gymnasts * 100)
            if total_gymnasts > 0 else 0
        ),
        'is_complete': fully_scored_gymnasts == total_gymnasts
    }

    if request.method == 'POST':
        entry_id = request.form.get('entry_id')
        apparatus_id = request.form.get('apparatus_id')
        e_score = float(request.form.get('e_score'))
        d_score = float(request.form.get('d_score'))
        penalty = float(request.form.get('penalty'))

        # Calculate total
        total = e_score + d_score - penalty

        # Check if score already exists for this entry/apparatus combination
        existing_score = models.Scores.query.filter_by(
            entry_id=entry_id,
            apparatus_id=apparatus_id
        ).first()

        if existing_score:
            # Update existing score
            existing_score.e_score = e_score
            existing_score.d_score = d_score
            existing_score.penalty = penalty
            existing_score.total = total
            flash('Score updated successfully!', 'success')
        else:
            # Create new score
            new_score = models.Scores(
                entry_id=entry_id,
                apparatus_id=apparatus_id,
                e_score=e_score,
                d_score=d_score,
                penalty=penalty,
                total=total
            )
            db.session.add(new_score)
            flash('Score added successfully!', 'success')

        db.session.commit()

        # Check if this completed scoring for a gymnast
        updated_entry = models.Entries.query.get(entry_id)
        if updated_entry:
            scored_apparatus_count = len(updated_entry.scores)
            if scored_apparatus_count == len(apparatus_list):
                gymnast_name = updated_entry.gymnast.name
                flash(f'✅ {gymnast_name} scoring complete!', 'info')

        return redirect(url_for('main.scoring'))

    return render_template(
        'scoring.html',
        entries=entries,
        apparatus_list=apparatus_list,
        live_competition=live_competition,
        scoring_progress=scoring_progress,
        overall_progress=overall_progress
    )


# Replace your existing /live route with this:

@main.route('/live')
def live():
    selected_level = request.args.get('level')
    selected_apparatus_id = request.args.get('apparatus')

    # Check if there's a live competition
    live_competition = models.Competitions.query.filter_by(
        status='live'
        ).first()

    if not live_competition:
        return render_template('live.html', no_live_competition=True)

    # Fetch all distinct levels from the live competition
    levels = db.session.query(
        models.Gymnasts.level
    ).join(models.Entries).filter(
        models.Entries.competition_id == live_competition.id
    ).distinct().order_by(models.Gymnasts.level).all()
    levels = [lvl[0] for lvl in levels]

    # Desired level order
    desired_order = [
        'Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5',
        'Level 6', 'Level 7', 'Level 8', 'Level 9',
        'Junior International', 'Senior International'
    ]

    # Sort levels to match the desired order
    levels = sorted(levels, key=lambda x: desired_order.index(x)
                    if x in desired_order else 100)

    # Fetch all apparatus for top buttons
    apparatus_list = models.Apparatus.query.order_by(
        models.Apparatus.name
    ).all()

    leaderboard_data = []

    if selected_level:
        if selected_apparatus_id and selected_apparatus_id != 'all_around':
            # Show scores for specific apparatus
            leaderboard_data = (
                db.session.query(models.Scores, models.Gymnasts, models.Clubs)
                .join(models.Entries,
                      models.Scores.entry_id == models.Entries.id)
                .join(models.Gymnasts,
                      models.Entries.gymnast_id == models.Gymnasts.id
                      )
                .join(models.Clubs, models.Gymnasts.club_id == models.Clubs.id)
                .filter(models.Entries.competition_id == live_competition.id)
                .filter(models.Gymnasts.level == selected_level)
                .filter(models.Scores.apparatus_id == selected_apparatus_id)
                .order_by(models.Scores.total.desc())
                .all()
            )
        else:
            # Show all-around scores (total of all apparatus)
            # or when no apparatus selected
            # Get all gymnasts for the selected level with their
            # total scores across all apparatus
            leaderboard_data = (
                db.session.query(
                    models.Gymnasts.id,
                    models.Gymnasts.name,
                    models.Gymnasts.level,
                    models.Clubs.name.label('club_name'),
                    db.func.sum(models.Scores.total).label('total_score')
                )
                .join(models.Entries,
                      models.Entries.gymnast_id == models.Gymnasts.id)
                .join(models.Clubs, models.Gymnasts.club_id == models.Clubs.id)
                .join(models.Scores,
                      models.Scores.entry_id == models.Entries.id)
                .filter(models.Entries.competition_id == live_competition.id)
                .filter(models.Gymnasts.level == selected_level)
                .group_by(
                    models.Gymnasts.id,
                    models.Gymnasts.name,
                    models.Gymnasts.level,
                    models.Clubs.name
                )
                .order_by(db.func.sum(models.Scores.total).desc())
                .all()
            )

    return render_template(
            'live.html',
            levels=levels,
            selected_level=selected_level,
            apparatus_list=apparatus_list,
            selected_apparatus_id=selected_apparatus_id,
            leaderboard_data=leaderboard_data,
            live_competition=live_competition
        )


@main.route('/calendar')
def calendar_view():
    # Get current date or date from query parameters
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    # Handle month navigation
    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1

    # Create calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Get competitions for the current month using competition_date
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)

    competitions = models.Competitions.query.filter(
        models.Competitions.competition_date.between(start_date, end_date)
    ).all()

    # Group competitions by date
    competitions_by_date = {}
    for comp in competitions:
        if comp.competition_date:
            day = comp.competition_date.day
            if day not in competitions_by_date:
                competitions_by_date[day] = []
            competitions_by_date[day].append(comp)

    # Calculate navigation dates
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return render_template(
        'calendar.html',
        calendar_data=cal,
        month_name=month_name,
        year=year,
        month=month,
        competitions_by_date=competitions_by_date,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
        today=datetime.now()
    )


# Add route for competition details modal/popup
@main.route('/competition/<int:competition_id>')
def competition_details(competition_id):
    competition = models.Competitions.query.get_or_404(competition_id)

    # Get entries count for this competition
    entries_count = models.Entries.query.filter_by(
        competition_id=competition_id
    ).count()

    # Get entries with gymnast and club details
    entries = db.session.query(models.Entries, models.Gymnasts, models.Clubs)\
        .join(models.Gymnasts,
              models.Entries.gymnast_id == models.Gymnasts.id)\
        .join(models.Clubs, models.Gymnasts.club_id == models.Clubs.id)\
        .filter(models.Entries.competition_id == competition_id)\
        .all()

    return render_template(
        'competition_details.html',
        competition=competition,
        entries_count=entries_count,
        entries=entries
    )


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

    # Add sorting parameters

    # Default sort by total score
    sort_by = request.args.get('sort_by', 'total', type=str)
    # Default descending
    sort_order = request.args.get('sort_order', 'desc', type=str)

    # Define pagination options
    pagination_options = [(5, '5'),
                          (10, '10'),
                          (20, '20'),
                          (50, '50'),
                          (100, '100'),
                          (1000, '1000'),
                          (-1, 'All')]

    # Define sorting options for the template
    sort_options = [
        ('total', 'Total Score'),
        ('e_score', 'Execution Score'),
        ('d_score', 'Difficulty Score'),
        ('penalty', 'Penalty'),
        ('gymnast_name', 'Gymnast Name'),
        ('club_name', 'Club Name'),
        ('competition_name', 'Competition'),
        ('apparatus_name', 'Apparatus'),
        ('level', 'Level'),
        ('id', 'ID'),
        ('entry_id', 'Entry ID')
    ]

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

    # Add sorting logic
    if sort_by == 'gymnast_name':
        sort_column = models.Gymnasts.name
    elif sort_by == 'club_name':
        sort_column = models.Clubs.name
    elif sort_by == 'competition_name':
        sort_column = models.Competitions.name
    elif sort_by == 'apparatus_name':
        sort_column = models.Apparatus.name
    elif sort_by == 'level':
        sort_column = models.Gymnasts.level
    elif sort_by == 'id':
        sort_column = models.Scores.id
    elif sort_by == 'entry_id':
        sort_column = models.Scores.entry_id
    elif sort_by == 'e_score':
        sort_column = models.Scores.e_score
    elif sort_by == 'd_score':
        sort_column = models.Scores.d_score
    elif sort_by == 'penalty':
        sort_column = models.Scores.penalty
    else:
        # Default to total score
        sort_column = models.Scores.total

    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

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
        pagination_options=pagination_options,
        sort_options=sort_options,
        current_sort_by=sort_by,
        current_sort_order=sort_order
    )


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))


# Add gymnasts to competitions
@main.route('/admin/entries', methods=['GET', 'POST'])
def entries():
    if 'user_id' not in session:
        return render_template('nologin.html')

    if 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return render_template('nologin.html')

    # Handle adding new entry
    if request.method == 'POST':
        competition_id = request.form.get('competition_id')
        gymnast_id = request.form.get('gymnast_id')

        # Check if entry already exists
        existing_entry = models.Entries.query.filter_by(
            competition_id=competition_id,
            gymnast_id=gymnast_id
        ).first()

        if existing_entry:
            flash('This gymnast is already entered in this competition!',
                  'warning')
        else:
            new_entry = models.Entries(
                competition_id=competition_id,
                gymnast_id=gymnast_id
            )
            db.session.add(new_entry)
            db.session.commit()
            flash('Entry added successfully!', 'success')

        return redirect(url_for('main.entries'))

    # Get all competitions and gymnasts
    competitions = models.Competitions.query.all()
    gymnasts = models.Gymnasts.query.all()

    # Get all entries with related data
    entries = db.session.query(models.Entries, models.Competitions,
                               models.Gymnasts, models.Clubs)\
        .join(models.Competitions,
              models.Entries.competition_id == models.Competitions.id)\
        .join(models.Gymnasts,
              models.Entries.gymnast_id == models.Gymnasts.id)\
        .join(models.Clubs,
              models.Gymnasts.club_id == models.Clubs.id)\
        .all()

    return render_template(
        'entries.html',
        competitions=competitions,
        gymnasts=gymnasts,
        entries=entries
    )


@main.route('/admin/competitions', methods=['GET', 'POST'])
def competitions():
    if 'user_id' not in session:
        return render_template('nologin.html')

    if 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return render_template('nologin.html')

    # Handle adding new competition
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        competition_date_str = request.form.get('competition_date')
        season_id = request.form.get('season_id')

        # Convert string date to datetime object
        try:
            competition_date = datetime.strptime(
                competition_date_str, '%Y-%m-%d').date()

        except ValueError:
            flash('Invalid date format!', 'danger')
            return redirect(url_for('main.competitions'))

        new_competition = models.Competitions(
            name=name,
            address=address,
            competition_date=competition_date,
            season_id=season_id,
            status='draft'
        )

        db.session.add(new_competition)
        db.session.commit()
        flash('Competition added successfully!', 'success')
        return redirect(url_for('main.competitions'))

    # Get all competitions ordered by date (newest first)
    competitions = models.Competitions.query.order_by(
        models.Competitions.competition_date.desc()).all()
    seasons = models.Seasons.query.all()

    # Pass today's date to the template for reference
    today = datetime.now()

    return render_template(
        'competitions.html',
        competitions=competitions,
        seasons=seasons,
        today=today
    )


@main.route('/admin/competition/<int:competition_id>/start')
def start_competition(competition_id):
    if 'user_id' not in session or 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))

    # End any currently live competition
    current_live = models.Competitions.query.filter_by(status='live').first()
    if current_live:
        current_live.status = 'ended'
        current_live.ended_at = db.func.now()

    # Start the selected competition
    competition = models.Competitions.query.get_or_404(competition_id)
    competition.status = 'live'
    competition.started_at = db.func.now()

    db.session.commit()
    flash(f'Competition "{competition.name}" is now live!', 'success')
    return redirect(url_for('main.competitions'))


@main.route('/admin/competition/<int:competition_id>/end')
def end_competition(competition_id):
    if 'user_id' not in session or 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return redirect(url_for('main.home'))

    competition = models.Competitions.query.get_or_404(competition_id)
    competition.status = 'ended'
    competition.ended_at = db.func.now()

    db.session.commit()
    flash(f'Competition "{competition.name}" has ended.', 'success')
    return redirect(url_for('main.competitions'))
