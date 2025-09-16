# HROT Extractor

from deps.utils import *
from deps.reader import *



SCRIPT_DIR = getDirPath(getAbsPath(__file__))
GAME_DIR = r'G:\Steam\steamapps\common\HROT'

SIGNATURE = b'HROT'
NO_EXT = '!unknown'



def unpack (filePath, unpackDir):
    print('Unpacking', filePath)

    manifest = []

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != SIGNATURE:
            print('Unknown signature')

        tocOffset, tocSize = f.u32(2)

        assert tocSize % 128 == 0

        itemCount = int(tocSize / 128)
        items = []

        f.seek(tocOffset)

        for i in range(itemCount):
            name = f.string(size=120)
            itemOffset, itemSize = f.u32(2)

            ext = getExt(name, True) or NO_EXT
            rawPath = joinPath(ext, name)

            items.append((name, itemOffset, itemSize, rawPath))

        items.sort(key=lambda item: item[1])

        for name, itemOffset, itemSize, rawPath in items:
            print(name)

            f.seek(itemOffset)

            data = f.read(itemSize)

            outPath = joinPath(unpackDir, rawPath)

            createDirs(getDirPath(outPath))

            with open(outPath, 'wb') as f2:
                f2.write(data)

            manifest.append({
                'name': name,
                'raw_path': rawPath
            })

        writeJson(joinPath(unpackDir, 'manifest.json'), manifest)


if __name__ == '__main__':
    unpack(joinPath(GAME_DIR, 'HROT.pak'), joinPath(GAME_DIR, '_unpacked'))