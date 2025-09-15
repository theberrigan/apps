# Unity Engine Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum



GOLDEN_LIGHT_DIR = r'G:\Steam\steamapps\common\Golden Light'



def unpackPak (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    with openFile(filePath) as f:
        signature = f.read(8)

        if signature not in _signatures:
            print(formatHex(signature), filePath)
            _signatures.add(signature)


def unpackAll ():
    for gameDir in [
        GOLDEN_LIGHT_DIR
    ]:
        print(gameDir)

        for filePath in iterFiles(gameDir, True, [ '.upk' ]):
            # print(filePath)

            unpackPak(filePath)

            # print(' ')


def main ():
    # unpackAll()

    GOLDEN_LIGHT_DIR



if __name__ == '__main__':
    main()
