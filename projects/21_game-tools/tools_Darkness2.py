# Darkness II Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\Darkness II'



def unpack (pkgPath, unpackDir):    
    pkgPath = getAbsPath(pkgPath)

    if not isFile(pkgPath):
        raise Exception(f'Cache file is not found: { pkgPath }')

    tocPath = replaceExt(pkgPath, '.toc')

    if not isFile(tocPath):
        raise Exception(f'TOC file is not found: { pkgPath }')

    with openFile(tocPath) as f:
        signature = f.read(4)

        assert signature == b'\x4E\xC6\x67\x18'

        unk1 = f.u32()

        assert unk1 == 16

        while f.remaining():
            unks1 = f.u32(8)

            offset = unks1[0]  # offset in .cache file
            sizeS  = unks1[4]  # size in .cache file
            sizeB  = unks1[5]  # sizeB >= sizeS
            index  = unks1[7]

            name = f.string(size=64)

            print(unks1, name)

            assert unks1[1] in [ 0xFFFFFFFF, 0 ]
            # assert unks1[6] in [ 0xFFFFFFFF, 0, 3, 12, 7, 8080, 2, 28, 15, 10, 330005 ], unks1[6]


    # exit()

def unpackAll (gameDir, unpackDir):
    for filePath in iterFiles(gameDir, True, [ '.cache' ]):
        print(filePath)

        unpack(filePath, unpackDir)

        print(' ')

def main ():
    # unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    # unpack(joinPath(GAME_DIR, 'Cache.Windows', 'H.Misc.cache'), joinPath(GAME_DIR, '.unpacked'))

    data = readBin(r"G:\Steam\steamapps\common\Darkness II\Cache.Windows\H.VideoTexture_en.cache", 111)

    for i in range(110):
        try:
            data = decompressData(data)
            print('Ok')
        except:
            data = data[1:]


if __name__ == '__main__':
    main()
