from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from extensions import db
from models import Users, Gymnasts, AthleteApplications, Clubs
from forms import (RegistorForm, LoginForm, EditGymnastProfileForm,
                   AthleteApplicationForm)
from . import main


def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def generate_unique_username(first_name, last_name, email):
    """Generate a unique username from user details."""
    import re
    
    # Clean names (remove special characters, convert to lowercase)
    clean_first = re.sub(r'[^a-zA-Z]', '', first_name.lower())
    clean_last = re.sub(r'[^a-zA-Z]', '', last_name.lower())
    
    # Try different username formats
    username_options = [
        f"{clean_first}{clean_last}",  # johnsmith
        f"{clean_first}.{clean_last}",  # john.smith
        f"{clean_first}_{clean_last}",  # john_smith
        f"{clean_first[0]}{clean_last}",  # jsmith
    ]
    
    for base_username in username_options:
        if len(base_username) >= 3:  # Ensure minimum length
            # Check if base username is available
            if not Users.query.filter_by(username=base_username).first():
                return base_username
            
            # Try with numbers 1-99
            for i in range(1, 100):
                numbered_username = f"{base_username}{i}"
                query = Users.query.filter_by(username=numbered_username)
                if not query.first():
                    return numbered_username
    
    # Fallback: use email prefix with numbers
    email_prefix = email.split('@')[0].lower()[:10]
    for i in range(1, 1000):
        fallback_username = f"{email_prefix}{i}"
        if not Users.query.filter_by(username=fallback_username).first():
            return fallback_username
    
    # Final fallback (should never happen)
    import uuid
    return f"user_{str(uuid.uuid4())[:8]}"


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistorForm()

    if form.validate_on_submit():
        # Check if email already exists
        existing_email = Users.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash(
                'Email already registered. Please use a different email.',
                'error'
                )
            return render_template('register.html', form=form)

        # Generate unique username automatically
        generated_username = generate_unique_username(
            form.first_name.data,
            form.last_name.data,
            form.email.data
        )

        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        new_user = Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            username=generated_username,
            password=hashed_password,
            role_id=3  # Regular user role
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash(
                'Registration successful! You can now log in.', 'success'
            )
            return redirect(url_for('main.login'))
        except Exception:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Check if user exists by username or email
        user = Users.query.filter(
            (Users.username == form.username.data) |
            (Users.email == form.username.data)
        ).first()

        if user and check_password_hash(user.password, form.password.data):
            # Successful login
            session['user_id'] = user.id
            session['username'] = user.username
            session['first_name'] = user.first_name
            session['role_id'] = user.role_id

            flash(f'Welcome back, {user.first_name}!', 'success')

            # Redirect to next page or home
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.home'))
        else:
            flash(
                'Invalid username/email or password. '
                'Please try again.',
                'error'
            )
    return render_template('login.html', form=form)


@main.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.home'))


@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing account info and linked gymnast profile"""
    current_user = Users.query.get(session['user_id'])

    # Find if user has a linked gymnast profile
    linked_gymnast = None
    if current_user:
        query = Gymnasts.query.filter_by(user_id=current_user.id)
        linked_gymnast = query.first()

    return render_template('dashboard.html',
                           user=current_user,
                           gymnast=linked_gymnast)


@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Allow users to edit their linked gymnast profile"""
    current_user = Users.query.get(session['user_id'])
    query = Gymnasts.query.filter_by(user_id=current_user.id)
    linked_gymnast = query.first()

    if not linked_gymnast:
        flash('No gymnast profile found. Contact admin to link profile.',
              'error')
        return redirect(url_for('main.dashboard'))

    form = EditGymnastProfileForm()

    if form.validate_on_submit():
        # Update gymnast profile with user's input
        
        # Update club
        if form.club_name.data:
            club = Clubs.query.filter_by(name=form.club_name.data).first()
            if not club:
                club = Clubs(name=form.club_name.data)
                db.session.add(club)
                db.session.flush()  # Get the club ID
            linked_gymnast.club_id = club.id
        
        # Update level
        if form.level.data:
            linked_gymnast.level = form.level.data
        
        # Update age
        if form.age.data:
            try:
                linked_gymnast.age = int(form.age.data)
            except ValueError:
                flash('Invalid age format', 'error')
                return render_template('edit_profile.html',
                                       form=form,
                                       gymnast=linked_gymnast)

        linked_gymnast.goals = form.goals.data
        linked_gymnast.achievements = form.achievements.data
        linked_gymnast.injuries = form.injuries.data

        try:
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')

    # Pre-populate form with existing data
    if request.method == 'GET':
        club_name = linked_gymnast.clubs.name if linked_gymnast.clubs else ''
        form.club_name.data = club_name
        
        # Ensure level matches exactly with SelectField choices
        current_level = linked_gymnast.level or ''
        form.level.data = current_level
        
        age_str = str(linked_gymnast.age) if linked_gymnast.age else ''
        form.age.data = age_str
        form.goals.data = linked_gymnast.goals or ''
        form.achievements.data = linked_gymnast.achievements or ''
        form.injuries.data = linked_gymnast.injuries or ''

    return render_template('edit_profile.html',
                           form=form,
                           gymnast=linked_gymnast)


