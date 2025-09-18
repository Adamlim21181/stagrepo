from flask import render_template, redirect, url_for, session, flash
from extensions import db
import models
import forms
from . import main


@main.route('/entries', methods=['GET', 'POST'])
def entries():
    if 'user_id' not in session:
        return render_template('nologin.html')

    if 'admin' not in session.get('roles', []):
        flash('Access denied', 'danger')
        return render_template('nologin.html')

    form = forms.AddEntryForm()

    competitions = (
        models.Competitions.query
        .order_by(models.Competitions.competition_date.desc())
        .all()
    )
    gymnasts = (
        models.Gymnasts.query
        .join(models.Clubs)
        .order_by(models.Gymnasts.name)
        .all()
    )

    # Populate form choices
    form.competition_id.choices = [(0, 'Select Competition...')] + [
        (comp.id, f"{comp.name} - {comp.competition_date}")
        for comp in competitions
    ]

    # Get additional data needed for template
    clubs = models.Clubs.query.order_by(models.Clubs.name).all()

    # Get unique levels
    levels = (
        db.session.query(models.Gymnasts.level)
        .distinct()
        .order_by(models.Gymnasts.level)
        .all()
    )
    levels = [level[0] for level in levels]

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
            models.Entries.id.desc(),  # Most recent entries first
            models.Competitions.competition_date.desc(),
            models.Gymnasts.name
        )
        .all()
    )

    if form.validate_on_submit():
        # Additional validation for competition_id
        if form.competition_id.data == 0:
            flash('Please select a valid competition.', 'error')
            return render_template(
                'entries.html',
                competitions=competitions,
                gymnasts=gymnasts,
                clubs=clubs,
                levels=levels,
                entries=entries,
                form=form
            )

        # Check if competition exists and is open for entries
        selected_competition = models.Competitions.query.get(
            form.competition_id.data
        )
        if not selected_competition:
            flash('Selected competition not found.', 'error')
            return render_template(
                'entries.html',
                competitions=competitions,
                gymnasts=gymnasts,
                clubs=clubs,
                levels=levels,
                entries=entries,
                form=form
            )

        # Check competition status
        if selected_competition.status in ['completed', 'closed']:
            flash(
                f'Cannot add entries to this competition. '
                f'Status: {selected_competition.status}',
                'error'
            )
            return render_template(
                'entries.html',
                competitions=competitions,
                gymnasts=gymnasts,
                clubs=clubs,
                levels=levels,
                entries=entries,
                form=form
            )

        # Find gymnast by exact name (case-insensitive)
        gymnast_name = form.gymnast_name.data.strip()
        if not gymnast_name:
            flash('Please enter a gymnast name.', 'error')
            return render_template(
                'entries.html',
                competitions=competitions,
                gymnasts=gymnasts,
                clubs=clubs,
                levels=levels,
                entries=entries,
                form=form
            )

        gymnast = (
            models.Gymnasts.query
            .filter(
                models.Gymnasts.name.ilike(f"{gymnast_name}")
            )
            .first()
        )

        if not gymnast:
            flash(
                f'No gymnast found with the name "{gymnast_name}". '
                'Please check the spelling or add the gymnast first.',
                'error'
            )
            return render_template(
                'entries.html',
                competitions=competitions,
                gymnasts=gymnasts,
                clubs=clubs,
                levels=levels,
                entries=entries,
                form=form
            )

        # Check if entry already exists
        existing_entry = models.Entries.query.filter_by(
            competition_id=form.competition_id.data,
            gymnast_id=gymnast.id
        ).first()

        if existing_entry:
            flash(
                'This gymnast is already entered in this competition!',
                'warning'
            )
        else:
            new_entry = models.Entries(
                competition_id=form.competition_id.data,
                gymnast_id=gymnast.id
            )
            db.session.add(new_entry)
            db.session.commit()
            flash('Entry added successfully!', 'success')

        return redirect(url_for('main.entries'))

    # Convert gymnasts to JSON-serializable format for JavaScript
    gymnasts_json = [{
        'id': g.id,
        'name': g.name,
        'level': g.level,
        'clubs': {'name': g.clubs.name}
    } for g in gymnasts]

    return render_template(
        'entries.html',
        competitions=competitions,
        gymnasts=gymnasts,
        gymnasts_json=gymnasts_json,
        clubs=clubs,
        levels=levels,
        entries=entries,
        form=form
    )
