# Deus Ex Mankind Divided Tools

import sys
import regex

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.native.limits import *



GAME_DIR = r'G:\Steam\steamapps\common\Deus Ex Mankind Divided'

HLIB_SIGNATURE = b'BILH'



def unpackHeaderLib (filePath, unpackDir):    
    filePath = getAbsPath(filePath)

    # print('Unpacking', filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    with openFile(filePath) as f:
        sinature = f.read(4)

        if sinature != HLIB_SIGNATURE:
            raise Exception('Unknown file signature')

        pathSize = f.u32()

        unk1 = f.u32()

        assert unk1 == 0

        contentSize = f.u32()

        unk2 = f.u64()

        assert unk2 == MAX_U64, unk2

        assert f.remaining() == (pathSize + contentSize)

        if pathSize:
            itemCount = f.u32()
            # unk4 = f.u32()  # 0
            # unk5 = f.u32()  # 16
            # unk6 = f.u32()  # 20

            assert itemCount in [ 1, 2 ], itemCount
            # assert unk4 == 0, unk4
            # assert unk5 in [ 16, 0 ], unk5
            # assert unk6 == 20, unk6

            if itemCount == 1:
                b = f.read(16)
                s1 = f.string()
                print(s1)
            elif itemCount == 2:
                b = f.read(24)
                s1 = f.string()
                s2 = f.string()
                print(s1)
                print(s2)


            # 00 00 00 00 | 10 00 00 00 | 14 00 00 00 | 00 00 00 80
            # 00 00 00 00 | 10 00 00 00 | 14 00 00 00 | 00 00 00 01
            # 00 00 00 00 | 00 00 00 00 | 14 00 00 00 | 1C 00 00 00 00 00 00 01 57 00 00 80
            # 00 00 00 00 | 00 00 00 00 | 14 00 00 00 | 1C 00 00 00 00 00 00 01 55 00 00 80
            # 00 00 00 00 | 00 00 00 00 | 14 00 00 00 | 1C 00 00 00 00 00 00 01 6F 00 00 80
            # 00 00 00 00 | 00 00 00 00 | 14 00 00 00 | 1C 00 00 00 00 00 00 01 58 00 00 80
            # 00 00 00 00 | 00 00 00 00 | 14 00 00 00 | 1C 00 00 00 00 00 00 01 54 00 00 80

            # Game.layer.0.all.archive
            # 267961 - BIN1
            # 7682 - BILR
            # D:\DXNG\Assembly\Sound\localization\dialogue\english\conversations\_common\news04_010_amb\common_news04_010_amb_003_eliza.wav
        
    print(' ')
    # exit()


def unpackAll (rootDir, unpackDir):
    # '.archive'
    # '.pc_binkvid'
    # '.pc_fsb'
    # '.pc_fsbm'
    # '.pc_headerlib' 1_291_964_695

    for filePath in iterFiles(rootDir, True):
        ext = getExt(filePath)

        match ext:
            case '.pc_headerlib':
                unpackHeaderLib(filePath, unpackDir)



if __name__ == '__main__':
    unpackAll(GAME_DIR, joinPath(GAME_DIR, '.unpacked'))
    # unpack(joinPath(GAME_DIR, 'Global.bix'), joinPath(GAME_DIR, '.unpacked'))