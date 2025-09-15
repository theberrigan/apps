import signal
import os, json, subprocess, zlib, sqlite3, random, time, math, sys, threading
# from shutil import copyfile
from datetime import datetime
from queue import Queue
from threading import Thread, Lock, Event as ThreadEvent
from requests.exceptions import ProxyError
from cloudscraper import CloudScraper

import regex

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE_PATH = os.path.join(SCRIPT_DIR, 'music.db')
PROXIES_CACHE_PATH = os.path.join(SCRIPT_DIR, 'proxies.json')
PROXIES_CACHE_EXPIRE_MS = 1 * 60 * 60 * 1000
YA_TOTAL_ALBUMS = 17500000

IPV4_REGEX = regex.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

WEBSHARE_API_KEY = '...'

EVENT_STOP_THREAD = 1
EVENT_WRITE_TO_DB = 2 

WORKER_TYPE_DB        = 1
WORKER_TYPE_COLLECTOR = 2

MAX_COLLECT_WORKERS = 32  # os.cpu_count()

COLLECT_ERROR_REQUEST_FAILED = -1
COLLECT_ERROR_RESPONSE_EMPTY = -2


def toJson (obj, pretty=False, toBytes=False):
    if pretty:
        data = json.dumps(obj, ensure_ascii=False, indent=4)
    else:
        data = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

    if toBytes:
        data = data.encode('utf-8')

    return data


def fromJson (jsonData):
    return json.loads(jsonData) if jsonData else None


def readJson (filePath):
    if not os.path.isfile(filePath):
        return None

    with open(filePath, 'rb') as f:
        try:
            return json.loads(f.read().decode('utf-8'))
        except:
            return None


def writeJson (filePath, obj, pretty=False):
    with open(filePath, 'wb') as f:
        f.write(toJson(obj, pretty=pretty, toBytes=True))


def compressData (data):
    if not data:
        return None

    compressor = zlib.compressobj(level=9)
    compData = compressor.compress(data)
    compData += compressor.flush()

    return compData


def decompressData (compData):
    decompressor = zlib.decompressobj()
    decompData = decompressor.decompress(compData)
    decompData += decompressor.flush()

    return decompData


def getTimestamp ():
    return int(time.time() * 1000)


def checkSuccessResponse (response):
    return 200 <= response.status_code < 400


def calcAvg (nums):
    return (sum(nums) / len(nums)) if nums else 0


def proxyToRequestProxy (proxy):
    if not proxy:
        return None
        
    return { 
        'https': f'https://{ proxy.user }:{ proxy.password }@{ proxy.ip }:{ proxy.portHttp }' 
    }


class NetworkMonitor:
    def __init__ (self):
        self.scrapper = CloudScraper()

    def get (self, url, responseType=None, proxy=None):
        try:
            response = self.scrapper.get(url, proxies=proxyToRequestProxy(proxy))

            if checkSuccessResponse(response):
                if responseType == 'json':
                    return response.json()
                elif responseType == 'text':
                    return response.text.strip()
                else:
                    return response
        except:
            pass

        return '' if responseType == 'text' else None

    def getExternalIp (self, proxy=None):
        response = self.get('https://api.ipify.org?format=json', responseType='json', proxy=proxy)

        if response and 'ip' in response:
            return response['ip']

        response = self.get('https://ifconfig.me/all.json', responseType='json', proxy=proxy)

        if response and 'ip_addr' in response:
            return response['ip_addr']

        response = self.get('https://icanhazip.com', responseType='text', proxy=proxy)

        if IPV4_REGEX.match(response):
            return response

        response = self.get('http://ip-api.com/json', responseType='json', proxy=proxy)

        if response and 'query' in response:
            return response['query']

        return None

    def checkProxy (self, proxy):
        return self.getExternalIp(proxy) == proxy.ip

    def checkConnection (self):
        services = [
            'https://www.google.com/',
            'https://www.youtube.com/',
            'https://yandex.ru/',
            'https://vk.com/',
            'https://mail.ru/',
            'https://2ip.ru/',
        ]

        for url in services:
            if self.get(url, responseType='text'):
                return True

        return False


