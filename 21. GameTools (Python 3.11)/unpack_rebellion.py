# Rebellion's Games Extractor

import os, struct, json, zlib, hashlib
from enum import Enum, IntEnum, unique

GAME_DIR = r'G:\Steam\steamapps\common\Zombie Army Trilogy'
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


class Enum:
    _values = None

    @classmethod
    def has (cls, value):
        if not cls._values:
            cls._values = [ v for k, v in cls.__dict__.items() if not k.startswith('_') ]

        return value in cls._values


class ArchiveType (Enum):
    NONE = b'   '
    ZLIB = b'Zlb'
    CMP  = b'Cmp'


class SectionType (Enum):
    NONE = b'\x00\x00\x00\x00'  # Generic section
    ADAM = b'ADAM'  # -    20    7.1 Kb  envs/Undead/NZA3_Horde_Alley/M00_NZA3_Horde_Alley.pc_decompressed:71858243:64; envs/Undead/NZA3_Horde_Church/M00_NZA3_Horde_Church.pc_decompressed:98914224:42; envs/Undead/NZA3_Horde_Coast/M00_NZA3_Horde_Coast.pc_decompressed:95443095:42
    ADSP = b'ADSP'  # -     1     809 B  Sounds/GmSndMeta.asr_decompressed:148527:809
    AFSO = b'AFSO'  # -     1      20 B  Misc/Common.asr_decompressed:571517996:20
    AMRO = b'AMRO'  # -     1     700 B  Misc/Common.asr_decompressed:571517268:700
    APFO = b'APFO'  # -     1      28 B  Misc/Common.asr_decompressed:571517968:28
    ASTS = b'ASTS'  # ~    21    1.1 Gb  envs/Prologue/NZA_Prologue.pc_ru:4319:281554; envs/Prologue_2/NZA_Prologue_2.pc_ru:4761:369784; envs/Prologue_3/NZA3_Prologue.pc_ru:11759:3154202
    ATRT = b'ATRT'  # -    17   21.0 Kb  envs/Undead/NZA3_Horde_Church/M00_NZA3_Horde_Church.pc_decompressed:99521306:812; envs/Undead/NZA3_Horde_Solitude/M00_NZA3_Horde_Solitude.pc_decompressed:79918452:812; envs/Undead/NZA3_LVL01_a/M00_NZA3_LVL01_a.pc_decompressed:263800596:2324
    AUDA = b'AUDA'  # -    24   95.8 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920122:189; envs/Prologue/NZA_Prologue.pc_decompressed:101949270:189; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37880028:189
    AXAT = b'AXAT'  # -     1   83.2 Kb  Misc/Common.asr_decompressed:570467621:85179
    AXBB = b'AXBB'  # -     1      76 B  Misc/Common.asr_decompressed:571517192:76
    AXBT = b'AXBT'  # -     1  941.8 Kb  Misc/Common.asr_decompressed:570552800:964392
    BLUE = b'BLUE'  # -    70  1005.7 Kb Misc/Common.asr_decompressed:139176:33131
    CONA = b'CONA'  # - 18015    2.2 Mb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:2960:300; envs/Prologue/NZA_Prologue.pc_decompressed:10480:72; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:7900:72
    CRNA = b'CRNA'  # -    24  419.5 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57919046:1032; envs/Prologue/NZA_Prologue.pc_decompressed:101923746:960; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37873120:240
    CTAC = b'CTAC'  # -   998  103.7 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920598:133; envs/Prologue/NZA_Prologue.pc_decompressed:101984216:92; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37928746:92
    CTAT = b'CTAT'  # -  1214  105.9 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57928802:92; envs/Prologue/NZA_Prologue.pc_decompressed:101995166:96; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37928966:76
    CTEV = b'CTEV'  # -  3319  356.5 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920863:88; envs/Prologue/NZA_Prologue.pc_decompressed:101986164:88; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37940888:88
    CTTR = b'CTTR'  # -  1066  164.3 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920731:132; envs/Prologue/NZA_Prologue.pc_decompressed:101984308:128; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37928838:128
    CUTS = b'CUTS'  # -   176  362.4 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920426:172; envs/Prologue/NZA_Prologue.pc_decompressed:101982140:2076; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37912898:15848
    DCAL = b'DCAL'  # -     1   18.3 Kb  Misc/Common.asr_decompressed:571518016:18785
    DLCL = b'dlcl'  # -    36    2.5 Kb  Misc/Common.asr_decompressed:573130655:70
    DLET = b'DLET'  # -    41    3.6 Kb  envs/Prologue/NZA_Prologue.pc_ru:32:80; envs/Prologue_2/NZA_Prologue_2.pc_ru:32:80; envs/Prologue_3/NZA3_Prologue.pc_ru:32:104
    DLEV = b'DLEV'  # -   112   12.3 Kb  envs/Prologue/NZA_Prologue.pc_decompressed:42196154:84; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:21291094:88; envs/Prologue_3/NZA3_Prologue.pc_decompressed:23225946:100
    DLLN = b'DLLN'  # -   901  116.1 Kb  envs/Prologue/NZA_Prologue.pc_ru:154:87; envs/Prologue_2/NZA_Prologue_2.pc_ru:154:137; envs/Prologue_3/NZA3_Prologue.pc_ru:178:95
    DLLT = b'DLLT'  # -    41    1.6 Kb  envs/Prologue/NZA_Prologue.pc_ru:112:42; envs/Prologue_2/NZA_Prologue_2.pc_ru:112:42; envs/Prologue_3/NZA3_Prologue.pc_ru:136:42
    DLRU = b'DLRU'  # -     1      32 B  Misc/Common.asr_decompressed:573130623:32
    DYMC = b'DYMC'  # ?     1   63.4 Kb  Sounds/GmSndMeta.asr_decompressed:83614:64893
    EMOD = b'EMOD'  # -    24     836 B  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57917838:32; envs/Prologue/NZA_Prologue.pc_decompressed:101801090:36; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37843668:36
    ENTI = b'ENTI'  # - 53836   12.8 Mb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:58071259:76; envs/Prologue/NZA_Prologue.pc_decompressed:102011188:80; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37957353:76
    FAAN = b'FAAN'  # -   902  778.9 Kb  envs/Prologue/NZA_Prologue.pc_ru:683:472; envs/Prologue_2/NZA_Prologue_2.pc_ru:881:1032; envs/Prologue_3/NZA3_Prologue.pc_decompressed:23227278:6524
    FACE = b'FACE'  # -   174   39.4 Kb  Chars/MP.pc_decompressed:1061583:224; envs/Prologue/NZA_Prologue.pc_decompressed:42196574:224; envs/Prologue_3/NZA3_Prologue.pc_decompressed:23227054:224
    FNFO = b'FNFO'  # ~    88    2.1 Kb  Chars/MP.pc_decompressed:8:24; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:8:24; envs/Prologue/NZA_Prologue.pc_decompressed:8:24
    FOG_ = b'FOG '  # -    24    1.3 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57295868:56; envs/Prologue/NZA_Prologue.pc_decompressed:94323630:56; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:35204160:56
    FONT = b'FONT'  # ?     4  841.3 Kb  Fonts/Fonts.asr:13635308:92333; Fonts/PrimitiveRenderFonts.asr:92:1784
    FSX2 = b'FSX2'  # ?    50   12.3 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:58193524:380; envs/Prologue/NZA_Prologue.pc_decompressed:102119898:364; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37996628:364
    FXET = b'FXET'  # -  2061  998.0 Kb  Chars/MP.pc_decompressed:10761986:787; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:58150647:682; envs/Prologue/NZA_Prologue.pc_decompressed:102090160:275
    FXPT = b'FXPT'  # -  7609    5.9 Mb  Chars/MP.pc_decompressed:10750686:888; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:58144391:504; envs/Prologue/NZA_Prologue.pc_decompressed:102089164:640
    FXST = b'FXST'  # -  7609    2.7 Mb  Chars/MP.pc_decompressed:10757670:472; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:58148299:388; envs/Prologue/NZA_Prologue.pc_decompressed:102089804:356
    FXTT = b'FXTT'  # ?   177  120.3 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:58211113:976; envs/Prologue/NZA_Prologue.pc_decompressed:102132558:744; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:38008935:876
    GISN = b'GISN'  # -    24    9.8 Mb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57917870:1112; envs/Prologue/NZA_Prologue.pc_decompressed:101801126:122552; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37843704:29372
    HCAN = b'HCAN'  # -  6335   68.6 Mb  Chars/MP.pc_decompressed:10638598:1600; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57295924:1828; envs/Prologue/NZA_Prologue.pc_decompressed:94323686:252
    HMPT = b'HMPT'  # -  2263    6.1 Mb  Chars/MP.pc_decompressed:1115236:688; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39928656:8672; envs/Prologue/NZA_Prologue.pc_decompressed:44574191:2804
    HSBB = b'HSBB'  # -  5493    3.7 Mb  Chars/MP.pc_decompressed:1115924:592; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39814308:52; envs/Prologue/NZA_Prologue.pc_decompressed:44322857:80
    HSKE = b'HSKE'  # -  5493  107.3 Kb  Chars/MP.pc_decompressed:1229046:20; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39835756:20; envs/Prologue/NZA_Prologue.pc_decompressed:44336537:20
    HSKL = b'HSKL'  # -  5019  358.9 Kb  Chars/MP.pc_decompressed:1115132:104; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39928496:80; envs/Prologue/NZA_Prologue.pc_decompressed:44322765:92
    HSKN = b'HSKN'  # -  5493  184.4 Mb  Chars/MP.pc_decompressed:1113831:1301; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39796377:17931; envs/Prologue/NZA_Prologue.pc_decompressed:44305870:16895
    HSND = b'HSND'  # -  1137    1.2 Mb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39937328:1848; envs/Prologue/NZA_Prologue.pc_decompressed:48395343:1876; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:22244206:1876
    HTXT = b'HTXT'  # ?    10  676.9 Kb  Text/CharacterSet/CharacterSet_Ru.asr:8:383569; Text/Credits/Credits_Ru.asr:8:8699; Text/Cutscene/Cutscene_Ru.asr:8:24193
    IKTM = b'IKTM'  # -     3    1.6 Kb  Misc/Common.asr_decompressed:570431290:624
    INST = b'INST'  # -    24  190.9 Mb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:56060656:550902; envs/Prologue/NZA_Prologue.pc_decompressed:80616338:5090384; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:30596384:2037900
    MARE = b'MARE'  # -    46    5.7 Mb  Chars/MP.pc_decompressed:1063535:5180; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39131513:70884; envs/Prologue/NZA_Prologue.pc_decompressed:42197662:183028
    META = b'META'  # -     1    1.9 Kb  Misc/Common.asr_decompressed:560405808:1972
    NAV1 = b'NAV1'  # -    24   12.4 Mb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920311:37; envs/Prologue/NZA_Prologue.pc_decompressed:101949459:32603; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37880217:32603
    NAVN = b'navn'  # -    24    4.9 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920402:24; envs/Prologue/NZA_Prologue.pc_decompressed:101982116:24; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37912874:24
    OCMH = b'OCMH'  # -    24  1019.6 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920078:24; envs/Prologue/NZA_Prologue.pc_decompressed:101924706:24544; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37873360:6648
    OINF = b'oinf'  # -    20    9.4 Kb  envs/Undead/NZA3_Horde_Alley/M00_NZA3_Horde_Alley.mimg_decompressed:1661120:24; envs/Undead/NZA3_Horde_Church/M00_NZA3_Horde_Church.mimg_decompressed:1661120:24; envs/Undead/NZA3_Horde_Coast/M00_NZA3_Horde_Coast.mimg_decompressed:1661120:24
    PASD = b'pasd'  # -    63    1.7 Mb  Misc/Common.asr_decompressed:573133175:25697
    PHEN = b'PHEN'  # -    23  332.0 Mb  envs/Prologue/NZA_Prologue.pc_decompressed:96151410:5649680; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37463240:380428; envs/Prologue_3/NZA3_Prologue.pc_decompressed:49101409:607953
    PLUT = b'PLUT'  # -     4    1.0 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57295348:216; envs/Undead/NZA3_LVL04/NZA3_LVL04.pc_decompressed:71075226:412; envs/Undead/Undead_B/Undead_B.pc_decompressed:84080754:216
    RAGD = b'RAGD'  # -     5   33.9 Kb  Misc/Common.asr_decompressed:570432878:5656
    REND = b'REND'  # -    24     480 B  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57295604:20; envs/Prologue/NZA_Prologue.pc_decompressed:94323366:20; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:35203896:20
    RSCF = b'RSCF'  # ~ 59431    9.5 Gb  Chars/MP.pc_decompressed:360:22088; envs/TheBlob1.PC_textures:8:5592648; envs/TheBlob2.PC_textures:8:1398352
    RSFL = b'RSFL'  # ~    68  538.1 Kb  Chars/MP.pc_decompressed:32:328; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:32:2928; envs/Prologue/NZA_Prologue.pc_decompressed:32:10448
    RVBP = b'RVBP'  # -    21    6.1 Kb  envs/Prologue_3/NZA3_Prologue.pc_decompressed:37122665:80; envs/Undead/NZA3_Horde_Alley/NZA3_Horde_Alley.pc_decompressed:6033184:84; envs/Undead/NZA3_Horde_Church/NZA3_Horde_Church.pc_decompressed:12681284:80
    SDDC = b'SDDC'  # -     3     896 B  envs/Undead/NZA3_LVL03/NZA3_LVL03.pc_decompressed:48381582:552; envs/Undead/NZA3_LVL04/NZA3_LVL04.pc_decompressed:71075998:96; envs/Undead/Undead_E/Undead_E.pc_decompressed:65472682:248
    SDEV = b'SDEV'  # -  5071    1.4 Mb  Chars/MP.pc_decompressed:1061041:297; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39117241:233; envs/Prologue/NZA_Prologue.pc_decompressed:42175837:233
    SDGS = b'SDGS'  # -     1      20 B  Sounds/GmSndMeta.asr_decompressed:148507:20
    SDMX = b'SDMX'  # ?     1   81.6 Kb  Sounds/GmSndMeta.asr_decompressed:8:83606
    SDPH = b'SDPH'  # -    24  678.7 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920102:20; envs/Prologue/NZA_Prologue.pc_decompressed:101949250:20; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37880008:20
    SDSM = b'SDSM'  # - 15540    2.4 Mb  Chars/MP.pc_decompressed:1059532:135; envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:39082164:179; envs/Prologue/NZA_Prologue.pc_decompressed:42125008:171
    SKYS = b'SKYS'  # -    24    4.5 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57295624:191; envs/Prologue/NZA_Prologue.pc_decompressed:94323386:191; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:35203916:191
    SMSG = b'SMSG'  # -    22  887.2 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:58080495:1504; envs/Prologue/NZA_Prologue.pc_decompressed:102011748:80; envs/Undead/NZA3_Horde_Alley/M00_NZA3_Horde_Alley.pc_decompressed:71884236:2234
    SUBT = b'SUBT'  # -     1    1.8 Kb  Misc/Common.asr_decompressed:571536801:1860
    TEXT = b'TEXT'  # -    72   17.7 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57295564:20; envs/Prologue/NZA_Prologue.pc_decompressed:94323326:20; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:35203856:20
    TTXT = b'TTXT'  # ?    28   20.1 Kb  Fonts/buttons.asr:1048768:1420; GUIMenu/Frontend.gui_decompressed:262340:1392; GUIMenu/global.gui_decompressed:262340:1088
    TXAN = b'TXAN'  # -   102    9.8 Kb  envs/Prologue/NZA_Prologue.pc_decompressed:42197470:84; envs/Prologue_3/NZA3_Prologue.pc_decompressed:23233802:84; envs/Undead/NZA3_Horde_Alley/M00_NZA3_Horde_Alley.pc_decompressed:37506273:96
    TXFL = b'TXFL'  # -    24     480 B  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57295584:20; envs/Prologue/NZA_Prologue.pc_decompressed:94323346:20; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:35203876:20
    TXST = b'TXST'  # ?    33  731.2 Kb  Chars/MP.ts:8:604; envs/3D_FrontEnd/3D_FrontEnd.ts:8:10516; envs/Prologue/NZA_Prologue.ts:8:25876
    UIAN = b'UIAN'  # ?     8  829.8 Kb  GUIMenu/Frontend.gui_decompressed:3820764:106220; GUIMenu/global.gui_decompressed:1096336:106220; GUIMenu/in_game.gui_decompressed:24225692:106220
    UIAU = b'UIAU'  # ?     1      52 B  GUIMenu/GUIAudio.asr_decompressed:8:52
    UIMP = b'UIMP'  # ?    70    1.5 Mb  GUIMenu/Frontend.gui_decompressed:3927132:43016; GUIMenu/global.gui_decompressed:1202628:19631; GUIMenu/in_game.gui_decompressed:24332072:24254
    UITP = b'UITP'  # ?    16     620 B  GUIMenu/Frontend.gui_decompressed:3926984:40; GUIMenu/global.gui_decompressed:1202556:32; GUIMenu/in_game.gui_decompressed:24331912:40
    VTEX = b'VTEX'  # ?    24   10.9 Mb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57442218:475620; envs/Prologue/NZA_Prologue.pc_decompressed:95675790:475620; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:36987620:475620
    WPSG = b'WPSG'  # -    24    1.3 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57920348:54; envs/Prologue/NZA_Prologue.pc_decompressed:101982062:54; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:37912820:54
    WTHR = b'WTHR'  #      24    1.2 Kb  envs/3D_FrontEnd/3D_FrontEnd.pc_decompressed:57295815:53; envs/Prologue/NZA_Prologue.pc_decompressed:94323577:53; envs/Prologue_2/NZA_Prologue_2.pc_decompressed:35204107:53


