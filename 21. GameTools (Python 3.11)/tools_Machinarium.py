# Machinarium Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR = r'G:\Steam\steamapps\common\Machinarium'
ARCH_DIR = joinPath(GAME_DIR, 'arch_win')

ARCH_KEY = bytes.fromhex('379C7BA3F13D5593039771136D9EFC7155CC1163BE56EE55C3D5B9F7779CA0E9')

ARCH_META_SIZE = 49152

ARCH_MAIN_NAME = '7005'



class ItemMeta:
    def __init__ (self):
        self.name   = None
        self.size   = None
        self.offset = None


def isASCIIString (data):
    for byte in data:
        if (byte < 32 or byte >= 127) and byte not in [ 9, 10, 13 ]: 
            return False

    return True


def isUTF16BOMString (data):
    try:
        data.decode('utf-16le')
        return True
    except:
        return False


def decompressCWS (data):
    with MemReader(data) as f:
        signature = f.read(4)

        assert signature == b'CWS\x07'

        decompSize = f.u32()  # +8 bytes

        data = f.read()
        data = decompressData(data)

        return data


def unpackArchByDescriptor (f, unpackDir):
    items = []

    for _ in range(4096):
        item = ItemMeta()

        item.name   = f.u32()
        item.offset = f.u32()
        item.size   = f.u32()

        if item.name != 0:
            items.append(item)

    items.sort(key=lambda item: item.offset)

    createDirs(unpackDir)

    for item in items:
        f.seek(item.offset)
        
        data = f.read(item.size)

        if data[:4] == b'OggS':
            ext = '.ogg'
        elif data[:3] == b'FWS':
            ext = '.swf'
        elif data[:3] == b'CWS':
            ext = '.swc'
            data = decompressCWS(data)
        elif isASCIIString(data) or isUTF16BOMString(data):
            ext = '.txt'            
        else:
            ext = '.bin'

        itemPath = joinPath(unpackDir, f'{item.name:08X}{ext}')

        writeBin(itemPath, data)


def unpackArch (filePath, unpackDir=None):
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    if getFileName(filePath) == ARCH_MAIN_NAME:
        with openFile(filePath) as f:
            unpackArchByDescriptor(f, unpackDir)
    else:
        data = bytearray(readBin(filePath))

        for i in range(len(data)):
            data[i] ^= ARCH_KEY[i % 32]

        with MemReader(data) as f:
            unpackArchByDescriptor(f, unpackDir)


def unpackAll ():
    for filePath in iterFiles(ARCH_DIR, True, [ '.jpg' ]):
        print(filePath)

        unpackArch(filePath)

        print(' ')


def main ():
    unpackAll()




if __name__ == '__main__':
    main()
