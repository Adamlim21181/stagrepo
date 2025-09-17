
from flask import render_template, request
from datetime import datetime, timedelta
import calendar
from extensions import db
import models
from . import main


@main.route('/calendar')
def calendar_view():
    # Get current date or date from query parameters
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

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

    competitions_by_date = {}
    for comp in competitions:
        if comp.competition_date:
            day = comp.competition_date.day
            if day not in competitions_by_date:
                competitions_by_date[day] = []
            competitions_by_date[day].append(comp)

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


@main.route('/competition/<int:competition_id>')
def competition_details(competition_id):
    """Display detailed information about a specific competition."""
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
