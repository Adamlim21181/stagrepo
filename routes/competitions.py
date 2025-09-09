"""
Competitions management routes.
Handles competition creation and management.
"""
from flask import render_template, redirect, url_for, session, flash, request
from datetime import datetime
from extensions import db
import models
import forms
from . import main


@main.route('/competitions', methods=['GET', 'POST'])
def competitions():
    """Manage competitions - admin only access."""
    if 'user_id' not in session:
        return render_template('nologin.html')

    if 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return render_template('nologin.html')

    form = forms.AddCompetitionForm()

    # Handle adding new competition
    if form.validate_on_submit():
        # If no season_id provided, use current year's season
        current_year = datetime.now().year
        current_season = models.Seasons.query.filter_by(year=current_year).first()
        season_id = current_season.id if current_season else None

        new_competition = models.Competitions(
            name=form.name.data,
            address=form.address.data,
            competition_date=form.competition_date.data,
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
        today=today,
        form=form
    )
