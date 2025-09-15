# Deus Ex Mankind Divided Extractor

import os, struct, json, ctypes, zlib
from collections import namedtuple

GAME_DIR = r'G:\Steam\steamapps\common\Deus Ex Mankind Divided'

UINT32_MAX = 0xFFFFFFFF

_tmp = []

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

        if signature != b'BILH':
            raise Exception('Signature BILH check failed')

        # header
        # unused1 - always 0
        # unused2 - always UINT32_MAX
        # unused3 - always UINT32_MAX
        subHeaderSize, unused1, contentSize, unused2, unused3 = readStruct('<5I', f)
        # print(subHeaderSize, unused1, contentSize, unused2, unused3)

        _beforeSubheader = f.tell()

        # subheader
        if subHeaderSize > 0:
            # itemCount - 1 | 2
            # unk6 - always 0
            # unk7 - 0 | 16
            # unk8 - always 20
            # unk9 - 28 | 16777216 | 2147483648
            # combination:
            # - itemCount == 1 and unk7 == 16 - always
            # - itemCount == 2 and unk7 == 0 and unk9 == 28  - always
            itemCount = readStruct('<I', f)
            assert itemCount in [1, 2]

            '''
            unk6, unk7, unk8, unk9, unk10 = readStruct('<3I2H', f)
            assert unk6 == 0 and unk8 == 20
            print(unk7, unk9, unk10)
            return
            '''

            if itemCount == 1:
                buff = formatBytes(f.read(4 * 4))
                # unk5 = None
                # unk6, unk7, unk8, unk9 = readStruct('<4I', f)
                # unk10 = None
                # unk11 = None
            else:
                buff = formatBytes(f.read(4 * 6))
                # unk5, unk6, unk7, unk8, unk9, unk10, unk11 = readStruct('<5I2H', f)
                # print('{} {:2X} {:8X} {:8X} {:4X} {:4X}'.format(itemCount, unk7, unk9, unk10, unk11, unk12))
                # print(unk6, unk7, unk8, unk9, unk10, unk11)

            if buff not in _tmp:
                _tmp.append(buff)
                print(buff)

            # string1 = readNullString(f)
            # print(string1)

        # f.seek(_beforeSubheader + subHeaderSize)
        # signature = f.read(4)

        # assert signature == b'BIN1', 'Signature BIN1 check failed'

        # unk1 = readStruct('<I', f)

        # assert unk1 == 67584, 'Unknown uint32 after BIN1'

        # while f.tell() < 0x153:
        #     print(readStruct('<I', f))


def unpackAll (filesDir):
    for i, item in enumerate(os.listdir(filesDir)):
        filePath = os.path.join(filesDir, item)

        if item.lower().endswith('.pc_headerlib'):
            unpack(filePath)
            # break


if __name__ == '__main__':
    # unpack(os.path.join(GAME_DIR, 'runtime', '83CD999107E651641915FF3FA3B14D09.pc_headerlib'))
    unpackAll(os.path.join(GAME_DIR, 'DLC', 'runtime'))
    # print(json.dumps(_tmp, ensure_ascii=False, indent=4))


    '''
    BIN1
    [[assembly:/scenes/game/40_london/00_lon_vista/_lon_vista.overlay].pc_resourcelibdef].pc_headerlib
    [[assembly:/scenes/game/40_london/00_lon_vista/lon_vista_towers.overlay].pc_resourcelibdef](0000).pc_resourcelib
    [[assembly:/scenes/game/40_london/00_lon_vista/lon_vista_towers.overlay].pc_resourcelibdef](0000).pc_resourcelib
    [assembly:/scenes/game/40_london/00_lon_vista/lon_vista_towers.overlay].pc_entitytemplate
    BILR

    exts = []
    files = []

    for item in os.listdir(os.path.join(GAME_DIR, 'runtime')):
        filePath = os.path.join(GAME_DIR, 'runtime', item)
        ext = os.path.splitext(filePath)[1].lower()

        if ext not in exts:
            exts.append(ext)

        if ext == '.pc_headerlib':
            files.append((item, os.path.getsize(filePath)))

    files = sorted(files, key=lambda item: item[1]) 

    print(exts)
    print(files[0])
    print(files[1])
    print(files[int(len(files) / 2)])
    print(files[int(len(files) / 2) + 1])
    print(files[-2])
    print(files[-1])
    '''

