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
    # Get upcoming competitions for public display
    upcoming_competitions = models.Competitions.query.filter(
        models.Competitions.competition_date >= datetime.now().date(),
        models.Competitions.status.in_(['draft', 'live'])
    ).order_by(models.Competitions.competition_date).limit(3).all()

    # Get live competitions
    live_competitions = models.Competitions.query.filter(
        models.Competitions.status == 'live'
    ).all()

    # Get recent results (ended competitions)
    recent_results = models.Competitions.query.filter(
        models.Competitions.status == 'ended'
    ).order_by(models.Competitions.ended_at.desc()).limit(3).all()

    return render_template('home.html',
                           upcoming_competitions=upcoming_competitions,
                           live_competitions=live_competitions,
                           recent_results=recent_results)


@main.route('/gymnasts', methods=['GET', 'POST'])
def gymnasts():

    if 'user_id' not in session:
        return render_template('nologin.html')

    if 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return render_template('nologin.html')

    gymnast_form = forms.AddGymnast()
    club_form = forms.AddClub()

    # Get clubs for the dropdown
    clubs = models.Clubs.query.all()

    if request.method == 'POST':
        # Check which form was submitted
        if (
            'name' in request.form and
            'club' in request.form and
            'level' in request.form
        ):
            # Gymnast form submitted - validate manually
            name = request.form.get('name', '').strip()
            club_id = request.form.get('club', '')
            level = request.form.get('level', '')

            # Simple validation
            if not name:
                flash('Please enter a gymnast name.', 'danger')
            elif not club_id:
                flash('Please select a club.', 'danger')
            elif not level:
                flash('Please select a level.', 'danger')
            else:
                try:
                    club_id = int(club_id)
                    new_gymnast = models.Gymnasts(
                        name=name,
                        club_id=club_id,
                        level=level
                    )

                    db.session.add(new_gymnast)
                    db.session.commit()

                    flash(f'Gymnast "{name}" added successfully!', 'success')
                    return redirect(url_for('main.gymnasts'))
                except ValueError:
                    flash('Invalid club selection.', 'danger')
                except Exception as e:
                    flash(f'Error adding gymnast: {str(e)}', 'danger')

        elif 'name' in request.form and 'club' not in request.form:
            # Club form submitted
            if club_form.validate_on_submit():
                name = club_form.name.data

                new_club = models.Clubs(
                    name=name
                )

                db.session.add(new_club)
                db.session.commit()

                flash(f'Club "{name}" added successfully!', 'success')
                return redirect(url_for('main.gymnasts'))

    gymnasts = models.Gymnasts.query.order_by(models.Gymnasts.id.desc()).all()
    # clubs already retrieved above for the form

    return render_template(
        'gymnasts.html',
        gymnasts=gymnasts,
        clubs=clubs,
        gymnast_form=gymnast_form,
        club_form=club_form
    )


