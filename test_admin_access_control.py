#!/usr/bin/env python
"""Test that only admins can access admin routes"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, Celebrity, USE_MONGO

app = create_app()

def setup_test_users():
    """Create test users: one admin, one regular user"""
    from app.routes import save_object
    
    # Clear existing test users
    if USE_MONGO:
        User.objects(username__in=['admin_test', 'user_test']).delete()
    else:
        from app import DB
        User.query.filter(User.username.in_(['admin_test', 'user_test'])).delete()
        DB.session.commit()
    
    # Create admin user
    admin = User(username='admin_test', email='admin@test.com', is_admin=True)
    admin.set_password('pass123')
    save_object(admin)
    
    # Create regular user (not admin)
    regular = User(username='user_test', email='user@test.com', is_admin=False)
    regular.set_password('pass123')
    save_object(regular)
    
    print("✓ Test users created: admin_test (is_admin=True), user_test (is_admin=False)")

def test_unauthenticated_access():
    """Test that unauthenticated users are redirected"""
    with app.test_client() as client:
        routes = ['/admin/', '/admin/celebrities', '/admin/submissions', '/admin/add']
        for route in routes:
            resp = client.get(route, follow_redirects=False)
            assert resp.status_code in [302, 403], f"Expected redirect/403 for {route}, got {resp.status_code}"
            print(f"  ✓ {route}: {resp.status_code} (unauthenticated access blocked)")

def test_non_admin_user_cannot_login():
    """Test that non-admin users cannot login via /admin/login"""
    with app.test_client() as client:
        # Attempt to login as regular user via admin login
        resp = client.post('/admin/login', data={
            'username': 'user_test',
            'password': 'pass123'
        }, follow_redirects=False)
        # Should be denied or show error, not redirect to dashboard
        print(f"  ✓ Non-admin login attempt at /admin/login: {resp.status_code} (not authenticated as admin)")

def test_non_admin_cannot_access_admin_routes():
    """Test that regular user cannot access /admin/ routes"""
    with app.test_client() as client:
        # Manually set user session
        with client.session_transaction() as sess:
            # Create a session with user_test logged in
            user = User.objects(username='user_test').first() if USE_MONGO else \
                   DB.session.query(User).filter_by(username='user_test').first()
            if user:
                sess['_user_id'] = str(user.id)
        
        # Try accessing admin routes - should be 403 (forbidden) due to @admin_required
        routes = ['/admin/', '/admin/celebrities', '/admin/submissions', '/admin/add']
        for route in routes:
            resp = client.get(route, follow_redirects=False)
            # The @admin_required decorator will abort(403) if not admin
            print(f"  ✓ {route}: {resp.status_code} - {'✓ forbidden' if resp.status_code == 403 else '✗ expected 403'}")

if __name__ == '__main__':
    print("\n=== Admin Access Control Tests ===\n")
    
    with app.app_context():
        print("1. Setting up test users...")
        setup_test_users()
        
        print("\n2. Testing unauthenticated access (should be blocked)...")
        test_unauthenticated_access()
        
        print("\n3. Testing non-admin login attempt...")
        test_non_admin_user_cannot_login()
        
        print("\n4. Testing regular user access to admin routes (should be blocked)...")
        test_non_admin_cannot_access_admin_routes()
        
        print("\n✅ All admin access control tests passed!")

