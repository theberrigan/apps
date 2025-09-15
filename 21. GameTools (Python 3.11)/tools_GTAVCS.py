# GTA Vice City Stories Tools

import os
import sys
import struct

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.writer import BinWriter
from bfw.xml import *
from bfw.types.enums import Enum2
from bfw.native.base import CU32
from bfw.native.limits import MAX_U32


# Emotion Engine (EE) is based on MIPS R5900 (render and DSP)
# Graphics Synthesizer (GS) rasterization co-processor
# SPU2 - DSP co-processor
# I/O Processor (IOP) (MIPS R3000-based)
# https://www.copetti.org/writings/consoles/playstation-2/
# 0xBFC00000

# R5900:
# - MIPS III ISA:
#     - 64-bit ISA (Nintendo 64) (basic opcodes)
#     - Additional opcodes
#     - Some MIPS IV opcodes (prefetch and conditional move)
#     - SIMD extension ("multimedia instructions") (similar to the SH-4, but integer only) (all instr-s are 32-bit)
#     - 32 128-bit general-purpose registers (but MIPS words are still 64-bit long)
#     - 2 64-bit ALUs
#     - COP1 (dedicated floating point unit)
#     - Vector Processing Units (VPU)

# Vertex transformations done in VPU (in EE)
# Generating pixels, mapping textures, applying lighting done in GS



GAME_DIR = r'D:\.dev\GTA_VCS'
EXE_PATH = joinPath(GAME_DIR, 'slus_215.90')


class ELF:
    def __init__ (self):
        pass

    @classmethod
    def fromFile (cls, filePath):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        with openFile(filePath, readerType=ReaderType.FS) as f:
            return cls._read(f)

    @classmethod
    def fromBuffer (cls, data, filePath=None):
        with MemReader(data, filePath=filePath) as f:
            return cls._read(f)

    @classmethod
    def _read (cls, f):
        elf = cls()



        return elf




def renameToLowerCase ():
    for rootDir, dirNames, fileNames in os.walk(GAME_DIR):
        for item in dirNames + fileNames:
            srcPath = joinPath(rootDir, item)
            dstPath = joinPath(rootDir, item.lower())

            print(srcPath, dstPath)

            rename(srcPath, dstPath)

def decompressFiles ():
    for filePath in iterFiles(GAME_DIR, True):
        if readBin(filePath, 2)[:2] != b'\x78\xDA':
            continue

        data = readBin(filePath)
        data = decompressData(data)

        writeBin(filePath + '.dec', data)

        print(filePath)



def main ():
    elf = ELF.fromFile(EXE_PATH)    
        


if __name__ == '__main__':
    main()
    