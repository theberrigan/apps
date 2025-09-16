# Silent Hill Origins Extractor

import os
import re
import sys
import json
import struct
import subprocess

from math import ceil
from zlib import decompressobj
from stat import S_IREAD, S_IWRITE
from os.path import join as joinPath, isfile as isFile, isdir as isDir, exists as checkPathExists, splitext as splitExt, abspath as getAbsPath, normpath as getNormPath, relpath as getRelPath, basename as getBaseName, dirname as getDirPath, getsize as getFileSize
from collections import namedtuple as createNamedTuple



ROOT_DIR       = r'D:\Documents\Games\SHO_PS2_original'
GAME_DIR       = joinPath(ROOT_DIR, 'game_files')
UNPACK_DIR     = joinPath(ROOT_DIR, 'unpacked')
MUSIC_DIR      = joinPath(GAME_DIR, 'MUSIC')
SECT_TREES_DIR = joinPath(ROOT_DIR, '.section_trees')
RWS_SECT_PATH  = joinPath(ROOT_DIR, 'rws_sections.json')
PARSERS_PATH   = joinPath(ROOT_DIR, 'parsers.json')
HXD_EXE        = r'C:\Program Files\HxD\HxD.exe'



def collectFiles (rootDir, isRecursive=True, includeExts=[], excludeExts=[]):
    assert not (includeExts and excludeExts), 'Expected only \'includeExts\' or \'excludeExts\' argument, not both'

    rootDir = getAbsPath(rootDir)
    includeExts = [ item.lower() for item in includeExts ]
    excludeExts = [ item.lower() for item in excludeExts ]

    if not isDir(rootDir):
        print(f'Dir does not exist: { rootDir }')
        return

    if isRecursive:
        for dirPath, _, fileNames in os.walk(rootDir):
            for fileName in fileNames:
                filePath = joinPath(dirPath, fileName)
                fileExt  = getExt(fileName)

                if (includeExts and fileExt not in includeExts) or (excludeExts and fileExt in excludeExts):
                    continue

                yield filePath
    else:
        for item in os.listdir(rootDir):
            itemPath = joinPath(rootDir, item)
            itemExt  = getExt(item)

            if not isFile(itemPath) or (includeExts and itemExt not in includeExts) or (excludeExts and itemExt in excludeExts):
                continue

            yield itemPath


def collectArcs (rootDir=GAME_DIR):
    for filePath in collectFiles(rootDir, False, includeExts=[ '.arc' ]):
        yield filePath


PathInfo = createNamedTuple('PathInfo', (
    'path',      # C:\Python\3.11_x64\python.EXE
    'dirPath',   # C:\Python\3.11_x64
    'baseName',  # python.EXE
    'fileName',  # python
    'fileExt'    # .exe (in lowercase)
))


def parsePath (path):
    path = getNormPath(path)
    dirPath = getDirPath(path)
    baseName = getBaseName(path)
    fileName, fileExt = splitExt(baseName)

    return PathInfo(
       path     = path, 
       dirPath  = dirPath, 
       baseName = baseName, 
       fileName = fileName, 
       fileExt  = fileExt.lower()
    )


def getExt (path):
    return splitExt(path)[1].lower()


def getFileName (path):
    return splitExt(getBaseName(path))[0]


def replaceExtension (filePath, newExt):
    if newExt[0] != '.':
        newExt = '.' + newExt

    return splitExt(filePath)[0] + newExt.lower()


def createDirs (dirPath):
    os.makedirs(dirPath, exist_ok=True)


def toJson (data, pretty=True):
    if pretty:
        indent = 4
        separators=(', ', ': ')
    else:
        indent = None
        separators=(',', ':')

    return json.dumps(data, indent=indent, separators=separators, ensure_ascii=False)  


def writeJson (filePath, data, pretty=True, encoding='utf-8'):
    data = toJson(data, pretty=pretty)

    with open(filePath, 'w', encoding=encoding) as f:
        f.write(data) 


