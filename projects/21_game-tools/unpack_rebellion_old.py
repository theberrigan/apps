import os, struct, zlib, json
from file import *

BASE_DIR = 'C:/Program Files (x86)/Steam/steamapps/common/Zombie Army Trilogy/'

ASR_SIGNATURE = b'Asura'

class Enum:
    _values = None

    @classmethod
    def hasValue (cls, value):
        if not cls._values:
            cls._values = [ v for k, v in cls.__dict__.items() if k[0] != '_' ]

        return value in cls._values

class ASRType (Enum):
    NONE = b'   '
    ZLIB = b'Zlb'
    CMP  = b'Cmp'

class ContentType (Enum):
    FNFO = b'FNFO'
    TXST = b'TXST'
    RSCF = b'RSCF'
    RSFL = b'RSFL'
    UIAU = b'UIAU'
    UIAN = b'UIAN'
    SDMX = b'SDMX'
    ASTS = b'ASTS'
    HTXT = b'HTXT'
    CONA = b'CONA'
    SDSM = b'SDSM'
    SDEV = b'SDEV'
    MARE = b'MARE'
    HSKN = b'HSKN'
    HSBB = b'HSBB'
    HSKE = b'HSKE'
    HSKL = b'HSKL'
    HMPT = b'HMPT'
    HSND = b'HSND'
    INST = b'INST'
    PLUT = b'PLUT'

