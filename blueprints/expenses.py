from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Expense
from extensions import db
from decorators import login_required  # Import the decorator
from collections import defaultdict

expenses_bp = Blueprint('expenses', __name__, url_prefix='/')

@expenses_bp.route('/')
def landing_page():
    expenses = Expense.query.all()
    return render_template('landing.html', expenses=expenses)

@expenses_bp.route('/index')
@login_required
def index():
    # Fetch all expenses from the database
    expenses = Expense.query.order_by(Expense.date.desc()).all()

    # Group expenses by category
    categorized_expenses = defaultdict(list)
    for expense in expenses:
        categorized_expenses[expense.category].append(expense)

    return render_template('index.html', categorized_expenses=categorized_expenses)

@expenses_bp.route('/add-expense', methods=['GET', 'POST'])
@login_required
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

@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses.index'))


@expenses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)

    if request.method == 'POST':
        expense.category = request.form['category']
        expense.amount = float(request.form['amount'])
        expense.description = request.form['description']
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses.index'))

    return render_template('edit_expense.html', expense=expense)