def readJson (filePath, encoding='utf-8'):
    with open(filePath, 'r', encoding=encoding) as f:
        return json.loads(f.read().strip())


def readJsonSafe (filePath, default=None, encoding='utf-8'):
    try:
        return readJson(filePath, encoding=encoding)
    except:
        return default


def decompressData (data):
    decompress = decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


def align (value, boundary):
    return ceil(value / boundary) * boundary


def formatSize (size):
    if size >= (1024 ** 3):
        return '{:.1f}GB'.format(size / (1024 ** 3))
    elif size >= (1024 ** 2):
        return '{:.1f}MB'.format(size / (1024 ** 2))
    elif size >= 1024:
        return '{:.1f}KB'.format(size / 1024)
    else:
        return '{}B'.format(size)


def formatHex (byteSeq, sep=' '):
    return sep.join([ f'{byte:02X}' for byte in byteSeq ])


def formatBytes (byteSeq):
    return '\\x' + formatHex(byteSeq, '\\x')


def readStruct (structFormat, source):
    structSize = struct.calcsize(structFormat)
    dataChunk  = source.read(structSize)
    values     = struct.unpack(structFormat, dataChunk)

    return values[0] if len(values) == 1 else values


def readString (source, size=-1, encoding='utf-8'):
    encoding = (encoding or '').lower()

    if encoding in [ '', 'ascii', 'utf8', 'utf-8' ]:
        null = b'\x00'
        width = 1
    elif encoding in [ 'utf16', 'utf-16', 'utf-16le', 'utf-16-le', 'utf-16be', 'utf-16-be' ]:
        null = b'\x00\x00'
        width = 2
    elif encoding is not None:
        raise Exception(f'Not supported encoding: { encoding }')

    if not isinstance(size, int):
        size = -1
    elif size == 0:
        return '' if encoding else b''

    startOffset = source.tell()
    endOffset   = (startOffset + size) if size > 0 else -1

    buff = b''

    while endOffset < 0 or (source.tell() + width) <= endOffset:
        byte = source.read(width)

        if len(byte) < width or byte == null:
            break

        buff += byte

    if endOffset > 0:
        assert source.tell() <= endOffset
        source.seek(endOffset)

    return buff.decode(encoding) if encoding else buff


def readAlignedString (source, boundary, encoding='utf-8'):
    startOffset = source.tell()
    string      = readString(source, encoding=encoding)
    endOffset   = source.tell()
    finalOffset = align(endOffset - startOffset, boundary)

    source.seek(finalOffset)

    return string


def findPattern (data, pattern):
    offsets = []

    if not data or not pattern:
        return offsets

    dataSize    = len(data)
    patternSize = len(pattern)
    startOffset = 0

    while startOffset < dataSize:
        chunk = data[startOffset:]

        try:
            offset = chunk.index(pattern)
        except:
            offset = -1

        if offset >= 0:
            offsets.append(startOffset + offset)
            startOffset = startOffset + offset + patternSize
        else:
            break

    return offsets



def checkReadOnly (path):
    if not checkPathExists(path):
        return False

    return not (os.stat(path).st_mode & S_IWRITE)


def setReadOnly (path, isReadOnly):
    if not checkPathExists(path):
        return 

    os.chmod(path, (S_IREAD if isReadOnly else S_IWRITE))


SIGNATURE_ARC = b'A2.0'

ArcIndexItem = createNamedTuple('ArcIndexItem', ('nameOffset', 'dataOffset', 'compSize', 'decompSize'))