class Database:
    def __init__ (self, dbPath):
        self.connection = sqlite3.connect(dbPath, detect_types=sqlite3.PARSE_DECLTYPES)
        self.initDB()

    def __del__ (self):
        self.close()

    def close (self):
        if self.connection:
            self.connection.close()
            self.connection = None    

    def initDB (self):
        self.execute('PRAGMA journal_mode=WAL')
        self.execute('PRAGMA busy_timeout=300000')
        self.execute('''
            CREATE TABLE IF NOT EXISTS ya_albums_raw (
                id INTEGER NOT NULL PRIMARY KEY, 
                album_id INTEGER NOT NULL,  
                data BLOB,             
                date TIMESTAMP NOT NULL,
                error_code INTEGER)
        ''')
        self.connection.execute('VACUUM')

    def execute (self, query, *args, **kwargs):
        self.connection.execute(query, *args, **kwargs)
        self.connection.commit()

    def fetchAll (self, query, *args, **kwargs):
        return self.connection.cursor().execute(query, *args, **kwargs).fetchall()

    def fetchOne (self, query, *args, **kwargs):
        item = self.connection.cursor().execute(query, *args, **kwargs).fetchone()
        return item[0] if item and len(item) == 1 else item


def getProxies (forceUpdate = False):
    proxies = None

    if not forceUpdate:
        cache = readJson(PROXIES_CACHE_PATH)

        if cache and (getTimestamp() - cache['lastUpdate']) < PROXIES_CACHE_EXPIRE_MS: 
            proxies = cache['proxies'] 

    if not proxies:
        response = CloudScraper().get('https://proxy.webshare.io/api/proxy/list/?page=1', headers={
            'Authorization': f'Token { WEBSHARE_API_KEY }'
        })

        if not checkSuccessResponse(response):
            return None

        data = response.json()
        proxies = data['results']

        writeJson(PROXIES_CACHE_PATH, {
            'lastUpdate': getTimestamp(),
            'proxies': proxies
        })

    return proxies


class Proxy:
    def __init__ (self, obj):
        self.ip          = obj['proxy_address']
        self.portHttp    = obj['ports']['http']
        self.portSocks5  = obj['ports']['socks5']
        self.user        = obj['username']
        self.password    = obj['password']
        self.countryCode = obj['country_code']


def chooseProxy (proxies, countryCode):
    if not proxies:
        return None

    for i in range(len(proxies)):
        proxy = proxies[i]

        if proxy['valid'] and proxy['country_code'] == countryCode:
            return Proxy(proxy)

    return None


def checkProxyWithIpify (proxy):
    response = CloudScraper().get('https://api.ipify.org?format=json', proxies=proxyToRequestProxy(proxy))

    if not checkSuccessResponse(response):
        return False

    return response.json()['ip'] == proxy.ip


def checkProxyWithYandex (proxy):
    albumId = 383779

    response = CloudScraper().get(
        'https://music.yandex.ru/handlers/album.jsx', 
        params={
            'album': str(albumId),
            'lang': 'en',
            'external-domain': 'music.yandex.ru',
            'overembed': 'false',
            'ncrnd': str(random.random())
        },
        proxies=proxyToRequestProxy(proxy)
    )

    if not checkSuccessResponse(response):
        return False

    try:
        return response.json()['id'] == albumId
    except:
        return False


