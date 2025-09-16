# Deus Ex: Human Revolution Extractor

import os, struct, math, sys, re, zlib
from collections import namedtuple

GAME_DIR = r"G:\Steam\steamapps\common\Resident Evil Village BIOHAZARD VILLAGE Gameplay Demo"

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


def decompressData (data, addHeader = True):
    if addHeader:
        data = b'\x78\xda' + data

    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data
# ------------------------------------------------------------------------------

Item = namedtuple('Item', ('unk1', 'offset', 'compSize', 'decompSize', 'flags', 'unk2'))

def bytesToString (byteSeq):
    items = []
    isLastChar = None

    for byte in byteSeq:
        if (48 <= byte <= 57) or (65 <= byte <= 90) or (97 <= byte <= 122) or chr(byte) in '_.!':
            if isLastChar == True:
                items[-1] += chr(byte)
            else:
                items.append(chr(byte))
                isLastChar = True
        else:
            isLastChar = False            
            items.append('{:02X}'.format(byte))

    return '_'.join(items)


def unpack (filePath, items=None):
    print(f'Unpacking { os.path.basename(filePath) }')

    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    # content: 1685052
    items = []
    signs = {
        'TEX_00': 16859,
        'MESH': 2705,
        'MCOL': 2439,
        'USR_00': 2299,
        'MDF_00': 2124,
        'SCN_00': 1478,
        'RBM_20': 1189,
        'PFB_00': 673,
        'RSZ_00': 654,
        'BKHD': 529,
        'efxr': 432,
        'BHVT': 389,
        'E6_01_00_00': 356,
        '40_00_S_00': 320,
        '2A_00_00_00': 296,
        '.SVU': 286,
        'AKPK': 280,
        '03_00_00_00': 268,
        'FOL_00': 256,
        'SDF_00': 248,
        'CLIP': 194,
        '97_1A_06_00': 140,
        'TERR': 134,
        'BODY': 109,
        'NPRB': 77,
        '11_00_00_00': 66,
        'RCOL': 59,
        '00_00_80_3E': 34,
        '27_00_00_00': 33,
        'FBFO': 28,
        'RTEX': 22,
        '02_00_00_00': 20,
        'CFIL': 17,
        'GCLO': 13,
        '10_00_00_00': 6,
        'CA_01_00_00': 5,
        'AIMP': 4,
        'SST!': 3,
        '0_26_B2_u': 2,
        '88_00_00_00': 2,
        '00_00_00_00': 2,
        'LOD_00': 2,
        'SSS_00': 2,
        'DEF_20': 2,
        'FXCT': 2,
        '18_00_00_00': 2,
        'CDEF': 2,
        '01_00_00_00': 2,
        'DBLC': 2,
        'REMV': 2,
        'lfar': 2,
        'FINF': 2,
        '17_04_00_00': 1,
        'GBUF': 1,
        'F5_86_7': 1,
        'GNPT': 1,
        '12_00_01_03': 1,
        '01_01_01_01': 1,
        '28_28_66': 1,
        'g_14_FA_H': 1,
        '05_05_7B_7B': 1,
        '02_02_06_06': 1,
        '09_09_08_08': 1,
        'C7_03_2B_2C': 1,
        'C2_t_90_!': 1,
        'BA_B1_E7_F1': 1,
        'II_FF_FF': 1,
        '!_8E_07_27': 1,
        'FF_1A_Q.': 1,
        '20_E2_HF': 1,
        '01_01_00_00': 1,
        'A2_A0_0B_03': 1,
        '09_09_1A_1A': 1,
        '92_7D_Ko': 1,
        '22_T7_3C': 1,
        'PSOP': 1,
        'F4_05_9F_AA': 1,
        'IES_00': 1,
        '00_00_20_40': 1,
        'PCTR': 1,
        'CF_EF_00_00': 1,
        '96_EC_00_00': 1,
        'AIMA': 1,
        '9D_10_00_00': 1,
        'ucls': 1,
    }

    unpackDir = os.path.join(os.path.dirname(filePath), '.unpack')


    with open(filePath, 'rb') as f:
        signature, unk1, itemCount, unk2 = readStruct('<4sIII', f)
        print(signature, unk1, itemCount)

        for i in range(itemCount):
            items.append(Item(*readStruct('<6Q', f)))

        items = sorted(items, key=lambda item: item[1])

        for item in items:
            unk1, offset, compSize, decompSize, flags, unk2 = item

            f.seek(offset)
            data = f.read(compSize)

            if (flags & 1):
                data = decompressData(data)
                assert len(data) == decompSize

            sign = bytesToString(data[:4])
            dirName = '{:05}. {}'.format(signs[sign], sign)            
            fileUnpackDir = os.path.join(unpackDir, dirName)
            os.makedirs(fileUnpackDir, exist_ok=True)
            outFilePath = os.path.join(fileUnpackDir, '{:016X}_{}.bin'.format(offset, flags))

            with open(outFilePath, 'wb') as f2:
                f2.write(data)

            # print(outFilePath)

            print('{:16X} {:12} {:12} {:12} {:6} {:16X}'.format(unk1, offset, compSize, decompSize, flags, unk2))

        print(f.tell())

    print('Done\n')


