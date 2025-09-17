
from flask import render_template, redirect, url_for, session, flash, request
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
        .order_by(models.Gymnasts.name)
        .all()
    )

    # Populate form choices
    form.competition_id.choices = [(0, 'Select Competition...')] + [
        (comp.id, f"{comp.name} - {comp.competition_date}")
        for comp in competitions
    ]
    form.gymnast_id.choices = [(0, 'Select Gymnast...')] + [
        (
            gym.id,
            f"#{gym.id:03d} - {gym.name} - {gym.clubs.name} ({gym.level})"
        )
        for gym in gymnasts
    ]

    if form.validate_on_submit():
        # Check if entry already exists
        existing_entry = models.Entries.query.filter_by(
            competition_id=form.competition_id.data,
            gymnast_id=form.gymnast_id.data
        ).first()

        if existing_entry:
            flash(
                'This gymnast is already entered in this competition!',
                'warning'
            )
        else:
            new_entry = models.Entries(
                competition_id=form.competition_id.data,
                gymnast_id=form.gymnast_id.data
            )
            db.session.add(new_entry)
            db.session.commit()
            flash('Entry added successfully!', 'success')

        return redirect(url_for('main.entries'))

    if request.method == 'POST' and not form.validate_on_submit():
        competition_id = request.form.get('competition_id')

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
        entries=entries,
        form=form
    )