class RessourceType (Enum):
    GENERIC = 0
    TEXTURE = 2
    AUDIO   = 3
    PC      = 6


def scanArchives (dbPath, gameDir, ignoreCache=False):
    files = readJson(dbPath, [])

    if ignoreCache or not files:
        for (dirName, _, fileNames) in os.walk(gameDir):
            for fileName in fileNames:
                if fileName.lower().endswith('_decompressed'):
                    continue

                filePath = os.path.join(dirName, fileName)

                with open(filePath, 'rb') as f:
                    if f.read(5) == ARCHIVE_SIGNATURE:
                        files.append(filePath)

        writeJson(dbPath, files)

    return files


def readHeader (f):
    signature, archiveType = readStruct('<5s3s', f)

    if signature != ARCHIVE_SIGNATURE:
        raise Exception(f'Not an Asura archive file: { f.name }')

    if not ArchiveType.has(archiveType):
        raise Exception(f'Unknown archive type { str(archiveType) } ({ f.name })')

    if archiveType == ArchiveType.CMP:
        raise NotImplemented(f'Archive type { str(archiveType) } is not implemented ({ f.name })')

    return archiveType

_stats = {
    '_unk1': [],
    '_unk2': [],
    '_unk5': [],
    'totalSize': 0,
    'payloadSize': 0
}