def unpackArc (arcPath, unpackDir):
    print(f'Unpacking { getBaseName(arcPath) }...\n')

    if not isFile(arcPath):
        print(f'File does not exist: { arcPath }')
        return

    subArcs = []

    with open(arcPath, 'rb') as f:
        signature = f.read(4)

        if signature != SIGNATURE_ARC:
            print('Signature check failed')
            return

        itemCount, dataBaseOffset, namesBaseOffset, namesSize = readStruct('<4I', f)

        indexItems = []

        for i in range(itemCount):
            item = readStruct('<4I', f)

            indexItems.append(ArcIndexItem(
                nameOffset = item[0],
                dataOffset = item[1],
                compSize   = item[2],
                decompSize = item[3]
            ))

        itemNames = []

        for item in indexItems:
            f.seek(namesBaseOffset + item.nameOffset)

            itemNames.append(readString(f))

        createDirs(unpackDir)

        for i, item in enumerate(indexItems):
            f.seek(item.dataOffset)

            data = f.read(item.compSize)

            if item.decompSize > 0:
                data = decompressData(data)
                assert len(data) == item.decompSize

            name = itemNames[i]

            filePath = joinPath(unpackDir, name)

            print(getRelPath(filePath, UNPACK_DIR))

            with open(filePath, 'wb') as outFile:
                outFile.write(data)

            if getExt(name) == '.arc':
                subUnpackDir = joinPath(unpackDir, getFileName(name))
                subArcs.append((filePath, subUnpackDir))

    for filePath, subUnpackDir in subArcs:
        unpackArc(filePath, subUnpackDir)
        os.remove(filePath)

    print('\nDone\n')


def unpackArcs (rootDir=GAME_DIR, rootUnpackDir=UNPACK_DIR):
    for arcPath in collectArcs():
        unpackDir = joinPath(rootUnpackDir, getFileName(arcPath))
        unpackArc(arcPath, unpackDir)


KNOWN_EXTS = [ '.txd', '.xml', '.jpg', '.arc', '.lst', '.log', '.ico', '.igcstream' ]


def collectStats ():
    byExtension = {}
    bySignature = {}

    for filePath in collectFiles(UNPACK_DIR):
        fileSize = getFileSize(filePath)
        fileExt  = getExt(filePath) or '.<no_ext>'

        stat = byExtension[fileExt] = byExtension.get(fileExt, {
            'count': 0,
            'size':  0,
        })

        stat['count'] += 1
        stat['size']  += fileSize

        if fileExt in KNOWN_EXTS:
            continue

        with open(filePath, 'rb') as f:
            signature = f.read(4)
            f.seek(8)
            version = decodeVersion(readStruct('<I', f))

        if version == 0x37002:
            print(getRelPath(filePath, UNPACK_DIR))
            continue

        stat = bySignature[signature] = bySignature.get(signature, {
            'count': 0,
            'size':  0
        })

        stat['count'] += 1
        stat['size']  += fileSize

    byExtension = sorted(byExtension.items(), key=lambda item: item[1]['count'], reverse=True)

    for ext, stat in byExtension:
        print('{}    {}    {}'.format(ext, stat['count'], formatSize(stat['size'])))

    bySignature = sorted(bySignature.items(), key=lambda item: item[1]['count'], reverse=True)

    for signature, stat in bySignature:
        print('{}    {}    {}'.format(formatBytes(signature), stat['count'], formatSize(stat['size'])))


def decodeVersion (version):
    if (version & 0xFFFF0000) == 0:
        return version << 8
    else:
        p1 = ((version >> 14) & 0x3FF00) + 0x30000
        p2 = (version >> 16) & 0x3F
        
        return p1 | p2


def analyzeBySignature ():
    signatures = [
        b'\x43\x4D\x49\x31',
        b'\x02\x00\x00\x00',
        b'\x00\x00\x01\x00',
        b'\xD0\xCF\x11\xE0',
    ]

    filePaths = []

    for filePath in collectFiles(UNPACK_DIR, excludeExts=KNOWN_EXTS):
        with open(filePath, 'rb') as f:
            signature = f.read(4)

            if signature not in signatures:  
                continue

            print(filePath, signatures.index(signature))

            filePaths.append(filePath)

    if not filePaths:
        return

    args = ' '.join([ f'"{ filePath }"' for filePath in filePaths ])

    # os.startfile(HXD_EXE, arguments=args)



