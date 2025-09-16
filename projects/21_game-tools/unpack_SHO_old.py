# Silent Hill Origins Extractor

import os, struct, math, sys, re, zlib, json, subprocess, math
from pathlib import Path
from collections import namedtuple

GAME_DIR = r'G:\Games\SHO'
USER_DIR = os.path.join(GAME_DIR, 'PSP_GAME', 'USRDIR')
UNPACK_DIR = os.path.join(GAME_DIR, '.unpack')

def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])

def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items

def decodeJson (data):
    try:
        if isinstance(data, bytes):
            data = data.decode('utf-8')

        return json.loads(data)
    except:
        return None

def readNullString (descriptor):
    buff = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'\x00':
            break

        buff += byte

    return buff.decode('utf-8')


def bytesToNullString (byteSeq):
    return ''.join([ chr(b) for b in byteSeq if b > 0 ])


def decompressData (data):
    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


def align (descriptor, boundry):
    descriptor.seek(math.ceil(descriptor.tell() / boundry) * boundry)


def findPattern (f, pattern, fromPos = 0, toPos = -1):
    maxBuffSize = 64 * 1024  # 64kb
    patternSize = len(pattern)
    wasPos = f.tell()
    fileSize = f.seek(0, 2)

    toPos = fileSize if toPos < 0 else min(toPos, fileSize)
    fromPos = min(toPos, max(fromPos, 0))

    if patternSize == 0 or (toPos - fromPos) < patternSize:
        f.seek(wasPos)
        return []

    f.seek(fromPos)

    offsets = []
    buffTail = b''

    while True:
        cursorPos = f.tell()
        tailSize = len(buffTail)
        buffBase = cursorPos - tailSize
        readSize = min(maxBuffSize - tailSize, toPos - cursorPos)
        buffSize = tailSize + readSize

        if buffSize <= patternSize:
            break

        buff = buffTail + f.read(readSize)
        buffTail = b''

        assert buffSize == len(buff), 'Expected buffer size is wrong'

        buffCursor = 0

        while True:
            try:
                foundIndex = buff.index(pattern, buffCursor)
                offsets.append(buffBase + foundIndex)
                buffCursor = foundIndex + patternSize
            except:
                buffCursor = buffSize

            if (buffSize - buffCursor) < patternSize:
                buffTail = buff[-(patternSize - 1):]
                break

    f.seek(wasPos)

    return offsets


def formatSize (size):
    if size >= (1024 ** 3):
        return '{:.1f}gb'.format(size / (1024 ** 3))
    elif size >= (1024 ** 2):
        return '{:.1f}mb'.format(size / (1024 ** 2))
    elif size >= 1024:
        return '{:.1f}kb'.format(size / 1024)
    else:
        return '{}b'.format(size)


# ------------------------------------------------------------------------------


class Item:
    def __init__ (self, nameRelOffset=None, offset=None, compSize=None, decompSize=None, name=None):
        self.nameRelOffset = nameRelOffset
        self.offset = offset
        self.compSize = compSize
        self.decompSize = decompSize
        self.name = name


def unpack (filePath, unpackDir):
    print(f'Unpacking { os.path.basename(filePath) }')

    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    with open(filePath, 'rb') as f:
        signature = f.read(4)

        if signature != b'A2.0':
            raise Exception('Signature check failed')

        itemCount, contentOffset, namesOffset, namesSize = readStruct('<4I', f)

        items = []

        for i in range(itemCount):
            nameRelOffset, offset, compSize, decompSize = readStruct('<4I', f)
            items.append(Item(nameRelOffset, offset, compSize, decompSize))

        f.seek(namesOffset)

        for item in items:
            f.seek(namesOffset + item.nameRelOffset)
            item.name = readNullString(f)

        for item in items:
            f.seek(item.offset)
            data = f.read(item.compSize)

            if item.decompSize > 0:
                data = decompressData(data)
                assert len(data) == item.decompSize

            with open(os.path.join(unpackDir, item.name), 'wb') as outFile:
                outFile.write(data)

    print('Done\n')


