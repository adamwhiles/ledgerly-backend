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

# Helper function for returning date objects from python to React
def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.strftime("%m/%d/%Y")

@login_required
def getUserLedger():
    # Get all of the transactions that belong to the logged in user
    txs = db.session.query(Transactions.LedgerID, Transactions.TransactionID, Transactions.Amount, Transactions.Description, Transactions.Date, Ledgers.StartingBalance, Categories.CategoryID, Categories.CategoryName, User.UserID)\
            .outerjoin(Ledgers, Transactions.LedgerID == Ledgers.LedgerID)\
            .outerjoin(User, User.UserID == Ledgers.UserID)\
            .outerjoin(Categories, Transactions.CategoryID == Categories.CategoryID)\
            .filter(User.UserID == current_user.UserID).order_by(Transactions.Date).order_by(Transactions.TypeID).order_by(Transactions.TransactionID).all()
    # Get the list of categories in the database, so these can be loaded into the form field in React
    cats = Categories.query.all()
    # Setup empty list and append json objects for each category so we can send to React
    catList = []
    for c in cats:
        catList.append({'CategoryID': c.CategoryID, 'CategoryName': c.CategoryName})
    return simplejson.dumps({'transactions': txs, 'categories': catList}, default=convert_timestamp)

@ledger.route('/api/getLedger')
@login_required
def getLedger():
    return getUserLedger()

@ledger.route('/api/deleteEntry', methods=['POST'])
@login_required
def deleteEntry():
    # Set data to the json object received from
    data = request.get_json()

    # Set id to our entry id from React
    id = data['entryID']

    # Get the current logged in user
    userid = current_user.get_id()

    # check that entry is valid and also belongs to our logged in user_id
    entry = db.session.query(User.UserID, Transactions.TransactionID)\
        .outerjoin(Ledgers, Ledgers.LedgerID == Transactions.LedgerID)\
        .outerjoin(User, Ledgers.UserID == User.UserID).filter(Transactions.TransactionID == id).first()
    if not entry:
        print("failed, entry invalid")
        return getUserLedger()
    else:
        # Verify that the logged in user is the owner of the entry
        if entry.UserID == current_user.UserID:
            # Get the transaction that needs to be deleted from the database
            e = Transactions.query.filter_by(TransactionID = id).first()
            # delete the entry and commit changes to the database
            db.session.delete(e)
            db.session.commit()
            print("success")
            return getUserLedger()
        else:
            print("failed")
            return getUserLedger()

@ledger.route('/api/editEntry', methods=['POST'])
@login_required
def editEntry():
    # Set data to the json object received from
    data = request.get_json()

    # Set id to our entry id from React
    id = data['EntryID']

    # Get the current logged in user
    userid = current_user.get_id()

    # check that entry is valid and also belongs to our logged in user_id
    entry = db.session.query(User.UserID, Transactions.TransactionID)\
        .outerjoin(Ledgers, Ledgers.LedgerID == Transactions.LedgerID)\
        .outerjoin(User, Ledgers.UserID == User.UserID).filter(Transactions.TransactionID == id).first()
    if not entry:
        print("No Match")
        flash('Pleasy try your action again.')
    else:
        # Verify that the logged in user is the owner of the entry
        if entry.UserID == current_user.UserID:
            # Format date from the json date type
            formatDate = datetime.datetime.strptime(data['Date'], '%Y-%m-%dT%H:%M:%S.%fZ')

            # Check if this is a debit, if so convert to negative
            if data['Type'] == 2:
                data['Amount'] = data['Amount'] * -1
            # Get the transaction that needs to be updated from the database
            e = Transactions.query.filter_by(TransactionID = id).first()
            # Set items to the updated values
            e.Date = formatDate
            e.Amount = data['Amount']
            e.Description = data['Description']
            e.CategoryID = data['Category']
            e.TypeID = data['Type']
            # Commit changes to database
            db.session.commit()
            print("Entry Modified")
        else:
            print("Edit Failed")
            flash('Pleasy try your action again.')
    return getUserLedger()

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