SECTION_TYPES = [
    b'RSCF',   # Entries: 59431  Sample file: envs/TheBlob1.PC_textures:8
    b'ENTI',   # Entries: 53836  Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:167073706
    b'CONA',   # Entries: 18015  Sample file: Misc/Common.asr.dcmp:1243105
    b'SDSM',   # Entries: 15540  Sample file: Sounds/GmSnd.asr.dcmp:65978230
    b'FXPT',   # Entries: 7609   Sample file: Misc/Common.asr.dcmp:573127779
    b'FXST',   # Entries: 7609   Sample file: Misc/Common.asr.dcmp:573129831
    b'HCAN',   # Entries: 6335   Sample file: Misc/Common.asr.dcmp:570429324
    b'HSKN',   # Entries: 5493   Sample file: Misc/Common.asr.dcmp:560386198
    b'HSBB',   # Entries: 5493   Sample file: Misc/Common.asr.dcmp:560393564
    b'HSKE',   # Entries: 5493   Sample file: Misc/Common.asr.dcmp:560405788
    b'SDEV',   # Entries: 5071   Sample file: Sounds/GmSnd.asr.dcmp:66275750
    b'HSKL',   # Entries: 5019   Sample file: Misc/Common.asr.dcmp:560124189
    b'CTEV',   # Entries: 3319   Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:166421397
    b'HMPT',   # Entries: 2263   Sample file: Misc/Common.asr.dcmp:560124249
    b'FXET',   # Entries: 2061   Sample file: Misc/Common.asr.dcmp:573130187
    b'CTAT',   # Entries: 1214   Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:166419348
    b'HSND',   # Entries: 1137   Sample file: Misc/Common.asr.dcmp:570322062
    b'CTTR',   # Entries: 1066   Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:166419128
    b'CTAC',   # Entries: 998    Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:166419032
    b'FAAN',   # Entries: 902    Sample file: Sounds/GmSnd.asr_ru:11003131
    b'DLLN',   # Entries: 901    Sample file: Sounds/GmSnd.asr_ru:10792644
    b'FXTT',   # Entries: 177    Sample file: Misc/Common.asr.dcmp:573096396
    b'CUTS',   # Entries: 176    Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:166412733
    b'FACE',   # Entries: 174    Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:75024268
    b'DLEV',   # Entries: 112    Sample file: Sounds/GmSnd.asr.dcmp:66283784
    b'TXAN',   # Entries: 102    Sample file: Misc/Common.asr.dcmp:524882668
    b'FNFO',   # Entries: 88     Sample file: Chars/MP.pc.dcmp:8
    b'TEXT',   # Entries: 72     Sample file: envs/Undead/Undead_E/Undead_E.pc.dcmp:65472930
    b'UIMP',   # Entries: 70     Sample file: GUIMenu/Options.gui.dcmp:577128
    b'BLUE',   # Entries: 70     Sample file: Misc/Common.asr.dcmp:1152809
    b'RSFL',   # Entries: 68     Sample file: Fonts/Fonts.asr:8
    b'pasd',   # Entries: 63     Sample file: Misc/Common.asr.dcmp:574936317
    b'FSX2',   # Entries: 50     Sample file: Misc/Common.asr.dcmp:573070275
    b'MARE',   # Entries: 46     Sample file: Misc/Common.asr.dcmp:524882768
    b'DLET',   # Entries: 41     Sample file: Sounds/GmSnd.asr_ru:10772016
    b'DLLT',   # Entries: 41     Sample file: Sounds/GmSnd.asr_ru:10772176
    b'dlcl',   # Entries: 36     Sample file: Misc/Common.asr.dcmp:573133105
    b'TXST',   # Entries: 33     Sample file: Chars/MP.ts:8
    b'TTXT',   # Entries: 28     Sample file: GUIMenu/Options.gui.dcmp:32964
    b'INST',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:117318573
    b'TXFL',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:144107015
    b'REND',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:144107035
    b'SKYS',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:144107055
    b'WTHR',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:144107246
    b'FOG ',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:144107299
    b'VTEX',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:145088813
    b'EMOD',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:165209709
    b'GISN',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:165209741
    b'CRNA',   # Entries: 24     Sample file: envs/Undead/Undead_E/Undead_E.pc.dcmp:65472982
    b'OCMH',   # Entries: 24     Sample file: envs/Undead/Undead_E/Undead_E.pc.dcmp:65482078
    b'SDPH',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:165502033
    b'AUDA',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:165531841
    b'NAV1',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:165543043
    b'WPSG',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:166408546
    b'navn',   # Entries: 24     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:166408600
    b'PHEN',   # Entries: 23     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:145564433
    b'SMSG',   # Entries: 22     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:166421961
    b'ASTS',   # Entries: 21     Sample file: Sounds/StreamingSounds.asr:8
    b'RVBP',   # Entries: 21     Sample file: envs/Undead/Undead_E/Undead_E.pc.dcmp:15836316
    b'oinf',   # Entries: 20     Sample file: envs/Undead/Undead_E/M05_Undead_E.mimg.dcmp:1661100
    b'ADAM',   # Entries: 20     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:165542275
    b'ATRT',   # Entries: 17     Sample file: envs/Undead/Undead_E/M05_Undead_E.pc.dcmp:167322604
    b'UITP',   # Entries: 16     Sample file: GUIMenu/Options.gui.dcmp:314384
    b'HTXT',   # Entries: 10     Sample file: Text/CharacterSet/CharacterSet_Ru.asr:8
    b'UIAN',   # Entries: 8      Sample file: GUIMenu/loading.gui.dcmp:8
    b'RAGD',   # Entries: 5      Sample file: Misc/Common.asr.dcmp:570467181
    b'PLUT',   # Entries: 4      Sample file: envs/Undead/Undead_C/Undead_C.pc.dcmp:101696846
    b'FONT',   # Entries: 4      Sample file: Fonts/PrimitiveRenderFonts.asr:92
    b'SDDC',   # Entries: 3      Sample file: envs/Undead/Undead_E/Undead_E.pc.dcmp:65472682
    b'IKTM',   # Entries: 3      Sample file: Misc/Common.asr.dcmp:570432682
    b'UIAU',   # Entries: 1      Sample file: GUIMenu/GUIAudio.asr.dcmp:8
    b'META',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:560405808
    b'AXAT',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:570467621
    b'AXBT',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:570552800
    b'AXBB',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:571517192
    b'AMRO',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:571517268
    b'APFO',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:571517968
    b'AFSO',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:571517996
    b'DCAL',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:571518016
    b'SUBT',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:571536801
    b'DLRU',   # Entries: 1      Sample file: Misc/Common.asr.dcmp:573130623
    b'SDMX',   # Entries: 1      Sample file: Sounds/GmSndMeta.asr.dcmp:8
    b'DYMC',   # Entries: 1      Sample file: Sounds/GmSndMeta.asr.dcmp:83614
    b'SDGS',   # Entries: 1      Sample file: Sounds/GmSndMeta.asr.dcmp:148507
    b'ADSP',   # Entries: 1      Sample file: Sounds/GmSndMeta.asr.dcmp:148527
]


