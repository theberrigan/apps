import os, json, time, requests, regex
import xml.etree.ElementTree as ET
from requests.models import PreparedRequest
from urllib.parse import urlparse, parse_qsl, urlencode

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from consts import STEAM_API_KEY, FRONTEND_DIR

app = Flask(__name__, static_url_path='', static_folder=FRONTEND_DIR)
CORS(app)

HOST = '0.0.0.0'
PORT = 48620
LOCAL_HOSTNAME = 'http://{}:{}'.format(HOST, PORT)

print(f'\n{LOCAL_HOSTNAME}\n')

MY_STEAM_ID = 0
MY_STEAM_ACCOUNT = ''

PLAYER_ACHS_URL_REGEX = regex.compile(r'^/(?:profiles|id)/(?P<userNameOrId>[^/]+)/stats(?:/appid)?/(?P<gameNameOrId>[^/]+)', regex.I)

GAME_COMMUNITY_URL_REGEX = regex.compile(r'https:\/\/steamcommunity\.com\/app\/(?P<gameId>\d+)/?', regex.I)

SEARCH_INPUT_URL_PATH_REGEX = regex.compile(r'^/(id/(?P<profileName>[a-z\d_-]+)|profiles/(?P<steamId>\d+))(/stats/((?P<gameNameOrId>[a-z\d_-]+)|appid/(?P<gameId>\d+)))?', regex.I)
SEARCH_INPUT_PAIR_REGEX = regex.compile(r'^(?P<profileNameOrId>[a-z\d_-]+)([^a-z\d_-]+(?P<gameNameOrId>[a-z\d_-]+)?)?$', regex.I)

MULTIPLAYER_CATEGORIES = [ 1, 9, 24, 27, 36, 37, 38, 39, 47, 48, 49 ]
MULTIPLAYER_REGEX = regex.compile(r'((^|\s+)(co-?op|pvp)([^a-z\d]|$)|multi\-?player|other\s+player|split(\s+|-)?screen|online|death-?match|ranked\s+match)', regex.I)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'


def log (*args, **kwargs):
    print(*args, **kwargs)
    # app.logger.info()

def getSubNodeText (parentNode, subNodeXPath, default=None):
    subNode = parentNode.find(subNodeXPath)

    if subNode is not None:
        return subNode.text or ''

    return default

def extractResponseJson (response, default=None):
    if 200 <= response.status_code < 400:
        try:
            return response.json()
        except Exception as e:
            log(e)

    return default

def getByKeyPath (obj, keyPath, default=None):
    obj = obj if isinstance(obj, dict) else {}

    keys = keyPath.split('/')
    lastKeyIndex = len(keys) - 1

    for i, key in enumerate(keys):
        if i == lastKeyIndex:
            return obj.get(key, default)

        obj = obj.get(key, {})

def isUrl (value):
    if not isinstance(value, str):
        return False

    return regex.match(r'^https?:\/\/', value, regex.I) is not None


# ENDPOINTS
# -------------------------------------------------

@app.route('/', methods=[ 'GET' ])
def indexHTML ():
    return send_from_directory(FRONTEND_DIR, 'index.html')

hltbSession = requests.Session()

