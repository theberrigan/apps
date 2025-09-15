# Wolfenstein: The New Order Extractor

import os, sys, struct, json, ctypes, zlib, subprocess
from io import BytesIO
from hashlib import md5

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

GAME_DIR = r'G:\Steam\steamapps\common\Rocksmith2014'
SIGNATURE_PSAR = b'PSAR'
COMPRESSION_METHODS = [ b'\x00\x00\x00\x00', b'zlib', b'lzma' ]
HEADER_SIZE = 32

ARC_KEY = bytes.fromhex("C53DB23870A1A2F71CAE64061FDD0E1157309DC85204D4C5BFDF25090DF2572C")
ARC_IV = bytes.fromhex("E915AA018FEF71FC508132E4BB4CEB42")
ARC_CIPHER = Cipher(algorithms.AES(ARC_KEY), modes.CFB(ARC_IV))



class BufferReader:
    def __init__ (self, data):
        self.buffer = data
        self.size = len(data)
        self.cursor = 0
        self.open()

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
        self.cursor = 0
        self.size = 0

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

    def isEOF (self):
        return not self.buffer or not self.size or (self.cursor + 1) >= self.size


def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])

def decompressData (data):
    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data

def readStruct (structFormat, descriptor):
    structSize = struct.calcsize(structFormat)
    dataBuffer = descriptor.read(structSize)

    if len(dataBuffer) != structSize:
        return None

    items = struct.unpack(structFormat, dataBuffer)

    return items[0] if len(items) == 1 else items

def readUInt40 (descriptor):
    high32, low8 = readStruct('>IB', descriptor)

    return ((high32 << 8) | low8) & 0xFFFFFFFFFF

def decryptIndex (data):
    decryptor = ARC_CIPHER.decryptor()
    return decryptor.update(data) + decryptor.finalize()

def unpack (filePath):
    # https://www.psdevwiki.com/ps3/PlayStation_archive_(PSARC)
    # https://github.com/Fuzzy-Logik/libPSARC/wiki/Documentation%5ClibPSARC%5CPSARC-File-Format
    # https://github.com/0x0L/rocksmith  https://www.rubydoc.info/gems/rsgt/0.0.1
    # See ./PSARC

    extractDir = filePath + '_extracted'
    items = []

    with open(filePath, 'rb') as f:
        signature, majorVersion, minorVersion, compressionMethod, metaSize, indexItemSize, indexItemCount, maxBlockSize, flags = readStruct('>4s2H4s5I', f)

        if signature != SIGNATURE_PSAR:
            raise Exception('Wrong .psarc file signature')

        if compressionMethod not in COMPRESSION_METHODS:
            raise Exception('Unknown compression method')

        indexSize = metaSize - HEADER_SIZE
        indexBuffer = BufferReader(decryptIndex(f.read(indexSize)))
        blockSizes = []

        for i in range(indexItemCount):
            itemNameHash = readStruct('>16s', indexBuffer).hex()
            itemIndex = readStruct('>I', indexBuffer)
            itemSize = readUInt40(indexBuffer)
            itemOffset = readUInt40(indexBuffer)

            items.append((itemNameHash, itemIndex, itemSize, itemOffset))

        while not indexBuffer.isEOF():
            blockSizes.append(readStruct('>H', indexBuffer))

        os.makedirs(extractDir, exist_ok = True)

        itemNames = None

        for i, (nameHash, index, size, offset) in enumerate(items):
            f.seek(offset)

            buffer = BytesIO()

            for blockSize in blockSizes[index:]:
                if len(buffer.getbuffer()) == size:
                    break

                data = f.read(blockSize or maxBlockSize)

                try:
                    data = zlib.decompress(data)
                except:
                    pass

                buffer.write(data)

            data = buffer.getvalue()

            assert len(data) == size

            if i == 0:
                itemNames = data.decode('utf8').splitlines()
            else:
                name = itemNames[i - 1]

                assert nameHash == md5(name.encode('utf8')).hexdigest()

                with open(os.path.join(extractDir, name), 'wb') as f2:
                    f2.write(data)

    # os.makedirs(extractDir, exist_ok = True)

    # for item in 

    # 

    # print(itemNames)

'''
def listArchiveContent (filePath):
    process = subprocess.run([ r'C:\Projects\GameTools\PSARC\psarc.exe', 'list', filePath ], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        result = (process.stdout + process.stderr).decode('utf8')
        return ('First file in archive is not a manifest file!' not in result)
    except:
        print('\n', process.stdout + process.stderr, '\n')
        return False


    print(result)


def listAll (rootDir):
    def walk (directory):
        if not os.path.isdir(directory):
            return

        for item in os.listdir(directory):
            itemPath = os.path.join(directory, item)

            if os.path.isdir(itemPath):
                walk(itemPath)
            elif os.path.isfile(itemPath):
                if item.lower().endswith('.psarc'):
                    print(os.path.relpath(itemPath, rootDir))

                    if listArchiveContent(itemPath):
                        print('Found!', itemPath)
                        break

    walk(rootDir)
'''

def getFiles (rootDir):
    files = []

    for (dirName, _, fileNames) in os.walk(rootDir):
        for fileName in fileNames:
            files.append(os.path.join(dirName, fileName))

    return files

def compareFileSets (dir1, files1, dir2, files2):
    relFiles1 = [ os.path.relpath(filePath, dir1) for filePath in files1 ]
    relFiles2 = [ os.path.relpath(filePath, dir2) for filePath in files2 ]

    diffFiles = set(relFiles1).symmetric_difference(set(relFiles2))

    if diffFiles:
        print('Different files:')

        for filePath in diffFiles:
            print('-', filePath)
    else:
        print('Same set of files')

def readBinFile (filePath):
    with open(filePath, 'rb') as f:
        return f.read()

def compare (dir1, dir2):
    dir1Files = getFiles(dir1)
    dir2Files = getFiles(dir2)

    compareFileSets(dir1, dir1Files, dir2, dir2Files)

    for file1 in dir1Files:
        file2 = os.path.join(dir2, os.path.relpath(file1, dir1))

        if readBinFile(file1) != readBinFile(file2):
            print(f'git diff "{ file1 }" "{ file2 }"')






    


if __name__ == '__main__':
    compare(
        os.path.join(GAME_DIR, '_PSARCs', 'original', 'files'),
        os.path.join(GAME_DIR, '_PSARCs', 'no_intro', 'files')
    )
    # for subDir in [ 'no_intro' ]:
    #     unpack(os.path.join(GAME_DIR, '_PSARCs', subDir, 'cache.psarc'))
    # unpack(os.path.join(GAME_DIR, 'cache.psarc'))
    # listArchiveContent(os.path.join(GAME_DIR, 'cache.psarc'))
    # listAll(GAME_DIR)