import zlib, os, struct, math

'''
offset = -1

for item in os.listdir('./'):
    path = './' + item

    if not os.path.isfile(path) or not item.lower().endswith('.ff'):
        continue

    print(item, round(os.path.getsize(path) / 1024 / 1024))
    data = None

    with open(path, 'rb') as f:
        data = f.read()

    for i in range(32):
        try:
            decompressed = zlib.decompress(data[i:])
            with open(path[:-3] + '.bin', 'wb') as f:
                f.write(decompressed)

            if offset != i:
                print('Found offset:', i)
                offset = i
            break
        except:
            continue
'''

'''
data = None

with open('./_sel.bin', 'rb') as f:
    data = f.read()

for i in range(32):
    try:
        decompressed = zlib.decompress(data[i:])        
        with open('./_sel.cfg', 'wb') as f:
            f.write(decompressed)
        print('Found offset:', i)
        break
    except:
        continue
'''

'''
entries = [
    'autoexec_dev.cfg',
    'autoexec_console_dev.cfg',
    'autoexec_pc_dev.cfg',
    'devgui_main.cfg',
    'devgui_xenon.cfg',
    'devgui_scriptart.cfg',
    'devgui_visibility.cfg',
    'devgui_renderer.cfg',
    'devgui_vehicles.cfg',
    'devgui_aimassist.cfg',
    'devgui_modelpreviewer.cfg',
    'devgui_maps_sp.cfg',
    'demo.cfg',
    'createfx.cfg',
    'avatar_dev.cfg',
    'avatar_createfx.cfg',
    'brent_dev.cfg',
    'chad.cfg',
    'dj.cfg',
    'jake.cfg',
    'jiesang.cfg',
    'massey.cfg',
    'mo.cfg',
    'preston.cfg',
    'robotg.cfg',
    'roger.cfg',
    'sean.cfg',
    'slime_dev.cfg',
    'tsuenami.cfg',
]

data = None

with open('./development.bin', 'rb') as f:
    data = f.read().decode('ascii', errors='replace')

for i, e in enumerate(entries):
    print(i, e, data.index(e))
'''


'''
with open(r'D:\Projects\SHSM\images\SHSM (Wii, PAL, Multi5)_extracted\DATA\files\data.arc_dec', 'wb+') as fOut:
    with open(r'D:\Projects\SHSM\images\SHSM (Wii, PAL, Multi5)_extracted\DATA\files\data.arc', 'rb') as f:
        f.seek(0x8000)
        decompressor = zlib.decompressobj(wbits=32)

        while True:
            lastTell = f.tell()
            buff = f.read(CHUNK)

            if len(buff) == 0:
                break

            data = decompressor.decompress(buff)

            if len(data) == 0:
                os.abort()
            #     if not lastError:
            #         lastError = True
            #         f.seek(lastTell)
            #         decompressor = zlib.decompressobj(wbits=32)
            #         print('---------------')
            #         continue
            #     else:
            #         print('fuck')
            #         os.abort()
            # else:
            #     lastError = False

            fOut.write(data)
            print(f.tell(), fOut.tell(), len(data))

# 0x8000 - 0xAF000
'''

'''
with open(r'D:\Projects\SHSM\images\SHSM (Wii, PAL, Multi5)_extracted\DATA\files\data.arc', 'rb') as f:
    f.seek(0x8000)
    while True:
        buff = f.read(1024 * 1024)

        if len(buff) == 0:
            os.abort()

        #print(f.tell())

        for i in range(len(buff)):
            if buff[i] == 0:
                print(hex(f.tell() + i))
                os.abort()
'''


class File:
    def __init__ (self, filePath, mode, encoding=None):
        self.filePath = filePath
        self.mode = mode
        self.encoding = encoding
        self.descriptor = None
        self.open()

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self):
        if self.descriptor is None:
            self.descriptor = open(self.filePath, self.mode, encoding=self.encoding)

    def close (self):
        if self.descriptor:
            self.descriptor.close()
            self.descriptor = None

    def tell (self):
        return self.descriptor.tell()

    def seek (self, pos):
        return self.descriptor.seek(pos)


class FileReader (File):
    def __init__ (self, filePath, mode='rb', encoding=None):
        super().__init__(filePath, mode, encoding)

    def read (self, size=None):
        return self.descriptor.read(size)

    def readStruct (self, structFormat):
        return struct.unpack(structFormat, self.descriptor.read(struct.calcsize(structFormat)))


class FileWriter (File):
    def __init__ (self, filePath, mode='wb', encoding=None):
        super().__init__(filePath, mode, encoding)

    def write (self, data):
        return self.descriptor.write(data) if data else 0

    def writeStruct (self, structFormat, *values):
        return self.write(struct.pack(structFormat, *values))


# ---------------------------


