from flask import Flask
from extensions import db, bcrypt
from flask_migrate import Migrate
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent client-side scripts from accessing the cookie
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Mitigate CSRF attacks
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Set session timeout to 30 minutes

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Register Blueprints
    from blueprints.auth import auth_bp
    from blueprints.expenses import expenses_bp
    from blueprints.main import main_bp
    app.register_blueprint(expenses_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
