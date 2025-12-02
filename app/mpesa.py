import os
import base64
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify

mpesa_bp = Blueprint('mpesa', __name__)

# Load credentials from .env
CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
PASSKEY = os.getenv("MPESA_PASSKEY")
SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")  # Sandbox default
CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")

# Generate token
def generate_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return r.json().get("access_token")


# ------------------------- STK PUSH -------------------------
@mpesa_bp.route("/pay", methods=["POST"])
def stk_push():
    data = request.json
    phone = data.get("phone")
    amount = data.get("amount", 1)

    access_token = generate_token()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "CelebHub Payment",
        "TransactionDesc": "Featured Profile Payment"
    }

    r = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )

    return jsonify(r.json())


# ---------------------- CALLBACK -------------------------
@mpesa_bp.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    data = request.get_json()
    print("MPESA CALLBACK RECEIVED:", data)

    return jsonify({
        "ResultCode": 0,
        "ResultDesc": "Callback received successfully"
    })
