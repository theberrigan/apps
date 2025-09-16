# Medal of Honor Classic Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.media.image.raw import RawImage
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Games\Medal of Honor Classic'




def main ():
    for imgName in [
        'compassback_2.png',
        'compassface_2.png',
        'compassglass_2.png',
        'compassobjarrow_2.png',
        'compassneedle_2.png',
        'compasspain_2.png',
        'compasspain_3.png',
        'healthback_4.png',
        'healthmeter_4.png',
    ]:
        pngPath = joinPath(GAME_DIR, 'main', '_', '_', imgName)
        tgaPath = replaceExt(pngPath, '.tga')

        image = RawImage.fromFile(pngPath)

        print(f'{ image.width }x{ image.height }:{ image.channels * 8 }, { image.colorCount } colors')

        image.save(tgaPath)
    


if __name__ == '__main__':
    main()