'''

Exts: ['.pc_headerlib', '.pc_fsbm', '.pc_binkvid', '.pc_fsb', '.archive']


size      sample
-------------------------------------------------------
1220      83CD999107E651641915FF3FA3B14D09.pc_headerlib
1301      C3583FF69A124E8C304E82EE99F313DF.pc_headerlib
29890     24524167A4E41AE07238A52118E05B49.pc_headerlib
30163     A6B38767483D1552265911E1CD1FEE26.pc_headerlib
27157748  BFEB0E8DCDF3267F8EB00A468DD8D2E2.pc_headerlib
46343913  4D93039E4D9A13B77CECD44E7F036367.pc_headerlib


unk5|7|9         cnt   samples
------------------------------------------------------------------------------------------------------------------------------------------------------------------
1|16|16777216    1405  00150427B3474AD286E38730E60FB032.pc_headerlib, 001BD34780935073B55BD2564FFF699C.pc_headerlib, 0044C22E9C72408A327EFD7C85A80C01.pc_headerlib
2|0|28           49    0C112228B758E1921B6B1C72E7426AAF.pc_headerlib, 11AE90CBB76AFBD4E90F666335B11C5E.pc_headerlib, 191E636C0F7A7BD6EAFA4EAF6D241702.pc_headerlib
1|16|2147483648  11    0EFA3489014E546F0E538F01035D24E9.pc_headerlib, 1E716CCBC2523DDE7463C80EE80E758C.pc_headerlib, 591201B9C499FF278B0BA3E57703A257.pc_headerlib


subHdr  cnt
------------------------------------------------------------------------------------------------------------------------------------------------------------------
yes     1465  00150427B3474AD286E38730E60FB032.pc_headerlib 001BD34780935073B55BD2564FFF699C.pc_headerlib 0044C22E9C72408A327EFD7C85A80C01.pc_headerlib
no      7     09382868F0EE1CDA1BA6BEE48D74EE22.pc_headerlib 12F4A26A629843106578ACDBDDA5224E.pc_headerlib 3133BD95C91CCB418964E1B8BA3BB23D.pc_headerlib
00 00 00 00 10 00 00 00 14 00 00 00 00 00 00 01
00 00 00 00 10 00 00 00 14 00 00 00 00 00 00 80
00 00 00 00 10 00 00 00 14 00 00 00             00 00 00 01
00 00 00 00 00 00 00 00 14 00 00 00 1C 00 00 00 00 00 00 01 57 00 00 80
00 00 00 00 10 00 00 00 14 00 00 00             00 00 00 80
00 00 00 00 00 00 00 00 14 00 00 00 1C 00 00 00 00 00 00 01 55 00 00 80
00 00 00 00 00 00 00 00 14 00 00 00 1C 00 00 00 00 00 00 01 6F 00 00 80
00 00 00 00 00 00 00 00 14 00 00 00 1C 00 00 00 00 00 00 01 58 00 00 80
00 00 00 00 00 00 00 00 14 00 00 00 1C 00 00 00 00 00 00 01 54 00 00 80



---------------------------------------------------------------------------------------------

{
    "unk5": {
        "1": [
            "00150427B3474AD286E38730E60FB032.pc_headerlib",
            "001BD34780935073B55BD2564FFF699C.pc_headerlib",
            "0044C22E9C72408A327EFD7C85A80C01.pc_headerlib",            
            1413 items...
        ],
        "2": [
            "0C112228B758E1921B6B1C72E7426AAF.pc_headerlib",
            "11AE90CBB76AFBD4E90F666335B11C5E.pc_headerlib",
            "191E636C0F7A7BD6EAFA4EAF6D241702.pc_headerlib",            
            46 items...
        ]
    },
    "unk7": {
        "16": [
            "00150427B3474AD286E38730E60FB032.pc_headerlib",
            "001BD34780935073B55BD2564FFF699C.pc_headerlib",
            "0044C22E9C72408A327EFD7C85A80C01.pc_headerlib",            
            1413 items...
        ],
        "0": [
            "0C112228B758E1921B6B1C72E7426AAF.pc_headerlib",
            "11AE90CBB76AFBD4E90F666335B11C5E.pc_headerlib",
            "191E636C0F7A7BD6EAFA4EAF6D241702.pc_headerlib",
            46 items...
        ]
    },
    "unk9": {
        "16777216": [
            "00150427B3474AD286E38730E60FB032.pc_headerlib",
            "001BD34780935073B55BD2564FFF699C.pc_headerlib",
            "0044C22E9C72408A327EFD7C85A80C01.pc_headerlib",
            1402 items...
        ],
        "28": [
            "0C112228B758E1921B6B1C72E7426AAF.pc_headerlib",
            "11AE90CBB76AFBD4E90F666335B11C5E.pc_headerlib",
            "191E636C0F7A7BD6EAFA4EAF6D241702.pc_headerlib",
            46 items...
        ],
        "2147483648": [
            "0EFA3489014E546F0E538F01035D24E9.pc_headerlib",
            "1E716CCBC2523DDE7463C80EE80E758C.pc_headerlib",            
            9 items...
        ]
    }
}
'''