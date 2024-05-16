from flask import Flask, request, jsonify
from flask_mpesa import MpesaAPI
from flask_migrate import Migrate

from models import db, Transaction


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///app.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["API_ENVIRONMENT"] = "sandbox"
app.config["APP_KEY"] = "KaDetUGGhUCIlhHqmmvGfKFDSHXsL4GpvAsbR3s0Z6VjdOS8"
app.config["APP_SECRET"] = "CfUuAoAi3exAyAF0yju9P9zSaAzLAYtIfgHjsMnAVoad5ASGnqqRyDbJGRDtykX8"

migrate = Migrate(app, db)
mpesa_api = MpesaAPI(app)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Welcome to my page!</h1>'


@app.route('/stk')
def simulate_stk_push():
    data = {
        "business_shortcode": "174379",
        "passcode": "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
        "amount": "1",
        "phone_number": "254700622570",
        "reference_code": "Banda",
        "callback_url": "https://38bc-197-139-44-10.ngrok-free.app/callback",
        "description": "Reverse afterwards"
    }
    resp = mpesa_api.MpesaExpress.stk_push(**data)
    return jsonify(resp),200

@app.route('/callback',methods=["GET", "POST"])
def works():
    if request.method == 'POST':
        json_data = request.get_json()
        result_code = json_data["Body"]["stkCallback"]["ResultCode"]
        message = {
            "ResultCode": result_code,
            "ResultDesc": "success",
            "ThirdPartyTransID": "h234k2h4krhk2"
        }

        if result_code == 0:
            amt = json_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
            code = json_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["Value"]
            date = json_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][2]["Value"]
            num = json_data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"]

            transaction = Transaction(Amount=amt, MpesaReceiptNumber=code, TransactionDate=date, PhoneNumber=num)
            db.session.add(transaction)
            db.session.commit()

        print(json_data)
        return jsonify(message),200

@app.route('/c2b')
def c2b():
    reg_data={
        "shortcode": "174379",
        "response_type": "Completed",
        "validation_url": "https://38bc-197-139-44-10.ngrok-free.app/confirmation"
    }
    v = mpesa_api.C2B.register(**reg_data)

    test_data={
        "shortcode": "174379",
        "command_id": "CustomerBuyGoodsOnline",
        "amount": "1",
        "msisdn": "254700622570",
        "bill_ref_number": "account"
    }
    new_v = mpesa_api.C2B.simulate(**test_data)
    return jsonify(new_v), 200

@app.route('/confirmation', methods=["POST"])
def c2b_confirmation():
    json_data = request.get_json()

    code = json_data["TransID"]
    date = json_data["TransTime"]
    num = json_data["MSISDN"]
    amt = json_data["TransAmount"]

    transaction = Transaction(Amount=amt, MpesaReceiptNumber=code, TransactionDate=date, PhoneNumber=num)
    db.session.add(transaction)
    db.session.commit()

    return jsonify(json_data), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)