class YandexMusicCollector (Thread):
    instances = 0

    def __init__(self, tasks, proxy, dbQueue):
        super().__init__()
        self.__class__.instances += 1
        self.workerId = self.__class__.instances
        self.workerType = WORKER_TYPE_COLLECTOR
        self.stopEvent = ThreadEvent()
        self.tasks = tasks
        self.proxy = proxyToRequestProxy(proxy)
        self.dbQueue = dbQueue
        self.scraper = None
        self.lastReqTs = None
        self.reqDurations = []
        self.avgReqTime = 0

    def processAlbum (self, albumId):
        url = 'https://music.yandex.ru/handlers/album.jsx'

        params = {
            'album': str(albumId),
            'lang': 'en',
            'external-domain': 'music.yandex.ru',
            'overembed': 'false',
            'ncrnd': str(random.random())
        }

        headers = {
            'Host': 'music.yandex.ru',
            'Connection': 'keep-alive',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Retpath-Y': f'https://music.yandex.ru/album/{ albumId }',
            'X-Current-UID': '173288788',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': 'yandexuid=7609018861621948623; yuidss=7609018861621948623; ymex=1938031392.yrts.1622671392; is_gdpr=0; pepsi_year=today; my=YycCAAMA; is_gdpr_b=CITuCxD+MygC; mda=0; yandex_gid=16; yabs-frequency=/5/0000000000000000/-n8SS980001KGI3v4XnmaW0005H18JPnGMs60000L44dWc51ROO0001KGIC0/; Session_id=3:1623556465.5.0.1623556465718:E6ClBQ:3.1|173288788.0.2|235959.926770.xf0gp4B_CW-OKtS-vm4Oab2JTmE; sessionid2=3:1623556465.5.0.1623556465718:E6ClBQ:3.1|173288788.0.2|235959.926770.xf0gp4B_CW-OKtS-vm4Oab2JTmE; yp=1626148451.ygu.1#1639324453.szm.1%3A1920x1080%3A1920x937#1938916465.udn.cDpTdGFuaXNsYXYgS3V6bmV0c292; ys=c_chck.528903867#udn.cDpTdGFuaXNsYXYgS3V6bmV0c292; L=cWx3eUBeW3t6DmYMU1dZbFR3DENtR1sJEFAKMRNHGzEXG2IF.1623556465.14631.349884.c1fd62088f5bcfb84c8fd838621a0f70; yandex_login=valveunion76; i=06MXqAXt3Cl9gbW2mkqpl2E61Xvwu6oSO0fCJuepIDQYGArEvAOj/6vAwVHf3UNbwRoIDnHIqDXTO5Smlt1LGH1E/5w=; device_id=ad12d0184f084ec05648b91692fc62c91ceb557f9; active-browser-timestamp=1623557057949; lastVisitedPage=%7B%22173288788%22%3A%22%2Falbum%2F383779%22%7D'
        }

        albumData = None
        errorCode = None

        try:
            response = self.scraper.get(url, params=params, headers=headers, proxies=self.proxy)
        except Exception as e:  # ProxyError
            sys.stdout.write(f'[ACW{self.workerId:02d}] FATAL: Failed to request album { albumId } ({ str(e) })\n')
            errorCode = COLLECT_ERROR_REQUEST_FAILED

        if errorCode == None:
            if checkSuccessResponse(response):
                responseData = response.json()

                if responseData:
                    albumData = sqlite3.Binary(compressData(toJson(responseData, toBytes=True)))
                else:
                    sys.stdout.write(f'[ACW{self.workerId:02d}] FATAL: Album { albumId } data is empty\n')
                    errorCode = COLLECT_ERROR_RESPONSE_EMPTY
            else:
                errorCode = response.status_code

                if errorCode == 404:
                    sys.stdout.write(f'[ACW{self.workerId:02d}] Album { albumId } not found\n')
                else:
                    sys.stdout.write(f'[ACW{self.workerId:02d}] FATAL: Failed to request album { albumId } (status_code: { errorCode })\n')


        self.dbQueue.put((EVENT_WRITE_TO_DB, (
            'INSERT INTO ya_albums_raw(album_id, data, date, error_code) VALUES (?, ?, ?, ?)', 
            (albumId, albumData, datetime.now(), errorCode)
        )))

        return errorCode

    def calcCollectingSpeed (self):
        curReqTs = getTimestamp()

        if self.lastReqTs:
            self.reqDurations.append(curReqTs - self.lastReqTs)
            self.reqDurations = self.reqDurations[-30:]
            self.avgReqTime = calcAvg(self.reqDurations)

        self.lastReqTs = curReqTs

    def run (self):
        sys.stdout.write(f'[ACW{self.workerId:02d}] Starting collector...\n')

        self.scraper = CloudScraper()

        collectedAlbumCount = 0

        for albumId in self.tasks:
            time.sleep(0.2)

            errorCode = self.processAlbum(albumId)

            if errorCode == None:
                collectedAlbumCount += 1
            elif errorCode != 404:
                break

            self.calcCollectingSpeed()

            if collectedAlbumCount % 10 == 0:
                sys.stdout.write(f'[ACW{self.workerId:02d}] Collected album { albumId } ({ int(self.avgReqTime) }ms/req)\n')                

            if self.stopEvent.is_set():
                break

            time.sleep(0.2)

        sys.stdout.write(f'[ACW{self.workerId:02d}] Stopped\n')

    def stop (self):        
        self.stopEvent.set()


