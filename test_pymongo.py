import pymongo
from urllib.parse import quote_plus
import sys

# --- CONFIGURATION ---
USER = "your_username"
PASS = "your_password"  # Enter it plainly here; quote_plus will fix it
CLUSTER = "cluster0.xxxx.mongodb.net"
DB_NAME = "test" # Use 'admin' or your specific DB

# 1. URL Encode credentials (prevents errors from @, :, / in passwords)
uri = f"mongodb+srv://{quote_plus(USER)}:{quote_plus(PASS)}@{CLUSTER}/{DB_NAME}?retryWrites=true&w=majority"

def debug_connection():
    print(f"--- Starting MongoDB Debugger ---")
    try:
        # 2. Initialize Client with a short timeout so you don't hang
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # 3. The "Ping" test - This forces the authentication attempt
        print(f"Attempting to ping Cluster...")
        client.admin.command('ping')
        print("✅ SUCCESS: Authentication and Connection verified!")
        
    except pymongo.errors.ConfigurationError as e:
        print(f"❌ CONFIG ERROR: Check your connection string format.\nDetails: {e}")
    except pymongo.errors.OperationFailure as e:
        print(f"❌ AUTH ERROR: The server rejected your credentials.\nDetails: {e}")
        print("\nPossible fixes:\n1. Check Database Access in Atlas for this user.\n2. Ensure the user has 'Read/Write' roles.")
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f"❌ NETWORK ERROR: Could not reach the server.\nDetails: {e}")
        print("\nPossible fix: Check 'Network Access' in Atlas. Is your IP whitelisted?")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}\n{e}")

if __name__ == "__main__":
    debug_connection()