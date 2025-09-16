# Deus Ex: Human Revolution Extractor

import os, struct, math, sys, re
from collections import namedtuple

GAME_DIR = r"G:\Steam\steamapps\common\Deus Ex Human Revolution Director's Cut"

Item = namedtuple('Item', ('fileIndex', 'nameHash', 'segOffset', 'offset', 'size', 'locale'))

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


def bytesToNullString (byteSeq):
    return ''.join([ chr(b) for b in byteSeq if b > 0 ])


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


def readIndex (gameDir):
    filePath = os.path.join(gameDir, 'BIGFILE.000')

    if not os.path.isfile(filePath):
        raise Exception(f'File BIGFILE.000 does not exist in game directory: { gameDir }')

    items = []

    with open(filePath, 'rb') as f:
        alignment = readStruct('<I', f)  # payload of every file in bytes
        segCount = alignment // 2048     # payload of every file in segments

        basePath = bytesToNullString(f.read(64))
        itemCount = readStruct('<I', f)

        for i in range(itemCount):
            nameHash = readStruct('<I', f)
            items.append(nameHash)

        for i in range(itemCount):            
            size, segOffset, locale, unk1 = readStruct('<4I', f)
            fileIndex = segOffset // segCount
            offset = segOffset % segCount * 2048
            items[i] = Item(fileIndex, items[i], segOffset, offset, size, locale)

    return sorted(items, key=lambda item: item.segOffset)


def getFileIndexFromPath (filePath):
    fileName = os.path.basename(filePath)
    match = re.match(r'^BIGFILE\.(\d{3})$', fileName.upper())
    return int(match.group(1)) if match else None

_x = {}

def unpack (filePath, items=None):
    print(f'Unpacking { os.path.basename(filePath) }')

    fileIndex = getFileIndexFromPath(filePath)

    if fileIndex == None:
        raise Exception(f'Unsupported file: { filePath }')

    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    if not items:
        items = readIndex(os.path.dirname(filePath))

    items = [ item for item in items if item.fileIndex == fileIndex ]

    print(f'Items: { len(items) }')

    if not items:
        return

    with open(filePath, 'rb') as f:
        for item in items:
            f.seek(item.offset)
            signature = f.read(4)

            if signature not in _x:
                _x[signature] = 0

            _x[signature] += 1

            if signature in [ b'Mus!', b'CRID' ]:
                print(signature, item.offset)


    print('Done\n')


def unpackAll (gameDir):
    if not os.path.isdir(gameDir):
        raise Exception(f'Game directory does not exist: { gameDir }')

    files = readIndex(gameDir)

    for item in os.listdir(gameDir):
        itemPath = os.path.join(gameDir, item)

        if os.path.isfile(itemPath) and getFileIndexFromPath(item) != None:
            unpack(itemPath, files)


def unpack2 (filePath):
    fileSize = os.path.getsize(filePath)

    with open(filePath, 'rb') as f:
        while f.tell() < fileSize:
            signature = f.read(4)

            if signature == b'CDRM':
                # unk1 looks like CDRM version
                # unk2 always zeroes?
                unk1, itemCount, unk2 = struct.unpack('<3I', f.read(4 * 3)) 
                items = []

                for i in range(itemCount):
                    # unk1 - falgs, pointer (not same per item)
                    unk1, itemSize = struct.unpack('<II', f.read(4 * 2))
                    print(unk1)

                    items.append((unk1, itemSize))

                    # print(unk1, itemSize)

                for _, itemSize in items:
                    f.read(itemSize)
                    align(f, 16)

                align(f, 2048)
            elif signature == b'\x44\xAC\x00\x00':  # 11728
                print(f.tell()) 
                align(f, 2048)  # skip header?

                # 44361728 159981 (53248)
                # 44414976 119332 (40960)
                # ...
                # 2047557632
                break

                # Item Header
                # unk1 - ?
                # unk2 - 0
                # unk3 - 0
                unk1, itemSize, unk2, unk3 = struct.unpack('<4I', f.read(4 * 4))

                unk4, unk5 = struct.unpack('<2I', f.read(4 * 2))
                str1 = f.read(4).decode('utf-8')
                unk6, unk7, str2size = struct.unpack('<3I', f.read(4 * 3))
                str2 = f.read(str2size).decode('utf-8')
                str3size = struct.unpack('<I', f.read(4))[0]
                str3 = f.read(str3size).decode('utf-8')

                unk8, unk9 = struct.unpack('<IH', f.read(4 + 2))

                unk10, unk11, unk12, str4size = struct.unpack('<IHIIII', f.read(4 * 5 + 2))
                str4 = f.read(str4size).decode('utf-8')
                unk13, unk14, unk15, str5size = struct.unpack('<HIII', f.read(4 * 3 + 2))
                str5 = f.read(str5size).decode('utf-8')
                unk16, unk17, unk18, str6size = struct.unpack('<HIII', f.read(4 * 3 + 2))
                str6 = f.read(str6size).decode('utf-8')
                unk19, unk20, unk21, str7size = struct.unpack('<HIII', f.read(4 * 3 + 2))
                str7 = f.read(str7size).decode('utf-8')
                unk22, unk23, unk24, str8size = struct.unpack('<HIII', f.read(4 * 3 + 2))
                str8 = f.read(str8size).decode('utf-8')
                unk25, unk26, unk27, str9size = struct.unpack('<HIII', f.read(4 * 3 + 2))
                

                # IHIII
                # I FxObject
                # HII
                # I FxAnim
                # HII
                # I FxAnimSet
                # HII
                # I FxNamedObject
                # HII
                # I FxName
                # HII
                # I FxAnimCurve
                # HII
                # I FxAnimGroup
                # HI
                # I det1_fw02_3tr_fu_01
                # I caucasian_01_head_a
                # I DET1_FW02_3TR_FU_01


                print(unk4, unk5, str1, unk6, unk7, str2, str3, unk8, unk9, unk10, unk11, unk12)
                print(str4, unk13, unk14, unk15)
                print(str5, unk16, unk17, unk18)
                print(str6, unk19, unk20, unk21)
                print(str7, unk22, unk23, unk24)
                print(str8, unk25, unk26, unk27)
                print(f.tell())
                break

                # 44414976 - 44361728 = 53248
            else:
                print('Unknown type:', signature, f.tell())
                break


if __name__ == '__main__':
    unpackAll(GAME_DIR)
    # unpack(os.path.join(GAME_DIR, 'BIGFILE.000'))
    for k, v in _x.items():
        print(k, v)


'''
b'<dx3' 1
b'\x1f\x00\x00\x00' 1
b'CDRM' 15552
b'FSB4' 157
b'Mus!' 157
b'D\xac\x00\x00' 87401
b'\x80\xbb\x00\x00' 10
b'"V\x00\x00' 11
b'CRID' 63
b'\xeb\x02\x00\x00' 1
b'4101' 1
b'746\r' 1
b'\x00}\x00\x00' 1
b'PCD9' 1
b'\x00\x00\x00\x00' 1
b'\x01\x00\x00\x00' 1
b'\x02\x00\x00\x00' 1
b'\x03\x00\x00\x00' 1
b'\x04\x00\x00\x00' 1
b'\x05\x00\x00\x00' 1
b'\x06\x00\x00\x00' 1
b'1,45' 1
b'6,26' 1
b'1,17' 1
b'6,58' 1
b'1,91' 1
b'4,49' 1
b'3,18' 1
'''