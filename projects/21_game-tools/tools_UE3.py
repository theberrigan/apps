# Unreal Engine 3 Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



DISHONORED_GAME_DIR      = r'G:\Steam\steamapps\common\Dishonored'
BULLETSTORM_GAME_DIR     = r'G:\Steam\steamapps\common\Bulletstorm Full Clip Edition'
LIFE_IS_STRANGE_GAME_DIR = r'G:\Steam\steamapps\common\Life Is Strange'



# G:\Steam\steamapps\common\Dishonored
# C1 83 2A 9E 21 03 1E 00 G:\Steam\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole\Abbey_01_Keys_SF.upk
# G:\Steam\steamapps\common\Bulletstorm Full Clip Edition
# C1 83 2A 9E 77 03 29 00 G:\Steam\steamapps\common\Bulletstorm Full Clip Edition\StormGame\CookedPCConsole\BaseAI.upk
# 4D 4D 4D 59 2B 39 34 3D G:\Steam\steamapps\common\Bulletstorm Full Clip Edition\StormGame\CookedPCConsole\BossArena_Fail.upk
# 4D 4D 4D 6D 2B 39 34 3D G:\Steam\steamapps\common\Bulletstorm Full Clip Edition\StormGame\CookedPCConsole\LoadingMovie00.upk
# G:\Steam\steamapps\common\Life Is Strange
# C1 83 2A 9E 7D 03 15 00 G:\Steam\steamapps\common\Life Is Strange\LifeIsStrangeGame\Build\PCConsole\DLC\Episode02\LifeIsStrangeGame\DLC\PCConsole\Episode02\CookedPCConsole\E2_1A.upk

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
        DISHONORED_GAME_DIR,
        BULLETSTORM_GAME_DIR,
        LIFE_IS_STRANGE_GAME_DIR,
    ]:
        print(gameDir)

        for filePath in iterFiles(gameDir, True, [ '.upk' ]):
            # print(filePath)

            unpackPak(filePath)

            # print(' ')


def main ():
    unpackAll()



if __name__ == '__main__':
    main()
