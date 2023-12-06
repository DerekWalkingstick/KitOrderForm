from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User, Role
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .static.services import password_check
import re

auth = Blueprint('auth', __name__)

# Login
@auth.route('/login', methods=['get', 'post'])
def login():
    # Check if session is still active
    if 'Role' in session:
        return redirect(url_for('views.orders'))
    
    email = None
    
    if request.method == 'POST':
        # Get the email and password from the form
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if the password matches the hashed password for user
            if check_password_hash(user.password, password):
                # Check if user has a role assigned
                if user.role_id == None:
                    flash('User does not have a role assigned, please contact the system admin', category='error')
                else:
                    # Log the user in and start a session
                    login_user(user, remember=True)
                    session.permanent = True
                    # Get the role for the user
                    role = Role.query.filter_by(id=user.role_id).first()
                    # Add the role to the session
                    session['Role'] = role.role
                    return redirect(url_for('views.orders'))
                
        flash('Incorrect credentials, please try again', category='error')

    return render_template("login.jinja", user=current_user, email=email)
    
# Logout
@auth.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('auth.login'))

# Create account
@auth.route('/create-account', methods=['get', 'post'])
def create_account():
    
    email = None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')

        # Get user if one exists
        user = User.query.filter_by(email=email).first()

        # Create the regex for the email address
        email_pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$" 

        # Check password requirements
        requirements = password_check(password)

        # Uesr already exists
        if user:
            flash('User already exists, please login instead', category='error')
        # Email doesn't match regex pattern
        elif re.match(email_pattern, email) == None:
            flash('Invalid email format, please try again', category='error')
        # Password not long enough
        elif (requirements['length_error']):
            flash('Password must be at least 8 characters', category='error')
        # Password doesn't contain a digit
        elif (requirements['digit_error']):
            flash('Password must contain at least one digit', category='error')
        # Password doesn't contain an uppercase letter  
        elif (requirements['uppercase_error']):
            flash('Password must contain at least one uppercase letter', category='error')
        # Password doesn't contain a lowercase letter
        elif (requirements['lowercase_error']):
            flash('Password must contain at least one lowercase letter', category='error')
        # Password doesn't contain a symbol
        elif (requirements['symbol_error']):
            flash('Password must contain at least one symbol', category='error')
        # Passwords don't match
        elif (password != password_confirmation):
            flash('Passwords do not match, please try again', category='error')
        else:
            # Add new user
            new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully', category='success')
            return redirect(url_for('auth.logout'))

    return render_template("create-account.jinja", user=current_user, email=email if email else None)
