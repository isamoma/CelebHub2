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

