import os
import dataset
import requests
import Constants
import requests_cache
from rq import Worker, Queue, Connection
from time import sleep

db = dataset.connect(Constants.DSN)


def get_match(region, sumid, match, hero):
    requests_cache.install_cache('matches.cache', backend='sqlite', expire_after=86400)
    url = 'https://{region}.api.pvp.net/api/lol/{region}/v2.2/match/{matchid}'.format(region=region, matchid=match)
    r = requests.get(url, params={'api_key': Constants.KEY, 'includeTimeline': 'true'})
    if r.status_code == 200:
        return r.json()
    else:
        return None


# hold every memory as you go
# and every road you take
# will always lead you home
def get_user_matches(matchlist, region, sumid, hero):
    for match in matchlist['matches']:
        print('Working on {0!s}'.format(match['matchId']))
        process_match_timeline(sumid, get_match(region, sumid, match['matchId'], match['champion']))
        # sleep(2)
    return True


# rpocs
def process_match_timeline(sumid, m):
    if m is None:
        return False
    m['timeline']['frames'].pop(0)
    winState, championId, target = None, None, None

    for identity in m['participantIdentities']:
        if identity['player']['summonerId'] == sumid:
            target = identity['participantId']
            break
    for participant in m['participants']:
        if participant['participantId'] == target:
            championId = participant['championId']
            winState = bool(participant['stats']['winner'])
            break

    print('Got participant {0!s} for match {1!s}'.format(target, m['matchId']))

    for frame in m['timeline']['frames']:
        for event in frame['events']:
            if event['eventType'] == 'ITEM_PURCHASED' and event['participantId'] == target:
                event['region'] = m['region'].lower()
                event['summonerId'] = int(sumid)
                event['matchId'] = m['matchId']
                event['win'] = bool(winState)
                event['championId'] = int(championId)
                event.pop('participantId', None)
                event.pop('eventType', None)
                table = db['events']
                table.upsert(event, ['region', 'matchId', 'summonerId', 'timestamp'])



if __name__ == '__main__':
    # dyrus, rumble
    test = get_match('na', 5908, 1907333545, 68)
    process_match_timeline(5908, test)
