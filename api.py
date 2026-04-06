import requests
from storage import load_tokens
import os

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
def report_lost_item(data, photo_path=None):
    access, _ = load_tokens()
    headers = {'Authorization': f'Bearer {access}'} if access else {}

    if photo_path:
        try:
            with open(photo_path, 'rb') as f:
                ext   = photo_path.split('.')[-1].lower()
                mime  = 'image/png' if ext == 'png' else 'image/jpeg'
                files = {'photo': (photo_path.split('/')[-1], f, mime)}
                r = requests.post(f'{BASE}/lost-items/', data=data, files=files, headers=headers)
        except FileNotFoundError:
            print(f"Photo file not found: {photo_path}")
            r = requests.post(f'{BASE}/lost-items/', data=data, headers=headers)
    else:
        r = requests.post(f'{BASE}/lost-items/', data=data, headers=headers)

    print(f"STATUS: {r.status_code}")
    print(f"RESPONSE: {r.json()}")
    return r.status_code, r.json()

def get_lost_items(keyword='', category='', date=''):
    params = {}
    if keyword:  params['search']    = keyword
    if category: params['category']  = category
    if date:     params['date_lost'] = date
    r = requests.get(f'{BASE}/lost-items/', params=params)
    return r.status_code, r.json()

def get_lost_item(pk):
    r = requests.get(f'{BASE}/lost-items/{pk}/', headers=_headers())
    return r.status_code, r.json()

# ── Found Items ──
def report_found_item(data, photo_path=None):
    access, _ = load_tokens()
    headers = {'Authorization': f'Bearer {access}'} if access else {}

    print(f"PHOTO PATH RECEIVED: '{photo_path}'")
    print(f"PHOTO PATH TYPE: {type(photo_path)}")

    if photo_path:
        print(f"PHOTO EXISTS: {os.path.exists(photo_path)}")

    if photo_path and os.path.exists(photo_path):
        with open(photo_path, 'rb') as f:
            ext   = photo_path.split('.')[-1].lower()
            mime  = 'image/png' if ext == 'png' else 'image/jpeg'
            files = {'photo': (photo_path.split('/')[-1], f, mime)}
            print(f"SENDING FILE: {photo_path.split('/')[-1]} as {mime}")
            r = requests.post(f'{BASE}/found-items/', data=data, files=files, headers=headers)
    else:
        print("NO PHOTO — sending without file")
        r = requests.post(f'{BASE}/found-items/', data=data, headers=headers)

    print(f"STATUS: {r.status_code}")
    print(f"RESPONSE: {r.json()}")
    return r.status_code, r.json()

def get_found_items(keyword='', category='', date=''):
    params = {}
    if keyword:  params['search']    = keyword
    if category: params['category']  = category
    if date:     params['date_found'] = date
    r = requests.get(f'{BASE}/found-items/', params=params)
    return r.status_code, r.json()

def get_found_item(pk):
    r = requests.get(f'{BASE}/found-items/{pk}/', headers=_headers())
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

# ── Claims ──
def submit_claim(item_type, item_id, details):
    """
    item_type: 'lost' or 'found'
    item_id:   the pk of the lost/found item
    details:   string describing proof of ownership/discovery
    """
    payload = {'details': details}
    if item_type == 'lost':
        payload['lost_item'] = item_id
    else:
        payload['found_item'] = item_id
    r = requests.post(f'{BASE}/claims/', json=payload, headers=_headers())
    return r.status_code, r.json()

def get_my_claims():
    r = requests.get(f'{BASE}/claims/', headers=_headers())
    return r.status_code, r.json()