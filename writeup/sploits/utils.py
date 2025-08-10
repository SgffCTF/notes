import requests



def attack_data(host):
    r = requests.get("http://10.10.10.10/api/client/attack_data")
    return r.json()["notes"][host]
