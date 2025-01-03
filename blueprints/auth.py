from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db, bcrypt
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Form validation
        if not email or not password:
            flash('Email and password are required!', 'danger')
            return redirect(url_for('auth.login'))

        # Authenticate the user
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('expenses.index'))
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('auth.signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use another.', 'danger')
            return redirect(url_for('auth.signup'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(username=username, email=email, password=hashed_password)

        # Save the user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