def decompressAll (directory):
    for item in os.listdir(directory):
        filePath = directory + item

        if os.path.isdir(filePath):
            decompressAll(filePath + '/')
            continue

        if not os.path.isfile(filePath):
            continue

        inputFile = FileReader(filePath)

        signature = inputFile.read(5)

        if signature != ASR_SIGNATURE:
            continue

        asrType = inputFile.read(3)

        if not ASRType.hasValue(asrType):
            continue

        if asrType == ASRType.ZLIB:
            inputFile.seek(12, 1)  # skip contentType, compressedSize, decompressedSize
            outFilePath = filePath + '.dcmp'
            outFile = FileWriter(outFilePath)
            outFile.write(zlib.decompress(inputFile.read()))
            print('Decompressed to:', outFilePath)

def formatHexSequence (*nums):
    return ('{:08X} ' * len(nums)).format(*nums).strip()

def readAlignedString (reader, alignment=4):
    buff = b''

    while True:
        chunk = reader.read(alignment)
        buff += chunk

        if b'\x00' in chunk:
            break

    return buff[:buff.index(b'\x00')].decode('utf-8')


def extractASRSections (asrFile, fileSize):
    minSectionHeaderLength = 8
    _sect = None

    while (fileSize - asrFile.tell()) >= minSectionHeaderLength:
        sectionStart = asrFile.tell()
        sectionType, sectionSize = asrFile.readStruct('<4sI')
        sectionEnd = sectionStart + sectionSize

        # TODO: not sure we have every possible sections name, so print out unsupported sections signature
        if sectionType not in SECTION_TYPES or sectionSize == 0 or sectionEnd > fileSize:
            break

        # -----------------------------

        if sectionType == ContentType.ASTS:
            unk1, unk2, entriesCount, unk3 = asrFile.readStruct('<3IB')

            for i in range(entriesCount):
                assetPath = readAlignedString(asrFile)
                unk4, audioSize, audioOffset = asrFile.readStruct('<BII')

        elif sectionType == ContentType.TXST:
            version, unk2, sourcesCount, entriesCount = asrFile.readStruct('<4I')
            sources = [ readAlignedString(asrFile) for i in range(sourcesCount) ]

            for i in range(entriesCount):
                if version == 2:
                    (unk1, offset, size, unk2, sourceIndex), unk3 = asrFile.readStruct('<5I'), 0
                elif version == 3:
                    unk1, offset, size, unk2, sourceIndex, unk3 = asrFile.readStruct('<6I')
                else:
                    raise Exception('Unknown version', version)

                print(formatHexSequence(unk1, offset, size, unk2, sourceIndex, unk3), _hdr)

        elif sectionType == ContentType.FNFO:
            unk, unk2, sectionSize, unk3 = asrFile.readStruct('<4I')
            # print(formatHexSequence(unk, unk2, sectionSize, unk3))

            # RSCF|size|00...|01...|00...|02
            # FNFO -> RSFL -> RSCF

        elif sectionType == ContentType.RSCF:
            unk1, unk2, unk3, unk4, resourceSize = asrFile.readStruct('<5I')
            resourcePath = readAlignedString(asrFile)
            asrFile.read(resourceSize)

            # if '#' in ddsPath:
            #     print(asrFile.filePath, ddsPath)

            # RSCF|size|00...|01...|00...|02
            # FNFO -> RSFL -> RSCF

        elif sectionType == ContentType.RSFL:
            unk1, unk2, itemsCount = asrFile.readStruct('<3I')

            for i in range(itemsCount):
                resourcePath = readAlignedString(asrFile)
                resourceOffset, resourceSize, unk3 = asrFile.readStruct('<3I')
                # print(formatHexSequence(resourceOffset, resourceSize, unk3), resourcePath)

        elif sectionType == ContentType.CONA:
            pass
            # TODO: dunno

        elif sectionType == ContentType.SDSM:
            unk1, unk2 = asrFile.readStruct('<2I')
            name = readAlignedString(asrFile)
            unk3 = asrFile.readStruct('<I')[0]
            path = readAlignedString(asrFile)
            unk4, unk5, unk6, unk7 = asrFile.readStruct('<3IB')
            def1 = readAlignedString(asrFile)
            def2 = readAlignedString(asrFile)
            unk8 = asrFile.readStruct('<I')[0]
            def3 = readAlignedString(asrFile)
            unk9, unk10, unk11, unk12 = asrFile.readStruct('<BBII')

            # print(formatHexSequence(unk1, unk2, unk3, unk4, unk5, unk6, unk7, unk8, unk9, unk10, unk11, unk12), name, path, def1, def2, def3, asrFile.tell(), sectionEnd - asrFile.tell())

        elif sectionType == ContentType.SDEV:
            unk1, unk2 = asrFile.readStruct('<2I')
            name = readAlignedString(asrFile)

            unks = asrFile.readStruct('<20IB')
            # name2 = readAlignedString(asrFile)
            # name3 = readAlignedString(asrFile)
            # name4 = readAlignedString(asrFile)

            # print(formatHexSequence(*unks), name, asrFile.tell(), sectionEnd - asrFile.tell())

        elif sectionType == ContentType.MARE:
            pass

        elif sectionType == ContentType.HSKN:
            pass

        elif sectionType == ContentType.HSBB:
            pass

        elif sectionType == ContentType.HSKE:
            pass

        elif sectionType == ContentType.HSKL:
            pass

        elif sectionType == ContentType.HMPT:
            pass

        elif sectionType == ContentType.HSND:
            pass

        elif sectionType == ContentType.INST:
            pass

        elif sectionType == ContentType.PLUT:
            pass

        else:
            if not _sect:
                _sect = [ sectionType, sectionStart]
            pass
            # print('Section is not implemented')


        # -----------------------------

        asrFile.seek(sectionEnd)

    print(_sect)



