from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from datetime import timedelta

# Setup the database
db = SQLAlchemy()
DB_NAME = 'database.db'

# Create the web application
def create_app():
    """
    Create the app, register the routes and setup the login manager
    """
    # Setup the app with a secret key and the database path
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key_flask'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=15)

    # Add the database the app
    db.init_app(app)

    # Import views
    from .views import views
    from .auth import auth

    # Register views
    # url_prefix = To reach views inside of the views, you would have to prefix them with this variable. 
    #   To just reach the page from home leave it blank
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Add the models the app
    from .models import User, Role, KitType, Customer

    create_database(app)

    # Create the login manager
    login_manager = LoginManager()

    # Tell it where to find the login view and add it to the app
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Tell the login manager how to find the user
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# Create the databse if it doesn't exist
def create_database(app):
    """
    If the database is not found in the instance folder, create it
    """

    if not path.exists('instance/' + DB_NAME):
        
        # Create all tables and the databse
        with app.app_context():
            db.create_all()

        print ('Created Database!')