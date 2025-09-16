# Glacier and Dawn Engine Tools
# Developer: IO Interactive, Eidos Montreal
# https://en.wikipedia.org/wiki/IO_Interactive#Glacier
# https://www.pcgamingwiki.com/wiki/Engine:Dawn_Engine

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



# GAME                             | YEAR | ENGINE      | NOTES
# ---------------------------------|------|-------------|---------------
# Hitman: Codename 47              | 2000 | Glacier     | zip, bin, pal, dls, ...
# Hitman 2: Silent Assassin        | 2002 | Glacier     | zip, ...
# Freedom Fighters                 | 2003 | Glacier     | zip, ...
# Hitman: Contracts                | 2004 | Glacier     | zip, ...
# Hitman: Blood Money              | 2006 | Glacier     | zip, str, ...
# Kane & Lynch: Dead Men           | 2007 | Glacier     | zip, str, ...
# Mini Ninjas                      | 2009 | Glacier     | zip, str, ...
# Kane & Lynch 2: Dog Days         | 2010 | Glacier     | zip, str, ...
# Hitman: Absolution               | 2012 | Glacier 2.0 | pc_*
# Hitman: Sniper Challenge         | 2012 | Glacier 2.0 | pc_*
# Hitman                           | 2016 | Glacier 2.0 | rpkg
# Hitman 2                         | 2018 | Glacier 2.0 | rpkg
# Hitman 3                         | 2021 | Glacier 2.0 | rpkg
# Deus Ex: Mankind Divided         | 2016 | Dawn        | pc_*
# Deus Ex: Breach                  | 2017 | Dawn        | pc_*
# Deus Ex: Mankind Divided (VR)    | 2017 | Dawn        | pc_*
# Marvel's Guardians of the Galaxy | 2021 | Dawn        | pc_*



HA_GAME_DIR   = r'G:\Steam\steamapps\common\Hitman Absolution'
DXMD_GAME_DIR = r'G:\Steam\steamapps\common\Deus Ex Mankind Divided'

GAME_DIRS = [
    HA_GAME_DIR,
    DXMD_GAME_DIR,
]

HLIB_EXT = '.pc_headerlib'
RLIB_EXT = '.pc_resourcelib'

HLIB_SIGNATURE = b'BILH'
RLIB_SIGNATURE = b'BILR'
ARCH_SIGNATURE = b'ARCH'


# Hitman Absolution:
# - pc_binkvid
# - pc_headerlib
# - pc_packagelist
# - pc_resourcelib

# Deus Ex Mankind Divided:
# - archive
# - pc_binkvid
# - pc_fsb
# - pc_fsbm
# - pc_headerlib


def readHeaderLib (libPath, unpackDir):
    libPath = getAbsPath(libPath)

    if not isFile(libPath):
        raise Exception(f'Header lib file is not found: { libPath }')

    with openFile(libPath) as f:
        signature = f.read(4)

        if signature != HLIB_SIGNATURE:
            raise Exception(f'Wrong signature: { signature }')

        tocSize = f.u32()
        unk2 = f.u32()

        assert unk2 == 0

        contentSize = f.u32()

        unk3  = f.u64()  # ptr?

        assert unk3 == 0xFFFFFFFFFFFFFFFF

        itemCount = f.u32()

        unk4 = f.u32()
        unk5 = f.u32()

        print(unk4, unk5)

        items = [ None ] * itemCount

        for i in range(itemCount):
            unk5 = f.u16()
            unk6 = f.u16()

            items[i] = [ None, unk5, unk6 ]

        for i in range(itemCount):
            path = f.string()

            items[i][0] = path

            print(*items[i])


def readResourceLib (libPath, unpackDir):
    libPath = getAbsPath(libPath)

    if not isFile(libPath):
        raise Exception(f'Resource lib file is not found: { libPath }')

    with openFile(libPath) as f:
        signature = f.read(4)

        if signature != RLIB_SIGNATURE:
            raise Exception(f'Wrong signature: { signature }')


def unpack (filePath, unpackDir):
    ext = getExt(filePath).lower()

    if ext == HLIB_EXT:
        readHeaderLib(filePath, unpackDir)
    elif ext == RLIB_EXT:
        readResourceLib(filePath, unpackDir)

def unpackAll (gameDir, unpackDir):
    if not isDir(gameDir):
        print(f'Game directory does not exist: { gameDir }')

    for filePath in iterFiles(gameDir, True, [ HLIB_EXT ]):  # , RLIB_EXT
        print(filePath)

        try:
            unpack(filePath, unpackDir)
        except Exception as e:
            print('ERROR:', e)

        print(' ')

def main ():
    # for gameDir in GAME_DIRS:
    # for gameDir in [ HA_GAME_DIR ]:
    #     unpackAll(gameDir, joinPath(gameDir, '.unpacked'))

    readHeaderLib(r"G:\Steam\steamapps\common\Hitman Absolution\runtime\templates\weapontemplates\weaponsandammo.template\95C9EB306FA69ACE22C9CCDE5B84D10C.pc_headerlib", joinPath(HA_GAME_DIR, '.unpacked'))


if __name__ == '__main__':
    main()
