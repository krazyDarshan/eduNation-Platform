from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlsplit
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me')
        
        user = User.query.filter(or_(func.lower(User.username) == username.lower(), func.lower(User.email) == username.lower())).first()
        
        if user and user.is_active and password and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=bool(remember_me))
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            safe_next = next_page and next_page.startswith('/') and not next_page.startswith('//') and '\\' not in next_page and not urlsplit(next_page).netloc
            return redirect(next_page if safe_next else url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        
        # Validation
        if not all([username, email, first_name, last_name, password]):
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        if len(username) > 80 or len(email) > 120 or len(first_name) > 50 or len(last_name) > 50:
            flash('Username, email, or name is too long.', 'danger')
            return render_template('auth/register.html')
        if role not in ('student', 'educator'):
            flash('Choose Student or Educator.', 'danger')
            return render_template('auth/register.html')
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            flash('Enter a valid email address.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter(func.lower(User.username) == username.lower()).first():
            flash('Username already exists', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter(func.lower(User.email) == email.lower()).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Username or email already registered. Please sign in.', 'danger')
            return render_template('auth/register.html')
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))
