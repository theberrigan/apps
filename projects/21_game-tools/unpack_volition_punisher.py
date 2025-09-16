import zlib, os, json, struct, math


def decompressFileZlib (filePath):
    data = None

    with open(filePath, 'rb') as f:
        data = f.read()

    decompObj = zlib.decompressobj() # wbits=zlib.MAX_WBITS
    data = decompObj.decompress(data)

    with open(filePath + '.decompressed', 'wb') as f:
        f.write(data)

        
def scan (filePath):
    fileSize = os.path.getsize(filePath)

    with open(filePath, 'rb') as f:
        while f.tell() < fileSize:
            print(struct.unpack('<I', f.read(4))[0])

'''
def unpack1 (filePath):
    with open(filePath, 'rb') as f:
        if f.read(4) != b'\xCE\x0A\x89\x51':
            raise Exception('Wrong signature')

        version, unk1, size, unk2, indexEntriesCount, indexSize, namesSize, unk4, size2 = struct.unpack('<9I', f.read(4 * 9))

        print(version, unk1, size, unk2, indexEntriesCount, indexSize, namesSize, unk4, size2)
        print('-' * 100)

        index = []

        for i in range(indexEntriesCount):
            nameOffset, unk2, relOffset, decompSize, compSize, unk4 = struct.unpack('<6I', f.read(4 * 6))
            index.append((nameOffset, unk2, relOffset, decompSize, compSize, unk4))
            print(nameOffset, unk2, relOffset, decompSize, compSize, unk4)

        print('-' * 100)

        namesBuff = f.read(namesSize)

        for item in index:
            name = b''
            byteIndex = 0

            while True:
                byte = bytes([ namesBuff[item[0] + byteIndex] ])

                if byte == b'\x00':
                    break

                name += byte
                byteIndex += 1

            name = name.decode('utf-8')

            print(name)

            zobj = zlib.decompressobj()
            data = zobj.decompress(f.read(item[4]))

        # print(f.tell())
        # print(zlib.decompress(f.read(684)))

        # index
        # names
        # bin-content
'''


def unpack (filePath):
    filePath = os.path.abspath(filePath)
    unpackDir = os.path.join(os.path.dirname(filePath), '_' + os.path.basename(filePath))

    os.makedirs(unpackDir, exist_ok=True)

    with open(filePath, 'rb') as f:
        if f.read(4) != b'\xCE\x0A\x89\x51':
            raise Exception('Wrong signature')

        version, entryCount, contentSize = struct.unpack('<3I', f.read(4 * 3))

        f.seek(0x800)

        items = []

        for i in range(entryCount):
            startPos = f.tell()
            name = b''

            while True:
                byte = f.read(1)

                if byte == b'\x00':
                    break

                name += byte

            f.seek(startPos + max(24, math.ceil(len(name) / 4) * 4))            

            name = name.decode('utf-8')

            decompSize, compSize = struct.unpack('<2I', f.read(4 * 2))

            items.append((name, decompSize, compSize))

        f.seek(0x800 + math.ceil((f.tell() - 0x800) / 2048) * 2048)

        for item in items:
            startPos = f.tell()
            name, decompSize, compSize = item

            # print(name, f.tell(), decompSize, compSize)

            data = f.read(compSize)

            if compSize != decompSize:
                try:
                    decompObj = zlib.decompressobj()
                    data = decompObj.decompress(data)
                except:
                    print('zlib error:', filePath, startPos, compSize)

            with open(os.path.join(unpackDir, name), 'wb') as f2:
                f2.write(data)

            f.seek(startPos + math.ceil((f.tell() - startPos) / 2048) * 2048)


def unpackAll (rootDir):
    for item in os.listdir(rootDir):
        itemPath = os.path.join(rootDir, item)

        if os.path.isfile(itemPath):
            if os.path.splitext(itemPath)[1].lower() == '.vpp':
                print(item)
                unpack(itemPath)
        elif os.path.isdir(itemPath):
            unpackAll(itemPath)


def scanExts (rootDir, exts={}):
    for item in os.listdir(rootDir):
        itemPath = os.path.join(rootDir, item)

        if os.path.isfile(itemPath):
            ext = os.path.splitext(itemPath)[1].lower()

            if ext in [ '.py', '.vpp', '.bik' ]:
                continue

            if ext not in exts:
                exts[ext] = 1
            else:
                exts[ext] += 1

        elif os.path.isdir(itemPath):
            exts = scanExts(itemPath, exts)

    return exts


'''
.rfa 50453
.ceg 1706
.dbr 97
.rfl 97
.tbl 306
.rxe 1884
.rxm 1456
.rmx 838
.rxc 537
.wav 10745
.btz 143
.vf2 18
.sys 1
.ico 1
.ver 1
.bpc 65
.mpc 23
.pso 7
.vso 3
.tbx 11
'''

# unpack('./shaders.vpp_pc')
# decompressFileZlib('./x.zlib')
# unpack('./shipping/nycrack/nycrack2.vpp')
# unpack('./shipping/Chop/Chop3.vpp')
# unpackAll('./')

for k, v in scanExts('./').items():
    print(k, v)