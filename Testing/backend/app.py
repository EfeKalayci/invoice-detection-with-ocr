from datetime import datetime
import datetime
from distutils.log import error
import re
from unittest.mock import patch
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import utils 

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Invoice(db.Model):
    invoice_id = db.Column(db.String(19), primary_key=True)
    total_amount = db.Column(db.Float)
    date = db.Column(db.Date)

    def __init__(self, invoice_id, total_amount, date ):
        self.invoice_id = invoice_id 
        self.total_amount = total_amount
        self.date = date


class InvoiceSchema(ma.Schema):
    class Meta:
        fields=("invoice_id","total_amount","date")

invoice_schema = InvoiceSchema()
fields = invoice_schema.Meta.fields
invoices_schema = InvoiceSchema(many=True)


db.create_all()

@app.route('/get', methods=['GET'])
def get_invoices():
    #return jsonify({"Helo":"World"})
    all_invoices = Invoice.query.all()
    results = invoices_schema.dump(all_invoices)
    print(results)
    print(jsonify(results))
    return jsonify(results)




@app.route('/findID/<path>', methods=['GET'])    
def find_ID(path):

    try:
        invoice_id,total_amount,date= utils.findInvoice(path)
        print('id:{0} \n price:{1} \n date:{2}'.format(invoice_id,total_amount,date))
        
    except error:
        print(error)
    return jsonify([{'invoice_ID': invoice_id,'total':total_amount, 'date':date}])

@app.route('/get/<invoice_id>/', methods=['GET'])
def get_by_id(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    return invoice_schema.jsonify(invoice)


@app.route('/update/<invoice_id>/', methods=['PUT'])
def update_invoice(invoice_id):
    invoice = Invoice.query.get(invoice_id)

    invoice.total_amount = request.json['total_amount']
    invoice.date = request.json['date']

    db.session.commit()
    return invoice_schema.jsonify(invoice)


@app.route('/delete/<invoice_id>/', methods=['DELETE'])
def invoice_delete(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    db.session.delete(invoice)
    db.session.commit()

    return invoice_schema.jsonify(invoice)


@app.route('/add', methods=['POST'])
def add_invoice():
    invoice_id = request.json['invoice_id']
    total_amount = request.json['total_amount']
    date = request.json['date']
    invoices = Invoice(invoice_id, total_amount, date)
    db.session.add(invoices)
    db.session.commit()
    return invoice_schema.jsonify(invoices)


if __name__ == "__main__":
    app.run( debug=True)
    