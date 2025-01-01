from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db  # Import db here

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
    app.config['SECRET_KEY'] = 'your_secret_key'
    db.init_app(app)  # Initialize the database with the app

    # Import models here to avoid circular imports
    from models import Expense
    with app.app_context():
        db.create_all()  # Ensure tables are created

    # Define routes
    @app.route('/')
    def index():
        expenses = Expense.query.all()
        return render_template('index.html', expenses=expenses)

    @app.route('/add', methods=['GET', 'POST'])
    def add_expense():
        if request.method == 'POST':
            category = request.form['category']
            amount = float(request.form['amount'])
            description = request.form.get('description', '')

            new_expense = Expense(category=category, amount=amount, description=description)
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('index'))

        return render_template('add_expense.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
