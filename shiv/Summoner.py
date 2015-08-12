import requests
import requests_cache
import Constants


def GetSummonerByName(region, ign):
    requests_cache.install_cache('summoner.names.cache', backend='sqlite', expire_after=480)
    url = 'https://{region}.api.pvp.net/api/lol/{region}/v1.4/summoner/by-name/{ign}'.format(region=region, ign=ign)
    r = requests.get(url, params={'api_key': Constants.KEY})
    if r.status_code == 200:
        return next(iter(r.json().values()))
    else:
        return None


def GetSummonerById(region, id):
    requests_cache.install_cache('summoner.id.cache', backend='sqlite', expire_after=480)
    url = 'https://{region}.api.pvp.net/api/lol/{region}/v1.4/summoner/{id}'.format(region=region, id=id)
    r = requests.get(url, params={'api_key': Constants.KEY})
    if r.status_code == 200:
        return next(iter(r.json().values()))
    else:
        return None


def GetSummonerMatchlist(region, sumid, hero):
    requests_cache.install_cache('summoner.matchlist.cache', backend='sqlite', expire_after=86400)
    url = 'https://{region}.api.pvp.net/api/lol/{region}/v2.2/matchlist/by-summoner/{id}'.format(region=region, id=sumid)
    r = requests.get(url, params={'api_key': Constants.KEY, 'championIds': hero, 'rankedQueues': 'RANKED_SOLO_5x5', 'seasons': 'SEASON2015'})
    if r.status_code == 200:
        return r.json()
    else:
        return None


if __name__ == '__main__':
    dyrusSummonerId = GetSummonerByName('na', 'cov0dyrus')['id']
    print(GetSummonerMatchlist('na', dyrusSummonerId, 68))
