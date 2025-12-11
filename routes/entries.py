from flask import render_template, redirect, url_for, session, flash
from extensions import db
import models
import forms
from . import main


@main.route('/entries', methods=['GET', 'POST'])
def entries():
    if 'user_id' not in session:
        return render_template('nologin.html')

    # Check if user is admin (using role_id check)
    if session.get('role_id') != 1:
        flash('Access denied - Admin privileges required', 'danger')
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
    
    # gymnast choices handled client-side for multi-select; keep data for JSON

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
        try:
            # Additional validation for competition_id
            if form.competition_id.data == 0:
                flash('Please select a valid competition.', 'error')
                return redirect(url_for('main.entries'))

            # Check if competition exists and is open for entries
            selected_competition = models.Competitions.query.get(
                form.competition_id.data
            )
            if not selected_competition:
                flash('Selected competition not found.', 'error')
                return redirect(url_for('main.entries'))

            # Check competition status
            if selected_competition.status in ['completed', 'closed']:
                flash(
                    f'Cannot add entries to this competition. '
                    f'Status: {selected_competition.status}',
                    'error'
                )
                return redirect(url_for('main.entries'))

            # Parse selected gymnasts (comma-separated ids from hidden field)
            ids_raw = (form.gymnast_ids.data or '').strip()
            gymnast_ids = [
                int(x) for x in ids_raw.split(',') if x.strip().isdigit()
            ]

            if not gymnast_ids:
                flash('Please select at least one gymnast.', 'error')
                return redirect(url_for('main.entries'))

            gymnast_ids = list(dict.fromkeys(gymnast_ids))

            added, duplicates, missing = [], [], []

            for gid in gymnast_ids:
                gymnast = models.Gymnasts.query.get(gid)
                if not gymnast:
                    missing.append(str(gid))
                    continue

                existing_entry = models.Entries.query.filter_by(
                    competition_id=form.competition_id.data,
                    gymnast_id=gid
                ).first()

                if existing_entry:
                    duplicates.append(gymnast.name)
                    continue

                new_entry = models.Entries(
                    competition_id=form.competition_id.data,
                    gymnast_id=gid
                )
                db.session.add(new_entry)
                added.append(gymnast.name)

            if added:
                db.session.commit()
                flash(
                    f"Added {len(added)} gymnast(s) to "
                    f"{selected_competition.name}: " + ', '.join(added),
                    'success'
                )

            if duplicates:
                flash(
                    f"Already entered: {', '.join(duplicates)}",
                    'warning'
                )

            if missing:
                flash(
                    f"Some gymnasts were not found: {', '.join(missing)}",
                    'error'
                )

        except Exception as e:
            db.session.rollback()
            flash(
                f'An error occurred while processing your request: {str(e)}',
                'error'
            )
        
        return redirect(url_for('main.entries'))

    # Convert gymnasts to JSON for search functionality
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


@main.route('/entries/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """Delete an entry."""
    if 'user_id' not in session:
        return render_template('nologin.html')

    # Check if user is admin
    if session.get('role_id') != 1:
        flash('Access denied - Admin privileges required', 'danger')
        return redirect(url_for('main.entries'))

    entry = models.Entries.query.get_or_404(entry_id)
    
    # Delete related scores first
    scores = models.Scores.query.filter_by(entry_id=entry_id).all()
    for score in scores:
        db.session.delete(score)
    
    # Store info for flash message
    gymnast_name = entry.gymnasts.name
    competition_name = entry.competitions.name
    
    # Delete the entry
    db.session.delete(entry)
    db.session.commit()
    
    flash(f'Entry for {gymnast_name} in {competition_name} has been deleted.',
          'success')
    return redirect(url_for('main.entries'))
