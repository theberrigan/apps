# Rise of Tomb Raider Extractor

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *

import os, struct, json, ctypes, zlib
from collections import namedtuple

GAME_DIR = r'G:\Steam\steamapps\common\Rise of the Tomb Raider'

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

def unpack (filePath):
    # print('\nUnpacking', filePath)
    fileSize = os.path.getsize(filePath)

    with open(filePath, 'rb') as f:
        signature = f.read(4)

        if signature != b'TAFS':
            raise Exception('Signature TAFS check failed')

        unk1, unk2, itemCount, *unks = readStruct('<13I', f)

        print(unk1, unk2, itemCount, *unks)

        # index size = 15239 * (4 * 6) = 365736

        f.seek(52) # 0x592B8

        for i in range(itemCount):
            data = readStruct('<6I', f)
            # print(data)

        # 1460
        meta = readStruct('<9I', f)
        print(meta)
        # print(f.tell(), meta[7])

        #f.seek(365812 + 12)

        print('-' * 60)

        for i in range(meta[7]):
            off = f.tell()
            data = readStruct('<5I', f)
            # print(off, '{:10d} {:10d} {:10d} {:10d} {:10d}'.format(*data))

        print(f.tell())

        print('-' * 60)

        f.seek(0x7F937)

        unk3 = readStruct('<I', f)

        print('unk3', unk3)

        for i in range(meta[7]):
            data = readStruct('<6I', f)
            # print(data)

        print(f.tell())

        print('-' * 60)

        # f.seek(0x7F937)

        unkX = readStruct('<B', f)
        print(unkX)

        unks = readStruct('<9I', f)
        print(unks)

        for i in range(unks[7]):
            data = readStruct('<5I', f)
            print('{:10d} {:10d} {:10d} {:10d} {:10d}'.format(*data))
            # print(data)



        print(f.tell())
        # 186245

        '''
        365740 4294580009
        365744 4294967295
        365748 3908
        365752 0
        365756 65536
        365760 146808832
        '''
        #         - 0x594D0 (365776)
        # strings - 0x7F340 (521024)


def unpackAll (filesDir):
    for i, item in enumerate(os.listdir(filesDir)):
        filePath = os.path.join(filesDir, item)

        if item.lower().endswith('.tiger'):
            unpack(filePath)
            # break


if __name__ == '__main__':
    # unpack(os.path.join(GAME_DIR, 'bigfile.000.tiger'))
    # unpackAll(os.path.join(GAME_DIR))
    # print(json.dumps(_tmp, ensure_ascii=False, indent=4))
    decompressFile(r"G:\Steam\userdata\108850163\391220\remote\lastcamp.dat")