@main.route('/scoring', methods=['GET', 'POST'])
def scoring():
    if 'user_id' not in session:
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
        d_score = request.form.get('d_score')
        penalty = request.form.get('penalty', 0)

        # Get execution scores (can be multiple)
        execution_scores = request.form.getlist('execution_scores')

        try:
            # Convert to floats and filter out empty values
            execution_scores = [
                float(score) for score in execution_scores
                if score and score.strip()
            ]

            if not execution_scores:
                flash('Please enter at least one execution score.', 'warning')
                return redirect(url_for('main.scoring'))

            d_score = float(d_score) if d_score else 0.0
            penalty = float(penalty) if penalty else 0.0

            # Find existing score or create new one
            existing_score = models.Scores.query.filter_by(
                entry_id=entry_id,
                apparatus_id=apparatus_id
            ).first()

            if existing_score:
                # Clear existing judge scores
                models.JudgeScores.query.filter_by(
                    score_id=existing_score.id
                ).delete()
            else:
                # Create new score record
                existing_score = models.Scores(
                    entry_id=entry_id,
                    apparatus_id=apparatus_id,
                    e_score=0.0,
                    d_score=d_score,
                    penalty=penalty,
                    total=0.0
                )
                db.session.add(existing_score)
                db.session.flush()  # Get the ID

            # Update D-score and penalty
            existing_score.d_score = d_score
            existing_score.penalty = penalty

            if len(execution_scores) == 1:
                # Single judge scoring
                existing_score.e_score = execution_scores[0]
                existing_score.total = (existing_score.e_score +
                                        existing_score.d_score -
                                        existing_score.penalty)
                flash(f'Score submitted! Total: {existing_score.total:.3f}',
                      'success')
            else:
                # Multiple judge scoring - save individual scores and average
                for judge_num, e_score in enumerate(execution_scores, 1):
                    judge_score = models.JudgeScores(
                        score_id=existing_score.id,
                        judge_number=judge_num,
                        e_score=round(e_score, 3)
                    )
                    db.session.add(judge_score)

                # Calculate and update averaged E-score
                existing_score.update_final_score()
                flash(f'Multi-judge score submitted! Average E-score: '
                      f'{existing_score.e_score:.3f}, Total: '
                      f'{existing_score.total:.3f}', 'success')

        except ValueError as e:
            flash(f'Invalid score values: {str(e)}', 'danger')
            return redirect(url_for('main.scoring'))

        db.session.commit()

        # Check if this completed scoring for a gymnast
        updated_entry = models.Entries.query.get(entry_id)
        if updated_entry:
            scored_apparatus_count = len(updated_entry.scores)
            if scored_apparatus_count == len(apparatus_list):
                gymnast_name = updated_entry.gymnasts.name
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
    """Results page with WTForms search, sorting, and pagination."""
    # Build WTForms-based search form (GET; CSRF off for idempotent query)
    form = forms.ResultsSearchForm(request.args, meta={'csrf': False})
    search_query = form.search.data or ''

    # Choices for the form
    pagination_options = [
        (5, '5'), (10, '10'), (20, '20'), (50, '50'),
        (100, '100'), (1000, '1000'), (-1, 'All'),
    ]
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
        ('id', 'Gymnast ID'),
        ('entry_id', 'Entry ID'),
    ]
    form.per_page.choices = pagination_options
    form.sort_by.choices = sort_options

    # Read current controls (with defaults)
    per_page = form.per_page.data if form.per_page.data is not None else 5
    sort_by = form.sort_by.data or 'total'
    sort_order = form.sort_order.data or request.args.get('sort_order', 'desc')

    # Base query: return Scores ORM objects and eager-load relations
    query = (
        models.Scores.query
        .join(models.Entries, models.Scores.entry_id == models.Entries.id)
        .join(models.Gymnasts, models.Entries.gymnast_id == models.Gymnasts.id)
        .join(models.Clubs, models.Gymnasts.club_id == models.Clubs.id)
        .join(
            models.Competitions,
            models.Entries.competition_id == models.Competitions.id
        )
        .join(
            models.Apparatus,
            models.Scores.apparatus_id == models.Apparatus.id
        )
        .options(
            db.joinedload(models.Scores.entry)
              .joinedload(models.Entries.gymnasts)
              .joinedload(models.Gymnasts.clubs),
            db.joinedload(models.Scores.entry)
              .joinedload(models.Entries.competitions),
            db.joinedload(models.Scores.apparatus),
        )
    )

    # Search filter
    if search_query:
        like = f"%{search_query}%"
        query = query.filter(
            db.or_(
                models.Gymnasts.name.ilike(like),
                models.Clubs.name.ilike(like),
                models.Competitions.name.ilike(like),
                models.Apparatus.name.ilike(like),
                models.Gymnasts.level.ilike(like),
                db.cast(models.Entries.id, db.String).ilike(like),
                db.cast(models.Gymnasts.id, db.String).ilike(like),
            )
        )

    # Sorting
    # For 'total', sort by e + d - penalty;
    # for others use columns/related columns
    total_expr = (
        models.Scores.e_score + models.Scores.d_score - models.Scores.penalty
    )
    sort_map = {
        'total': total_expr,
        'e_score': models.Scores.e_score,
        'd_score': models.Scores.d_score,
        'penalty': models.Scores.penalty,
        'gymnast_name': models.Gymnasts.name,
        'club_name': models.Clubs.name,
        'competition_name': models.Competitions.name,
        'apparatus_name': models.Apparatus.name,
        'level': models.Gymnasts.level,
        'id': models.Gymnasts.id,
        'entry_id': models.Entries.id,
    }
    sort_col = sort_map.get(sort_by, total_expr)
    query = query.order_by(
        db.desc(sort_col) if sort_order == 'desc' else db.asc(sort_col)
    )

    # Pagination
    if per_page == -1:  # show all
        results = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        # If you’re on Flask-SQLAlchemy >=3, prefer db.paginate(query, ...)
        try:
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        except AttributeError:
            pagination = db.paginate(
                query,
                page=page,
                per_page=per_page,
                error_out=False
            )
        results = pagination.items

    print('DEBUG total rows:', query.count())

    return render_template(
        'results.html',
        search_query=search_query,
        current_sort_by=sort_by,
        current_sort_order=sort_order,
        per_page=per_page,
        form=form,
        results=results,
        pagination=pagination,
        pagination_options=pagination_options,
        sort_options=sort_options,
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

        # Check if this is bulk add
        if request.form.get('bulk_add'):
            gymnast_ids = request.form.getlist('gymnast_ids')
            added_count = 0
            duplicate_count = 0

            for gymnast_id in gymnast_ids:
                # Check if entry already exists
                existing_entry = models.Entries.query.filter_by(
                    competition_id=competition_id,
                    gymnast_id=gymnast_id
                ).first()

                if not existing_entry:
                    new_entry = models.Entries(
                        competition_id=competition_id,
                        gymnast_id=gymnast_id
                    )
                    db.session.add(new_entry)
                    added_count += 1
                else:
                    duplicate_count += 1

            db.session.commit()

            if added_count > 0:
                flash(
                    f'Added {added_count} gymnasts to the competition!',
                    'success'
                )
            if duplicate_count > 0:
                flash(
                    (f'{duplicate_count} gymnasts were already in the '
                     'competition.'),
                    'info'
                )

        else:
            # Single gymnast add
            gymnast_id = request.form.get('gymnast_id')

            # Check if entry already exists
            existing_entry = models.Entries.query.filter_by(
                competition_id=competition_id,
                gymnast_id=gymnast_id
            ).first()

            if existing_entry:
                flash(
                    'This gymnast is already entered in this competition!',
                    'warning'
                )
            else:
                new_entry = models.Entries(
                    competition_id=competition_id,
                    gymnast_id=gymnast_id
                )
                db.session.add(new_entry)
                db.session.commit()
                flash('Entry added successfully!', 'success')

        return redirect(url_for('main.entries'))

    # Get all competitions, gymnasts, and clubs
    competitions = (
        models.Competitions.query
        .order_by(models.Competitions.competition_date.desc())
        .all()
    )
    gymnasts = (
        models.Gymnasts.query
        .order_by(models.Gymnasts.name)
        .all()
    )
    clubs = models.Clubs.query.order_by(models.Clubs.name).all()

    # Get unique levels
    levels = (
        db.session.query(models.Gymnasts.level)
        .distinct()
        .order_by(models.Gymnasts.level)
        .all()
    )
    levels = [level[0] for level in levels]

    # Get all entries with related data
    entries = (
        db.session.query(
            models.Entries,
            models.Competitions,
            models.Gymnasts,
            models.Clubs
        )
        .join(
            models.Competitions,
            models.Entries.competition_id == models.Competitions.id
        )
        .join(
            models.Gymnasts,
            models.Entries.gymnast_id == models.Gymnasts.id
        )
        .join(
            models.Clubs,
            models.Gymnasts.club_id == models.Clubs.id
        )
        .order_by(
            models.Competitions.competition_date.desc(),
            models.Gymnasts.name
        )
        .all()
    )

    return render_template(
        'entries.html',
        competitions=competitions,
        gymnasts=gymnasts,
        clubs=clubs,
        levels=levels,
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

        # If no season_id provided, use current year's season
        if not season_id:
            current_year = datetime.now().year
            current_season = models.Seasons.query.filter_by(
                year=current_year
            ).first()

            if current_season:
                season_id = current_season.id

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

    # Get all competitions ordered by date (newest first),
    # then by ID (newest first)
    competitions = models.Competitions.query.order_by(
        models.Competitions.competition_date.desc(),
        models.Competitions.id.desc()
    ).all()
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
