from flask import render_template
from app import app
from dotenv import load_dotenv
import os
from argon2 import PasswordHasher
from flask_login import LoginManager

ph = PasswordHasher()
login_manager = LoginManager()
login_manager.init_app(app)

get_hash = 'select Password from ledger_5432.Users where Name="Adam"'

user = os.getenv('DBUSER')
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', name=user)
@app.route('/db_test')
def conn_test():
    conn = mysql.connection
    cur = conn.cursor()
    hash = cur.execute(get_hash)
    output = cur.fetchall()
    pass1 = "Afni2020s!!"
    try:
        if ph.verify(output[0][0], pass1):
            return "true"
    except:
            return "false"
    #return str(output[0][0])
