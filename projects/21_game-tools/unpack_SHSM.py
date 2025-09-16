# Silent Hill Shattered Memories Extractor

import os, struct, math, sys, re, zlib, json, subprocess, shutil
from stat import S_IREAD, S_IWRITE
from pathlib import Path
from collections import namedtuple
from hashlib import md5
import concurrent.futures

GAME_DIR = r'G:\Games\Silent Hill Shattered Memories'
UNPACK_DIR = os.path.join(GAME_DIR, '.unpack')

def formatBytes (byteSeq, sep=' '):
    return sep.join([ '{:02X}'.format(b) for b in byteSeq ])

def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items


def readNullString (descriptor, encoding='utf-8'):
    buff = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'' or byte == b'\x00':
            break

        buff += byte

    return buff.decode(encoding, errors='ignore')


def bytesToNullString (byteSeq):
    return ''.join([ chr(b) for b in byteSeq if b > 0 ])


def decompressData (data):
    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


def align (descriptor, boundry):
    descriptor.seek(math.ceil(descriptor.tell() / boundry) * boundry)


def findPattern (f, pattern, fromPos = 0, toPos = -1, maxBuffSize=(64 * 1024)):
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


def findPattern2 (data, pattern):
    offsets = []

    if not pattern:
        return offsets

    dataSize    = len(data)
    patternSize = len(pattern)
    startPos    = 0

    while startPos < dataSize:
        chunk = data[startPos:]

        try:
            offset = chunk.index(pattern)
        except:
            offset = -1

        if offset >= 0:
            offsets.append(startPos + offset)
            startPos += offset + patternSize
        else:
            break

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


class Item:
    def __init__ (self, nameHash=None, offset=None, compSize=None, decompSize=None):
        self.nameHash = nameHash
        self.offset = offset
        self.compSize = compSize
        self.decompSize = decompSize


def unpack (filePath, unpackDir):
    print(f'Unpacking { os.path.basename(filePath) }')

    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    os.makedirs(unpackDir, exist_ok=True)

    manifest = []

    with open(filePath, 'rb') as f:
        signature = f.read(4)

        if signature != b'\x10\xFA\x00\x00':
            raise Exception('Signature check failed')

        itemCount, contentOffset, zero1 = readStruct('<3I', f)
        items = []

        assert zero1 == 0

        print(itemCount, contentOffset, zero1)

        for i in range(itemCount):
            nameHash, offset, compSize, decompSize = readStruct('<4I', f)
            items.append(Item(nameHash, offset, compSize, decompSize))
            # print(nameHash, offset, compSize, decompSize)

        for item in items:
            f.seek(item.offset)
            data = f.read(item.compSize)

            if item.decompSize > 0:
                data = decompressData(data)
                assert len(data) == item.decompSize

            itemName = f'{item.offset:08X}_{item.nameHash:08X}.bin'

            manifest.append({
                'nameHash': item.nameHash,
                'offset': item.offset,
                'compSize': item.compSize,
                'decompSize': item.decompSize,
                'name': itemName
            })

            with open(os.path.join(unpackDir, itemName), 'wb') as f2:
                f2.write(data)

        print(f.tell())

    print('Done\n')

    return manifest