def readSections (f, fileSize):
    global _stats

    while (fileSize - f.tell()) >= MIN_SECTION_SIZE:
        sectionStart = f.tell()
        sectionType = f.read(4)

        if sectionType == SectionType.NONE:  # TODO: alignment?
            break

        if not SectionType.has(sectionType):
            raise Exception(f'Unknown section type { str(sectionType) } ({ f.name }:{ sectionStart })')

        sectionSize = readStruct('<I', f) 
        sectionEnd = sectionStart + sectionSize

        if sectionType == SectionType.FNFO:
            # - Always 24 bytes
            # - Not in every archive
            # - Structure: UINT32 - 1 | UINT32 - 0 or 1 | UINT32 - file size related number | UINT32 - 7 or 8

            _const1, _always0or1, _fileSizeRelated, _always7or8 = readStruct('<4I', f)

            assert _const1 == 1
            assert _always0or1 in [ 0, 1 ]
            assert _always7or8 in [ 7, 8 ]

        elif sectionType == SectionType.RSCF:
            # - RSCF always contains single resource/asset
            # - _unk4 has alotta values - flags? (all bits: 111010100000011000010010101111)

            _unk1, _unk2, resType, _unk4, resSize = readStruct('<5I', f)

            assert _unk1 in [ 0, 1, 2, 3, 4, 6, 10 ]
            assert _unk2 in [ 0, 1, 2 ]
            assert RessourceType.has(resType)

            resPath = readAlignedString(f, 4)
            res = f.read(resSize)

        elif sectionType == SectionType.ASTS:
            # - Current resAbsOffset always greater than previous one
            # - ASTS contains audio only (.wav)
            # - _0or1: not mono/stereo, not long/short, not music/sfx/speech, not big/small file, not format/encoding, not streamed/static

            _const2, _const0, resCount, hasMetaOnly = readStruct('<3IB', f)

            assert _const2 == 2
            assert _const0 == 0
            assert hasMetaOnly in [ 0, 1 ]

            resources = []

            for i in range(resCount):
                resPath = readAlignedString(f, 4)
                _0or1, resSize, resAbsOffset = readStruct('<B2I', f)

                assert _0or1 in [ 0, 1 ]
                assert resPath.lower().endswith('.wav')

                resources.append({
                    '_0or1': _0or1,
                    'path': resPath,
                    'size': resSize,
                    'offset': resAbsOffset,
                    'data': None
                })

            if not hasMetaOnly:
                for resource in resources:
                    f.seek(resource['offset'])

                    assert f.tell() == resource['offset']

                    resource['data'] = f.read(resource['size'])

                    assert len(resource['data']) == resource['size']

        elif sectionType == SectionType.RSFL:
            _const1, _const0, resCount = readStruct('<3I', f)

            assert _const1 == 1
            assert _const0 == 0

            for i in range(resCount):
                resPath = readAlignedString(f, 4)
                _resOffset, _resSize, _const1 = readStruct('<3I', f)

                assert _const1 == 1

            # TODO: read tail (EF BE AD DE...)

            f.seek(sectionEnd)

        else:
            f.seek(sectionEnd)
        '''
        elif sectionType == SectionType.DYMC:
            _unk1, _unk2, layerCount = readStruct('<3I', f)

            layerNames = [ readAlignedString(f, 4) for _ in range(layerCount) ]

            soundCount = readStruct('<I', f)

            for i in range(soundCount):
                _unk3 = readStruct('<I', f)
                soundName = readAlignedString(f, 4)
                _unk4 = readStruct('<I', f)
                soundPath = readAlignedString(f, 4)
                break

            print(soundPath)

            # data = f.read(sectionEnd - f.tell())
            # findStrings(data)
            f.seek(sectionEnd)
        '''

        assert (sectionEnd - f.tell()) == 0, 'Section must be read to the end'

        # print(sectionType, sectionSize)


