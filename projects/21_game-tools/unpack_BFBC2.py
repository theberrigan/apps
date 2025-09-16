# Battlefield Bad Company 2 Extractor

import os, struct, gzip

GAME_DIR = r'G:\Steam\steamapps\common\Battlefield Bad Company 2'

FBRB_SIGNATURE = b'FbRB'


class VirtualReader:
    def __init__ (self, data):
        self.buffer = data
        self.size = len(data)
        self.cursor = 0

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
    return gzip.decompress(data)


def unpack (filePath):
    print(filePath)

    assert os.path.isfile(filePath), f'File does not exist: { filePath }'

    with open(filePath, 'rb') as f:
        signature, indexSize = readStruct('>4sI', f)

        if signature != FBRB_SIGNATURE:
            raise Exception('Unsupported file')

        data = f.read(indexSize)
        data = decompressData(data)

        uncFilePath = filePath + '_uncompressed'

        if not os.path.isfile(uncFilePath):
            with open(uncFilePath, 'wb') as f2:
                f2.write(data)

        with VirtualReader(data) as f2:
            unk1, namesSize = readStruct('>II', f2)

            namesEnd = f2.tell() + namesSize

            names = []

            while f2.tell() < namesEnd:
                names.append(readNullString(f2))
                print(names[-1])

            count = readStruct('>I5x', f2)

            for i in range(count):
                print(readStruct('>6I', f2))

            # print(f2.tell())


        # print(len(names))  # 4745

        # for i, name in enumerate(names):
        #     print(i, name)




def unpackAll (rootDir):
    for dirName, _, fileNames in os.walk(rootDir):
        for fileName in fileNames:
            filePath = os.path.join(dirName, fileName)

            if filePath.lower().endswith('.fbrb'):
                unpack(filePath)


if __name__ == '__main__':
    # unpackAll(GAME_DIR)
    unpack(os.path.join(GAME_DIR, 'dist', 'win32', 'async', 'startup-00.fbrb'))
    # unpack(os.path.join(GAME_DIR, 'dist', 'win32', 'build_overlay-00.fbrb'))
