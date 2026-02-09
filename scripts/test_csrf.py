import sys, os
# Ensure MONGO_URI is not set to trigger local in-memory MongoDB mode
os.environ.pop('MONGO_URI', None)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app
# Use MongoEngine models (app will use in-memory MongoDB locally)
from app.models import User, CelebritySubmission, Celebrity
import re


def extract_csrf(html: str):
    # Try common patterns for the hidden csrf input (name or id, value can be anywhere)
    patterns = [
        r'name=["\']csrf_token["\']\s+value=["\']([^"\']+)["\']',
        r'id=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']',
        r'value=["\']([^"\']+)["\'][^>]*id=["\']csrf_token["\']',
    ]
    for p in patterns:
        m = re.search(p, html)
        if m:
            return m.group(1)
    return None


def run_test():
    app = create_app()
    with app.app_context():
        # Ensure admin exists
        admin = User.objects(username='admin').first()
        if not admin:
            u = User(username='admin')
            u.set_password('admin123')
            u.save()

        client = app.test_client()

        # Login: fetch login page to get CSRF
        r = client.get('/admin/login')
        page = r.get_data(as_text=True)
        token = extract_csrf(page)
        if not token:
            print('LOGIN PAGE HTML:\n', page[:500])
        assert token, 'No CSRF token on login page'

        login_resp = client.post('/admin/login', data={'username': 'admin', 'password': 'admin123', 'csrf_token': token}, follow_redirects=True)
        assert b'Logged in successfully' in login_resp.data or login_resp.status_code in (200, 302), f"Login failed: {login_resp.status_code}"

        # Create a submission to approve
        sub = CelebritySubmission(name='Test User', email='t@example.com', phone='0712345678', category='Actor', bio='Bio')
        sub.save()

        # Visit view_submission to get CSRF token
        view = client.get(f'/admin/submissions/{sub.id}')
        token = extract_csrf(view.get_data(as_text=True))
        if not token:
            print('VIEW SUBMISSION HTML:\n', view.get_data(as_text=True)[:500])
        assert token, 'No CSRF token on view_submission page'

        # POST approve
        apr = client.post(f'/admin/submission/{sub.id}/approve', data={'csrf_token': token}, follow_redirects=True)
        assert apr.status_code in (200, 302), f"Approve failed: {apr.status_code}"

        # Refresh submission from DB
        updated = CelebritySubmission.objects(id=sub.id).first()
        print('✓ After approve, status=', updated.status)
        assert updated.status == 'approved', f"Expected status 'approved', got '{updated.status}'"

        # Create another submission to reject
        sub2 = CelebritySubmission(name='Reject User', email='r@example.com', phone='0712000000', category='Musician', bio='Bio')
        sub2.save()

        view2 = client.get(f'/admin/submissions/{sub2.id}')
        token2 = extract_csrf(view2.get_data(as_text=True))
        assert token2, 'No CSRF token on view_submission page (reject)'

        rej = client.post(f'/admin/submission/{sub2.id}/reject', data={'csrf_token': token2}, follow_redirects=True)
        assert rej.status_code in (200, 302), f"Reject failed: {rej.status_code}"

        updated2 = CelebritySubmission.objects(id=sub2.id).first()
        print('✓ After reject, status=', updated2.status)
        assert updated2.status == 'rejected', f"Expected status 'rejected', got '{updated2.status}'"

        print('\n✅ All CSRF tests passed!')


if __name__ == '__main__':
    run_test()