def unpack (filePath):
    print(filePath)

    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    fileSize = os.path.getsize(filePath)

    with open(filePath, 'rb') as f:
        archiveType = readHeader(f)

        if archiveType == ArchiveType.ZLIB:
            _zero1, compSize, decompSize = readStruct('<3I', f)

            assert _zero1 == 0

            data = f.read(compSize)
            data = decompressData(data)

            if len(data) != decompSize:
                raise Exception(f'Decompressed data has unexpected size')

            decompFilePath = filePath + '_decompressed'

            if not os.path.isfile(decompFilePath):
                with open(decompFilePath, 'wb') as f2:
                    f2.write(data)

                print(f'Decompressed file: { decompFilePath }')

            f = VirtualReader(data, name=decompFilePath)
            archiveType = readHeader(f)
            fileSize = len(data)

            if archiveType != ArchiveType.NONE:
                raise Exception(f'Expected decompressed data to be an \'Asura   \' archive')

        readSections(f, fileSize)


def unpackAll (rootDir, rescanArchives=False):
    archives = scanArchives(ARCHIVES_JSON_PATH, GAME_DIR, rescanArchives)

    for filePath in archives:
        unpack(filePath)


if __name__ == '__main__': 
    # unpackAll(GAME_DIR)
    # print(json.dumps(_stats, indent=4, ensure_ascii=False))

    with open(r'C:\Projects\_Sources\GameEngines\SourceEngine2013\lib\public\socketlib.lib', 'rb') as f:
        findStrings(f.read())
    
    # unpack(os.path.join(GAME_DIR, 'Sounds', 'GmSndMeta.asr_decompressed'))
    # unpack(os.path.join(GAME_DIR, 'Sounds', 'GmSnd.asr'))
    # unpack(os.path.join(GAME_DIR, 'Fonts', 'buttons.asr'))