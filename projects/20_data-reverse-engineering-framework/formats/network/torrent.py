# http://bittorrent.org/beps/bep_0003.html
# https://wiki.theory.org/BitTorrentSpecification
# https://en.wikipedia.org/wiki/Torrent_file
# https://github.com/transmission/transmission/issues/3442
# http://bittorrent.org/bittorrentecon.pdf

import os
import sys
import zipfile as zf

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) 

from bfw.utils import *
from bfw.reader import *

from bfw.fs.scan.collecting import GLOBAL_SAMPLES_DIR, collectSamplesInFile, iterSamplesInFile



TORRENT_SAMPLES_DIR  = joinPath(GLOBAL_SAMPLES_DIR, 'torrent')
TORRENT_SAMPLES_PATH = joinPath(GLOBAL_SAMPLES_DIR, 'torrent.bin')

TORRENT_SAMPLES_ZIP_PATH = r'D:\Documents\Downloads\Torrents Sources\!archive.zip'

TORRENT_EXT = '.torrent'
TORRENT_ENCODING = 'utf-8'

SHA1_SIZE     = 20
SHA1_HEX_SIZE = SHA1_SIZE * 2



class Byte:
    Colon = ord(':')
    Zero  = ord('0')
    Minus = ord('-')
    I     = ord('i')
    L     = ord('l')
    D     = ord('d')
    E     = ord('e')


class TorrentParser:
    def __init__ (self):
        self.data   = None
        self.size   = None
        self.cursor = 0

    def parse (self, data):
        if not isinstance(data, bytes) and not isinstance(data, bytearray):
            raise Exception('Data must be of type bytes or bytearray')

        if not data:
            raise Exception('Torrent file is empty')

        self.data   = data
        self.size   = len(data)
        self.cursor = 0

        data = self.readDict()

        # pjp(data['info']['pieces']); exit()

        # data['info']['pieces'] = self.splitPieces(data['info']['pieces'])

        return data

    # <n>:<string> - string
    # i<int>e      - integer
    # l...e        - list of items
    # d...e        - dict

    def splitPieces (self, pieces):
        piecesSize = len(pieces)

        assert piecesSize % SHA1_HEX_SIZE == 0

        pieceCount = piecesSize // SHA1_HEX_SIZE

        checksums = [ None ] * pieceCount

        for i in range(pieceCount):
            checksum = pieces[SHA1_HEX_SIZE * i:SHA1_HEX_SIZE * i + SHA1_HEX_SIZE]

            assert len(checksum) == SHA1_HEX_SIZE

            checksums[i] = checksum

        return checksums

    def readEntity (self, encoding=TORRENT_ENCODING):
        byte = self.peek()

        if byte == Byte.I:
            entity = self.readInt()
        elif byte == Byte.L:
            entity = self.readList(encoding)
        elif byte == Byte.D:
            entity = self.readDict()
        elif self.isDigit(byte):
            entity = self.readString(encoding)            
        elif byte == Byte.E:
            raise Exception('Unexpected end of entity')
        elif byte is None:
            raise Exception('Unexpected EOF, entity expected')
        else:
            raise Exception('Unexpected byte')

        return entity

    def readInt (self):
        byte = self.advance()

        if byte != Byte.I:
            raise Exception('Integer start mark expected')

        num = ''

        hasLeadingZero = False

        while True:
            byte = self.advance()

            if byte is None:
                raise Exception('Unexpected EOF, integer byte expected')

            if byte == Byte.E:                
                break

            if hasLeadingZero:
                raise Exception(f'Integer must not start from 0')

            if byte not in b'-0123456789':
                raise Exception('Integer byte expected')                

            if byte == Byte.Minus and num:
                raise Exception('Unexpected - in the middle of integer')
            elif byte == Byte.Zero:
                if not num:
                    hasLeadingZero = True
                elif num[-1] == Byte.Minus:
                    raise Exception(f'Unexpected 0 after -')

            num += chr(byte)

        return int(num, 10)

    def readList (self, encoding=TORRENT_ENCODING):
        store = {}

        byte = self.advance()

        if byte != Byte.L:
            raise Exception('List start mark expected')

        count = 0

        while True:
            byte = self.peek()

            if byte is None:
                raise Exception('Unexpected EOF, list item or list end mark expected')

            if byte == Byte.E:
                self.cursor += 1                
                break

            store[count] = self.readEntity(encoding)

            count += 1

        return list(store.values())

    def readDict (self):
        store = {}

        byte = self.advance()

        if byte != Byte.D:
            raise Exception('Dictionary start mark expected')

        while True:
            byte = self.peek()

            if byte is None:
                raise Exception('Unexpected EOF, dictionary key or dictionary end mark expected')

            if byte == Byte.E:
                self.cursor += 1                
                break

            key = self.readString()

            key, encoding  = self.parseDictKey(key)

            val = self.readEntity(encoding)

            store[key] = val

        return store

    def parseDictKey (self, key):
        parts = key.rsplit('.', 1)
        partCount = len(parts)

        if partCount == 1:
            return parts[0], TORRENT_ENCODING

        assert partCount == 2
        
        return parts[0], self.normalizeEncoding(parts[1])

    def normalizeEncoding (self, encoding):
        encoding = encoding.lower()

        return encoding

    def readString (self, encoding=TORRENT_ENCODING):
        size = ''

        while True:
            byte = self.advance()

            if byte == Byte.Colon:
                break

            if byte is None:
                raise Exception('Unexpected EOF, string size is truncated')

            if not self.isDigit(byte):
                raise Exception('String size expected')

            size += chr(byte)

        size = int(size, 10)

        if self.remaining() < size:
            raise Exception('Unexpected EOF, string is truncated')

        # print(self.cursor, size)

        string = self.read(size)

        try:
            string = string.decode(encoding)
        except:
            string = string.hex()

        return string

    def isDigit (self, byte):
        return byte in b'0123456789'

    def remaining (self):
        return self.size - self.cursor

    def read (self, size):
        data = self.data[self.cursor:self.cursor + size]

        self.cursor += size

        return data

    def peek (self):
        if self.isEnd():
            return None

        return self.data[self.cursor]

    def advance (self):
        if self.isEnd():
            return None

        byte = self.data[self.cursor]

        self.cursor += 1

        return byte

    def isEnd (self):
        return self.cursor >= self.size


