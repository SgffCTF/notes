import requests
import string
from random import choice


alphabet = string.ascii_letters + string.digits


def generate_random_string(length: int):
    result = ''
    for _ in range(length):
        result += choice(alphabet)
    return result


def attack_data(host):
    r = requests.get("http://10.10.10.10/api/client/attack_data")
    return r.json()["notes"][host]
