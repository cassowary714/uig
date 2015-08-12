import json

with open('data/champion.json') as c: 
	heroes = json.load(c)['data']
	list = []
	for h in heroes.values():
		list.append(h['key'])
	print(list)
