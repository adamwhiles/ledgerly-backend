from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from .models import Ledgers, TransactionTypes, Categories, Transactions, User, TransactionsSchema, UserSchema, TypesSchema, CategoriesSchema, LedgersSchema
from . import db
from flask_login import login_required, current_user
from pprint import pprint
import datetime
#from datetime import date, datetime
import sys
import json
import simplejson

ledger = Blueprint('ledger', __name__)

def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.strftime("%m/%d/%Y")

@ledger.route('/api/getLedger')
@login_required
def getLedger():
    # get ledger and transactions for the current user
    #u_ledger = Ledgers.query.filter_by(UserID=current_user.UserID).first()
    #txs = Transactions.query.filter_by(LedgerID=u_ledger.LedgerID).all()
    txs = db.session.query(Transactions.LedgerID, Transactions.TransactionID, Transactions.Amount, Transactions.Description, Transactions.Date, Ledgers.StartingBalance, Categories.CategoryName, User.UserID)\
            .outerjoin(Ledgers, Transactions.LedgerID == Ledgers.LedgerID)\
            .outerjoin(User, User.UserID == Ledgers.UserID)\
            .outerjoin(Categories, Transactions.CategoryID == Categories.CategoryID)\
            .filter(User.UserID == 1).order_by(Transactions.Date).all()
    cats = db.session.query(Categories).all()
    types = db.session.query(TransactionTypes).all()
    #new_ledger = Ledgers(UserID=5, StartingBalance=10.34)
    #db.session.add(new_ledger)
    #db.session.commit()
    #txs_schema = TransactionsSchema(many=True)
    #output = txs_schema.dump(txs)
    #return jsonify({'transactions' : output})
    return simplejson.dumps({'transactions': txs }, default=convert_timestamp)
    #return render_template('ledger.html', txs=txs, cats=cats, types=types)

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
    return redirect(url_for('ledger.getLedger'))

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
    return redirect(url_for('ledger.getLedger'))

@ledger.route('/api/addEntry', methods=['POST'])
@login_required
def addEntry():

    userid = current_user.get_id()
    eDate = request.form.get('date')
    eDesc = request.form.get('desc')
    eAmount = float(request.form.get('amount'))
    eCategory = int(request.form.get('category'))
    eType = int(request.form.get('type'))
    print(eDate)
    print(eDesc)
    print(eAmount)
    print(eCategory)
    print(eType)
    print("Type of type is: ")
    print(type(eType))
    print(current_user.get_id())
    userLedger = Ledgers.query.filter_by(UserID=userid).first()
    print("got ledger")
    print(userLedger.LedgerID)
    #eDate = datetime.fromisoformat(eDate[0])
    print("Date: " + eDate)
    #datetime.strptime(eDate, '%B %-d, %Y')
    try:
        print("Adding New Entry")
        # Check if the entry is a debit, if so, convert to negative amount
        if eType == 2:
            print("This is a debit")
            eAmount = eAmount * -1
        new_entry = Transactions(LedgerID=userLedger.LedgerID, TypeID=eType, Amount=eAmount, Description=eDesc, Date=datetime.strptime(eDate, '%B %d, %Y'), DateAdded=date.today(), CategoryID=eCategory, Cleared=0)
        db.session.add(new_entry)
        db.session.commit()
        flash('New Entry Added')
        return redirect(url_for('ledger.getLedger'))
    except Exception as e:
        print("Failed to add New Entry")
        print(e)
        flash('Pleasy try your action again.')
        return redirect(url_for('ledger.getLedger'))
