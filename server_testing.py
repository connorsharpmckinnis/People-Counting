import requests

SERVER_URL = "http://10.9.81.124:8000"


def server_is_reachable():
    try:
        r = requests.get(f"{SERVER_URL}/ping", timeout=1)
        return r.status_code == 200
    except Exception:
        return False
    
    
    
    
print(server_is_reachable())