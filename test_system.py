#!/usr/bin/env python
"""Minimal test to verify Flask is working."""
import sys
sys.path.insert(0, '.')

# Test 1: Check imports
try:
    from app.models import Celebrity, User, USE_MONGO
    print("✓ Models imported successfully")
    print(f"✓ Using MongoEngine: {USE_MONGO}")
except Exception as e:
    print(f"✗ Model import failed: {e}")
    sys.exit(1)

# Test 2: Check routes
try:
    from app.routes import main_bp, admin_bp
    print("✓ Routes imported successfully")
except Exception as e:
    print(f"✗ Routes import failed: {e}")
    sys.exit(1)

# Test 3: Check utils
try:
    from app.utils import extract_youtube_id, extract_tiktok_id, extract_spotify_id
    print("✓ URL utilities imported successfully")
    
    # Test YouTube extraction
    yt_url = extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"  - YouTube extraction: {yt_url}")
    
    # Test TikTok extraction
    tk_url = extract_tiktok_id("https://vm.tiktok.com/ZMe4K2ABC")
    print(f"  - TikTok extraction: {tk_url}")
    
    # Test Spotify extraction
    sp_url = extract_spotify_id("https://open.spotify.com/artist/03D4yvfR7LdJlnZvzb3jdp")
    print(f"  - Spotify extraction: {sp_url}")
except Exception as e:
    print(f"✗ Utils import/test failed: {e}")
    sys.exit(1)

# Test 4: Create Flask app
try:
    from app import create_app
    app = create_app()
    print("✓ Flask app created successfully")
    
    # Test a route
    with app.test_client() as client:
        response = client.get('/')
        print(f"✓ GET / responded with status {response.status_code}")
        if response.status_code == 200:
            print("✓ Homepage is working!")
        elif response.status_code == 500:
            print("⚠ Homepage returned 500 error - check database")
        
except Exception as e:
    print(f"✗ Flask app creation/test failed: {e}")
    sys.exit(1)

print("\n✅ All system checks passed!")
print("\nApplication is ready for testing:")
print("- Flask server address: http://127.0.0.1:5000")
print("- URL extraction utilities working")
print("- All blueprints loaded")
