"""
Gymnasts management routes.
Handles gymnast and club management.
"""
from flask import render_template, redirect, url_for, session, flash, request
from extensions import db
import models
import forms
from . import main


@main.route('/gymnasts', methods=['GET', 'POST'])
def gymnasts():
    """Manage gymnasts and clubs - admin only access."""
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
