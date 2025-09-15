# Deus Ex GOTY Tools

import sys
import shutil
import subprocess

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR = r'G:\Steam\steamapps\common\Deus Ex'

PAK_SIGNATURE = b'\xC1\x83\x2A\x9E'
PAK_VERSIONS  = [ 61, 68 ]


def unpack (filePath):
    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != PAK_SIGNATURE:
            raise Exception('Unknown signature')

        version      = f.u32()
        flags        = f.u32()
        nameCount    = f.u32()
        nameOffset   = f.u32()
        exportCount  = f.u32()
        exportOffset = f.u32()
        importCount  = f.u32()
        importOffset = f.u32()

        # for other versions see Core\Src\UnLinker.h:183
        if version not in PAK_VERSIONS:
            raise Exception(f'Unsupported version { version }')

        if version >= 68:
            guid     = f.read(16)  # 4x u32; see Core\Inc\UnObjBas.h:176
            genCount = f.u32()
            gens     = []

            for i in range(genCount):
                exportCount = f.u32()
                nameCount   = f.u32()

                gens.append((exportCount, nameCount))
        else:
            guid = None

            heritageCount  = f.u32()
            heritageOffset = f.u32()

            start = f.tell()

            if heritageCount:
                f.seek(heritageOffset)

                print(heritageOffset)

                for i in range(heritageCount):
                    guid = f.read(16)

            f.seek(start)

            genCount = 1
            gens     = [ (nameCount, exportCount) ]

        if nameCount:
            f.seek(nameOffset)

            for i in range(nameCount):
                if version >= 68:
                    size = f.u8()
                    name = f.string(size)
                else:
                    name = f.string()

                flags = f.u32()

                # TODO: NameMap.AddItem( (NameEntry.Flags & _ContextFlags) ? FName( NameEntry.Name, FNAME_Add ) : NAME_None );

                print(name, flags)



# 61 (1), 68 (all)
def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True):
        signature = readBin(filePath, 4)

        if signature == PAK_SIGNATURE:
            print(filePath)
            unpack(filePath)
            print(' ')


def main ():
    unpackAll()



if __name__ == '__main__':
    main()
