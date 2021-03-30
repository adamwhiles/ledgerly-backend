from flask import Blueprint, redirect, request, flash, jsonify
from .models import User
from . import db
from argon2 import PasswordHasher
from flask_login import login_user, logout_user, current_user
from datetime import date

auth = Blueprint('auth', __name__)
ph = PasswordHasher() # argon2id passwordhasher

@auth.route('/api/isLoggedIn', methods=['GET'])
def isLoggedIn():
    return jsonify({'user': current_user.get_id(), 'user_info': current_user.get_user()})

# Route to handle login form submission
@auth.route('/api/login', methods=['POST'])
def login_post():
    # assign login form variables
    print("Login called")
    email = request.json['email']
    password = request.json['password']
    # remember = True if request.form.get('remember') else False
    print(ph.hash(password))
    # query db for user matching on email
    user = User.query.filter_by(Email=email).first()
    if user:
        # if we found a user check for password match
        try:
            # verify password with argon2
            if ph.verify(user.Password, password):
                # if password matches, login the user and send to profile page
                login_user(user)
                return {'login': "success", 'user': current_user.get_id()}
        except Exception as e:
            # if password verification failed, redirect to login with error
            #flash('Please check you login details.')
            return {'login': "failed"}
    else:
        # if user was not matched in db on email, redirect to login with error
        #flash('Please check you login details.')
        return {'login': "failed"}


# Route to handle signup form submission
@auth.route('/signup', methods=['POST'])
def signup_post():
    # assign form variables
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    # query db to see if user exists already with that email
    user = User.query.filter_by(Email=email).first()

    if user:
        # if a user is found to already exist, send back to signup form
        flash('Email address already exists')
        return "send to sign up form"
    # create new user and add to database
    new_user = User(Email=email, Name=name, Password=ph.hash(password), DateJoined=date.today())
    db.session.add(new_user)
    db.session.commit()

    # upon successful signup, send to login form
    return "go to login"

# logout route
@auth.route('/api/logout')
def logout():
    logout_user()
    return jsonify({'status': 'success'})