class IdGenerator:
    def __init__ (self, *args, **kwargs):
        self.gen = (i for i in range(*args, **kwargs))
        self.lock = Lock()

    def __iter__ (self):
        return self

    def __next__ (self):
        with self.lock:
            return next(self.gen)

    def next (self):
        return self.__next__()


class QueuedDatabaseWriter (Thread):
    instances = 0

    def __init__(self, queue):
        super().__init__()        
        self.__class__.instances += 1
        self.workerId = self.__class__.instances
        self.workerType = WORKER_TYPE_DB
        self.queue = queue
        self.db = None
        self.stopEvent = ThreadEvent()

    def run (self):
        self.db = Database(DATABASE_PATH)

        while not self.stopEvent.is_set():
            try:
                task = self.queue.get(timeout=0.5)
            except:
                continue

            action, payload = task

            if action == EVENT_STOP_THREAD:
                self.stop()
            elif action == EVENT_WRITE_TO_DB:
                query, queryArgs = payload                
                self.db.execute(query, queryArgs)

            self.queue.task_done()

        self.db.close()

        sys.stdout.write(f'[QDBW{self.workerId:02d}] Stopped\n')

    def stop (self):
        self.stopEvent.set()


def checkAliveWorker (workers):
    if not workers:
        return False

    for worker in workers:            
        if worker.is_alive():
            return True

    return False


class Application:
    def __init__(self):
        self.collectWorkers = []
        self.dbWorker = None

    def addWorker (self, worker):
        if worker.workerType == WORKER_TYPE_COLLECTOR:
            self.collectWorkers.append(worker)

    def run (self):
        print('\nStarting application...')

        db = Database(DATABASE_PATH)

        lastAlbumId = db.fetchOne('SELECT album_id FROM ya_albums_raw ORDER BY album_id DESC LIMIT 1') or 0

        print(f'Start from album id: { lastAlbumId + 1 }')

        db.close()

        tasks = IdGenerator(lastAlbumId + 1, YA_TOTAL_ALBUMS)

        dbQueue = Queue()
        self.dbWorker = QueuedDatabaseWriter(dbQueue)
        self.dbWorker.start()

        print('Gathering available proxies...')

        proxies = getProxies()
        random.shuffle(proxies)

        print('Selecting suitable proxies...')

        for proxy in proxies:
            if not proxy['valid'] or proxy['country_code'] != 'RU':
                continue

            proxy = Proxy(proxy)

            if not checkProxyWithYandex(proxy):
                continue

            collectWorker = YandexMusicCollector(tasks, proxy, dbQueue)
            collectWorker.start()
            self.addWorker(collectWorker)

            workerCount = len(self.collectWorkers)

            print(f'{workerCount:02d}: { proxy.ip }:{ proxy.portHttp }')

            if workerCount >= MAX_COLLECT_WORKERS:
                break

        try:
            while checkAliveWorker(self.collectWorkers):
                time.sleep(1)
        except KeyboardInterrupt:
            print('Stopping application...')

            for worker in self.collectWorkers:  
                worker.stop()

            for worker in self.collectWorkers:  
                worker.join()

            self.dbWorker.stop()
            self.dbWorker.join()

        print('--- EXIT ---')

if __name__ == '__main__':
    app = Application()
    app.run()