def validate ():
    groups  = readJsonSafe(PARSERS_PATH, [])
    extMap  = {}
    fileMap = {}

    for group in groups:
        if group['type'] == 'extension':
            for ext in group['items']:
                extMap[ext.lower()] = group['parser']
        elif group['type'] == 'files':
            for filePath in group['items']:
                filePath = getAbsPath(joinPath(UNPACK_DIR, filePath)).lower()
                fileMap[filePath] = group['parser']

    del groups

    for filePath in collectFiles(UNPACK_DIR):
        filePathLC = getAbsPath(filePath).lower()
        fileExt    = getExt(filePath)

        if filePathLC in fileMap:
            print(fileMap[filePathLC], filePath)
        elif fileExt in extMap:
            print(extMap[fileExt], filePath) 
        else:
            print('Unknown type:', filePath)


def parseRWS (filePath):
    print(filePath)

    fileSize = getFileSize(filePath)

    with open(filePath, 'rb') as f:
        while True:
            if (fileSize - f.tell()) < 12:
                break

            # 0x80d 75 - music?
            sectionType, sectionSize, version = readStruct('<3I', f)
            version = decodeVersion(version)

            if 'music' in filePath.lower() and sectionType not in _wasInMusic:
                _wasInMusic.append(sectionType)

            if abs(version - 0x37000) > 0x2000:
                break

            data = f.read(sectionSize)

            count = _stats[sectionType] = _stats.get(sectionType, 0)

            # if count < 20:
            #     with open(f'D:\\Documents\\Games\\SHO_PS2_original\\_sections\\{sectionType:X}_{count:02d}.bin', 'wb') as f2:
            #         f2.write(data)

            _stats[sectionType] += 1

            print(hex(sectionType), hex(version), sectionSize)

        assert (fileSize - f.tell()) == 0



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

    def getSize (self):
        return self.size


def getRWSSections ():
    secMap = readJsonSafe(RWS_SECT_PATH, {})

    return { int(k, 16): v for k, v in secMap.items() }


def writeSections (f, sections, level=0):
    for section in sections:
        line = ' ' * (4 * level)

        if isinstance(section, SectionNode):
            line += f'{section.type:X} [{ section.start }|{ section.dataStart }-{ section.end }]({ section.dataSize })'

            if section.name:
                line += f' - { section.name }'
        elif isinstance(section, SectionHole):
            line += f'<{ section.start }-{ section.end }>({ section.size })'

        f.write(line + '\n')

        if isinstance(section, SectionNode):
            writeSections(f, section.children, level + 1)


SectionNode = createNamedTuple('SectionNode', ('type', 'name', 'start', 'dataStart', 'end', 'dataSize', 'children'))
SectionHole = createNamedTuple('SectionNode', ('start', 'end', 'size'))

_stats = {}

def findRWSHoles (sections, startOffset, endOffset, parent=None):
    global _stats

    if not sections:
        return

    maxIndex = len(sections) - 1
    holes = []

    for i, section in enumerate(sections):
        if section.start > startOffset:
            holes.append((i, SectionHole(
                start = startOffset, 
                end   = section.start,
                size  = section.start - startOffset
            )))
            
        startOffset = section.end

        if i >= maxIndex and section.end < endOffset:
            holes.append((i + 1, SectionHole(
                start = section.end, 
                end   = endOffset,
                size  = endOffset - section.end
            )))

        if section.children:
            findRWSHoles(section.children, section.dataStart, section.end, section)

    holes.reverse()

    for i, hole in holes:
        sections.insert(i, hole)

    firstChild = sections[0]

    if parent:
        stat = _stats[parent.type] = _stats.get(parent.type, {
            'startHoleCount': 0,
            'sectionCount': 0,
            'holeSizes': []
        })

        stat['sectionCount'] += 1

        if isinstance(firstChild, SectionHole):
            stat['startHoleCount'] += 1

            if firstChild.size not in stat['holeSizes'] and len(stat['holeSizes']) < 5:
                stat['holeSizes'].append(firstChild.size)

            # if parent.type == 0x120 and firstChild.size == 24:
            #     print('\n\n\n', parent.dataStart, '\n\n\n')


