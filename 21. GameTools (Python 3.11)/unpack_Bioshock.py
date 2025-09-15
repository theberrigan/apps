# Bioshock Extractor

from datetime import datetime

from deps.utils import *
from deps.reader import *



SCRIPT_DIR = getDirPath(getAbsPath(__file__))
GAME_DIR = r'G:\Steam\steamapps\common\Bioshock'



# ItemMeta = createNamedTuple('ItemMeta', (
#     'path',
#     'decompSize',
#     'compSize',
#     'offset',
#     'unk4',
#     'unk5',
#     'unk6',
# ))


def unpack (filePath, outputDir):
    print('Unpacking', filePath)

    outputDir = dropExt(filePath)

    with openFile(filePath) as f:
        unk1 = f.read(12) 

        if unk1 != b'\xC1\x83\x2A\x9E\x8D\x00\x38\x00\x01\x00\x27\x00':
            return

        createDirs(outputDir)

        f.seek(64)

        itemCount = f.u32()

        offsets = f.struct(f'<{ itemCount }I')

        for i, offset in enumerate(offsets):
            f.seek(offset)

            compSize = f.u32()

            if compSize <= 0:
                continue

            data = f.read(compSize)
            data = decompressData(data)

            outputPath = joinPath(outputDir, f'{(i + 1):09d}.bin')

            with open(outputPath, 'wb') as f2:
                f2.write(data)

            print(len(data))




def unpackAll (rootDir, outputDir):
    for filePath in iterFiles(rootDir, True, [ '.u' ]):
        unpack(filePath, outputDir)


def unpackShaders (filePath):
    outputDir = filePath + '_unpacked'

    createDirs(outputDir)

    with openFile(filePath) as f:
        unk1 = f.u32()
        shaderCount = f.u32()

        for i in range(shaderCount):
            always1, ts, nameLen = f.struct('<3I')

            assert always1 == 1

            date = datetime.fromtimestamp(ts)

            shaderName = f.string(nameLen * 2, 'utf-16')

            contentSize = f.u32()

            content = f.read(contentSize)
            content = content.decode('utf-8')

            shaderPath = joinPath(outputDir, shaderName)

            print(date, shaderName)

            with open(shaderPath, 'w', encoding='utf-8') as f2:
                f2.write(content)


def unpackBulks (bulksDir):
    catalogPath = joinPath(bulksDir, 'Catalog.bdc')

    with openFile(filePath) as f:
        pass


if __name__ == '__main__':
    # unpack(joinPath(GAME_DIR, 'pc_arch_scripts.bin'), joinPath(GAME_DIR, 'pc_arch_scripts'))
    # unpackAll(GAME_DIR, None)  # joinPath(GAME_DIR, 'extracted')
    # unpackShaders(joinPath(GAME_DIR, 'Builds', 'Release', 'shaders.spk'))
    unpackBulks(joinPath(GAME_DIR, 'Content', 'BulkContent'))

