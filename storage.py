import json, os

TOKEN_FILE = os.path.join(os.path.dirname(__file__), '.token.json')

def save_tokens(access, refresh):
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'access': access, 'refresh': refresh}, f)

def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return None, None
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    return data.get('access'), data.get('refresh')

def clear_tokens():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)