_stats2 = []
_txdSampleCount = 0


# TODO:
# - conflicts
# - content of the sections
# - holes between sections
def analyzeRWSs ():
    global _stats2, _txdSampleCount

    knownSections = getRWSSections() 
    filePaths = readJsonSafe(joinPath(ROOT_DIR, 'rws.json'), [])

    createDirs(SECT_TREES_DIR)

    for filePath in filePaths:
        filePath = joinPath(ROOT_DIR, filePath)

        assert isFile(filePath)

        print(filePath)

        with open(filePath, 'rb') as f:
            data = f.read()

        reader = VirtualReader(data)
        sections = []

        for pattern in [ b'\x65\x00\x02\x1C', b'\x37\x00\x02\x1C' ]:
            offsets = findPattern(data, pattern)
            
            for offset in offsets:
                if offset < 8:
                    continue

                sectionStart = offset - 8
                reader.seek(sectionStart)

                sectionType, dataSize, version = readStruct('<3I', reader)

                dataStart  = reader.tell()

                version    = decodeVersion(version)
                sectionEnd = dataStart + dataSize

                if sectionEnd > reader.getSize():
                    continue

                sections.append(SectionNode(
                    type      = sectionType,
                    name      = knownSections.get(sectionType, ''),
                    start     = sectionStart,
                    dataStart = dataStart,
                    end       = sectionEnd,
                    dataSize  = dataSize,
                    children  = []
                ))

        sections = sorted(sections, key=lambda item: item.start)
        children = []

        if len(sections) > 1:
            # Conflicts
            # ------------------------------------

            isConflict = False

            for i in range(1, len(sections)):
                child = sections[i]

                for j in range(i - 1, -1, -1):
                    parent = sections[j]

                    if child.start < parent.end and child.end > parent.end:
                        isConflict = True

                        offsets = {
                            'ps': parent.start,
                            'pe': parent.end,
                            'cs': child.start,
                            'ce': child.end
                        }

                        offsets = sorted(offsets.items(), key=lambda item: item[1])

                        out = 'Conflict:'

                        for k, v in offsets:
                            out += f' { k }:{ v }'

                        out += f' (ps: {parent.type:X} { parent.name }, cs: {child.type:X} { child.name })'

                        print(out)

                        break

                if isConflict:
                    break

            if isConflict:
                continue

            # ------------------------------------

            for section in sections:
                if section.type != 0x716:
                    continue

                reader.seek(section.dataStart)

                metaSize = readStruct('<I', reader)

                metaStart = reader.tell()

                metaEnd = metaStart + metaSize

                if not metaSize:
                    print('\n\n', section.type, section.start, section.dataStart, '\n\n')
                    continue

                srcFileNameLen = readStruct('<I', reader)
                srcFileName = readString(reader, size=srcFileNameLen)

                guid = reader.read(16)

                secTypeLen = readStruct('<I', reader)
                secType = readString(reader, size=secTypeLen)

                dstFileNameLen = readStruct('<I', reader)
                dstFileName = readString(reader, size=dstFileNameLen)

                srcFileDirLen = readStruct('<I', reader)
                srcFileDir = readString(reader, size=srcFileDirLen)

                if secType not in _stats2:
                    _stats2.append(secType)

                assert (metaEnd - reader.tell()) in [ 0, 4 ]

                reader.seek(metaEnd)

                # print(metaEnd)

                contentSize = readStruct('<I', reader)

                contentStart = reader.tell()

                assert (section.end - (contentStart + contentSize)) >= 0

                content = reader.read(contentSize)

                assert (section.end - reader.tell()) < 4
         
                if _txdSampleCount < 10 and secType == 'rwID_AUDIOCUES':
                    _txdSampleCount += 1

                    if srcFileName:
                        fn, ex = splitExt(srcFileName)
                        fn = f'{ fn }_{ _txdSampleCount }{ ex }'
                    else:
                        fn = f'sample_{ _txdSampleCount }.bin'

                    with open(f'D:\\Documents\\Games\\SHO_PS2_original\\.samples\\{fn}', 'wb') as f2:
                        f2.write(content)

                # print('-' * 100)
                # print(srcFileName)
                # print(secType)
                # print(dstFileName)
                # print(srcFileDir)
                # print('-' * 100)

            # sys.exit(0)


            # Output
            # ------------------------------------

            for i in range(1, len(sections)):
                child = sections[i]

                for j in range(i - 1, -1, -1):
                    parent = sections[j]

                    if child.start >= parent.dataStart and child.end <= parent.end:
                        parent.children.append(child)

                        if child not in children:
                            children.append(child)

                        break

            sections = [ section for section in sections if section not in children ]

            findRWSHoles(sections, 0, reader.getSize())

        outFileName = re.sub(r'[\\/]+', '~', getRelPath(filePath, ROOT_DIR)) 
        outFilePath = joinPath(SECT_TREES_DIR, outFileName)

        # with open(outFilePath, 'w', encoding='utf-8') as f:
        #     writeSections(f, sections)

    print(toJson(sorted(_stats2)))

    # for sectionType, item in _stats.items():
    #     sectionCount   = item['sectionCount']
    #     startHoleCount = item['startHoleCount']
    #     holeSizes      = str(item['holeSizes'])

    #     if not item['startHoleCount']:
    #         continue

    #     print(f'{sectionType:x} { startHoleCount }/{ sectionCount }', holeSizes, knownSections.get(sectionType, ''))


