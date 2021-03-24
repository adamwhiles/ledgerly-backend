from flask import Blueprint, flash, request, jsonify
from .models import Ledgers, TransactionTypes, Categories, Transactions, User
from . import db
from flask_login import login_required, current_user
from pprint import pprint
import datetime
import sys
import json
import simplejson

ledger = Blueprint('ledger', __name__)

def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.strftime("%m/%d/%Y")

def getUserLedger():
    txs = db.session.query(Transactions.LedgerID, Transactions.TransactionID, Transactions.Amount, Transactions.Description, Transactions.Date, Ledgers.StartingBalance, Categories.CategoryName, User.UserID)\
            .outerjoin(Ledgers, Transactions.LedgerID == Ledgers.LedgerID)\
            .outerjoin(User, User.UserID == Ledgers.UserID)\
            .outerjoin(Categories, Transactions.CategoryID == Categories.CategoryID)\
            .filter(User.UserID == current_user.UserID).order_by(Transactions.Date).all()
    cats = Categories.query.all()
    types = db.session.query(TransactionTypes).all()
    for t in txs:
        print(type(t))
    typeList = []
    for c in cats:
        typeList.append({'CategoryID': c.CategoryID, 'CategoryName': c.CategoryName})
    return simplejson.dumps({'transactions': txs, 'categories': typeList}, default=convert_timestamp)

@ledger.route('/api/getLedger')
@login_required
def getLedger():
    return getUserLedger()

@ledger.route('/api/deleteEntry/<id>')
@login_required
def deleteEntry(id):
    # check that entry is valid and also belongs to our logged in user_id
    entry = db.session.query(User.UserID, Transactions.TransactionID)\
        .outerjoin(Ledgers, Ledgers.LedgerID == Transactions.LedgerID)\
        .outerjoin(User, Ledgers.UserID == User.UserID).filter(Transactions.TransactionID == id).first()
    if not entry:
        flash('Pleasy try your action again.')
    else:
        if entry.UserID == current_user.UserID:
            e = Transactions.query.filter_by(TransactionID = id).first()
            db.session.delete(e)
            db.session.commit()
            flash('Entry Deleted')
        else:
            flash('Pleasy try your action again.')
    return "go back to ledger"

@ledger.route('/api/editEntry/<id>')
@login_required
def editEntry(id):
    # check that entry is valid and also belongs to our logged in user_id
    entry = db.session.query(User.UserID, Transactions.TransactionID)\
        .outerjoin(Ledgers, Ledgers.LedgerID == Transactions.LedgerID)\
        .outerjoin(User, Ledgers.UserID == User.UserID).filter(Transactions.TransactionID == id).first()
    if not entry:
        flash('Pleasy try your action again.')
    else:
        if entry.UserID == current_user.UserID:
            e = Transactions.query.filter_by(TransactionID = id).first()
            db.session.delete(e)
            db.session.commit()
            flash('Entry Deleted')
        else:
            flash('Pleasy try your action again.')
    return "go back to ledger"

@ledger.route('/api/addEntry', methods=['POST'])
@login_required
def addEntry():
    # Set data to the json object received from
    data = request.get_json()

    # Get the current logged in user
    userid = current_user.get_id()

    # Get the ledger for the current logged in user
    userLedger = Ledgers.query.filter_by(UserID=userid).first()

    # Format date from the json date type
    formatDate = datetime.datetime.strptime(data['Date'], '%Y-%m-%dT%H:%M:%S.%fZ')

    # Add to database
    try:
        # Check if the entry is a debit, if so, convert to negative amount
        if data['Type'] == 2:
            data['Amount'] = data['Amount'] * -1
        # Setup out new entry to be added
        new_entry = Transactions(LedgerID=userLedger.LedgerID, TypeID=data['Type'], Amount=data['Amount'], Description=data['Description'], Date=formatDate, DateAdded=datetime.date.today(), CategoryID=data['Category'], Cleared=0)
        db.session.add(new_entry)
        db.session.commit()
        flash('New Entry Added')
        return getUserLedger()
    except Exception as e:
        print("Failed to add New Entry")
        print(e)
        flash('Pleasy try your action again.')
        return jsonify({'status': "failed"})
