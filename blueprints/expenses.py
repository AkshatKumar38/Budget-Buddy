from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Expense
from extensions import db
from decorators import login_required  # Import the decorator
from collections import defaultdict
from sqlalchemy import func
import matplotlib.pyplot as plt
import io
import base64

# Initialize Blueprint
expenses_bp = Blueprint('expenses', __name__, template_folder='templates')

@expenses_bp.route('/')
def landing_page():
    expenses = Expense.query.all()
    return render_template('landing.html', expenses=expenses)

@expenses_bp.route('/index')
@login_required
def index():
    # Fetch and organize expenses by category
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    categorized_expenses = defaultdict(list)
    for expense in expenses:
        categorized_expenses[expense.category].append(expense)

    return render_template('index.html', categorized_expenses=categorized_expenses)

@expenses_bp.route('/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        # Extract form data
        category = request.form['category']
        amount = float(request.form['amount'])
        description = request.form.get('description', '')

        # Add new expense to the database
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
        # Update expense data
        expense.category = request.form['category']
        expense.amount = float(request.form['amount'])
        expense.description = request.form['description']
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses.index'))

    return render_template('edit_expense.html', expense=expense)

@expenses_bp.route('/spending')
def spending_report():
    # Total spending
    total_spending = db.session.query(func.sum(Expense.amount)).scalar() or 0
    # Category-wise breakdown
    category_breakdown = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .group_by(Expense.category)
        .all()
    )

    # Monthly and Weekly spending
    monthly_spending = (
        db.session.query(func.strftime('%Y-%m', Expense.date), func.sum(Expense.amount))
        .group_by(func.strftime('%Y-%m', Expense.date))
        .all()
    )

    weekly_spending = (
        db.session.query(func.strftime('%Y-%W', Expense.date), func.sum(Expense.amount))
        .group_by(func.strftime('%Y-%W', Expense.date))
        .all()
    )
    # Generate category-wise pie chart
    category_graph = generate_category_pie_chart(category_breakdown)

    return render_template(
        'spending_report.html',
        total_spending=total_spending,
        category_breakdown=category_breakdown,
        monthly_spending=monthly_spending,
        weekly_spending=weekly_spending,
        category_graph=category_graph
    )






def generate_category_pie_chart(category_breakdown):
    # Prepare data
    labels = [item[0] for item in category_breakdown]
    values = [item[1] for item in category_breakdown]

    # Plot pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Category-wise Spending')

    # Save to base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    graph_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    
    return f"data:image/png;base64,{graph_url}"