def readRWS (f, sections, level=0):
    fileSize = f.getSize()

    while True:
        if (fileSize - f.tell()) < 12:
            break

        sectionType, sectionSize, version = readStruct('<3I', f)
        version = decodeVersion(version)

        if version != 0x37002 or sectionSize > (fileSize - f.tell()):
            break

        if sectionType in sections:
            sectionName = sections[sectionType]
        else:
            sectionName = 'Unknown'

        print(' ' * (4 * level) + f'{sectionType:X} ({ sectionName })')

        readRWS(VirtualReader(f.read(sectionSize)), sections, level + 1)

    # assert (fileSize - f.tell()) == 0


RWSHeader = createNamedTuple('RWSHeader', ('type', 'dataSize', 'version'))


def scanRWS (source, knownSections, level=0):
    totalSize   = source.getSize()
    levelPad    = ' ' * (4 * level)
    subLevelPad = ' ' * (4 * (level + 1))

    while (totalSize - source.tell()) >= 12:
        sectionStart = source.tell()

        assert (totalSize - sectionStart) >= 12

        sectionType, dataSize = readStruct('<2I', source)
        version = decodeVersion(readStruct('<I', source))

        dataStart  = source.tell()
        sectionEnd = dataStart + dataSize

        sectionName = knownSections.get(sectionType, '?')

        header = RWSHeader(
            type     = sectionType,
            dataSize = dataSize,
            version  = version
        )

        if version != 0x37002:
            raise Exception(f'Unexpected version: {version:x}')

        print(f'{ levelPad }{header.type:x} - { sectionName }')

        if header.type == 0x716:
            source.seek(dataStart)

            metaSize  = readStruct('<I', source)
            metaStart = source.tell()
            metaEnd   = metaStart + metaSize

            assert metaSize

            sourceFileNameLen = readStruct('<I', source)
            sourceFileName = readString(source, sourceFileNameLen)

            guid = source.read(16)  # TODO

            contentTypeLen = readStruct('<I', source)
            contentType = readString(source, contentTypeLen)

            outputFileNameLen = readStruct('<I', source)
            outputFileName = readString(source, outputFileNameLen)

            sourceFileDirLen = readStruct('<I', source)
            sourceFileDir = readString(source, sourceFileDirLen)

            assert (metaEnd - source.tell()) in [ 0, 4 ]

            source.seek(metaEnd)

            contentSize  = readStruct('<I', source)
            contentStart = source.tell()
            contentEnd   = contentStart + contentSize

            assert contentEnd <= sectionEnd

            content = source.read(contentSize)

            assert (sectionEnd - source.tell()) < 4

            if contentType == 'rwID_RWS':
                print(f'{ subLevelPad }{ outputFileName }')

                scanRWS(VirtualReader(content), knownSections, level + 2)
            else:
                print(contentType)

        elif header.type == 0x10:
            source.seek(dataStart)

            scanRWS(VirtualReader(source.read(dataSize)), knownSections, level + 1)
        else:
            source.seek(dataStart)

            subReader = VirtualReader(source.read(dataSize))

            isOk = True

            while (subReader.getSize() - subReader.tell()) >= 12:
                subSectionType, subDataSize = readStruct('<2I', subReader)
                subVersion = decodeVersion(readStruct('<I', subReader))

                subDataStart  = subReader.tell()
                subSectionEnd = subDataStart + subDataSize

                if subVersion != 0x37002 or subSectionEnd > subReader.getSize():
                    isOk = False
                    break

                subReader.seek(subSectionEnd)

            if (subReader.getSize() - subReader.tell()) >= 12:
                isOk = False

            if isOk:
                subReader.seek(0)
                scanRWS(subReader, knownSections, level + 1)

        source.seek(sectionEnd)


