import os
import re
import pymongo
from app import create_app

# --- Configuration ---
# Manually paste your URI here for a 1-time check, or let it load from .env
URI = "mongodb+srv://isamoma_db_user:323831442Isa@cluster0.wxg60qw.mongodb.net/"

def run_diagnostic():
    print("=== 1. Testing Connection to Atlas ===")
    try:
        client = pymongo.MongoClient(URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB Connection Successful!")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    print("\n=== 2. Testing Flask CSRF & Session ===")
    app = create_app()
    app.config['TESTING'] = True
    # Ensure this is the SAME URI as above
    app.config['MONGO_URI'] = URI 
    
    with app.test_client() as client:
        # GET the login page
        response = client.get('/admin/login')
        print(f"GET /admin/login Status: {response.status_code}")

        if response.status_code == 500:
            print("❌ Server Error 500: Check your Flask console logs for a Traceback.")
            return

        # Check for CSRF Token in HTML
        html = response.data.decode()
        # Simpler regex to find the token
        csrf_match = re.search(r'name="csrf_token".+?value="([^"]+)"', html)
        
        if csrf_match:
            token = csrf_match.group(1)
            print(f"✅ CSRF Token Found: {token[:15]}...")
        else:
            print("❌ CSRF Token NOT found in the HTML form!")

        # Check for Session Cookie
        # In Flask testing, you check the 'Set-Cookie' header
        if 'Set-Cookie' in response.headers:
            print(f"✅ Session Cookie was set by the server.")
        else:
            print("❌ No Session Cookie found! (CSRF will always fail without this)")

if __name__ == "__main__":
    run_diagnostic()