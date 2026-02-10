from app import create_app
c=create_app()
with c.test_client() as client:
    r=client.get('/admin/login')
    print(r.data.decode('utf-8'))
