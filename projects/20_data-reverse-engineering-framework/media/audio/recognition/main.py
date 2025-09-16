import os
import sys
import sqlite3 as sql

from hashlib import sha1
from operator import itemgetter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

import numpy as np
import matplotlib.mlab as mlab
 
from scipy.ndimage import maximum_filter, binary_erosion, generate_binary_structure, iterate_structure

from bfw.utils import *
from bfw.writer import *
from bfw.native.limits import MAX_U32, I16_BYTES
from bfw.native.base import *
from bfw.native.windows.types import HWND, BOOL, WCHAR, DWORD
from bfw.sfml import SFMLSoundBuffer

from bfw.media.ffmpeg import FFProbe



# TODO: try libav (ffmpeg)
class SampleBuffer:
    @classmethod
    def fromSFMLSoundBuffer (cls, soundBuffer):
        sampleType = CI16

        sampleBuffer = cls()

        # TODO: assert size
        sampleBuffer._rawData      = soundBuffer.samples
        sampleBuffer._sampleType   = sampleType
        sampleBuffer._sampleSize   = cSizeOf(sampleType)
        sampleBuffer._sampleRate   = soundBuffer.sampleRate
        sampleBuffer._channelCount = soundBuffer.channelCount
        sampleBuffer._duration     = soundBuffer.duration

        return sampleBuffer

    @property
    def rawData (self):
        return self._rawData

    @property
    def sampleType (self):
        return self._sampleType

    @property
    def sampleSize (self):
        return self._sampleSize

    @property
    def sampleRate (self):
        return self._sampleRate

    @property
    def channelCount (self):
        return self._channelCount

    @property
    def duration (self):
        return self._duration

    @property
    def rawDataHash (self):
        if not self._rawDataHash:
            self._rawDataHash = sha1(self.rawData).hexdigest().lower()

        return self._rawDataHash

    @property
    def channels (self):
        if not self._channels:
            self._channels = []

            channelCount = self.channelCount
            channels     = self._channels
            samples      = np.frombuffer(self.rawData, np.int16)

            for i in range(channelCount):
                channels.append(samples[i::channelCount])

        return self._channels

    def __init__ (self):
        self._rawData      = None
        self._sampleType   = None
        self._sampleSize   = None
        self._sampleRate   = None
        self._channelCount = None
        self._duration     = None
        self._rawDataHash  = None
        self._channels     = None


DB_SONGS_TABLE_NAME = 'songs'

DB_SONG_ID_FIELD_NAME       = 'song_id'
DB_SONGNAME_FIELD_NAME      = 'song_name'
DB_FINGERPRINTED_FIELD_NAME = 'fingerprinted'
DB_FILE_PCM_HASH_FIELD_NAME = 'pcm_hash'
DB_TOTAL_HASHES_FIELD_NAME  = 'total_hashes'

DB_FINGERPRINTS_TABLE_NAME = 'fingerprints'

DB_HASH_FIELD_NAME   = 'hash'
DB_OFFSET_FIELD_NAME = 'offset'


CREATE_SONGS_TABLE_QUERY = f'''
    CREATE TABLE IF NOT EXISTS `{ DB_SONGS_TABLE_NAME }` (
        `{ DB_SONG_ID_FIELD_NAME }` INTEGER UNIQUE PRIMARY KEY,
        `{ DB_SONGNAME_FIELD_NAME }` VARCHAR(1024) NOT NULL,
        `{ DB_FINGERPRINTED_FIELD_NAME }` TINYINT DEFAULT 0,
        `{ DB_FILE_PCM_HASH_FIELD_NAME }` BINARY(20) NOT NULL,
        `{ DB_TOTAL_HASHES_FIELD_NAME }` INT NOT NULL DEFAULT 0,
        `date_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
'''

# TODO: is it ok? -> BINARY(10)
CREATE_FINGERPRINTS_TABLE_QUERY = f'''
    CREATE TABLE IF NOT EXISTS `{ DB_FINGERPRINTS_TABLE_NAME }` (
        `{ DB_HASH_FIELD_NAME }` BINARY(10) NOT NULL,
        `{ DB_SONG_ID_FIELD_NAME }` INTEGER UNSIGNED NOT NULL,
        `{ DB_OFFSET_FIELD_NAME }` INTEGER UNSIGNED NOT NULL,
        `date_created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(`{ DB_SONG_ID_FIELD_NAME }`, `{ DB_OFFSET_FIELD_NAME }`, `{ DB_HASH_FIELD_NAME }`) ON CONFLICT REPLACE,
        FOREIGN KEY (`{ DB_SONG_ID_FIELD_NAME }`) REFERENCES `{ DB_SONGS_TABLE_NAME }`(`{ DB_SONG_ID_FIELD_NAME }`) ON DELETE CASCADE
    )
'''