def extractASR (filePath):
    if not os.path.isfile(filePath):
        raise Exception('File doesn\'t exist')

    fileSize = os.path.getsize(filePath)

    if fileSize < 8:
        raise Exception('File too small to be an ASR archive')

    asrFile = FileReader(filePath)
    signature = asrFile.read(5)

    if signature != ASR_SIGNATURE:
        raise Exception('It\'s not an ASR archive')

    asrType = asrFile.read(3)

    if not ASRType.hasValue(asrType):
        raise Exception('Unknown ASR archive type')

    if asrType == ASRType.ZLIB:
        unk1, compressedSize, decompressedSize = asrFile.readStruct('<3I')

        if decompressedSize < 8:
            raise Exception('Decompressed data too small to be an ASR archive')

        decompressedData = zlib.decompress(asrFile.read())

        if len(decompressedData) != decompressedSize:
            raise Exception('Incorrect uncompressed data size')

        asrFile = VirtualFileReader(buffer=decompressedData)
        fileSize = decompressedSize
        signature = asrFile.read(5)

        if signature != ASR_SIGNATURE:
            raise Exception('Decompressed data is not an ASR archive')

        asrType = asrFile.read(3)

        if asrType != ASRType.NONE:
            raise Exception('Expected decompressed data to be an \'Asura   \' archive')

    elif asrType == ASRType.CMP:
        raise Exception('ASR type \'Cmp\' is not implemented')

    extractASRSections(asrFile, fileSize)


