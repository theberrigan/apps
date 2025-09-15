# Remedy's Games Extractor

import os, struct, json, zlib, hashlib
from enum import Enum, IntEnum, unique

GAME_DIR = r'G:\Steam\steamapps\common\Max Payne RU'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVES_JSON_PATH = os.path.join(GAME_DIR, 'archives.json')
STATS_JSON_PATH = os.path.join(GAME_DIR, 'stats.json')

ARCHIVE_SIGNATURE = b'Asura'
MIN_SECTION_SIZE = 8


class VirtualReader:
    def __init__ (self, data, name=None):
        self.buffer = data
        self.size = len(data)
        self.cursor = 0
        self.name = name

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self):
        pass

    def close (self):
        self.buffer = None
        self.size = 0
        self.cursor = 0

    def read (self, sizeToRead = None):
        sizeLeft = max(0, self.size - self.cursor)

        if sizeToRead is None or sizeToRead < 0 or sizeToRead >= sizeLeft:
            sizeToRead = sizeLeft

        if sizeToRead == 0:
            return b''

        chunk = self.buffer[self.cursor:self.cursor + sizeToRead]
        self.cursor += sizeToRead

        return chunk

    def tell (self):
        return self.cursor

    def seek (self, offset):
        if type(offset) != int or offset < 0:
            raise OSError('Invalid argument')

        self.cursor = offset

        return self.cursor


def readJson (filePath, defaultValue=None):
    if not os.path.isfile(filePath):
        return defaultValue

    with open(filePath, 'rb') as f:
        try:
            return json.loads(f.read().decode('utf-8').strip())
        except:
            print('Can\'t parse json file:', filePath)
            return defaultValue


def writeJson (filePath, data):
    with open(filePath, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


def md5 (data):
    if data is None:
        return None

    if not isinstance(data, bytes):
        data = str(data).encode('utf-8')

    return hashlib.md5(data).hexdigest().lower()


def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])


def formatSize (size):
    if size >= (1024 ** 3):
        return '{:.1f} Gb'.format(size / (1024 ** 3))
    elif size >= (1024 ** 2):
        return '{:.1f} Mb'.format(size / (1024 ** 2))
    elif size >= 1024:
        return '{:.1f} Kb'.format(size / 1024)
    else:
        return '{} B'.format(size)


def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items


def readNullString (descriptor):
    buff = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'\x00':
            break

        buff += byte

    return buff.decode('utf-8')


def readAlignedString (reader, alignment=4):
    buff = b''

    while True:
        chunk = reader.read(alignment)
        buff += chunk

        if b'\x00' in chunk:
            return buff[:buff.index(b'\x00')].decode('utf-8')


def decompressData (data):
    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


def findStrings (data):
    if not data:
        return

    cursor = 0
    size = len(data)
    start = None

    for i in range(size):
        char = data[i]
        isASCII = 0x20 <= char <= 0x7e
        # isASCII = (0x30 <= char <= 0x39) or (0x41 <= char <= 0x5a) or (0x61 <= char <= 0x7a)

        if isASCII and start is None:
            start = i
        elif not isASCII or i == (size - 1):
            if start is not None:
                if (i - start) >= 4:
                    chunk = data[start:i] 
                    okCharCount = 0

                    for c in chunk:
                        if (0x30 <= c <= 0x39) or (0x41 <= c <= 0x5a) or (0x61 <= c <= 0x7a):
                            okCharCount += 1

                    if (okCharCount / len(chunk)) >= 0.5:
                        print(chunk.decode('utf-8'))

                start = None


# ------------------------------------------------------------------------------------


def unpack (rasPath):
    with open(rasPath, 'rb') as f:
        f.seek(9)

        data = f.read(200000)

        decompressData(data)

        # for i in range(199900):



if __name__ == '__main__': 
    unpack(os.path.join(GAME_DIR, 'x_data.ras'))