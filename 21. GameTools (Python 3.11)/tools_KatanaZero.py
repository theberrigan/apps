# Katana Zero Tools

from sys import stdout

from deps.utils import *
from deps.reader import *



GAME_DIR = r'G:\Steam\steamapps\common\Katana ZERO'


def readAUDO (f, outDir):
    createDirs(outDir)

    count = f.u32()
    offsets = f.u32(count)

    for offset in offsets:
        f.seek(offset)

        size = f.u32()
        data = f.read(size)

        outPath = joinPath(outDir, f'{ offset }.wav')

        writeBin(outPath, data)

# TODO: smth wrong with sizes
# TODO: some unread data on the end of the section
# TODO: _unk1? (0 or 1)
def readTXTR (f, outDir, contentEnd):
    createDirs(outDir)

    count = f.u32()
    entryOffsets = f.u32(count)

    items = []

    for entryOffset in entryOffsets:
        f.seek(entryOffset)

        _unk1, _zeros, dataOffset = f.u32(3)

        items.append((_unk1, dataOffset))

    for i, (_unk1, dataOffset) in enumerate(items):
        if i == (count - 1):
            dataSize = contentEnd - dataOffset
        else:
            dataSize = items[i + 1][1] - dataOffset

        f.seek(dataOffset)

        data = f.read(dataSize)

        outPath = joinPath(outDir, f'{ dataOffset }_{ _unk1 }.png')

        writeBin(outPath, data)

def readSTRG (f):
    count = f.u32()
    offsets = f.u32(count)

    strings = []

    for offset in offsets:
        f.seek(offset)

        size = f.u32()
        string = f.string(size)

        strings.append(string)

    for s in strings:
        if s.strip().startswith('#version'):
            print('-' * 100)
            print('\n'.join([ s.rstrip() for s in s.split('\n') ]))

def readSCPT (f):
    count = f.u32()
    entryOffsets = f.u32(count)

    for entryOffset in entryOffsets:
        f.seek(entryOffset)

        strOffset = f.u32()  # offset to NT-string (see readSTRG)
        strIndex  = f.u32()  # 0-N

def unpack (filePath):
    print('Unpacking', filePath)

    outRootDir = filePath + '_unpacked'

    with openFile(filePath) as f:
        form = f.read(4)
        
        assert form == b'FORM'

        formSize = f.u32()
        formEnd  = f.tell() + formSize

        assert formEnd == f.getSize()

        while f.tell() < f.getSize():
            sectionName = f.read(4).decode('utf-8')
            contentSize = f.u32()
            contentEnd  = f.tell() + contentSize

            print(sectionName)

            outDir = joinPath(outRootDir, sectionName)

            match sectionName:
                # case 'AUDO':
                #     readAUDO(f, outDir)
                # case 'TXTR':
                #     readTXTR(f, outDir, contentEnd)
                case 'STRG':
                    readSTRG(f)
                case 'SCPT':
                    readSCPT(f)
                case _:
                    f.skip(contentSize)

            f.seek(contentEnd)

def unpackAll (rootDir):
    for filePath in iterFiles(rootDir, True, [ '.dat', '.win' ]):
        unpack(filePath)



if __name__ == '__main__':
    # unpackAll(GAME_DIR)
    unpack(joinPath(GAME_DIR, 'data.win'))

# GEN8 - ?
# OPTN - small section
# LANG -- almost empty
# EXTN -- empty
# SOND - ?
# AGRP - audio groups, contains ptrs to strings
# SPRT - raw sprites
# BGND - ?
# - PATH -- empty
# + SCPT
# GLOB - just 3 u32
# SHDR - compiled DX shaders
# FONT - ?
# - TMLN -- empty
# OBJT - ?
# ROOM - ?
# - DAFL -- empty
# - EMBI -- empty
# TPAG - ?
# TGIN - ?
# + STRG
# + TXTR
# + AUDO