import simplejson as json


def Output(loadout_names, loadout, summoner):
    # explicit key order
    keys = ['starting', 'consumable', 'early', 'core', 'situational']
    output = {
        'title': '{name!s} Build (via UIG)'.format(name=summoner['name']),
        'type': 'custom',
        'map': 'any',
        'mode': 'any',
        'sortrank': 1,
        'priority': False
    }

    blocks = []
    for key in keys:
        _ = {
            'type': loadout_names[key],
            'items': []
        }
        for item in loadout[key]:
            if key == 'consumable':
                _['items'].append({'id': str(item), 'count': 5})
            else:
                _['items'].append({'id': str(item), 'count': 1})

        blocks.append(_)

    output['blocks'] = blocks
    return json.dumps(output)