CREATE_FINGERPRINTS_TABLE_INDEX_QUERY = f'''
    CREATE INDEX IF NOT EXISTS `ix_{ DB_FINGERPRINTS_TABLE_NAME }_{ DB_HASH_FIELD_NAME }` ON `{ DB_FINGERPRINTS_TABLE_NAME }` (`{ DB_HASH_FIELD_NAME }`)
'''

# -------------

INSERT_SONG_QUERY = f'''
    INSERT INTO `{ DB_SONGS_TABLE_NAME }` (`{ DB_SONGNAME_FIELD_NAME }`, `{ DB_FILE_PCM_HASH_FIELD_NAME }`, `{ DB_TOTAL_HASHES_FIELD_NAME }`) VALUES (?, UNHEX(?), ?)
'''

INSERT_FINGERPRINT_QUERY = f'''
    INSERT INTO `{ DB_FINGERPRINTS_TABLE_NAME }` (`{ DB_SONG_ID_FIELD_NAME }`, `{ DB_HASH_FIELD_NAME }`, `{ DB_OFFSET_FIELD_NAME }`) VALUES (?, UNHEX(?), ?)
'''

# -------------

SELECT_FINGERPRINT_QUERY = f'''
    SELECT `{ DB_SONG_ID_FIELD_NAME }`, `{ DB_OFFSET_FIELD_NAME }`
    FROM `{ DB_FINGERPRINTS_TABLE_NAME }`
    WHERE `{ DB_HASH_FIELD_NAME }` = UNHEX(?)
'''

SELECT_MULTIPLE_FINGERPRINT_QUERY = f'''
    SELECT LOWER(HEX(`{ DB_HASH_FIELD_NAME }`)), `{ DB_SONG_ID_FIELD_NAME }`, `{ DB_OFFSET_FIELD_NAME }`
    FROM `{ DB_FINGERPRINTS_TABLE_NAME }`
    WHERE `{ DB_HASH_FIELD_NAME }` IN ({{}})
'''

SELECT_ALL_FINGERPRINT_QUERY = f'''
    SELECT `{ DB_SONG_ID_FIELD_NAME }`, `{ DB_OFFSET_FIELD_NAME }` FROM `{ DB_FINGERPRINTS_TABLE_NAME }`
'''


class Database:
    @classmethod
    def connect (cls, dbPath):
        return cls(dbPath).open()

    @property
    def path (self):
        return self._path

    @property
    def isConnected (self):
        return self._isConnected

    def __init__ (self, dbPath):
        self._path        = getAbsPath(dbPath)
        self._conn        = None
        self._isConnected = False

    def __del__ (self):
        self.close()

    def _ensureConnected (self):
        if not self.isConnected:
            raise Exception('Database connection not established')

    def open (self):
        if self.isConnected:
            return self

        dbPath = self.path

        assert dbPath, dbPath

        createFileDirs(dbPath)

        self.conn = sql.connect(dbPath, detect_types=sql.PARSE_DECLTYPES)

        self._isConnected = True

        self.execute('PRAGMA journal_mode=WAL')
        self.execute('PRAGMA busy_timeout=300000')
        self.execute('PRAGMA foreign_keys=ON')

        self.execute(CREATE_SONGS_TABLE_QUERY)
        self.execute(CREATE_FINGERPRINTS_TABLE_QUERY)
        self.execute(CREATE_FINGERPRINTS_TABLE_INDEX_QUERY)

        cursor = self.insert(INSERT_SONG_QUERY, ('Rameses B - Revival', '2aae6c35c94fcfb415dbe95f408b9ce91ee846ed', 0))

        songId = cursor.lastrowid

        self.insert(INSERT_FINGERPRINT_QUERY, (songId, '2aae6c35c94fcfb415db', 255))
        self.insert(INSERT_FINGERPRINT_QUERY, (songId, '4fcfb415dbe95f408b9c', 255))
        self.insert(INSERT_FINGERPRINT_QUERY, (songId, 'e95f408b9ce91ee846ed', 255))

        items = self.select(SELECT_FINGERPRINT_QUERY, ('2aae6c35c94fcfb415db',))
        # max: 999 "?"s
        items = self.select(SELECT_MULTIPLE_FINGERPRINT_QUERY.format(','.join([ 'UNHEX(?)', 'UNHEX(?)' ])), ('4fcfb415dbe95f408b9c', 'e95f408b9ce91ee846ed'))
        items = self.select(SELECT_ALL_FINGERPRINT_QUERY)

        print(items)

        # self.execute('''
        #     CREATE TABLE IF NOT EXISTS ya_albums_raw (
        #         id INTEGER NOT NULL PRIMARY KEY, 
        #         album_id INTEGER NOT NULL,  
        #         data BLOB,             
        #         date TIMESTAMP NOT NULL,
        #         error_code INTEGER)
        # ''')

        return self

    def close (self):
        if self.isConnected:
            self.conn.close()
            self.conn = None
            self._isConnected = False

    def vacuum (self):
        self._ensureConnected()

        self.conn.execute('VACUUM')

    def execute (self, query, *args, **kwargs):
        self._ensureConnected()

        self.conn.execute(query, *args, **kwargs)
        self.conn.commit()

    def insert (self, query, *args, cursor=None, commit=True, **kwargs):
        self._ensureConnected()

        if not cursor:
            cursor = self.conn.cursor()

        cursor.execute(query, *args, **kwargs)

        if commit:
            self.conn.commit()

        return cursor

    def select (self, query, *args, **kwargs):
        self._ensureConnected()

        return self.conn.execute(query, *args, **kwargs).fetchall()

    def selectOne (self, query, *args, unpackSingleField=True, **kwargs):
        self._ensureConnected()

        item = self.conn.execute(query, *args, **kwargs).fetchone()

        if item and unpackSingleField and len(item) == 1:
            return item[0]

        return item


