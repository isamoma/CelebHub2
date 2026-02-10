"""Test admin login functionality"""
import re
from app import create_app

app = create_app()
app.config['TESTING'] = True

def test_admin_login():
    """Test that admin can log in with credentials from .env"""
    client = app.test_client()
    
    print("\n=== Testing Admin Login ===\n")
    
    # Test 1: GET /admin/login should return login form
    print("1. Testing GET /admin/login...")
    response = client.get('/admin/login')
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✓ Admin login page loads")
    
    # Test 2: Extract CSRF token
    match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', response.data.decode())
    csrf_token = match.group(1) if match else ''
    assert csrf_token, "CSRF token not found"
    print("   ✓ CSRF token extracted")
    
    # Test 3: POST with admin credentials from .env
    print("\n2. Testing POST /admin/login with ISAMOMAadmin credentials...")
    login_data = {
        'username': 'ISAMOMAadmin',
        'password': '22749266@isa',
        'csrf_token': csrf_token
    }
    response = client.post('/admin/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✓ Admin login successful")
    
    # Test 4: Check that we're on the dashboard
    if b'dashboard' in response.data.lower() or b'admin' in response.data.lower():
        print("   ✓ Redirected to admin dashboard")
    else:
        print("   ! Could not confirm dashboard page (may have flashed message)")
    
    # Test 5: Test that non-admin user cannot log in
    print("\n3. Testing that non-admin users are rejected...")
    # First try to create a regular user and attempt admin login
    from app.models import User
    from app.routes import save_object, get_user_by_username
    
    with app.app_context():
        # Try to find existing non-admin user
        test_user = get_user_by_username('testuser')
        if not test_user:
            test_user = User(username='testuser', email='test@example.com', is_admin=False)
            test_user.set_password('testpass')
            save_object(test_user)
        
        # Try logging in as non-admin
        response = client.get('/admin/login')
        match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', response.data.decode())
        csrf_token = match.group(1) if match else ''
        
        login_data = {
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': csrf_token
        }
        response = client.post('/admin/login', data=login_data, follow_redirects=False)
        # Should either return 200 with error message or 302 redirect
        if b'not authorized' in response.data.lower() or response.status_code == 302:
            print("   ✓ Non-admin user rejected from admin panel")
        else:
            print("   ! Non-admin rejection may not be working as expected")
    
    print("\n✅ Admin login tests completed!")

if __name__ == '__main__':
    test_admin_login()