@app.route('/achievements', methods=[ 'POST' ])
def getAchievements ():
    reqData = json.loads(request.data)

    if 'url' not in reqData:
        return jsonify({
            'isOk': False,
            'error': 'URL is not specified'
        })

    url = reqData['url'].strip()

    if url.isnumeric():
        profileName = MY_STEAM_ACCOUNT
        steamId = None

        gameName = None
        gameId = int(url)
    elif not isUrl(url):
        profileName = MY_STEAM_ACCOUNT
        steamId = None

        gameName = url
        gameId = None
    else:
        # https://store.steampowered.com/app/501590
        # https://store.steampowered.com/app/305620/The_Long_Dark/
        match1 = regex.match(r'^https?:\/\/store\.steampowered\.com\/app\/(\d+)', url, flags=regex.I)
        match2 = regex.match(PLAYER_ACHS_URL_REGEX, urlparse(url).path)

        if match1:
            profileName = MY_STEAM_ACCOUNT
            steamId = None

            gameName = None
            gameId = int(match1.group(1))
        elif match2:
            matchGroups = match2.groupdict()

            userNameOrId = matchGroups['userNameOrId']
            gameNameOrId = matchGroups['gameNameOrId']

            if userNameOrId.isnumeric():
                profileName = None
                steamId = int(userNameOrId)
            else:
                profileName = userNameOrId
                steamId = None

            if gameNameOrId.isnumeric():
                gameName = None
                gameId = int(gameNameOrId)
            else:
                gameName = gameNameOrId
                gameId = None
        else:
            return jsonify({
                'isOk': False,
                'error': 'Invalid URL'
            })

    path = ''

    if steamId:
        path += f'/profiles/{ steamId }'
    else:
        path += f'/id/{ profileName }'

    if gameId == 384110:
        gameName = gameId
        gameId   = None

    if gameId and gameId != 384110:
        path += f'/stats/appid/{ gameId }'
    else:
        path += f'/stats/{ gameName }'

    url = f'https://steamcommunity.com{ path }?tab=achievements&xml=1'

    app.logger.info(url)

    response = requests.get(url, allow_redirects=True)

    # redirected
    if response.history:
        req = PreparedRequest()

        req.prepare_url(response.url, {
            'xml': '1'
        })

        response = requests.get(req.url, allow_redirects=False)

    if response.status_code >= 400:
        return jsonify({
            'isOk': False,
            'error': 'Failed to request Steam API'
        })

    response = (response.text or '').strip()

    if not response:
        return jsonify({
            'isOk': False,
            'error': 'Steam response is empty'
        })

    rootNode = ET.fromstring(response)

    if rootNode.tag != 'playerstats':
        if rootNode.tag == 'response':
            errorNode = rootNode.find('error')

            if errorNode:
                return jsonify({
                    'isOk': False,
                    'error': errorNode.text
                })

        return jsonify({
            'isOk': False,
            'error': 'Unexpected Steam response'
        })

    gameNode   = rootNode.find('game')
    playerNode = rootNode.find('player')
    statsNode  = rootNode.find('stats')

    gameSlug = getSubNodeText(gameNode, 'gameFriendlyName')
    gameURL  = getSubNodeText(gameNode, 'gameLink')
    gameName = getSubNodeText(gameNode, 'gameName')

    if not gameId:
        if gameSlug.isnumeric():
            gameId = int(gameSlug)
        elif gameURL:
            match = regex.fullmatch(GAME_COMMUNITY_URL_REGEX, gameURL)

            if match:
                gameId = int(match.groupdict().get('gameId', '0')) or None

    steamId = int(getSubNodeText(playerNode, 'steamID64'))

    data = {
        'game': {
            'id': gameId,
            'slug': gameSlug,
            'name': gameName,
            'description': '',
            'url': gameURL,
            'iconURL': getSubNodeText(gameNode, 'gameIcon'),
            'logoURL': getSubNodeText(gameNode, 'gameLogo'),
            'smallLogoURL': getSubNodeText(gameNode, 'gameLogoSmall'),
            'headerURL': None,
            'mpScore': 0
        },
        'player': {
            'steamId': steamId,
            'profileName': getSubNodeText(playerNode, 'customURL')
        },
        'stats': {
            'hoursPlayed': getSubNodeText(statsNode, 'hoursPlayed'),
            'ingame': []
        },
        'achievements': [],
        'hltb': None,
        'bgUrl': None
    }

    response = requests.get('https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/', params={
        'key': STEAM_API_KEY,
        'gameid': gameId
    })

    response = (extractResponseJson(response) or {}).get('achievementpercentages', {}).get('achievements', {})
    percentage = { item['name'].lower(): item['percent'] for item in response }
    # app.logger.info(percentage)

    for achNode in rootNode.findall('achievements/achievement'):
        achId = getSubNodeText(achNode, 'apiname')
        descr = getSubNodeText(achNode, 'description', '')

        data['achievements'].append({
            'id': achId,
            'name': getSubNodeText(achNode, 'name').strip(),
            'description': descr.strip(),
            'isAchieved': bool(int(achNode.attrib.get('closed', '0'))),
            'achievedIconURL': getSubNodeText(achNode, 'iconClosed'),
            'unachievedIconURL': getSubNodeText(achNode, 'iconOpen'),
            'achieveDate': int(getSubNodeText(achNode, 'unlockTimestamp', '0')),
            'globalPercent': percentage.get(achId.lower(), 0)
        })

    # -------------------------------

    response = requests.get('https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/', params={
        'key': STEAM_API_KEY,
        'l': 'en',
        'steamid': steamId,
        'appid': gameId
    })

    response = extractResponseJson(response, {})

    data['stats']['ingame'] = getByKeyPath(response, 'playerstats/stats', [])

    # -------------------------------

    response = requests.get('https://store.steampowered.com/api/appdetails', params={
        'appids': gameId,
        'cc': 'us'
    })

    response = extractResponseJson(response, {}).get(str(gameId), {})

    if response['success']:
        response = response.get('data', {})

        data['bgUrl'] = response.get('background')
        data['game']['description'] = response.get('short_description', '')
        data['game']['headerURL'] = response.get('header_image', None)

        categories = response.get('categories', [])

        for cat in categories:
            if cat['id'] in MULTIPLAYER_CATEGORIES:
                data['game']['mpScore'] = 2
                break

    if data['game']['mpScore'] == 0:
        for ach in data['achievements']:
            string = ach['name'] + ' ' + ach['description']

            if regex.search(MULTIPLAYER_REGEX, string):
                data['game']['mpScore'] = 1
                break
        
    # -------------------------------

    if gameId and gameName:
        searchData = {
            'searchType': 'games', 
            'searchTerms': None, 
            'searchPage': 1, 
            'size': 20, 
            'searchOptions': {
                'games': {
                    'userId': 0, 
                    'platform': '', 
                    'sortCategory': 'popular', 
                    'rangeCategory': 'main', 
                    'rangeTime': {
                        'min': None, 
                        'max': None
                    }, 
                    'gameplay': {
                        'perspective': '', 
                        'flow': '', 
                        'genre': ''
                    }, 
                    'rangeYear': {
                        'min': '', 
                        'max': ''
                    }, 
                    'modifier': ''
                }, 
                'users': {
                    'sortCategory': 'postcount'
                }, 
                'lists': {
                    'sortCategory': 'follows'
                }, 
                'filter': '', 
                'sort': 0, 
                'randomizer': 0
            }
        }

        searchData['searchTerms'] = regex.split(r'[\r\s\t\n]+', gameName.strip())

        response = hltbSession.post('https://howlongtobeat.com/api/search', json=searchData, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Referer': 'https://howlongtobeat.com/',
            'User-Agent': USER_AGENT
        })

        response = extractResponseJson(response, {}).get('data', [])

        for item in response:
            if item.get('profile_steam') == gameId:
                data['hltb'] = {
                    'id': item.get('game_id'),
                    'main': item.get('comp_main'),  # Main Story
                    'plus': item.get('comp_plus'),  # Main + Extras
                    'full': item.get('comp_100'),   # Completionist
                }

                break

        # app.logger.info(json.dumps(gameInfo))

    # -------------------------------

    return jsonify({
        'isOk': True,
        'data': data
    })

