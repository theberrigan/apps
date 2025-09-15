# Wolfenstein (2009) Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Games\Wolfenstein'

SMPK_SIGNATURE = b'\x2C\x01\x00\x00'



class SectionType (Enum2):
    RTXT = b'RTXT'  # B 966   4.1GB
    LDOM = b'LDOM'  # B 510 524.1MB
    SDNS = b'SDNS'  # B 574 458.5MB
    FBBP = b'FBBP'  # B  78 446.5MB
    SXKH = b'SXKH'  # B  28 117.3MB
    AXKH = b'AXKH'  # B  31  90.5MB
    SSAA = b'SSAA'  # M  27  74.6MB
    CORP = b'CORP'  # B  54  70.6MB
    LCED = b'LCED'  # B  53  63.7MB
    ODIV = b'ODIV'  # M   4  32.0MB
    STNE = b'STNE'  # B  54  10.2MB
    IARB = b'IARB'  # M  23   3.8MB
    RXKH = b'RXKH'  # B  25   3.1MB
    XFGS = b'XFGS'  # S   6   2.2MB
    LEKS = b'LEKS'  # B  26   2.0MB



def unpack (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    createDirs(unpackDir)

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != SMPK_SIGNATURE:
            raise Exception('Wrong signature')

        count = 0

        while f.remaining():
            count += 1

            sectionName = f.read(4)

            assert SectionType.hasValue(sectionName)

            decompSize = f.u32()
            compSize   = f.u32()

            data = f.read(compSize)
            data = decompressData(data)

            dstExt  = sectionName.decode('ascii').lower()
            dstName = f'{count:04}.{ dstExt }'
            dstPath = joinPath(unpackDir, dstName)

            print(dstPath)

            writeBin(dstPath, data)

    # exit()

def unpackAll (gameDir, unpackDir=None):
    for filePath in iterFiles(gameDir, True, [ '.mpk', '.spk' ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')



def main ():
    # unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    # unpackAll(joinPath(GAME_DIR, 'base', 'maps', 'game', 'menu'))
    unpack(joinPath(GAME_DIR, 'base', 'streampacks', 'music_cannery_intro.spk'))
    # unpack(joinPath(GAME_DIR, 'base', 'maps', 'game', 'menu', 'menu.mpk'))
    # unpack(joinPath(GAME_DIR, 'base', 'maps', 'game', 'menu', 'menu@tpn.spk'))
    # unpack(joinPath(GAME_DIR, 'base', 'maps', 'game', 'menu', 'menu_vo_russian.spk'))


if __name__ == '__main__':
    main()
