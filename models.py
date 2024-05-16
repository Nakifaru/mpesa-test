from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    MpesaReceiptNumber = db.Column(db.String)
    Amount = db.Column(db.Integer)
    TransactionDate = db.Column(db.Integer)
    PhoneNumber = db.Column(db.Integer)
