# Visceral Games Extractor

import os, struct, json, ctypes, zlib
from collections import namedtuple

GAME_DIR = r'G:\Steam\steamapps\common\Dead Space 3'
UNPACK_DIR = os.path.join(GAME_DIR, '.unpack')

def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])

def formatSize (size):
    if size >= (1024 ** 3):
        return '{:.1f}gb'.format(size / (1024 ** 3))
    elif size >= (1024 ** 2):
        return '{:.1f}mb'.format(size / (1024 ** 2))
    elif size >= 1024:
        return '{:.1f}kb'.format(size / 1024)
    else:
        return '{}b'.format(size)

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

def unpack (filePath, unpackDir):
    print(f'Unpacking { os.path.basename(filePath) }')

    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    with open(filePath, 'rb') as f:
        signature = f.read(4)

        if signature != b'BIGH':
            raise Exception('Signature check failed')

        fileSize = readStruct('<I', f)
        itemCount, indexSize = readStruct('>2I', f)

        items = []

        for i in range(itemCount):
            offset, size, unk6 = readStruct('>3I', f)
            items.append((offset, size, unk6))
            # print('{:8X}  {:10}  {:10}  {}'.format(offset, size, unk6, offset % 2048 == 0))

        items = sorted(items, key=lambda item: item[0])

        unkStr1 = f.read(4).decode('ascii')
        unk7 = readStruct('<I', f)

        for item in items:
            f.seek(item[0])
            sign = f.read(4)

            if sign == b'3slo':
                print(*item)


        # for offset, size, unk6 in items:
        #     print(offset, size)

        # print(_total, f.tell())

    print('Done\n')


def unpackAll (gameDir, unpackDir):
    if not os.path.isdir(gameDir):
        raise Exception(f'Game dir does not exist: { gameDir }')

    for item in os.listdir(gameDir):
        itemPath = os.path.join(gameDir, item)

        if item.lower().endswith('.viv') and os.path.isfile(itemPath):
            unpack(itemPath, unpackDir)


if __name__ == '__main__':
    unpackAll(GAME_DIR, UNPACK_DIR)
    # unpack(os.path.join(GAME_DIR, 'bigfile5.viv'), UNPACK_DIR)

'''
b'/MAP'                         1        43.1kb
b'3slo'                      1786         7.6gb
b'({\xba\x9c'                 105       504.0kb
b'\x03\x00\x00\x02'           715       281.1mb
b'\x03\x00\x00\x06'           134       288.0mb
b'\x03\x00\x00\x01'          2101        93.2mb
b'\x03\x00\x00\x04'           334       531.5mb
b'\x03\x00\x00\x08'            53       390.8mb
b'\x03\x0c\x00\x04'             3         9.8mb
b'\x03\n\x00\x04'               5        22.0mb
b'\x03\x04\x00\x04'             1         2.5mb
b'\x03\x06\x00\x04'             3        12.2mb
b'\x01\x00\x00\x00'             1       473.5kb
b'\x03\x02\x00\x04'             3         7.0mb
b'\x03\x0e\x00\x04'             2         4.3mb
b'\x03\x08\x00\x04'             5        15.4mb
b'\x03\x08\x00\x01'             1         1.9mb
b'MVhd'                        24       603.4mb
b'SCHl'                         2        10.1mb
b'12\nn'                        1          282b
'''