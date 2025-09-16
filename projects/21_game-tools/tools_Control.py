# Control Tools

from sys import exit

from deps.utils import *
from deps.reader import *
from deps.xml import XMLNode



GAME_DIR = r'G:\Steam\steamapps\common\Control'
PAKS_DIR = joinPath(GAME_DIR, 'data_packfiles')



def unpackPackFile (filePath):
    print(filePath)

    with openFile(filePath) as f:
        itemCount  = f.u32()
        unk1       = f.u32()
        itemCount2 = f.u32()
        pathsSize  = f.u32()

        assert itemCount == itemCount2
        assert unk1 == 1

        paths = [ f.string() for _ in range(itemCount) ]

        assert f.tell() == (4 * 4 + pathsSize)

        pathEndOffsets = f.u32(itemCount)

        itemCount3 = f.u32()

        assert itemCount == itemCount3

        # Current offset: 961389
        # ~1868-1888

        # unks1 = f.u64(itemCount3)

        for _ in range(itemCount3):
            unk3 = f.u32()
            unk4 = f.u32()
            print(unk3, unk4)

        # Current offset: 1042621

        stringOffsets = f.u32(itemCount3)  # 0, 48, 157...

        # Current offset: 1083237

        paramCount = f.u32()

        for _ in range(paramCount):
            unk5 = f.u32()
            nameSize = f.u32()
            name = f.string(size=nameSize)
            value = f.u32()

            print(name, value)

        # Current offset: 1084486
        # print(f.tell())


def unpackPackFiles (rootDir):
    for filePath in iterFiles(rootDir, True, [ '.packmeta' ]):
        unpackPackFile(filePath)
        print(' ')


if __name__ == '__main__':
    # unpackPackFiles(GAME_DIR)
    unpackPackFile(joinPath(PAKS_DIR, 'ep100-000-generic.packmeta'))