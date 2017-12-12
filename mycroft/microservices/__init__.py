__author__ = "jarbas"

import os
import base64
import json
from os import makedirs
from os.path import dirname, join, exists


def gen_api(user="demo_user"):
    k = os.urandom(32)
    k = base64.urlsafe_b64encode(k)
    k = "JARBAS_"+str(k)
    if not exists(join(dirname(__file__), "database")):
        makedirs(join(dirname(__file__), "database"))
    if not exists(join(dirname(__file__), "database", "users.json")):
        users = {}
    else:
        with open(join(dirname(__file__), "database", "users.json"), "r") as f:
            users = json.load(f)
    while k in users.keys():
        k = gen_api(user)
    k = k[:-1]
    users[k] = {"id": user, "last_active": 0, "name": user}
    with open(join(dirname(__file__), "database", "users.json"), "w") as f:
        data = json.dumps(users)
        f.write(data)
    return k

if __name__ == "__main__":
    gen_api("admin")