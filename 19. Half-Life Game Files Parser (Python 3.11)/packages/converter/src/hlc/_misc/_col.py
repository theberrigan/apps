import os
import re
import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *

GAME_ROOT = r'C:\Projects\_Sources\GameEngines\Goldsrc\Xash3D_3\game\valve'
SPRITES_DIR = joinPath(GAME_ROOT, 'sprites')


def scan ():
    paths = [ getRelPath(p, GAME_ROOT).replace('\\', '/') for p in iterFiles(GAME_ROOT, True) ]

    ml = 0

    for p in paths:
        ml = max(ml, len(p))

    for p in paths:
        print(f'{p:{ml}} |')

def colFSSprites ():
    sprites = {}

    for p in iterFiles(SPRITES_DIR, True, [ '.txt' ]):
        print(p)

        manName = getFileName(p)

        lines = readText(p, 'cp1252').split('\n')

        isFirstLine = True

        for line in lines:
            line = line.split('//', 1)[0].strip()

            if not line:
                continue

            if isFirstLine:
                isFirstLine = False
                assert line.isnumeric(), line
                continue

            line = re.split(r'\s+', line)

            name   = line[0]
            res    = int(line[1], 10)
            sprite = line[2]
            x      = int(line[3], 10)
            y      = int(line[4], 10)
            w      = int(line[5], 10)
            h      = int(line[6], 10)

            assert isFile(joinPath(SPRITES_DIR, f'{ sprite }.spr'))

            info = (name, res, sprite, x, y, w, h)

            sprites[sprite] = True

    for p in iterFiles(SPRITES_DIR, True, [ '.spr' ]):
        sName = getFileName(p)

        if sName not in sprites:
            print(sName)








if __name__ == '__main__':
    colFSSprites()