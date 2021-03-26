from flask import Flask, redirect, url_for, jsonify
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.config['SECRET_KEY'] = os.getenv('SECRET')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DBURI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    #login_manager.login_view = 'login_view'
    login_manager.init_app(app)
    @login_manager.unauthorized_handler
    def unauthorized():
        print("unauth called")
        return jsonify({'status': 'needlogin'})
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .ledger import ledger as ledger_blueprint
    app.register_blueprint(ledger_blueprint)


    return app
