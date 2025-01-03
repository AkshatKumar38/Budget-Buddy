from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Expense
from extensions import db

expenses_bp = Blueprint('expenses', __name__, url_prefix='/')

@expenses_bp.route('/')
def landing_page():
    expenses = Expense.query.all()
    return render_template('landing.html', expenses=expenses)

@expenses_bp.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')

        new_expense = Expense(category=category, amount=amount, description=description)
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses.index'))

    return render_template('add_expense.html')
