"""Diagnostic test to see exact CSRF error"""
from app import create_app
import re

app = create_app()
app.config['TESTING'] = True
client = app.test_client()

print("\n=== Admin Login CSRF Diagnostic ===\n")

# Step 1: GET the form
print("1. GET /admin/login...")
response = client.get('/admin/login')
print(f"   Status: {response.status_code}")

# Extract CSRF token from HTML
html = response.data.decode('utf-8')
match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]*)"', html)
if match:
    csrf_token = match.group(1)
    print(f"   ✓ CSRF token found: {csrf_token[:20]}...")
else:
    print("   ✗ CSRF token NOT found in HTML!")
    print("   Form HTML snippet:")
    form_start = html.find('<form')
    if form_start > 0:
        form_end = html.find('</form>', form_start)
        print(html[form_start:form_end+7])

# Step 2: Check cookies
print("\n2. Checking cookies after GET...")
cookies = client.cookie_jar
print(f"   Cookies set: {len(list(cookies))}")
for cookie in cookies:
    print(f"     - {cookie.name}: {cookie.value[:20]}...")

# Step 3: POST with CSRF token
print("\n3. POST /admin/login with credentials...")
if match:
    response = client.post(
        '/admin/login',
        data={
            'username': 'ISAMOMAadmin',
            'password': '22749266@isa',
            'csrf_token': csrf_token
        }
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        # Print error
        if b'csrf' in response.data.lower():
            print("   ✗ CSRF validation failed!")
            # Find error message
            if b'session' in response.data.lower():
                print("   Error: Session token missing or invalid")
        else:
            print("   Checking response for error...")
            resp_text = response.data.decode('utf-8')
            if 'error' in resp_text.lower():
                error_match = re.search(r'<[^>]*>([^<]*(?:error|invalid)[^<]*)<', resp_text, re.I)
                if error_match:
                    print(f"   Error: {error_match.group(1)}")
else:
    print("   Skipped (no CSRF token found)")

print("\n=== End Diagnostic ===\n")
