#!/usr/bin/env python
"""CSRF-aware login, /pay smoke test, and M-Pesa callback simulation."""
import re
import sys
sys.path.insert(0, '.')
from app import create_app
from app.models import Celebrity, User, USE_MONGO

app = create_app()

with app.app_context():
    client = app.test_client()

    # Ensure admin exists
    if USE_MONGO:
        admin = User.objects(username='admin').first()
    else:
        from app import DB
        admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin')
        if USE_MONGO:
            admin.save()
        else:
            DB.session.add(admin)
            DB.session.commit()
        print('Created admin/admin')

    # Create or get celebrity
    slug = 'test-artist'
    celeb = Celebrity.objects(slug=slug).first() if USE_MONGO else Celebrity.query.filter_by(slug=slug).first()
    if not celeb:
        celeb = Celebrity(name='Test Artist', slug=slug, bio='Smoke test', youtube='dQw4w9WgXcQ', tiktok='https://vm.tiktok.com/ZMe4K2ABC', spotify='https://open.spotify.com/embed/track/0VjIjW4GlUZAMYd2vXMwbk', featured=False)
        if USE_MONGO:
            celeb.save()
        else:
            DB.session.add(celeb)
            DB.session.commit()
        print('Created celeb')

    # GET login page to obtain csrf token
    r = client.get('/admin/login')
    html = r.data.decode('utf-8')
    # Debug: show login HTML snippet for inspection
    print('--- /admin/login HTML snippet ---')
    print(html[:4000])
    print('--- end snippet ---')
    # Extract CSRF token by locating the csrf input and reading its value attribute
    csrf = None
    # Try id first
    id_pos = html.find('id="csrf_token"')
    if id_pos == -1:
        id_pos = html.find("id='csrf_token'")
    if id_pos != -1:
        # find the value= after this position
        val_pos = html.find('value="', id_pos)
        if val_pos == -1:
            val_pos = html.find("value='", id_pos)
        if val_pos != -1:
            start = val_pos + len('value="')
            end = html.find('"', start)
            if end == -1:
                end = html.find("'", start)
            if end != -1:
                csrf = html[start:end]
    # Fallback: regex search anywhere
    if not csrf:
        m = re.search(r'value=["\']([^"\']+)["\']\s+name=["\']csrf_token["\']', html)
        if m:
            csrf = m.group(1)
    if not csrf:
        print('✗ Could not find csrf token on login page')
        sys.exit(2)
    print('CSRF token obtained')

    # POST login with csrf token
    r = client.post('/admin/login', data={'username':'admin','password':'admin','csrf_token':csrf}, follow_redirects=True)
    print('/admin/login POST ->', r.status_code)
    if r.status_code != 200:
        print('Login failed; status', r.status_code)
        sys.exit(3)
    print('Logged in via test client')

    # Use same csrf token for JSON header
    headers = {'Content-Type':'application/json', 'X-CSRFToken': csrf}

    # Mock external Safaricom requests to avoid real network calls during test
    import requests as _requests
    class MockResp:
        def __init__(self, data):
            self._data = data
        def json(self):
            return self._data

    _orig_get = _requests.get
    _orig_post = _requests.post
    _requests.get = lambda *a, **k: MockResp({'access_token': 'MOCK_TOKEN'})
    _requests.post = lambda *a, **k: MockResp({'ResponseCode': '0', 'ResponseDescription': 'Success'})

    # Call /pay
    import json
    payload = {'phone':'254700000000','amount':500,'celebrity_slug':slug}
    r = client.post('/pay', data=json.dumps(payload), headers=headers)
    # Restore requests
    _requests.get = _orig_get
    _requests.post = _orig_post
    print('/pay ->', r.status_code)
    if r.status_code != 200:
        print('PAY failed', r.data)
        sys.exit(4)
    result = r.get_json()
    payment_ref = result.get('payment_ref')
    print('Payment ref:', payment_ref)

    # Verify celeb status pending
    celeb.reload() if USE_MONGO else None
    if USE_MONGO:
        celeb = Celebrity.objects(slug=slug).first()
    else:
        celeb = Celebrity.query.filter_by(slug=slug).first()
    print('Feature status after /pay:', getattr(celeb, 'feature_status', None))
    assert celeb.feature_status == 'pending'
    assert celeb.feature_payment_id == payment_ref

    # Simulate M-Pesa callback
    callback_json = {
        "Body": {
            "stkCallback": {
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name":"Amount","Value":500},
                        {"Name":"MpesaReceiptNumber","Value":"ABCD1234"},
                        {"Name":"TransactionDate","Value":20260210120000},
                        {"Name":"PhoneNumber","Value":"254700000000"},
                        {"Name":"AccountReference","Value":payment_ref}
                    ]
                }
            }
        }
    }

    r = client.post('/mpesa/callback', json=callback_json, headers={'Content-Type':'application/json','X-CSRFToken':csrf})
    print('/mpesa/callback ->', r.status_code)
    res = r.get_json()
    print('Callback response:', res)

    # Reload celeb and verify featured
    if USE_MONGO:
        celeb.reload()
    else:
        DB.session.refresh(celeb)
    print('Feature status after callback:', celeb.feature_status)
    print('Featured flag:', celeb.featured)
    print('Featured until:', celeb.featured_until)
    if celeb.featured and celeb.feature_status == 'paid':
        print('\n✅ Payment callback processed and celebrity marked featured')
        sys.exit(0)
    else:
        print('\n✗ Callback processing failed')
        sys.exit(5)
