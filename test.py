app = Flask(__name__, instance_relative_config=True)
@app.route('/mpesa/token')
def generate_token():
    import requests, os
    from requests.auth import HTTPBasicAuth

    key = os.getenv("MPESA_CONSUMER_KEY")
    secret = os.getenv("MPESA_CONSUMER_SECRET")

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(key, secret))

    return response.json()
