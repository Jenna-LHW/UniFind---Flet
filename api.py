import requests
from storage import load_tokens

BASE = 'http://127.0.0.1:8000/api'

def _headers():
    access, _ = load_tokens()
    return {'Authorization': f'Bearer {access}'} if access else {}

# ── Auth ──
def login(username, password):
    r = requests.post(f'{BASE}/auth/login/', json={'username': username, 'password': password})
    return r.status_code, r.json()

def register(data):
    r = requests.post(f'{BASE}/auth/register/', json=data)
    return r.status_code, r.json()

def get_user():
    r = requests.get(f'{BASE}/auth/user/', headers=_headers())
    return r.status_code, r.json()

def refresh_token(refresh):
    r = requests.post(f'{BASE}/auth/refresh/', json={'refresh': refresh})
    return r.status_code, r.json()

# ── Lost Items ──
def get_lost_items(keyword='', category='', date=''):
    params = {}
    if keyword:  params['search']   = keyword
    if category: params['category'] = category
    if date:     params['date_lost'] = date
    r = requests.get(f'{BASE}/lost-items/', params=params)
    return r.status_code, r.json()

def report_lost_item(data, files=None):
    r = requests.post(f'{BASE}/lost-items/', data=data, files=files, headers=_headers())
    return r.status_code, r.json()

# ── Found Items ──
def get_found_items(keyword='', category='', date=''):
    params = {}
    if keyword:  params['search']    = keyword
    if category: params['category']  = category
    if date:     params['date_found'] = date
    r = requests.get(f'{BASE}/found-items/', params=params)
    return r.status_code, r.json()

def report_found_item(data, files=None):
    r = requests.post(f'{BASE}/found-items/', data=data, files=files, headers=_headers())
    return r.status_code, r.json()

# ── Reviews ──
def get_reviews():
    r = requests.get(f'{BASE}/reviews/')
    return r.status_code, r.json()

def post_review(data):
    r = requests.post(f'{BASE}/reviews/', json=data, headers=_headers())
    return r.status_code, r.json()

# ── Contact ──
def send_contact(data):
    r = requests.post(f'{BASE}/contacts/', json=data)
    return r.status_code, r.json()