class Torrent:
    def __init__ (self):
        pass

    @classmethod
    def fromFile (cls, filePath):
        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        return cls._read(readBin(filePath))

    @classmethod
    def fromBuffer (cls, data):
        return cls._read(data)

    @classmethod
    def _read (cls, data):
        # t = Torrent()

        data = TorrentParser().parse(data)

        return data

'''
{
    'announce': '',
    'info': {
        'name': '',
        'piece length': '',
        'pieces': '',
        'length' or 'files',

    }
}

'''




################################################
####               AUXILIARY                ####
################################################

_BLACKLISTED = [
    filePath.lower() for filePath in [

    ]
]

def _collectSamples ():
    def check (filePath, fileSize, fileCRC):
        print(filePath, fileSize, fileCRC)
        return _checkTorrentFile(filePath)        

    collectSamplesInFile(
        rootDirs     = getDrives(True),
        destPath     = TORRENT_SAMPLES_PATH,
        exts         = [ TORRENT_EXT ], 
        isRecursive  = True, 
        minSize      = 1, 
        maxSize      = None,
        noDups       = True,
        checkFn      = check
    )

def _checkTorrentFile (filePath):
    if filePath.lower() in _BLACKLISTED:
        return False

    return True

def _parseSampleFromPath (filePath):
    if _checkTorrentFile(filePath):
        print(filePath)

        try:
            Torrent.fromFile(filePath)
        except Exception as e:
            # print('ERROR:', e)
            pass

        print(' ')

def _parseSamplesFromFile (listFilePath=TORRENT_SAMPLES_PATH):
    for filePath in iterSamplesInFile(listFilePath):
        _parseSampleFromPath(filePath)

def _parseSamplesFromDir (rootDir=TORRENT_SAMPLES_DIR):
    for filePath in iterFiles(rootDir, True, [ TORRENT_EXT ]):
        _parseSampleFromPath(filePath)

def _checkTorrentBuffer (data):
    return True

def _parseSampleFromBuffer (data, filePath=None):
    if _checkTorrentBuffer(data):
        try:
            data = Torrent.fromBuffer(data)
            # data = toJson(data)

            # if filePath:
            #     jsonName = getBaseName(filePath)
            #     jsonName = replaceExt(jsonName, '.json')
            #     jsonPath = joinPath(TORRENT_SAMPLES_DIR, 'json', jsonName)

            #     createFileDirs(jsonPath)
            #     writeJson(jsonPath, data)
            if 'files' in data['info']:
                print(toJson(data))
                sys.exit()
        except Exception as e:
            if filePath:
                print(filePath)

            print('ERROR:', e)

            if filePath:
                print(' ')

            # sys.exit()

def _parseSamplesFromZip (zipPath=TORRENT_SAMPLES_ZIP_PATH):
    assert isFile(zipPath)

    with zf.ZipFile(zipPath, 'r') as arc:
        for entry in arc.infolist():
            if entry.is_dir():
                continue

            itemPath = entry.filename

            if getExt(itemPath) != TORRENT_EXT:
                continue

            data = arc.read(itemPath)

            try:
                torrentPath = itemPath.encode('cp437').decode('cp866')
            except:
                torrentPath = itemPath

            _parseSampleFromBuffer(data, torrentPath)

def _requestAnnouncer (filePath):
    data = Torrent.fromFile(filePath)

    # info_hash=B5374288AFEFE41CB92A4E136EC6858041AD4BBF
    # peer_id=genFixedId(10)
    # ip=None
    # port=13795
    # uploaded=0
    # downloaded=0
    # left=1024
    # event=empty

    import requests
    # from bfw.crypto import genFixedId

    # info_hash=B5374288AFEFE41CB92A4E136EC6858041AD4BBF&peer_id=ec0e438f68b9eab8d247&port=13795&uploaded=0&downloaded=0&left=1024&event=empty

    response = requests.get('https://bt2.t-ru.org/ann?pk=bef29bc681da89a4438c66620c903a5b', params={
        'info_hash': b'\xb57B\x88\xaf\xef\xe4\x1c\xb9*N\x13n\xc6\x85\x80A\xadK\xbf',
        'peer_id': 'ec0e438f68b9eab8d247',
        'port': 13795,
        'uploaded': 0,
        'downloaded': 0,
        'left': 1024,
        'event': 'empty'
    }, headers={
        'User-Agent': 'BitTorrent/7.9.9',
    })

    print(Torrent.fromBuffer(response.content))

    print(toJson(data))
    # print(genFixedId(10))

################################################
####                TESTING                 ####
################################################

def _test_ ():
    pass


################################################
####                 EXPORT                 ####
################################################

__all__ = [
    'Torrent'
]



if __name__ == '__main__':
    # _test_()
    # _collectSamples()
    # _parseSamplesFromFile()
    # _parseSamplesFromDir()
    # _parseSamplesFromZip()
    # try:
    #     Torrent.fromFile(joinPath(TORRENT_SAMPLES_DIR, 'Rush Hour 2.torrent'))
    # except Exception as e:
    #     print('ERROR:', e)
    _requestAnnouncer(joinPath(TORRENT_SAMPLES_DIR, 'Cryostasis.torrent'))