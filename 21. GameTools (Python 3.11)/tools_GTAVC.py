# GTA Vice City Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR  = r'G:\Steam\steamapps\common\Grand Theft Auto Vice City'
AUDIO_DIR = joinPath(GAME_DIR, 'audio')



def decryptADF (filePath):
    dstPath = replaceExt(filePath, '.mp3')

    data = bytearray(readBin(filePath))

    for i in range(len(data)):
        data[i] ^= 0x22 

    writeBin(dstPath, data)


def decryptADFs (rootDir):
    for filePath in iterFiles(rootDir, True, [ '.adf' ]):
        print(filePath)
        decryptADF(filePath)
        print(' ')



def main ():
    decryptADFs(AUDIO_DIR)



if __name__ == '__main__':
    main()
