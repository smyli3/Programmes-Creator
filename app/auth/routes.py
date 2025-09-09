from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from app.auth import bp
from ..models import User
from .forms import LoginForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        flash('Invalid email or password', 'error')

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    """User logout."""
    logout_user()
    return redirect(url_for('main.index'))

# Placeholder endpoints to satisfy template links
@bp.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
    """Placeholder for password reset request flow."""
    flash('Password reset is not configured yet.', 'warning')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Placeholder for user registration flow."""
    flash('Registration is currently disabled.', 'warning')
    return redirect(url_for('auth.login'))