ROOT_DIR = 'D:/Projects/SHSM/images/SHSM (Wii, PAL, Multi5)_extracted/DATA/files/'
ARC_SIGNATURE = b'\x10\xfa\x00\x00'
JPG_SIGNATURE = b'\xFF\xD8\xFF\xE0'


def extractArc (arcPath, decompressOnly=False):
    pathParts = os.path.splitext(arcPath)
    extractDir = pathParts[0] + '_' + pathParts[1][1:]

    os.makedirs(extractDir, exist_ok=True)

    inputFile = FileReader(arcPath)

    signature, entriesCount, unk1, unk2 = inputFile.readStruct('<4s3I')

    if signature != ARC_SIGNATURE:
        raise Exception('Wrong ARC signature!')

    # ? | offset | comp w/o alignment size | uncomp size
    entries = [ inputFile.readStruct('<4I') for _ in range(entriesCount) ]

    if decompressOnly:
        outputFile = FileWriter(arcPath + '_decompressed')
        outputFile.writeStruct('<4s3I', signature, entriesCount, unk1, unk2)
        outputFile.write(b'\x00' * (16 * len(entries)))
        outEntriesBuff = b''

    for i, (unk3, offset, size, decompressedSize) in enumerate(entries):
        print('{} of {}'.format(i + 1, len(entries)))

        inputFile.seek(offset)
        data = inputFile.read(size)

        if decompressedSize > 0:
            data = zlib.decompress(data)

        if decompressOnly:
            outOffset = outputFile.tell()
            outputFile.write(data.ljust(16 * math.ceil(len(data) / 16), b'\x00'))
            outEntriesBuff += struct.pack('<4I', unk3, outOffset, len(data), 0)
        else:
            if data[:4] == JPG_SIGNATURE:
                ext = '.jpg'
            else:
                ext = '.bin'

            outputFilePath = os.path.join(extractDir, '{}{}'.format(offset, ext))

            # do not rewrite valid file
            if os.path.isfile(outputFilePath) and os.path.getsize(outputFilePath) == (decompressedSize or size):
                continue

            FileWriter(outputFilePath).write(data)

    if decompressOnly:
        outputFile.seek(16)
        outputFile.write(outEntriesBuff)


def scanFiles (directory):
    for item in os.listdir(directory):
        filePath = directory + item

        if not os.path.isfile(filePath) or item.endswith('.jpg'):
            continue

        chunk = FileReader(filePath).read(16 * 30)   # .decode('ascii', errors='ignore')

        if b'Extended Module:' not in chunk and b'rwID_TEXDICTIONARY' not in chunk:
            print(item)

'''

11083776.bin      - params.csv
1270173696.bin    - subs_tech_en.bin  (end credits, tech text)
1270284288.bin    - subtitles_en.bin
1270394880.bin    - subtitles_fr.bin
1270507520.bin    - subtitles_fr.bin
1270620160.bin    - subs_tech_de.bin
1270738944.bin    - subs_tech_it.bin
1270855680.bin    - subs_tech_jp.bin
1270951936.bin    - subs_tech_es.bin
1271068672.bin    - subs_tech_es.bin
1306476544.bin    - xm?
1306484736.bin    - save file xml-scheme
1306945536.bin    - xm? 
1306966016.bin    - ? (uncompressed)
1310291968.bin    - ! seems like index file names
                  dw? | dw content offset
14016512.bin      - audio filter params for interiors csv
2885632.bin       - some audio params csv
84854784.bin      - small tech text file bin en
84856832.bin      - small tech text file bin en
84858880.bin      - small tech text file bin fr
84860928.bin      - small tech text file bin fr
84862976.bin      - small tech text file bin de
84865024.bin      - small tech text file bin it
84867072.bin      - small tech text file bin jp
84869120.bin      - small tech text file bin es
84871168.bin      - small tech text file bin es
982878208.bin     - boot data bin ?
983179264.bin     - callers map csv
983220224.bin     - psy/moral map csv
983228416.bin     - interiors (player directions) moral csv

'''

def parseSubtitlesScript ():
    '''
    2016 - sign
    181316 - content start
    1180189254 - ? no offset
    273496 - file/content end
    '''
    f = FileReader(ROOT_DIR + 'data_arc/1310291968.bin')
    f.seek(16)
    items = f.readStruct('<80I')
    repDict = {}
    for i in items:
        extra = ''
        if i > 180000 and i < 185000:
            f.seek(i)
            buff = b''
            while True:
                b = f.read(1)
                if b == b'\x00':
                    break
                buff += b
            extra = buff.decode('ascii')
        else:
            if i not in repDict:
                repDict[i] = 1
            else:
                repDict[i] += 1
        print(i, extra)

    for k, v in repDict.items():
        print(k, v)


# --------------------------------------------------    
# extractArc(ROOT_DIR + 'data.arc', True)
# scanFiles(ROOT_DIR + 'data_arc/')
extractArc(ROOT_DIR + 'igc.arc')