def unpackAll (gameDir, unpackDir):
    if not os.path.isdir(gameDir):
        raise Exception(f'Game dir does not exist: { gameDir }')

    manifest = {}

    for item in os.listdir(gameDir):
        itemPath = os.path.join(gameDir, item)

        if item.lower().endswith('.arc') and os.path.isfile(itemPath):
            unpackDir = os.path.splitext(itemPath)[0]
            manifest[item] = unpack(itemPath, unpackDir)

    with open(os.path.join(gameDir, 'manifest.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(manifest, ensure_ascii=False, indent=4))


def setReadOnly (path, isReadOnly):
    if not os.path.exists(path):
        return 

    os.chmod(path, (S_IREAD if isReadOnly else S_IWRITE))


def checkReadOnly (path):
    if not os.path.exists(path):
        return False

    return not (os.stat(path).st_mode & S_IWRITE)


def replaceExtension (filePath, newExt):
    return os.path.splitext(filePath)[0] + newExt.lower()



# def calcStringRandomness (string):
#     if not string:
#         return 9223372036854775807

#     charFreqs  = {}
#     totalCount = 0

#     for char in string:
#         charCode = ord(char)

#         if not ((48 <= charCode <= 57) or (65 <= charCode <= 90) or (97 <= charCode <= 122)):
#             continue

#         charFreqs[char] = charFreqs.get(char, 0) + 1
#         totalCount += 1

#     if not charFreqs:
#         return 9223372036854775807

#     deviation = 0

#     for char, charFreq in charFreqs.items():
#         deviation += abs(ENG_FREQS[char] - (charFreq / totalCount))

#     return deviation

# ------------------------------------------------------------------------------------------------------------------------------------


ROOT_DIR = r'D:\Documents\Downloads\Torrents\Silent Hill Shattered Memories (Wii)'
DATA_DIR = os.path.join(ROOT_DIR, 'data')
HXD_EXE  = r'C:\Program Files\HxD\HxD.exe'
# ENG_FREQS    = None
# with open(os.path.join(ARCHIVES_DIR, 'char_freqs.json'), 'r', encoding='utf-8') as f:
#     ENG_FREQS = json.load(f)


class FileInfo:
    def __init__ (self, rootDir=None, absPath=None, relPath=None, dirPath=None, fileName=None, baseName=None, ext=None):
        self.rootDir  = rootDir   # C:\Python
        self.absPath  = absPath   # C:\Python\3.11_x64\python.exe
        self.relPath  = relPath   # 3.11_x64\python.exe
        self.dirPath  = dirPath   # C:\Python\3.11_x64
        self.fileName = fileName  # python.exe
        self.baseName = baseName  # python
        self.ext      = ext       # ext


def scanFiles (rootDir=DATA_DIR, includeExts=[], excludeExts=[]):
    assert not (includeExts and excludeExts), 'Expected only \'includeExts\' or \'excludeExts\' argument, not both'

    rootDir = os.path.abspath(rootDir)

    if not os.path.isdir(rootDir):
        print(f'Dir does not exist: { rootDir }')
        return

    for dirPath, _, fileNames in os.walk(rootDir):
        for fileName in fileNames:
            itemAbsPath = os.path.abspath(os.path.join(dirPath, fileName))
            itemRelPath = os.path.relpath(itemAbsPath, rootDir)
            itemBaseName, itemExt = os.path.splitext(fileName)

            itemExt = itemExt.lower()

            if (includeExts and itemExt not in includeExts) or (excludeExts and itemExt in excludeExts):
                continue

            yield FileInfo(
               rootDir  = rootDir, 
               absPath  = itemAbsPath, 
               relPath  = itemRelPath, 
               dirPath  = dirPath, 
               fileName = fileName, 
               baseName = itemBaseName, 
               ext      = itemExt
            )


def collectArcDirs (withArcName=False):
    result = []

    if not os.path.isdir(ARCHIVES_DIR):
        print('Dir doesn\'t exist:', ARCHIVES_DIR)
        return result

    for item in os.listdir(ARCHIVES_DIR):
        itemPath = os.path.abspath(os.path.join(ARCHIVES_DIR, item))

        if not os.path.isdir(itemPath):
            continue

        if withArcName:
            result.append((item, itemPath))
        else:
            result.append(itemPath)            

    return result


def collectStats ():
    stats = {}

    for arcName, arcDir in collectArcDirs(True):
        for fileInfo in scanFiles(arcDir, includeExts=[ '.bin' ]):
            filePath = fileInfo.absPath

            with open(filePath, 'rb') as f:
                signature = f.read(4)

                stat = stats[signature] = stats.get(signature, {
                    'totalSize': 0,
                    'totalItems': 0,
                    'itemsPerArc': {}
                })

                stat['totalSize'] += os.path.getsize(filePath)
                stat['totalItems'] += 1
                stat['itemsPerArc'][arcName] = stat['itemsPerArc'].get(arcName, 0) + 1

    stats = sorted(stats.items(), key=lambda item: item[1]['totalItems'], reverse=True)
    maxSignLen = 0
    maxSizeLen = 0
    maxTILen   = 0

    for i, (signature, stat) in enumerate(stats):
        signRepr   = repr(signature)
        signHex    = formatBytes(signature, '_')
        totalSize  = formatSize(stat['totalSize'])
        totalItems = stat['totalItems']
        ratios     = []


        for arcName, itemsPerArc in stat['itemsPerArc'].items():
            ratios.append(f'{ arcName }: {(itemsPerArc / totalItems * 100):.1f}%')

        stats[i]   = (signRepr, signHex, totalSize, totalItems, ', '.join(ratios))
        maxSignLen = max(maxSignLen, len(signRepr))
        maxSizeLen = max(maxSizeLen, len(totalSize))
        maxTILen   = max(maxTILen, len(str(totalItems)))

    for signRepr, signHex, totalSize, totalItems, ratios in stats:
        print('{}    {}    {}    {}    ({})'.format(
            signRepr.ljust(maxSignLen),
            signHex,
            totalSize.rjust(maxSizeLen),
            str(totalItems).rjust(maxTILen),
            ratios
        ))


# Decode .baml_ files
def decodeBaml (): 
    # https://learn.microsoft.com/ru-ru/dotnet/desktop/wpf/advanced/xaml-namespaces-and-namespace-mapping-for-wpf-xaml?view=netframeworkdesktop-4.8#code-try-1
    # https://gist.github.com/forki/2161484
    # ILSpy, dotPeek 
    filePath = r'D:\Documents\Downloads\Torrents\Silent Hill Shattered Memories (Wii)\archives\igc\00361800_181DFBA2__0001E700_0D610CBE.bin'
    fileSize = os.path.getsize(filePath)

    with open(filePath, 'rb') as f:
        f.seek(12)

        minOffset = 408
        maxOffset = 1191

        for i in readStruct('<99I', f):
            if minOffset <= i <= maxOffset:
                f.seek(i)
                print(i, readNullString(f))
                continue
            print(i)


# Decode .i10n files
def decodeLocale ():
    filePaths = []

    # filePath = r'D:\Documents\Downloads\Torrents\Silent Hill Shattered Memories (Wii)\archives\data\050EC800_7EFCA512.bin'

    for filePath in filePaths:
        print(filePath)

        with open(filePath, 'rb') as f:
            signature = f.read(4)

            assert signature == b'\x02\x00\x00\x00'

            itemCount = readStruct('<I', f)
            items = []  # ptr, offset

            for i in range(itemCount):
                items.append(readStruct('<2I', f))

            contentStart = f.tell()

            for i, (ptr, offset) in enumerate(items):
                f.seek(contentStart + (offset * 2))

                chunk = b''

                while True:
                    pair = f.read(2)

                    assert len(pair) == 0 or len(pair) == 2

                    if pair == b'' or pair == b'\x00\x00':
                        break

                    chunk += pair

                # BOM?
                assert chunk[:4] == b'\x01\x00\x01\x00'

                string = chunk.decode('utf-16')

                if i < 2:
                    print(ptr, offset, string)

        print('\n\n')


# Decode .arc_ files
def decodeWiiArcFile ():
    # - .arc - (by Nintendo) not compressed archive
    #   Open with: https://github.com/libertyernie/brawltools
    #   Formats: https://gota7.github.io/Citric-Composer/specs/binaryWav.html
    pass


def analyzeBySignature ():
    signatures = [
        b'\x00\x20\xaf\x30',
        b'\x1E\xF1\xC7\x7E',
        b'\x00\x00\x00\x00',
    ]

    filePaths = []

    for fileInfo in scanFiles(collectArcDirs(), includeExts=[ '.bin' ]):
        filePath = fileInfo.absPath
        fileSize = os.path.getsize(filePath)

        with open(filePath, 'rb') as f:
            signature = f.read(4)

            if signature not in signatures:  
                continue

            f.seek(0)

            uint1, uint2 = readStruct('<II', f)

            print(filePath, formatBytes(signature), fileSize, (uint1 + uint2) == fileSize)

            filePaths.append(filePath)

    args = ' '.join([ f'"{ filePath }"' for filePath in filePaths ])

    os.startfile(HXD_EXE, arguments=args)


def analyzeByContent ():
    filePaths = []

    for fileInfo in scanFiles(collectArcDirs(), includeExts=[ '.bin' ]):
        filePath = fileInfo.absPath

        with open(filePath, 'rb') as f:
            signature = f.read(4)

            if findPattern(f, b'FSB4'):
                filePaths.append(filePath)
                print(filePath, formatBytes(signature))

    args = ' '.join([ f'"{ filePath }"' for filePath in filePaths ])

    os.startfile(HXD_EXE, arguments=args)


# D:\Documents\Downloads\Torrents\Silent Hill Shattered Memories (Wii)\archives\igc\00361800_181DFBA2__0004A960_00000F7C.bin
def renameFilesBySignature ():
    signatureMap = {}

    maxSignLen = 0
    signLens   = []

    for signature in signatureMap.keys():
        signLen = len(signature)
        maxSignLen = max(maxSignLen, signLen)
        signLens.append(signLen)

    signLens = sorted(list(set(signLens)), reverse=True)

    for fileInfo in scanFiles(collectArcDirs(), includeExts=[ '.bin' ]):
        filePath = fileInfo.absPath

        with open(filePath, 'rb') as f:
            signature = f.read(maxSignLen)

        targetExt = None

        for signLen in signLens:
            shortSign = signature[:signLen]

            if shortSign in signatureMap:
                targetExt = signatureMap[shortSign]
                break

        if not targetExt:
            continue

        targetFilePath = os.path.join(fileInfo.dirPath, fileInfo.baseName + targetExt)

        print(filePath)
        print(targetFilePath)
        print(' ')

        wasReadOnly = checkReadOnly(filePath)

        setReadOnly(filePath, False)

        os.rename(filePath, targetFilePath)

        setReadOnly(targetFilePath, wasReadOnly)


def decompress_10_FA_00_00 ():
    for fileInfo in scanFiles(collectArcDirs(), includeExts=[ '.bin' ]): 
        filePath = fileInfo.absPath

        with open(filePath, 'rb') as f:
            signature = f.read(4)

            if signature != b'\x10\xFA\x00\x00':
                continue

            print(filePath)

            itemCount, contentOffset, zero1 = readStruct('<3I', f)
            items = []

            assert zero1 == 0

            for i in range(itemCount):
                nameHash, offset, compSize, decompSize = readStruct('<4I', f)
                items.append(Item(nameHash, offset, compSize, decompSize))

            for item in items:
                f.seek(item.offset)

                data = f.read(item.compSize)

                if item.decompSize > 0:
                    data = decompressData(data)
                    assert len(data) == item.decompSize

                itemName = f'{fileInfo.baseName}__{item.offset:08X}_{item.nameHash:08X}.bin'
                itemPath = os.path.join(fileInfo.dirPath, itemName)

                print('-', itemPath)

                setReadOnly(itemPath, False)

                with open(itemPath, 'wb') as f2:
                    f2.write(data)

                setReadOnly(itemPath, True)

        setReadOnly(filePath, False)
        os.remove(filePath)


def changeFileExtension (filePath, newExt):
    if not os.path.isfile(filePath):
        print('File does not exist:', filePath)
        return

    targetFilePath = replaceExtension(filePath, newExt)

    print(filePath)
    print(targetFilePath)
    print(' ')

    wasReadOnly = checkReadOnly(filePath)

    os.rename(filePath, targetFilePath)

    setReadOnly(targetFilePath, wasReadOnly)


def extractNameHashes (filePath):
    baseName = os.path.basename(os.path.splitext(filePath)[0])

    match = re.match(r'^[\da-f]{8}_([\da-f]{8})$', baseName, flags=re.I)

    if match:
        return (int(match.group(1), 16), None)

    match = re.match(r'^[\da-f]{8}_([\da-f]{8})__[\da-f]{8}_([\da-f]{8})$', baseName, flags=re.I)

    if match:
        return (int(match.group(1), 16), int(match.group(2), 16))

    return (None, None)


def analyzeByNameHash ():
    pathMap = {}

    for fileInfo in scanFiles(collectArcDirs()):
        match = re.match(r'^[\da-f]{8}_([\da-f]{8})$', fileInfo.baseName, flags=re.I)

        if not match:
            match = re.match(r'^[\da-f]{8}_[\da-f]{8}__[\da-f]{8}_([\da-f]{8})$', fileInfo.baseName, flags=re.I)

        if not match:
            print('Failed:', fileInfo.fileName)
            return

        nameHash = int(match.group(1), 16)

        filePaths = pathMap[nameHash] = pathMap.get(nameHash, [])

        filePaths.append(fileInfo.absPath)

    for nameHash, filePaths in pathMap.items():
        if len(filePaths) <= 1:
            continue

        print(hex(nameHash))

        expectedChecksum = None

        for filePath in filePaths:
            print('-', filePath)

            with open(filePath, 'rb') as f:
                checksum = md5(f.read()).digest()

            if expectedChecksum is None:
                expectedChecksum = checksum
            elif expectedChecksum != checksum:
                print('Failed')        


def findDups ():
    hashMap = {}
    sizeMap = {}

    for fileInfo in scanFiles(collectArcDirs()):
        filePath = fileInfo.absPath

        with open(filePath, 'rb') as f:
            checksum = md5(f.read()).hexdigest()

        filePaths = hashMap[checksum] = hashMap.get(checksum, [])

        filePaths.append(filePath)

        if checksum not in sizeMap:
            sizeMap[checksum] = os.path.getsize(filePath)

    totalOverhead = 0

    for contentHash, filePaths in hashMap.items():
        dupCount = len(filePaths)

        if dupCount < 2:
            continue

        totalOverhead += sizeMap[contentHash] * (dupCount - 1)

        print(contentHash)

        for filePath in filePaths:
            print('-', filePath)

    print(formatSize(totalOverhead))


def findPatternsThread (filePath, patterns):
    print(filePath)

    results = []

    with open(filePath, 'rb') as f:
        for pattern in patterns:
            offsets = findPattern(f, pattern, 0, -1, os.path.getsize(filePath))
            results.append((pattern, offsets))

    return (filePath, results)


def analyzeDeps ():
    nameHashes = []

    for fileInfo in scanFiles(collectArcDirs()):
        filePath = fileInfo.absPath

        parentNameHash, childNameHash = extractNameHashes(filePath)

        if parentNameHash:
            parentNameHash = struct.pack('<I', parentNameHash)
            nameHashes.append(parentNameHash)

        if childNameHash:
            childNameHash = struct.pack('<I', childNameHash)
            nameHashes.append(childNameHash)

    nameHashes = list(set(nameHashes))
    matches = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for fileInfo in scanFiles(collectArcDirs(), excludeExts=[ '.jpg', '.xml', '.csv' ]):
            futures.append(executor.submit(findPatternsThread, fileInfo.absPath, nameHashes))

        for future in concurrent.futures.as_completed(futures):
            filePath, results = future.result()
            offsets = []

            for _, patternOffsets in results:
                offsets += patternOffsets

            matches.append((filePath, sorted(offsets)))

    matches = sorted(matches, reverse=True, key=lambda item: len(item[1]))

    for filePath, offsets in matches:
        print(filePath, len(offsets))


def collectNameHashes ():
    hashes  = []
    pairs   = []
    uniques = []

    for fileInfo in scanFiles(collectArcDirs()):
        parentHash, childHash = extractNameHashes(fileInfo.absPath)

        if parentHash:
            hashes.append(parentHash)

        if childHash:
            hashes.append(childHash)

        if not parentHash or not childHash:
            continue

        unique = f'{ parentHash }_{ childHash }'

        if unique not in uniques:
            uniques.append(unique)
            pairs.append((parentHash, childHash))

    result = {
        'hashes': sorted(list(set(hashes))),
        'pairs': sorted(pairs, key=lambda item: item[0])
    }

    with open(os.path.join(ARCHIVES_DIR, 'name_hashes.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


def findStrings (f, fromPos=0, toPos=-1, minLen=4):
    results = []

    wasPos = f.tell()

    fromPos = max(0, fromPos)

    f.seek(fromPos)

    if toPos > fromPos:
        data = f.read(toPos - fromPos)
    else:
        data = f.read()

    if not data:
        return results

    dataSize = len(data)
    startPos = 0

    while startPos < dataSize:
        chunk = ''

        for i in range(startPos, dataSize):
            byte = data[i]

            if (byte in b'\r\n\t') or (32 <= byte <= 126):
                chunk += chr(byte)
            else:
                startPos = i + 1
                break

        if len(chunk) >= minLen:
            results.append(chunk)

    f.seek(wasPos)

    return results


def collectStats2 ():
    stats       = {}
    totalSize   = 0
    maxExtLen   = 0
    maxCountLen = 0
    maxSizeLen  = 0

    for fileInfo in scanFiles():
        filePath = fileInfo.absPath
        fileExt  = fileInfo.ext
        fileSize = os.path.getsize(filePath)

        print(filePath)

        stat = stats[fileExt] = stats.get(fileExt, {
            'count': 0,
            'size':  0,
            'signature': None
        })

        stat['count'] += 1
        stat['size']  += fileSize
        totalSize     += fileSize

        maxExtLen   = max(maxExtLen, len(fileExt))
        maxCountLen = max(maxCountLen, len(str(stat['count'])))
        maxSizeLen  = max(maxSizeLen, len(str(stat['size'])))

        if stat['signature'] == False:
            continue

        with open(filePath, 'rb') as f:
            signature = f.read(4)

            if stat['signature'] is None:
                stat['signature'] = signature
            elif stat['signature'] != signature:
                stat['signature'] = False

    stats = sorted(stats.items(), key=lambda item: item[1]['size'], reverse=True)

    for ext, stat in stats:
        if stat['signature']:
            signature = '\\x' + formatBytes(stat['signature'], '\\x')
        else:
            signature = ''

        print('{}    {}    {}    {}'.format(
            str(ext).ljust(maxExtLen),
            str(stat['count']).rjust(maxCountLen),
            formatSize(stat['size']).rjust(maxSizeLen),
            signature
        ))


def findPatternsFromBootmenu ():
    with open(os.path.join(ROOT_DIR, '.misc', 'data_1696.xml.json'), 'r', encoding='utf-8') as f:
        items = json.load(f)

    results = {}
    _count  = 0

    for fileInfo in scanFiles(excludeExts=[ '.xml', '.jpg', '.i10n' ]):
        # if _count >= 50:
        #     break

        _count += 1

        filePath = fileInfo.absPath
        fileName = fileInfo.fileName
        fileSize = os.path.getsize(filePath)

        print(filePath)

        with open(fileInfo.absPath, 'rb') as f:
            data = f.read()

            for sel, value in items:
                # offsets = findPattern(f, value.encode('ascii'), maxBuffSize=fileSize)
                offsets = findPattern2(data, value.encode('ascii'))  # 23.8s

                if not offsets:
                    continue

                stats = results[fileName] = results.get(fileName, [])

                stats.append([ sel, value, offsets ])

    with open(os.path.join(ROOT_DIR, '.misc', 'level_patterns.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


def findPaths ():
    results = {}
    paths = []
    exts = {}

    for fileInfo in scanFiles(excludeExts=[ '.xml', '.jpg', '.i10n', '.csv' ]):
        filePath = fileInfo.absPath
        fileName = fileInfo.fileName

        print(filePath)

        with open(fileInfo.absPath, 'rb') as f:
            offsets = findPattern2(f.read(), b'z:\\')

            if not offsets:
                continue

            stats = results[fileName] = results.get(fileName, [])

            for offset in offsets:
                f.seek(offset)

                path = readNullString(f, 'ascii')

                if not path:
                    continue

                for i, char in enumerate(path):
                    charCode = ord(char)

                    if charCode < 32 or charCode > 126 or char in '*?"<>|':
                        path = path[:i]
                        break

                if len(path) < 50:
                    continue

                stats.append(path)
                paths.append(path)

    with open(os.path.join(ROOT_DIR, '.misc', 'paths_by_file.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    with open(os.path.join(ROOT_DIR, '.misc', 'paths.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(list(set(paths)))))

    paths = sorted(list(set([ os.path.normpath(path).lower() for path in paths ])))

    for path in paths:
        ext = os.path.splitext(path)[1]
        exts[ext] = exts.get(ext, 0) + 1

    exts = sorted(exts.items(), key=lambda item: item[1], reverse=True)

    for ext, count in exts:
        print(ext, count)


def decodeVersion (version):
    if (version & 0xFFFF0000) == 0:
        return version << 8
    else:
        p1 = ((version >> 14) & 0x3FF00) + 0x30000
        p2 = (version >> 16) & 0x3F
        
        return p1 | p2


def readRWS ():
    for fileInfo in scanFiles(includeExts=[ '.rws' ]):
        filePath = fileInfo.absPath
        fileSize = os.path.getsize(filePath)

        print(filePath)

        with open(filePath, 'rb') as f:
            while True:
                if (fileSize - f.tell()) < 12:
                    break

                sectionStart = f.tell()
                sectionType, sectionSize, version = readStruct('<3I', f)
                version = decodeVersion(version)

                if sectionType == 0:
                    assert (f.tell() + sectionSize) == fileSize
                    break

                f.seek(sectionStart + (sectionSize or 12))

                print(hex(sectionType), hex(version), sectionSize, sectionStart)


        print('\n\n')





if __name__ == '__main__':
    # renameFilesBySignature()
    # analyzeByContent()
    # analyzeBySignature()
    # collectStats()
    # analyzeByNameHash()
    # findDups()
    # analyzeDeps()
    # collectNameHashes()
    # collectStats2()
    # findPaths()
    # readRWS()

    print(hex(decodeVersion(469893221)))

    '''
    store = {}

    for fileInfo in scanFiles(includeExts=[ '.unk1_' ]):
        filePath = fileInfo.absPath

        with open(filePath, 'rb') as f:
            size1, size2 = readStruct('<II', f)

            files = store[size1] = store.get(size1, [])

            files.append(filePath)

            assert (size1 + size2) == os.path.getsize(filePath)

    store = sorted(store.items(), key=lambda item: item[0])

    for key, files in store:
        print(key)

        for i in range(min(2, len(files))):
            print('-', files[i])
    '''

    # ------------------------------------------------------- 
    # .anm    1987     RW animations
    # .dff     982     RW dynamic models
    # .rws     923     RW container for different streams (bsp, dff, txd, ...) (https://rwsreader.sourceforge.net/)
    # .bsp     620     RW static models (world map)
    # .dma     399     RW details of morph animation (legacy?)
    # .txd     159     RW texture dictionary
    # .fdp     159     FMOD project file
    # .spl     144     ? (spline?)
    # .nav     144     ?
    # .fgb      16     ?
    # .MZI       9     ?
    # .Kft       2     ?
    # .jpg       2     jackal
    # .mtd       1     ?
    # ------------------------------------------------------- 
    # .rws      1868         2.1gb    \x16\x07\x00\x00
    # .unk1_     260         1.1gb    
    # .unk2_      19       186.7mb    \x01\x0F\x00\x00
    # .xmp        24        20.9mb    
    # .arc_       27         7.3mb    \x55\xAA\x38\x2D
    # .i10n       18         3.6mb    \x02\x00\x00\x00
    # .jpg        87         2.6mb    \xFF\xD8\xFF\xE0
    # .baml_      95         1.2mb    
    # .unk6_       1       331.2kb    \x00\x00\x00\x00
    # .unk5_       2       203.3kb    \x1E\xF1\xC7\x7E
    # .csv        21       188.2kb    
    # .xml         2       117.4kb    \x3C\x42\x4F\x4F
    # .unk4_       4        57.2kb    \x00\x20\xAF\x30
    # .unk3_       9        39.8kb    \xFE\xFF\x00\x22
    # ------------------------------------------------------- 
    # Formats:
    # - .unk1_ - # 4 size1 | 4 size2    // size1 + size2 = fileSize
    # -------------------------------------------------------    
    # TODO:
    # - find file dups
    # + find by name hash ((nameHash1 == nameHash2) <=/=> (content1 == content2))
    # - find FSB4
    # - find strings in .bin
    # -------------------------------------------------------
    #     try:
    #         process = subprocess.run([ '.\\rwsedit.exe', '-v', '-l', '50', itemPath ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     except:
    #         pass
    #     if process.stderr:
    #         print(process.stderr.decode('ascii'))
    #     if process.stdout:
    #         print(process.stdout.decode('ascii'))
    # -------------------------------------------------------
    # https://neerc.ifmo.ru/wiki/index.php?title=%D0%9F%D0%BE%D0%B8%D1%81%D0%BA_%D0%BF%D0%BE%D0%B4%D1%81%D1%82%D1%80%D0%BE%D0%BA%D0%B8_%D0%B2_%D1%81%D1%82%D1%80%D0%BE%D0%BA%D0%B5_%D1%81_%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5%D0%BC_%D1%85%D0%B5%D1%88%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F._%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC_%D0%A0%D0%B0%D0%B1%D0%B8%D0%BD%D0%B0-%D0%9A%D0%B0%D1%80%D0%BF%D0%B0
    # -------------------------------------------------------