@main.route('/apply/athlete', methods=['GET', 'POST'])
@login_required
def apply_athlete():
    """Apply for athlete profile"""
    current_user = Users.query.get(session['user_id'])
    
    # Prevent admins from applying to be athletes
    if current_user.role_id == 1:
        flash('Admin users do not need to apply for athlete profiles.', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Check if user already has a linked gymnast profile
    existing_gymnast = Gymnasts.query.filter_by(user_id=current_user.id).first()
    if existing_gymnast:
        flash('You already have an athlete profile!', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Check if user already has a pending application
    existing_app = AthleteApplications.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).first()
    if existing_app:
        flash('You already have a pending application!', 'info')
        return redirect(url_for('main.dashboard'))
    
    form = AthleteApplicationForm()
    
    if form.validate_on_submit():
        # Create new application
        application = AthleteApplications(
            user_id=session.get('user_id'),
            club_name=form.club_name.data,
            gymnastics_level=form.gymnastics_level.data,
            years_experience=form.years_experience.data,
            coach_name=form.coach_name.data,
            achievements=form.achievements.data,
            status='pending'
        )
        
        try:
            db.session.add(application)
            db.session.commit()
            flash('✅ Application submitted successfully! Your application is now '
                  'pending review. Check your dashboard for status updates.',
                  'success')
            return redirect(url_for('main.dashboard'))
        except Exception:
            db.session.rollback()
            flash('Error submitting application. Please try again.', 'error')
    
    return render_template('apply_athlete.html', form=form)


@main.route('/admin/applications')
@login_required
def review_applications():
    """Admin page to review athlete applications"""
    current_user = Users.query.get(session['user_id'])
    
    # Check if user is admin (assuming role_id 1 is admin)
    if not current_user or current_user.role_id != 1:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('main.dashboard'))
    
    pending_apps = AthleteApplications.query.filter_by(status='pending').all()
    
    return render_template('admin_applications.html', applications=pending_apps)


@main.route('/admin/approve/<int:app_id>')
@login_required
def approve_application(app_id):
    """Approve an athlete application and create gymnast profile"""
    current_user = Users.query.get(session['user_id'])
    
    # Check if user is admin
    if not current_user or current_user.role_id != 1:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('main.dashboard'))
    
    application = AthleteApplications.query.get_or_404(app_id)
    
    if application.status != 'pending':
        flash('Application already processed!', 'error')
        return redirect(url_for('main.review_applications'))
    
    try:
        # Get or create club by name
        club = Clubs.query.filter_by(name=application.club_name).first()
        if not club:
            club = Clubs(name=application.club_name)
            db.session.add(club)
            db.session.flush()  # Get the ID
        
        # Get user's full name
        user = Users.query.get(application.user_id)
        user_full_name = f"{user.first_name} {user.last_name}".strip()
        
        # Create new gymnast profile
        new_gymnast = Gymnasts(
            name=user_full_name,
            club_id=club.id,
            level=application.gymnastics_level,
            user_id=application.user_id
        )
        
        # Update application status
        application.status = 'approved'
        application.reviewed_at = db.func.current_timestamp()
        
        db.session.add(new_gymnast)
        db.session.commit()
        
        flash(f'Application approved! {user_full_name} is now registered as '
              'an athlete.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error approving application. Please try again.', 'error')
    
    return redirect(url_for('main.review_applications'))


@main.route('/admin/reject/<int:app_id>')
@login_required
def reject_application(app_id):
    """Reject an athlete application"""
    current_user = Users.query.get(session['user_id'])
    
    # Check if user is admin
    if not current_user or current_user.role_id != 1:
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('main.dashboard'))
    
    application = AthleteApplications.query.get_or_404(app_id)
    
    if application.status != 'pending':
        flash('Application already processed!', 'error')
        return redirect(url_for('main.review_applications'))
    
    try:
        application.status = 'rejected'
        application.reviewed_at = db.func.current_timestamp()
        db.session.commit()
        
        user = Users.query.get(application.user_id)
        user_name = f"{user.first_name} {user.last_name}".strip()
        flash(f'Application for {user_name} has been rejected.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error rejecting application. Please try again.', 'error')
    
    return redirect(url_for('main.review_applications'))


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('main.login'))
        
        current_user = Users.query.get(session['user_id'])
        if not current_user or current_user.role_id != 1:  # Admin role ID is 1
            flash('Admin access required.', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


@main.route('/admin/users')
@admin_required
def manage_users():
    """Admin page to manage user roles"""
    from models import Roles
    
    # Get all users with their role information
    users = db.session.query(Users, Roles).join(Roles, Users.role_id == Roles.id).all()
    
    # Get all available roles
    all_roles = Roles.query.all()
    
    return render_template('admin_users.html', 
                         users=users, 
                         roles=all_roles)


@main.route('/admin/users/<int:user_id>/promote/<int:role_id>', methods=['POST'])
@admin_required
def promote_user(user_id, role_id):
    """Promote user to a specific role"""
    from models import Roles
    
    user = Users.query.get_or_404(user_id)
    role = Roles.query.get_or_404(role_id)
    
    # Don't allow changing the admin's role
    if user.role_id == 1 and session['user_id'] == user.id:
        flash('Cannot change your own admin role.', 'error')
        return redirect(url_for('main.manage_users'))
    
    try:
        old_role = Roles.query.get(user.role_id)
        user.role_id = role_id
        db.session.commit()
        
        flash(f'{user.first_name} {user.last_name} promoted from {old_role.name} to {role.name}.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error updating user role. Please try again.', 'error')
    
    return redirect(url_for('main.manage_users'))
