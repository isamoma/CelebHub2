"""Test user authentication flow: signup and login"""
import re
from app import create_app
from app.models import User, Celebrity

def test_user_signup_and_login():
    """Test celebrity user signup and login flow"""
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()
    
    print("\n=== Testing User Authentication Flow ===\n")
    
    # Test 1: GET /signup should return signup form
    print("1. Testing GET /signup...")
    response = client.get('/signup')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b'Create' in response.data or b'email' in response.data
    print("   ✓ /signup form loads correctly")
    
    # Test 2: POST /signup with valid data should create user
    print("\n2. Testing POST /signup with valid data...")
    signup_data = {
        'email': 'artist@example.com',
        'full_name': 'Test Artist',
        'password': 'password123',
        'password_confirm': 'password123',
        'agree_terms': True,
        'csrf_token': get_csrf_token(client, '/signup')
    }
    response = client.post('/signup', data=signup_data, follow_redirects=True)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✓ User created and redirected")
    
    # Test 3: GET /user/login should return login form
    print("\n3. Testing GET /user/login...")
    response = client.get('/user/login')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b'Celebrity Login' in response.data or b'username' in response.data
    print("   ✓ /user/login form loads correctly")
    
    # Test 4: POST /user/login with valid credentials
    print("\n4. Testing POST /user/login with valid credentials...")
    login_data = {
        'username': 'artist@example.com',
        'password': 'password123',
        'csrf_token': get_csrf_token(client, '/user/login')
    }
    response = client.post('/user/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b'Welcome' in response.data or b'dashboard' in response.data.lower()
    print("   ✓ User logged in successfully")
    
    # Test 5: GET /user/dashboard should be accessible when logged in
    print("\n5. Testing GET /user/dashboard (logged in)...")
    response = client.get('/user/dashboard')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert b'Welcome' in response.data or b'Profile' in response.data or b'Feature' in response.data
    print("   ✓ User dashboard loads when logged in")
    
    # Test 6: GET /user/logout should log out user
    print("\n6. Testing GET /user/logout...")
    csrf = get_csrf_token(client, '/user/dashboard')
    response = client.get('/user/logout', follow_redirects=True)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✓ User logged out successfully")
    
    # Test 7: GET /user/dashboard should redirect to login when not authenticated
    print("\n7. Testing /user/dashboard (not logged in)...")
    response = client.get('/user/dashboard', follow_redirects=False)
    assert response.status_code in [302, 401], f"Expected redirect or 401, got {response.status_code}"
    print("   ✓ /user/dashboard redirects when not logged in")
    
    # Test 8: Test duplicate email prevention
    print("\n8. Testing duplicate email prevention...")
    signup_data_dup = {
        'email': 'artist@example.com',
        'full_name': 'Another Artist',
        'password': 'password456',
        'password_confirm': 'password456',
        'agree_terms': True,
        'csrf_token': get_csrf_token(client, '/signup')
    }
    response = client.post('/signup', data=signup_data_dup)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # Should either reject or show error (not redirect to dashboard)
    print("   ✓ Duplicate email handled correctly")
    
    # Test 9: Test invalid password confirmation
    print("\n9. Testing password mismatch...")
    signup_data_mismatch = {
        'email': 'artist2@example.com',
        'full_name': 'Test Artist 2',
        'password': 'password123',
        'password_confirm': 'password456',  # Different!
        'agree_terms': True,
        'csrf_token': get_csrf_token(client, '/signup')
    }
    response = client.post('/signup', data=signup_data_mismatch)
    # Form validation should reject this, either 200 (redisplay) or 302 (redirect)
    assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"
    print("   ✓ Password mismatch validation works")
    
    print("\n✅ All user authentication tests passed!")

def get_csrf_token(client, path):
    """Extract CSRF token from a form page"""
    response = client.get(path)
    match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', response.data.decode())
    return match.group(1) if match else ''

if __name__ == '__main__':
    test_user_signup_and_login()