def loadAudio (filePath):
    soundBuffer = SFMLSoundBuffer.fromFile(filePath)

    return SampleBuffer.fromSFMLSoundBuffer(soundBuffer)


DEFAULT_WINDOW_SIZE = 4096
DEFAULT_OVERLAP_RATIO = 0.5
DEFAULT_FAN_VALUE = 5
DEFAULT_AMP_MIN = 10
CONNECTIVITY_MASK = 2
PEAK_NEIGHBORHOOD_SIZE = 10
PEAK_SORT = True
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200

def get_2D_peaks (arr2D):
    struct = generate_binary_structure(2, CONNECTIVITY_MASK)

    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D

    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    detected_peaks = local_max != eroded_background

    amps = arr2D[detected_peaks]
    freqs, times = np.where(detected_peaks)

    amps = amps.flatten()

    filter_idxs = np.where(amps > DEFAULT_AMP_MIN)

    freqs_filter = freqs[filter_idxs]
    times_filter = times[filter_idxs]

    return list(zip(freqs_filter, times_filter))

def generate_hashes (peaks):
    idx_freq = 0
    idx_time = 1

    if PEAK_SORT:
        peaks.sort(key=itemgetter(1))

    hashes = []

    for i in range(len(peaks)):
        for j in range(1, DEFAULT_FAN_VALUE):
            if (i + j) < len(peaks):
                freq1 = peaks[i][idx_freq]
                freq2 = peaks[i + j][idx_freq]

                t1 = peaks[i][idx_time]
                t2 = peaks[i + j][idx_time]

                t_delta = t2 - t1

                if MIN_HASH_TIME_DELTA <= t_delta <= MAX_HASH_TIME_DELTA:
                    h = sha1(f"{str(freq1)}|{str(freq2)}|{str(t_delta)}".encode('utf-8'))

                    hashes.append((h.hexdigest(), t1))

    return hashes

def createFingerprint (channelSamples, sampleRate):
    arr2D = mlab.specgram(
        channelSamples,
        NFFT     = DEFAULT_WINDOW_SIZE,
        Fs       = sampleRate,
        window   = mlab.window_hanning,
        noverlap = int(DEFAULT_WINDOW_SIZE * DEFAULT_OVERLAP_RATIO)
    )[0]

    arr2D = 10 * np.log10(arr2D, out=np.zeros_like(arr2D), where=(arr2D != 0))

    local_maxima = get_2D_peaks(arr2D)

    return generate_hashes(local_maxima)


def fingerprintFile (filePath):
    audio = loadAudio(filePath)

    # print(audio.sampleRate, audio.channelCount, audio.duration, audio.rawDataHash, len(audio.channels), len(audio.channels[0]))

    # pjp(FFProbe.getMeta(
    #     r'C:\Projects\_Data_Samples\_audio\.tmp\sample.wav',
    #     includeFormat  = True,
    #     includeStreams = True,
    #     entries        = 'stream_tags:format_tags'
    # ))

    fingerprints = set()

    for channelSamples in audio.channels:
        fp = createFingerprint(channelSamples, audio.sampleRate)

        fingerprints |= set(fp)

    fileName = getFileName(filePath)


        
def _test_ ():
    dbPath = r'D:\Documents\Музыка\!Misc\recognition\music.db'

    Database.connect(dbPath)

    # fingerprintFile(r'D:\Documents\Музыка\OST - Michael McCann - Deus Ex Human Revolution\DLC The Missing Link\22. DLC RestrictedArea Music.mp3')

    # pjp(FFProbe.getMeta(
    #     r'C:\Projects\_Data_Samples\_audio\.tmp\sample.wav',
    #     includeFormat  = True,
    #     includeStreams = True,
    #     entries        = 'stream_tags:format_tags'
    # ))



__all__ = [

]



if __name__ == '__main__':
    _test_()