def forEach (directory, targetContentType, fn):
    for item in os.listdir(directory):
        filePath = directory + item

        if os.path.isdir(filePath):
            forEach(filePath + '/', targetContentType, fn)
            continue

        if not os.path.isfile(filePath):
            continue

        inputFile = FileReader(filePath)

        signature = inputFile.read(5)

        if signature != ASR_SIGNATURE:
            continue

        asrType = inputFile.read(3)

        if not ASRType.hasValue(asrType):
            continue

        contentType = inputFile.read(4)

        if contentType == targetContentType:
            print(filePath)
            fn(filePath)


def readRSCF (filePath):
    f = FileReader(filePath)
    maxIndex = os.path.getsize(filePath) - 4
    f.seek(8)
    count = 0

    while f.tell() < maxIndex:
        sectionStart = f.tell()
        sectionType = f.read(4)
        sectionSize = f.readStruct('<I')[0]
        sectionEnd = sectionStart + sectionSize

        if sectionType != b'RSCF':
            break

        count += 1
        unk1, unk2, unk3, unk4 = f.readStruct('<4I')  # [1]: childrenCount
        ddsSize = f.readStruct('<I')[0]
        ddsPath = readAlignedString(f)
        f.seek(ddsSize, 1)
        print(str(count).rjust(4), formatHexSequence(unk1, unk2, unk3, unk4), ddsPath)
        # f.seek(sectionEnd)


def checkFiles (directory):
    sectionTypes = {}
    samples = {}

    def walk (directory):
        for item in os.listdir(directory):
            filePath = directory + item

            if os.path.isdir(filePath):
                walk(filePath + '/')
                continue

            if not os.path.isfile(filePath):
                continue

            inputFile = FileReader(filePath)

            signature = inputFile.read(5)

            if signature != ASR_SIGNATURE:
                continue

            relFilePath = os.path.relpath(filePath, BASE_DIR).replace('\\', '/')

            asrType = inputFile.read(3)

            if asrType != ASRType.ZLIB:
                fileSize = os.path.getsize(filePath)

                while (inputFile.tell() + 4) < fileSize:
                    sectionStart = inputFile.tell()
                    sectionType, sectionSize = inputFile.readStruct('<4sI')
                    sectionEnd = sectionStart + sectionSize

                    if sectionSize == 0:
                        print(fileSize - sectionEnd)
                        break

                    if sectionType not in sectionTypes:
                        sectionTypes[sectionType] = [ 0, None ]

                    sectionTypes[sectionType][0] += 1 

                    if not sectionTypes[sectionType][1] and sectionStart == 8:
                        sectionTypes[sectionType][1] = relFilePath + ':8'

                    samples[sectionType] = '{}:{}'.format(relFilePath, sectionStart)

                    inputFile.seek(sectionEnd)

    walk(directory)

    for k, v in sectionTypes.items():
        if not v[1]:
            sectionTypes[k][1] = samples[k]

    sectionTypes = dict(sorted(sectionTypes.items(), key=lambda item: item[1][0], reverse=True))

    for sectionType, (entryCount, sampleFile) in sectionTypes.items():
        print("    b'{}',   # Entries: {:<5}  Sample file: {}".format(sectionType.decode('ascii'), entryCount, sampleFile))






# extractASR(BASE_DIR + 'Sounds/StreamingSounds.asr')
# decompressAll(BASE_DIR)
# forEach(BASE_DIR, ContentType.ASTS, extractASR)
# extractASR(BASE_DIR + 'envs/3D_FrontEnd/3D_FrontEnd.ts')
# forEach(BASE_DIR, ContentType.TXST, extractASR)
# forEach(BASE_DIR, ContentType.FNFO, extractASR)
# readRSCF(BASE_DIR + 'envs/TheBlob1.PC_textures')

extractASR(BASE_DIR + 'envs/3D_FrontEnd/3D_FrontEnd.pc')