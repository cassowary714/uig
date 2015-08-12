import json

with open('data/item.json') as c:
    items = json.load(c)['data']


def Id(id):
    id = str(id)
    if id in items:
        return items[id]
    else:
        return None


def Consumable(id):
    i = Id(id)
    if i is None:
        return False
    if 'consumed' in i and i['consumed'] == True:
        return True
    else:
        return False


def Basic(id):
    i = Id(id)
    if i is None:
        return False
    if 'depth' not in i:
        return True
    elif i['depth'] < 3:
        return True
    return False
