import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app, DB, ME
from app.models import CelebritySubmission, User, Celebrity
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
        # If we're using SQLite locally, ensure tables exist
        if not os.getenv('MONGO_URI'):
            DB.create_all()

        # Ensure admin exists (create directly to avoid route-side DB errors)
        if os.getenv('MONGO_URI'):
            if not User.objects(username='admin').first():
                u = User(username='admin')
                u.set_password('admin123')
                u.save()
        else:
            if not User.query.filter_by(username='admin').first():
                u = User(username='admin')
                u.set_password('admin123')
                DB.session.add(u)
                DB.session.commit()
        client = app.test_client()

        # Login: fetch login page to get CSRF
        r = client.get('/admin/login')
        page = r.get_data(as_text=True)
        token = extract_csrf(page)
        if not token:
            print('LOGIN PAGE HTML:\n', page)
        assert token, 'No CSRF token on login page'

        login_resp = client.post('/admin/login', data={'username': 'admin', 'password': 'admin123', 'csrf_token': token}, follow_redirects=True)
        assert b'Logged in successfully' in login_resp.data or login_resp.status_code in (200, 302)

        # Create a submission to approve
        if os.getenv('MONGO_URI'):
            sub = CelebritySubmission(name='Test User', email='t@example.com', phone='0712345678', category='Actor', bio='Bio')
            sub.save()
        else:
            sub = CelebritySubmission(name='Test User', email='t@example.com', phone='0712345678', category='Actor', bio='Bio')
            DB.session.add(sub)
            DB.session.commit()

        # Visit view_submission to get CSRF token
        view = client.get(f'/admin/submissions/{sub.id}')
        token = extract_csrf(view.get_data(as_text=True))
        assert token, 'No CSRF token on view_submission page'

        # POST approve
        apr = client.post(f'/admin/submission/{sub.id}/approve', data={'csrf_token': token}, follow_redirects=True)
        assert apr.status_code in (200, 302)

        # Refresh submission from DB
        if os.getenv('MONGO_URI'):
            updated = CelebritySubmission.objects(id=sub.id).first()
        else:
            updated = CelebritySubmission.query.get(sub.id)
        print('After approve, status=', updated.status)

        # Create another submission to reject
        if os.getenv('MONGO_URI'):
            sub2 = CelebritySubmission(name='Reject User', email='r@example.com', phone='0712000000', category='Musician', bio='Bio')
            sub2.save()
        else:
            sub2 = CelebritySubmission(name='Reject User', email='r@example.com', phone='0712000000', category='Musician', bio='Bio')
            DB.session.add(sub2)
            DB.session.commit()

        view2 = client.get(f'/admin/submissions/{sub2.id}')
        token2 = extract_csrf(view2.get_data(as_text=True))
        assert token2, 'No CSRF token on view_submission page (reject)'

        rej = client.post(f'/admin/submission/{sub2.id}/reject', data={'csrf_token': token2}, follow_redirects=True)
        assert rej.status_code in (200, 302)

        if os.getenv('MONGO_URI'):
            updated2 = CelebritySubmission.objects(id=sub2.id).first()
        else:
            updated2 = CelebritySubmission.query.get(sub2.id)
        print('After reject, status=', updated2.status)


if __name__ == '__main__':
    run_test()
