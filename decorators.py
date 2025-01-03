from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):  # Check if the user is logged in
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login'))  # Redirect to the login page
        return f(*args, **kwargs)
    return decorated_function
