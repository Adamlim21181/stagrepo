from flask import render_template, redirect, url_for, session, flash, request
from extensions import db
import models
import forms
from .login import login_required
from . import main


@main.route('/gymnasts')
@login_required
def gymnasts():
    """View all gymnasts - admin only."""
    # Check if user has admin role (role_id 1 = admin)
    if session.get('role_id') != 1:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.home'))

    # Get all gymnasts with their club information
    gymnasts = models.Gymnasts.query.order_by(models.Gymnasts.name).all()

    return render_template('view_gymnasts.html', gymnasts=gymnasts)


@main.route('/gymnasts/<int:gymnast_id>/delete', methods=['POST'])
@login_required
def delete_gymnast(gymnast_id):
    """Delete a gymnast - requires admin privileges."""
    # Check if user has admin role
    if session.get('role_id') != 1:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.home'))
    
    try:
        gymnast = models.Gymnasts.query.get_or_404(gymnast_id)
        gymnast_name = gymnast.name
        
        db.session.delete(gymnast)
        db.session.commit()
        
        flash(f'Gymnast "{gymnast_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting gymnast: {str(e)}', 'error')
    
    return redirect(url_for('main.gymnasts'))


@main.route('/add_gymnast', methods=['GET', 'POST'])
@login_required
def add_gymnast():
    """Add a new gymnast directly - admin only."""
    # Check admin privileges
    if session.get('role_id') != 1:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.home'))
    
    print(f"DEBUG: Request method is {request.method}")
    
    form = forms.AddGymnast()
    clubs = models.Clubs.query.all()
    print(f"DEBUG: Found {len(clubs)} clubs")
    
    # Check if there are any clubs
    if not clubs:
        flash('No clubs found! You need to create a club first.', 'warning')
        # Create a default club if none exist
        try:
            default_club = models.Clubs(name='Default Gymnastics Club')
            db.session.add(default_club)
            db.session.commit()
            clubs = [default_club]
            flash('Created a default club for you!', 'success')
        except Exception as e:
            flash(f'Error creating default club: {str(e)}', 'error')
            return redirect(url_for('main.manage_users'))
    
    # Populate club choices
    form.club.choices = [(club.id, club.name) for club in clubs]
    print(f"DEBUG: Club choices: {form.club.choices}")
    
    if request.method == 'POST':
        print("DEBUG: POST request received")
        print(f"DEBUG: Form data: {request.form}")
        print(f"DEBUG: Form validates: {form.validate()}")
        if form.errors:
            print(f"DEBUG: Form errors: {form.errors}")
    
    if form.validate_on_submit():
        try:
            # Combine bio and experience into achievements field
            combined_text = []
            if form.experience.data:
                combined_text.append(f"Experience: {form.experience.data}")
            if form.bio.data:
                combined_text.append(f"Bio: {form.bio.data}")
            achievements_text = None
            if combined_text:
                achievements_text = "\n\n".join(combined_text)
            
            new_gymnast = models.Gymnasts(
                name=form.name.data,
                club_id=form.club.data,
                level=form.level.data,
                age=form.age.data if form.age.data else None,
                goals=form.goals.data if form.goals.data else None,
                achievements=achievements_text
            )
            
            db.session.add(new_gymnast)
            db.session.commit()
            
            flash(f'Gymnast "{new_gymnast.name}" added successfully! 🎉',
                  'success')
            return redirect(url_for('main.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding gymnast: {str(e)}', 'error')
    else:
        # Show validation errors for debugging
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
    
    return render_template('add_gymnast.html', form=form, clubs=clubs)


@main.route('/admin/gymnast/<int:gymnast_id>/edit-bio', methods=['GET', 'POST'])
@login_required
def admin_edit_gymnast_bio(gymnast_id):
    """Admin route to edit gymnast bio details."""
    # Check if user has admin role
    if session.get('role_id') != 1:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.home'))
    
    gymnast = models.Gymnasts.query.get_or_404(gymnast_id)
    form = forms.AdminEditGymnastBioForm()
    
    if form.validate_on_submit():
        # Update club
        if form.club_name.data:
            club = models.Clubs.query.filter_by(name=form.club_name.data).first()
            if not club:
                club = models.Clubs(name=form.club_name.data)
                db.session.add(club)
                db.session.flush()  # Get the club ID
            gymnast.club_id = club.id
        
        # Update level
        if form.level.data:
            gymnast.level = form.level.data
        
        # Update age
        if form.age.data:
            try:
                gymnast.age = int(form.age.data)
            except ValueError:
                flash('Invalid age format', 'error')
                return render_template('admin_edit_gymnast_bio.html',
                                       form=form, gymnast=gymnast)
        
        # Update bio fields
        gymnast.goals = form.goals.data
        gymnast.achievements = form.achievements.data
        gymnast.injuries = form.injuries.data
        
        try:
            db.session.commit()
            flash(f'Bio updated successfully for {gymnast.name}!', 'success')
            return redirect(url_for('main.gymnasts'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating bio. Please try again.', 'error')
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        club_name = gymnast.clubs.name if gymnast.clubs else ''
        form.club_name.data = club_name
        form.level.data = gymnast.level or ''
        age_str = str(gymnast.age) if gymnast.age else ''
        form.age.data = age_str
        form.goals.data = gymnast.goals or ''
        form.achievements.data = gymnast.achievements or ''
        form.injuries.data = gymnast.injuries or ''
    
    return render_template('admin_edit_gymnast_bio.html', form=form, gymnast=gymnast)



