import sys
from urllib.request import urlopen

BASE = 'http://127.0.0.1:5000'
PAGES = [
    ('Home', '/'),
    ('Signup', '/signup'),
    ('User login', '/user/login'),
    ('Admin login', '/admin/login'),
    ('Sample profile', '/celebrity/test-artist')
]

KEYS = {
    '/': ['Featured Kenyan Celebrities', 'Create account', 'Login'],
    '/signup': ['Create Your Account', 'email', 'Create account'],
    '/user/login': ['Celebrity Login', 'username', 'Login'],
    '/admin/login': ['Admin Login', 'username', 'Login'],
    '/celebrity/test-artist': ['Feature your profile', 'YouTube', 'TikTok', 'Spotify']
}

for name, path in PAGES:
    url = BASE + path
    try:
        res = urlopen(url, timeout=5)
        html = res.read().decode('utf-8', errors='ignore')
        ok = True
        found = []
        for k in KEYS.get(path, []):
            present = k in html
            found.append((k, present))
            if not present:
                ok = False
        print(f"{name}: {url} -> HTTP {res.status} | markers: {found}")
    except Exception as e:
        print(f"{name}: {url} -> ERROR: {e}")

sys.exit(0)
