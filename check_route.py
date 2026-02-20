import requests

session = requests.Session()

# 1. Login
# Assuming default test user or I need to create one? 
# I'll rely on the existing 'admin@example.com' or similar if I knew it.
# Or better, I can check if the server *code* has the route by simple introspection if I can't login.
# But requests is better to test the running process.

# Let's try to hit the route. If it's 404, it's definitely missing.
# If it's 302 (redirect to login), then the route EXISTs but needs auth.
# If it's 404, it doesn't exist.

try:
    response = session.get('http://127.0.0.1:5000/appointments')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 404:
        print("Route /appointments NOT FOUND (Server likely needs restart)")
    elif response.status_code in [200, 302, 401]:
        print("Route /appointments EXISTS")
    else:
        print(f"Unexpected status: {response.status_code}")
except Exception as e:
    print(f"Connection failed: {e}")
