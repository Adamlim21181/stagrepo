from flask import render_template, redirect, url_for, session, flash
import models
import forms
from . import main


@main.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with username and code verification."""
    form = forms.LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        code = form.code.data
        user = models.Users.query.filter_by(username=username).first()

        if user and user.code == code:
            session['user_id'] = user.id
            session['username'] = user.username
            session['roles'] = [user.role.name] if user.role else []
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or code', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html', form=form)


@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))
