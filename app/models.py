from flask import jsonify
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = "Users"
    UserID = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    Email = db.Column(db.String(100), unique=True)
    Password = db.Column(db.String(250))
    Name = db.Column(db.String(100))
    DateJoined = db.Column(db.Date)

    def get_id(self):
           return (self.UserID)
    def get_user(self):
           return({'UserID': self.UserID, 'Email': self.Email, 'Name': self.Name, 'DateJoined': self.DateJoined})


class Ledgers(db.Model):
    __tablename__ = "Ledgers"
    LedgerID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey(User.UserID))
    StartingBalance = db.Column(db.Numeric(10,2))


class Categories(db.Model):
    __tablename__ = "Categories"
    CategoryID = db.Column(db.Integer, primary_key=True)
    CategoryName = db.Column(db.String(100))


class TransactionTypes(db.Model):
    __tablename__ = "TransactionTypes"
    TypeID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))

class Transactions(db.Model):
    __tablename__ = "Transactions"
    TransactionID = db.Column(db.Integer, primary_key=True)
    LedgerID = db.Column(db.Integer, db.ForeignKey(Ledgers.LedgerID))
    TypeID = db.Column(db.Integer, db.ForeignKey(TransactionTypes.TypeID))
    Amount = db.Column(db.Numeric(10,2))
    Description = db.Column(db.String(100))
    Date = db.Column(db.Date)
    DateAdded = db.Column(db.Date)
    CategoryID = db.Column(db.Integer, db.ForeignKey(Categories.CategoryID))
    Cleared = db.Column(db.Integer)
