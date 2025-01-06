from flask import Blueprint, render_template, session,  request, redirect, url_for, flash, session
from blueprints.expenses import Expense, fetch_categorized_expenses
from decorators import login_required
from models import User,Group
from werkzeug.security import generate_password_hash
from extensions import db

# Initialize Blueprint
main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def landing_page():
    expenses = Expense.query.limit(10).all()  # Fetch a subset if data is large
    return render_template('landing.html', expenses=expenses)

@main_bp.route('/index')
@login_required
def index():
    user_id = session.get('user_id')  # Get the logged-in user's ID
    
    # Fetch individual expenses categorized by category
    individual_expenses = {}
    individual_expenses = fetch_categorized_expenses(user_id)
    
    # Fetch group expenses
    groups = Group.query.filter(Group.members.any(id=user_id)).all()
    # Pass the data to the template
    
    return render_template(
        'index.html',
        categorized_expenses=individual_expenses,
        groups=groups
    )

@main_bp.route('/account-detail', methods=['GET', 'POST'])
@login_required
def acc_detail():
    user = User.query.get(session['user_id'])  # Get the logged-in user

    if request.method == 'POST':
        # Handle the form submission and update the user details
        email = request.form.get('email')
        password = request.form.get('password')

        if email:
            user.email = email
        
        if password:
            user.password = generate_password_hash(password)

        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('main.acc_detail'))

    # For GET request, render the account detail page
    return render_template('account_details.html', user=user)


@main_bp.route('/create-group', methods=['GET'])
@login_required
def group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        description = request.form.get('description', '')

        # Create a new group
        new_group = Group(name=group_name, description=description, user_id=User.id)
        db.session.add(new_group)
        db.session.commit()

        flash('Group created successfully!', 'success')
        return redirect(url_for('group.list_groups'))

    return render_template('create_group.html')

@main_bp.route('/groups')
@login_required
def groups():
    user_id = session.get('user_id')
    user_groups = Group.query.filter(Group.members.any(id=user_id)).all()
    return render_template('index.html', groups=user_groups)