def parseSceneFile (filePath):
    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    with open(filePath, 'rb') as f:
        signature = readStruct('<4s', f)

        if signature != b'SCN\x00':
            raise Exception('Signature check failed')






if __name__ == '__main__':
    # unpack(os.path.join(GAME_DIR, 're_chunk_000.pak'))
    # parseSceneFile(os.path.join(GAME_DIR, '.unpack', '01478. SCN_00__refs_MDFs', '00000001B4387830_1.bin'))

    with open(os.path.join(GAME_DIR, '.unpack', '16859. TEX_00', '0000000000D6B294_1025.bin'), 'rb') as f:
        data = f.read()

        for i in range(1024):
            try:
                decompressData(data[i:])
                print(1)
                break
            except Exception as e:
                pass

'''
b'TEX\x00'           16859
b'MESH'              2705
b'MCOL'              2439
b'USR\x00'           2299
b'MDF\x00'           2124
b'SCN\x00'           1478
b'RBM '              1189
b'PFB\x00'           673
b'RSZ\x00'           654
b'BKHD'              529    # Wwise Bank: https://wiki.xentax.com/index.php/Wwise_SoundBank_(*.bnk)#BKHD_section
b'efxr'              432
b'BHVT'              389
b'\xe6\x01\x00\x00'  356
b'@\x00S\x00'        320
b'*\x00\x00\x00'     296
b'.SVU'              286
b'AKPK'              280
b'\x03\x00\x00\x00'  268
b'FOL\x00'           256
b'SDF\x00'           248
b'CLIP'              194
b'\x97\x1a\x06\x00'  140
b'TERR'              134
b'BODY'              109
b'NPRB'              77
b'\x11\x00\x00\x00'  66
b'RCOL'              59
b'\x00\x00\x80>'     34
b"'\x00\x00\x00"     33
b'FBFO'              28
b'RTEX'              22
b'\x02\x00\x00\x00'  20
b'CFIL'              17
b'GCLO'              13
b'\x10\x00\x00\x00'  6
b'\xca\x01\x00\x00'  5
b'AIMP'              4
b'SST!'              3
b'0&\xb2u'           2
b'\x88\x00\x00\x00'  2
b'\x00\x00\x00\x00'  2
b'LOD\x00'           2
b'SSS\x00'           2
b'DEF '              2
b'FXCT'              2
b'\x18\x00\x00\x00'  2
b'CDEF'              2
b'\x01\x00\x00\x00'  2
b'DBLC'              2
b'REMV'              2
b'lfar'              2
b'FINF'              2
b'\x17\x04\x00\x00'  1
b'GBUF'              1
b'F5\x867'           1
b'GNPT'              1
b'\x12\x00\x01\x03'  1
b'\x01\x01\x01\x01'  1
b'((66'              1
b'g\x14\xfaH'        1
b'\x05\x05{{'        1
b'\x02\x02\x06\x06'  1
b'\t\t\x08\x08'      1
b'\xc7\x03+,'        1
b'\xc2t\x90!'        1
b'\xba\xb1\xe7\xf1'  1
b'II\xff\xff'        1
b"!\x8e\x07'"        1
b'\xff\x1aQ.'        1
b' \xe2HF'           1
b'\x01\x01\x00\x00'  1
b'\xa2\xa0\x0b\x03'  1
b'\t\t\x1a\x1a'      1
b'\x92}Ko'           1
b'"T7<'              1
b'PSOP'              1
b'\xf4\x05\x9f\xaa'  1
b'IES\x00'           1
b'\x00\x00 @'        1
b'PCTR'              1
b'\xcf\xef\x00\x00'  1
b'\x96\xec\x00\x00'  1
b'AIMA'              1
b'\x9d\x10\x00\x00'  1
b'ucls'              1
'''