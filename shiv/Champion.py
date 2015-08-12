import json

with open('data/champion.json') as c:
    heroes = json.load(c)['data']


def Id(id):
    for h in heroes.values():
        if h['key'] == id:
            return h
