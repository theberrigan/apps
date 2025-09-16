import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *

import os, json
from datetime import datetime, date as createDate

import requests
from requests.adapters import HTTPAdapter

from consts import STEAM_API_KEY, MISC_DIR


STEAM_API_PATH = os.path.join(MISC_DIR, 'steam_api.json')
ACHIEV_DB_PATH = os.path.join(MISC_DIR, 'achievements.json')
APPS_DB_PATH   = os.path.join(MISC_DIR, 'apps.json')
GAMES_DB_PATH  = os.path.join(MISC_DIR, 'games.json')


def extractResponseJson (response, default=None):
    if 200 <= response.status_code < 400:
        try:
            return response.json()
        except Exception as e:
            print(e)

    return default


def collectSteamApis (showStats=False):
    response = requests.get('http://api.steampowered.com/ISteamWebAPIUtil/GetSupportedAPIList/v0001/', params={
        'key': STEAM_API_KEY,
        'format': 'json',
        'l': 'english',
        'cc': 'us',
    })

    apis = extractResponseJson(response, {}).get('apilist', {}).get('interfaces', [])

    useful  = []
    useless = []

    for interface in apis:
        name = interface['name'].lower()

        if name.startswith('icsgo') or \
           name.startswith('idota') or \
           name.startswith('itf') or \
           name.startswith('iecondota2_') or \
           name.startswith('ieconitems_') or \
           name.startswith('ieconservice') or \
           name.startswith('igcversion_'):
            interface['isUseful'] = False
            useless.append(interface)
        else:
            interface['isUseful'] = True
            useful.append(interface)

    useful.sort(key=lambda item: item['name'])

    apis = useful + useless

    os.makedirs(MISC_DIR, exist_ok=True)

    with open(STEAM_API_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(apis, ensure_ascii=False, indent=4))

    if showStats:
        print('Collected Steam API interfaces:')
        print(f'Useful:  {len(useful)}')
        print(f'Useless: {len(useless)}')
        print(f'Total:   {len(apis)}')


def showApis ():
    collectSteamApis()

    if not os.path.isfile(STEAM_API_PATH):
        print('File not found')
        return

    with open(STEAM_API_PATH, 'r', encoding='utf-8') as f:
        apis = json.loads(f.read())

    for interface in apis:
        if not interface['isUseful']:
            continue

        intName = interface['name']

        for method in interface['methods']:
            methodName  = method['name']
            version     = method['version']
            httpMethod  = method['httpmethod']
            description = method.get('description', '')

            print(f'{httpMethod:<4} https://api.steampowered.com/{intName}/{methodName}/v{version}/ -- { description }')


def fetchPlayerAchievements ():
    response = requests.get('https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/', params={
        'key': STEAM_API_KEY,
        'format': 'json',
        'l': 'english',
        'cc': 'us',
        'steamid': 0,
        'include_appinfo': 0,
        'include_extended_appinfo': 0,
        'include_played_free_games': 1,
        'appids_filter': '',
        'include_free_sub': 1,
        'skip_unvetted_apps': 0,
        'language': 'english'
    })

    print(response.url)

    apps = extractResponseJson(response, {}).get('response', {}).get('games', [])
    appCount = len(apps)

    db = []

    for i, app in enumerate(apps):
        appId = app['appid']

        print(f'{(i + 1)}/{appCount} - {appId}')

        response = requests.get('https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/', params={
            'key': STEAM_API_KEY,
            'format': 'json',
            'l': 'english',
            'cc': 'us',
            'steamid': 0,
            'appid': appId
        })

        response = extractResponseJson(response, {}).get('playerstats', {})

        if not response.get('success'):
            error = response.get('error')

            if error:
                print('ERROR:', error)

            continue

        achievements = response.get('achievements', [])

        db.append({
            'appId': appId,
            'achievements': achievements
        })

        # break

    db.sort(key=lambda item: item['appId'])

    os.makedirs(MISC_DIR, exist_ok=True)

    with open(ACHIEV_DB_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(db, ensure_ascii=False, separators=(',', ':')))

def showPerYearStats ():
    if not os.path.isfile(ACHIEV_DB_PATH):
        print('File not found')
        return

    with open(ACHIEV_DB_PATH, 'r', encoding='utf-8') as f:
        db = json.loads(f.read())

    totalCount = 0
    achievedCount = 0
    stats = {}

    for app in db:
        achs = app['achievements']
        totalCount += len(achs)

        for ach in achs:
            if ach['achieved']:
                achievedCount += 1
                achieveDate = datetime.fromtimestamp(ach['unlocktime'])
                year = achieveDate.year

                stats[year] = stats.get(year, 0) + 1

    stats = sorted(stats.items(), key=lambda item: item[0])

    print(f'Achievements: {achievedCount}/{totalCount}')

    for year, count in stats:
        print(f'- {year}: {count}')