def scanRWSs ():
    knownSections = getRWSSections() 
    filePaths = readJsonSafe(joinPath(ROOT_DIR, 'rws.json'), [])

    for filePath in filePaths:
        filePath = joinPath(ROOT_DIR, filePath)

        print(filePath)

        with open(filePath, 'rb') as f:
            reader = VirtualReader(f.read())

        scanRWS(reader, knownSections)

        print('\n\n')






if __name__ == '__main__':
    # unpackArcs()
    # collectStats()
    # analyzeBySignature()
    # validate()
    # print(hex(decodeVersion(469893221)))
    # print(hex(decodeVersion(469893175)))
    # parseRWSs()
    # print(getRWSSections())
    # analyzeRWSs()
    scanRWSs()

    # SEE: D:\Documents\Games\SHO_PS2_original.7z

    # with open(r"D:\Documents\Games\SHO_PS2_original\game_files\MUSIC\A\APRTMENT.RWS", 'rb') as f:        
    #     scanRWS(VirtualReader(f.read()), getRWSSections())

    # with open(r"D:\Documents\Games\SHO_PS2_original\_sections\704_00.bin", 'rb') as f:
    #     f.seek(27)
    #     guid = readGuid(f)

    #     for filePath in collectFiles(UNPACK_DIR):
    #         with open(filePath, 'rb') as f:
    #             data = f.read()

    #             offsets = findPattern(data, guid.encode('ascii'))

    #             if offsets:
    #                 print(filePath, offsets)

