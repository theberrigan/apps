# Witcher 3 Extractor

import os, struct, json, ctypes, zlib
from collections import namedtuple

GAME_DIR = r'G:\Steam\steamapps\common\The Witcher 3'

UINT32_MAX = 0xFFFFFFFF

PACK_TYPE_SOUNDS       = 1
PACK_TYPE_SOUNDS_PATCH = 2

_tmp = []

SoundPackHeader = namedtuple('SoundPackHeader', ('type', 'unk2', 'unk3', 'indexOffset', 'itemCount', 'namesOffset', 'namesSize', 'unk4', 'unk5', 'unk6', 'unk7'))
SoundPackItemHeader = namedtuple('SoundPackItemHeader', ('unk1', 'offset', 'size', 'name'))

SoundPatchPackHeader = namedtuple('SoundPatchPackHeader', ('type', 'unk2', 'unk3', 'indexOffset', 'unk4', 'itemCount', 'unk5', 'namesOffset', 'unk6', 'namesSize', 'unk7', 'unk8', 'unk9', 'unk10', 'unk11'))
SoundPatchPackItemHeader = namedtuple('SoundPatchPackItemHeader', ('unk1', 'unk2', 'offset', 'unk3', 'size', 'unk4', 'name'))

def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])

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

def decompressData (data):
    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


def unpackSoundPatchPack (filePath): 
    with open(filePath, 'rb') as f:
        signature = f.read(4)

        if signature != b'CS3W':
            raise Exception('Signature CS3W check failed')

        packHeader = SoundPatchPackHeader(*readStruct('<15I', f))

        if packHeader.type != 2:
            raise Exception('Expected base sound pack, but patch pack given')

        print(packHeader)
        
        f.seek(packHeader.indexOffset)

        items = []

        for i in range(packHeader.itemCount):
            unk1, unk2, offset, unk3, size, unk4 = readStruct('<6I', f)
            items.append([ unk1, unk2, offset, unk3, size, unk4 ])

        f.seek(packHeader.namesOffset)

        for i, item in enumerate(items):
            name = readNullString(f)
            item.append(name)
            items[i] = SoundPatchPackItemHeader(*item)

        # for item in items:
        #     print(item)


def unpackSoundPack (filePath):
    with open(filePath, 'rb') as f:
        signature = f.read(4)

        if signature != b'CS3W':
            raise Exception('Signature CS3W check failed')

        packHeader = SoundPackHeader(*readStruct('<11I', f))

        if packHeader.type != 1:
            raise Exception('Expected base sound pack, but patch pack given')

        print(packHeader)
        
        f.seek(packHeader.indexOffset)

        items = []

        for i in range(packHeader.itemCount):
            unk1, offset, size = readStruct('<3I', f)
            items.append([ unk1, offset, size ])

        f.seek(packHeader.namesOffset)

        for i, item in enumerate(items):
            name = readNullString(f)
            item.append(name)
            items[i] = SoundPackItemHeader(*item)

        # for item in items:
        #     print(item)

        '''

        (                                   (
            0 1,          # pack type           0 2,           # pack type
            1 2112987136, #                     1 2114196480,  # ~ 1
            2 51351336,                         2 38609098,    
            3 354341876,  # index offset        3 1110508438,  # index offset
            4 485,        # item count          4 0,  
            5 354331704,  # names offset        5 486,         # item count
            6 10172,      # names size          6 0,  
            7 34856960,                         7 1110499904,  # names offset
            8 0,                                8 0,  
            9 1131649364,                       9 8534,        # names size
           10 365060041                         10 1, 
        )                                       11 39948288, 
                                                12 0, 
                                                13 725106852, 
                                                14 2319663152
                                            )
        '''


def detectPackType (filePath):
    packType = None

    with open(filePath, 'rb') as f:
        signature = f.read(4)

        if signature == b'CS3W':
            soundPackType = readStruct('<I', f)

            if soundPackType == 1:
                return PACK_TYPE_SOUNDS
                unpackSoundPack(filePath)
            elif soundPackType == 2:
                return PACK_TYPE_SOUNDS_PATCH
                unpackSoundPatchPack(filePath)

    return packType


def unpack (filePath):
    print('\nUnpacking', filePath)

    packType = detectPackType(filePath)

    if packType == PACK_TYPE_SOUNDS:
        unpackSoundPack(filePath)
    elif packType == PACK_TYPE_SOUNDS_PATCH:
        unpackSoundPatchPack(filePath)


def unpackAll (filesDir):
    for i, item in enumerate(os.listdir(filesDir)):
        filePath = os.path.join(filesDir, item)

        if item.lower().endswith('.pc_headerlib'):
            unpack(filePath)
            # break


def walkDir (directory, fileCallback=None, dirCallback=None, recursive=True):
    def walk (directory):
        if not os.path.isdir(directory):
            return

        for item in os.listdir(directory):
            itemPath = os.path.join(directory, item)

            if os.path.isdir(itemPath):
                if dirCallback:
                    dirCallback(itemPath)

                walk(itemPath)

            elif os.path.isfile(itemPath):
                if fileCallback:
                    fileCallback(itemPath)

        return

    return walk(directory)


def collectFilesWithSignatire (baseDir, signature):
    files = []

    def checkFile (filePath):
        with open(filePath, 'rb') as f:
            if f.read(len(signature)) == signature:
                files.append(filePath)

    walkDir(GAME_DIR, checkFile)

    return files


if __name__ == '__main__':
    for filePath in [
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content0\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content1\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content10\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content2\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content3\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content4\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content5\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content6\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\content7\\soundspc.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\patch0\\sounds.cache",
        "G:\\Steam\\steamapps\\common\\The Witcher 3\\content\\patch1\\sounds.cache"
    ]:
        unpack(filePath)

    print()

    # unpack(os.path.join(GAME_DIR, 'content', 'content0', 'soundspc.cache'))
    # unpackAll(os.path.join(GAME_DIR, 'DLC', 'runtime'))
    # print(json.dumps(collectFilesWithSignatire(GAME_DIR, b'CS3W'), ensure_ascii=False, indent=4))

