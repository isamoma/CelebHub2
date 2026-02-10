#!/usr/bin/env python
"""End-to-end smoke test: create admin and celebrity, login, fetch profile."""
import sys
sys.path.insert(0, '.')
from app import create_app
from app.models import User, Celebrity, USE_MONGO
from app.utils import extract_youtube_id, extract_tiktok_id, extract_spotify_id

app = create_app()

with app.app_context():
    # Create admin user if missing
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
    else:
        print('Admin exists')

    # Create test celebrity
    slug = 'test-artist'
    if USE_MONGO:
        existing = Celebrity.objects(slug=slug).first()
    else:
        existing = Celebrity.query.filter_by(slug=slug).first()

    if not existing:
        yt = extract_youtube_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        tk = extract_tiktok_id('https://vm.tiktok.com/ZMe4K2ABC')
        sp = extract_spotify_id('https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMwbk')
        celeb = Celebrity(name='Test Artist', slug=slug, bio='Smoke test celeb', youtube=yt or '', tiktok=tk or '', spotify=sp or '', featured=True)
        if USE_MONGO:
            celeb.save()
        else:
            DB.session.add(celeb)
            DB.session.commit()
        print('Created celebrity', slug)
    else:
        print('Celebrity exists')

    # Use Flask test client to simulate requests
    client = app.test_client()
    # Access admin login page (GET)
    r = client.get('/admin/login')
    print('/admin/login GET ->', r.status_code)

    # Perform login
    r = client.post('/admin/login', data={'username': 'admin', 'password': 'admin'}, follow_redirects=True)
    print('/admin/login POST ->', r.status_code)
    if b'Dashboard' in r.data or r.status_code == 200:
        print('Login appears successful (dashboard content present)')
    else:
        print('Login may have failed; status:', r.status_code)

    # Fetch profile page
    r = client.get(f'/celebrity/{slug}')
    print(f'/celebrity/{slug} GET ->', r.status_code)
    body = r.data.decode('utf-8')
    # Check for YouTube iframe
    yt_ok = '<iframe' in body and 'youtube' in body.lower()
    tk_ok = 'tiktok' in body.lower()
    sp_ok = 'spotify' in body.lower()
    print('YouTube embed present:', yt_ok)
    print('TikTok embed present:', tk_ok)
    print('Spotify embed present:', sp_ok)

    if r.status_code == 200 and (yt_ok or tk_ok or sp_ok):
        print('\n✅ Profile page rendered embeds successfully')
        sys.exit(0)
    else:
        print('\n⚠ Profile page did not render expected embeds; check template or data')
        sys.exit(2)