def unpackAll (gameDir, unpackDir):
    if not os.path.isdir(gameDir):
        raise Exception(f'Game dir does not exist: { gameDir }')

    def walk (directory):
        for item in os.listdir(directory):
            itemPath = os.path.join(directory, item)

            if os.path.isdir(itemPath):
                walk(itemPath)
            elif item.lower().endswith('.arc') and os.path.isfile(itemPath):
                itemRelPath = os.path.relpath(itemPath, gameDir)
                itemUnpackDir = os.path.join(unpackDir, itemRelPath)
                itemUnpackDir = os.path.normpath(os.path.abspath(itemUnpackDir))

                os.makedirs(itemUnpackDir, exist_ok=True)

                unpack(itemPath, itemUnpackDir)

    walk(gameDir)


def convertAudio (srcPath, dstPath):
    proc = subprocess.run([ 'ffprobe', '-v', 'quiet', '-show_format', '-show_streams', '-select_streams', 'a:0', '-print_format', 'json', srcPath ], shell=True, stdout=subprocess.PIPE)
    data = decodeJson(proc.stdout)

    assert data, f'Failed to ffprobe file: { srcPath }'

    # print(json.dumps(data, ensure_ascii=False, indent=4))

    stream     = data['streams'][0]
    sampleRate = int(stream['sample_rate'])
    bitRate    = int(stream['bit_rate'])
    channels   = stream['channels']
    '''
    vbrRanges  = [ (45, 85, 9), (70, 105, 8), (80, 120, 7), (100, 130, 6), (120, 150, 5), (140, 185, 4), (150, 195, 3), (170, 210, 2), (190, 250, 1), (220, 260, 0) ] 
    brArgName  = '-b:a'
    brArgValue = '320k'

    for minBitRate, maxBitRate, rangeIndex in vbrRanges:
        if minBitRate <= math.ceil(bitRate / 1000) <= maxBitRate: 
            brArgName = '-q:a'
            brArgValue = str(rangeIndex)
            break

    # proc = subprocess.run([ 'ffmpeg', '-i', srcPath, '-y', '-v', 'quiet', '-vn', '-ac', str(channels), '-ar', str(sampleRate), brArgName, brArgValue, dstPath ], shell=True, stdout=subprocess.PIPE)

    print(' '.join([ 'ffmpeg', '-i', srcPath, '-y', '-v', 'quiet', '-vn', '-ac', str(channels), '-ar', str(sampleRate), brArgName, brArgValue, dstPath ]))
    '''

    bitRates   = [ 64, 80, 96, 112, 128, 160, 192, 224, 256, 320 ]
    dstBitRate = bitRates[-1]

    for n in bitRates:
        if (n * 1000) >= bitRate:
            dstBitRate = n
            break

    proc = subprocess.run([ 'ffmpeg', '-i', srcPath, '-y', '-v', 'quiet', '-vn', '-ac', str(channels), '-ar', str(sampleRate), '-b:a', f'{ dstBitRate }k', dstPath ], shell=True, stdout=subprocess.PIPE)

def convertAudioAll (gameDir, unpackDir):
    if not os.path.isdir(gameDir):
        raise Exception(f'Game dir does not exist: { gameDir }')

    def walk (directory):
        for item in os.listdir(directory):
            itemPath = os.path.join(directory, item)

            if os.path.isdir(itemPath):
                walk(itemPath)
            elif item.lower().endswith('.rws') and os.path.isfile(itemPath):
                itemRelPath = os.path.relpath(itemPath, gameDir)
                dstPath = os.path.join(unpackDir, itemRelPath)
                dstPath = os.path.splitext(dstPath)[0] + '.mp3'
                dstPath = os.path.normpath(os.path.abspath(dstPath))
                
                os.makedirs(os.path.dirname(dstPath), exist_ok=True)

                convertAudio(itemPath, dstPath)

    walk(gameDir)


if __name__ == '__main__':
    convertAudioAll(GAME_DIR, UNPACK_DIR)
    # unpackAll(GAME_DIR, UNPACK_DIR)
    # unpack(os.path.join(USER_DIR, 'IGC.ARC'), UNPACK_DIR)
    # unpack(os.path.join(USER_DIR, 'SH.ARC'), UNPACK_DIR)