# call fetchPlayerAchievements first
def showPerYearStats2 ():
    if not isFile(ACHIEV_DB_PATH):
        print(f'File not found: { ACHIEV_DB_PATH }')
        return

    apps = readJson(ACHIEV_DB_PATH)

    totalCount = 0
    doneCount  = 0
    yearStats  = {}

    for app in apps:
        achievements = app['achievements']
        totalCount += len(achievements)

        isPerfect  = True
        latestYear = 0

        for ach in achievements:
            if not ach['achieved']:
                isPerfect = False
                continue

            doneCount += 1

            unlockTime = ach['unlocktime']
            unlockYear = datetime.fromtimestamp(unlockTime).year
            latestYear = max(latestYear, unlockYear)

            if unlockYear not in yearStats:
                yearStats[unlockYear] = [ 0, 0 ]

            yearStats[unlockYear][0] += 1

        if isPerfect:
            yearStats[unlockYear][1] += 1

    yearStats = sorted(yearStats.items(), key=lambda item: item[0])

    print(f'Achievements: { doneCount }/{ totalCount }')

    for year, (achCount, perfectCount) in yearStats:
        print(f'- { year }: { achCount } ({ perfectCount } perfect games)')


def showDateRangeStats (fromDay, toDay):
    if not os.path.isfile(ACHIEV_DB_PATH):
        print('File not found')
        return

    with open(ACHIEV_DB_PATH, 'r', encoding='utf-8') as f:
        db = json.loads(f.read())

    fromDate = datetime(fromDay[2], fromDay[1], fromDay[0])
    toDate   = datetime(toDay[2], toDay[1], toDay[0])

    achievedCount = 0

    for app in db:
        achs = app['achievements']

        for ach in achs:
            if not ach['achieved']:
                continue

            achieveDate = datetime.fromtimestamp(ach['unlocktime'])

            if fromDate <= achieveDate < toDate:
                achievedCount += 1

    print(f'Achieved in { fromDate }-{ toDate }: { achievedCount }')

def showGamesWithAchevements ():
    if not os.path.isfile(ACHIEV_DB_PATH):
        print('File not found')
        return

    with open(ACHIEV_DB_PATH, 'r', encoding='utf-8') as f:
        db = json.loads(f.read())

    appsMap = getAppsMap()
    games = {}

    for app in db:
        achs = app['achievements']
        closedCount = 0

        for ach in achs:
            if not ach['achieved']:
                closedCount += 1

        if not closedCount:
            continue

        gameId = app['appId']
        gameName = appsMap.get(gameId, f'GAME_{ gameId }')

        games[gameId] = {
            'gameName': gameName,
            'gameId': gameId,
            'totalAchievements': len(achs),
            'closedAchievements': closedCount
        }

    games = list(games.values())

    games.sort(key=lambda item: item['gameName'])

    totalClosedAchievements = 0

    for game in games:
        gameName = game['gameName']
        gameId = game['gameId']
        totalAchievements = game['totalAchievements']
        closedAchievements = game['closedAchievements']

        totalClosedAchievements += closedAchievements

        print(f'{ gameName } [{ gameId }] ({ closedAchievements }/{ totalAchievements })')

    print(' ')
    print('Closed achievements:', totalClosedAchievements)

def getAppsMap ():
    if not os.path.isfile(APPS_DB_PATH):
        print('File not found')
        return

    with open(APPS_DB_PATH, 'r', encoding='utf-8') as f:
        apps = json.loads(f.read())

    return { app['id']: app['title'] for app in apps }

def fetchGames ():
    session = requests.Session()
    session.mount('https://api.steampowered.com', HTTPAdapter(max_retries=3))

    games = []
    hasNext = True
    lastAppId = None

    reqNumber = 0

    while hasNext:
        reqNumber += 1

        print(f'Request { reqNumber }')

        params = {
            'key': STEAM_API_KEY,
            'format': 'json',
            'l': 'english',
            'cc': 'us',
            'include_games': 1,
            'include_dlc': 0,
            'include_software': 0,
            'include_videos': 0,
            'include_hardware': 0
        }

        if lastAppId is not None:
            params['last_appid'] = lastAppId

        response = session.get('https://api.steampowered.com/IStoreService/GetAppList/v1/', params=params)

        response = extractResponseJson(response, {}).get('response', {})

        appsList  = response.get('apps', [])
        hasNext   = response.get('have_more_results', False)
        lastAppId = response.get('last_appid', None)

        for app in appsList:
            games.append({
                'id': app['appid'],
                'title': app['name'],
            })

        assert not hasNext or lastAppId is not None

    print(f'Collected games: {len(games)}')

    games.sort(key=lambda item: item['id'])

    with open(GAMES_DB_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(games, ensure_ascii=False, separators=(',', ':')))

def fetchApps ():
    params = {
        'key': STEAM_API_KEY,
        'format': 'json',
        'l': 'english',
        'cc': 'us'
    }

    response = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2/', params=params)

    apps = extractResponseJson(response, {}).get('applist', {}).get('apps', {})
    
    apps = [ {
        'id': app['appid'],
        'title': app['name']
    } for app in apps ]

    print(f'Collected apps: { len(apps) }')

    apps.sort(key=lambda item: item['id'])

    with open(APPS_DB_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(apps, ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    fetchPlayerAchievements()
    showPerYearStats2()