STEAM_ID_REGEX = regex.compile(r'^STEAM_(?P<accountUniverse>\d+):(?P<authServer>[01]):(?P<accountNumber>\d+)$', regex.I)
STEAM_ID_3_REGEX = regex.compile(r'^\[(?P<accountTypeLetter>[IUMGAPCgTLca]):1:(?P<accountNumber>\d+)\]$')



class SteamID:
    def __init__ (self, steamId=None):
        self._steamId = None
        self._steamId3 = None
        self._steamId64 = None
        self._isValid = False

        self.set(steamId)

    def _setSteamId64 (self, steamId64):
        if steamId64 is not None:
            self._steamId64 = steamId64
            self._isValid = True
        else:
            self._steamId64 = None
            self._isValid = False

        self._steamId = None
        self._steamId3 = None

    def set (self, steamId):
        steamId64 = None

        if isinstance(steamId, int) and steamId > 0:
            steamId64 = steamId
        elif isinstance(steamId, str):
            if steamId.isnumeric() and steamId != '0':
                steamId64 = int(steamId, 10)
            elif regex.fullmatch(STEAM_ID_REGEX, steamId):
                steamId64 = self.__class__.fromRegularTo64(steamId)
            elif regex.fullmatch(STEAM_ID_3_REGEX, steamId):
                steamId64 = self.__class__.from3To64(steamId)

        self._setSteamId64(steamId64)

    def isValid (self):
        return self._isValid

    def asRegular (self):
        if not self.isValid():
            return None

        if self._steamId is None:
            self._steamId = self.__class__.from64toRegular(self._steamId64)

        return self._steamId

    def as3 (self):
        if not self.isValid():
            return None

        if self._steamId3 is None:
            self._steamId3 = self.__class__.from64to3(self._steamId64)

        return self._steamId3

    def as64 (self):
        return self._steamId64

    # https://developer.valvesoftware.com/wiki/SteamID
    @classmethod
    def from64toRegular (cls, steamId64):
        if isinstance(steamId64, str) and steamId64.isnumeric():
            steamId64 = int(steamId64, 10)

        if not isinstance(steamId64, int) or steamId64 <= 0:
            return None

        authServer      = steamId64 & 1
        accountNumber   = (steamId64 >> 1) & 0x7FFFFFFF
        accountInstance = (steamId64 >> 32) & 0xFFFFF
        accountType     = (steamId64 >> 52) & 0xF
        accountUniverse = (steamId64 >> 56) & 0xFF

        return f'STEAM_{ accountUniverse }:{ authServer }:{ accountNumber }'

    @classmethod
    def fromRegularTo64 (cls, steamId):
        if not isinstance(steamId, str):
            return None

        match = regex.fullmatch(STEAM_ID_REGEX, steamId)

        if not match:
            return None

        matchGroups = match.groupdict()

        accountUniverse = int(matchGroups['accountUniverse'], 10)
        authServer      = int(matchGroups['authServer'], 10)
        accountNumber   = int(matchGroups['accountNumber'], 10)

        steamId64 = 0

        steamId64 |= authServer & 1
        steamId64 |= (accountNumber & 0x7FFFFFFF) << 1
        steamId64 |= (1 & 0xFFFFF) << 32
        steamId64 |= (1 & 0xF) << 52
        steamId64 |= (accountUniverse & 0xFF) << 56

        return steamId64 if steamId64 > 0 else None

    @classmethod
    def from64to3 (cls, steamId64):
        if isinstance(steamId64, str) and steamId64.isnumeric():
            steamId64 = int(steamId64, 10)

        if not isinstance(steamId64, int) or steamId64 <= 0:
            return None

        authServer      = steamId64 & 1
        accountNumber   = (steamId64 >> 1) & 0x7FFFFFFF
        accountInstance = (steamId64 >> 32) & 0xFFFFF
        accountType     = (steamId64 >> 52) & 0xF
        accountUniverse = (steamId64 >> 56) & 0xFF

        accountTypes = {
            0:  'I',
            1:  'U',
            2:  'M',
            3:  'G',
            4:  'A',
            5:  'P',
            6:  'C',
            7:  'g',
            8:  'T',
            10: 'a',
        }

        if accountType not in accountTypes:
            return None

        return f'[{ accountTypes[accountType] }:1:{ (accountNumber * 2 + authServer) }]'

    @classmethod
    def from3To64 (cls, steamId3):
        pass

    @classmethod
    def fromRegularTo3 (cls, steamId):
        pass

    @classmethod
    def from3ToRegular (cls, steamId3):
        pass


if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
