from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import Expense, User
from extensions import db
from decorators import login_required
from collections import defaultdict
from sqlalchemy import func
import matplotlib.pyplot as plt
import io
import base64

# Initialize Blueprint
expenses_bp = Blueprint('expenses', __name__, template_folder='templates')

def fetch_categorized_expenses(user_id):
    """Utility function to fetch and organize expenses by category for a specific user."""
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    categorized_expenses = defaultdict(list)
    for expense in expenses:
        categorized_expenses[expense.category].append(expense)
    return categorized_expenses

def generate_category_pie_chart(category_breakdown):
    """Generates a pie chart for category-wise spending."""
    labels = [item[0] for item in category_breakdown]
    values = [item[1] for item in category_breakdown]

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Category-wise Spending')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    return f"data:image/png;base64,{graph_url}"

@expenses_bp.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        try:
            category = request.form['category']
            amount = float(request.form['amount'])
            description = request.form.get('description', '')
            user_id = session.get('user_id')  # Get the logged-in user's ID
            
            new_expense = Expense(category=category, amount=amount, description=description, user_id=user_id)
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('expenses.index'))

    return render_template('add_expense.html')

@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_expense(id):
    try:
        user_id = session.get('user_id')  # Get the logged-in user's ID
        expense = Expense.query.filter_by(id=id, user_id=user_id).first_or_404()  # Check user ownership
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", 'danger')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    user_id = session.get('user_id')  # Get the logged-in user's ID
    expense = Expense.query.filter_by(id=id, user_id=user_id).first_or_404()  # Check user ownership

    if request.method == 'POST':
        try:
            expense.category = request.form['category']
            expense.amount = float(request.form['amount'])
            expense.description = request.form['description']
            db.session.commit()
            flash('Expense updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('expenses.index'))

    return render_template('edit_expense.html', expense=expense)

@expenses_bp.route('/spending')
@login_required
def spending_report():
    user_id = session.get('user_id')  # Get the logged-in user's ID

    # Total spending
    total_spending = db.session.query(func.sum(Expense.amount)).filter_by(user_id=user_id).scalar() or 0

    # Category-wise breakdown
    category_breakdown = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter_by(user_id=user_id)
        .group_by(Expense.category)
        .all()
    )

    # Generate category graph
    category_graph = generate_category_pie_chart(category_breakdown)

    return render_template(
        'spending_report.html',
        total_spending=total_spending,
        category_breakdown=category_breakdown,
        category_graph=category_graph,
    )