'''
# RWS, Audio: http://wiki.xentax.com/index.php/RenderWare_RWS

80d
    80e - meta?
    80f - VAG (Sony ADPCM)?
716
    metaSize = readU32()
    meta = read(metaSize)
        size1 = U32()
        sourceFileName = str(size1)

        guid = read(16)

        size2 = U32()
        type = str(size2)  // rwID_*

        size3 = U32()
        outputFileName = str(size3)

        size4 = U32()
        sourceFileDir = str(size4)

        U32() == 0 ???
    readData()
    align(4)
80C (related to rwaID_WAVEDICT?)
    itemCount = readU32()
    for i in itemCount:
        802 - some container
            803 - only inside 802
            804 - only inside 802
809 (rwaID_WAVEDICT?)
    80A
    80C (see 80C)
11d
    unk1 = readU32()
    readChildSections()
29
    strSecCount = readU32()
    for i in strSecCount:
        read_rwID_STRING()
a05
    indexOfFollowingDataInParentStruct = readU32()
    readChildSections()   



11d 795/795 [4]      Collision PLG / rwID_COLLISPLUGIN
120 309/309 [20, 24] Material Effects PLG / rwID_MATERIALEFFECTSPLUGIN
29  125/125 [4]      Chunk Group Start / rwID_CHUNKGROUPSTART
a05   73/73 [4] 
23      7/7 [8]      Platform Independent Texture Dictionary / rwID_PITEXDICTIONARY
1b      1/1 [68]     Anim Animation / rwID_ANIMANIMATION

# ---------------------------------

Types of 0x716 section:

- JPG
- rwID_AINAVMESH
- rwID_AUDIOCUES
- rwID_CBSP
- rwID_CLUMP
- rwID_COMBATCOLLISION
- rwID_DMORPHANIMATION
- rwID_HANIMANIMATION
- rwID_KFONT
- rwID_POLYAREA
- rwID_RWS
- rwID_SPLINE
- rwID_STATETRANSITION
- rwID_TEXDICTIONARY
- rwID_WORLD
- rwaID_WAVEDICT
- rwpID_BODYDEF

# ---------------------------------



1    91088    Struct / rwID_STRUCT
3    82664    Extension / rwID_EXTENSION
2    62653    String / rwID_STRING
110    30865    Sky Mipmap Val / rwID_SKYMIPMAPVAL
a01    30403    
7    30402    Material / rwID_MATERIAL
6    29614    Texture / rwID_TEXTURE
11f    15032    User Data PLG / rwID_USERDATAPLUGIN / User Data
1f    12663    Right To Render / rwID_RIGHTTORENDER
704    12330    
a0b    10697    
11e    9637    HAnim PLG / rwID_HANIMPLUGIN / Bone
716    6312    
50e    5379    Bin Mesh PLG / rwID_BINMESHPLUGIN / Material Split
510    5098    Native Data PLG / rwID_NATIVEDATAPLUGIN / VC Geometry Data
1b    3930    Anim Animation / rwID_ANIMANIMATION
8    3670    Material List / rwID_MATLIST
802    3377    
803    3377    
804    3377    
f    3061    Geometry / rwID_GEOMETRY
a03    3061    
14    3061    Atomic / rwID_ATOMIC
a06    3061    
a07    3061    
1101    3018    
9    2318    Atomic Section / rwID_ATOMICSECT / Atomic Sect
a    1709    Plane Section / rwID_PLANESECT / Plane Sect
120    1506    Material Effects PLG / rwID_MATERIALEFFECTSPLUGIN
15    1302    Texture Native / rwID_TEXTURENATIVE
10    1111    Clump / rwID_CLUMP
e    1061    Frame List / rwID_FRAMELIST
1a    1061    Geometry List / rwID_GEOMETRYLIST
11d    887    Collision PLG / rwID_COLLISPLUGIN
2c    887    Coll Tree / rwID_COLLTREE
12a    854    Geometric PVS PLG / rwID_GPVSPLUGIN
116    741    Skin PLG / rwID_SKINPLUGIN / Skin
29    683    Chunk Group Start / rwID_CHUNKGROUPSTART
2a    683    Chunk Group End / rwID_CHUNKGROUPEND
71c    648    
b    609    World / rwID_WORLD
135    503    UV Animation PLG / rwID_UVANIMPLUGIN
16    449    Texture Dictionary / rwID_TEXDICTIONARY
a05    355    
24    293    Table of Contents / rwID_TOC / TOC
809    273    
80a    273    
80c    273    
f00    265    
1100    214    
c08    154    
c00    151    
a04    123    
c02    115    
a0a    107    
a09    107    
1e    98    Delta Morph Animation / rwID_DMORPHANIMATION
2b    80    UV Animation Dictionary / rwID_UVANIMDICT / UV Anim Dict
80d    75    
80e    75    
80f    75    
c01    63    
5    55    Camera / rwID_CAMERA
18    52    Image / rwID_IMAGE
907    48    
122    40    Delta Morph PLG / rwID_DMORPHPLUGIN
c    32    Spline / rwID_SPLINE
23    20    Platform Independent Texture Dictionary / rwID_PITEXDICTIONARY
64    18    
0    2    N/A Object / rwID_NAOBJECT
1000    2    
12ef    2    
781f    1    
78    1    
3ee2    1    
6263    1 

'''