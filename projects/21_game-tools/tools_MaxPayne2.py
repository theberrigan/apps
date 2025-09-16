# Max Payne 2 Tools

import sys

from sys import exit
from ctypes import c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint, c_longlong, c_ulonglong

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR = r'C:\Steam\steamapps\common\Max Payne 2 Ru'

SIGNATURE_RAS = b'RAS\x00'

INT_C_TYPES = {
    1: [ c_byte,     c_ubyte     ],
    2: [ c_short,    c_ushort    ],
    4: [ c_int,      c_uint      ],
    8: [ c_longlong, c_ulonglong ]
}

INT_MASKS = {
    1: 2 ** 8 - 1,
    2: 2 ** 16 - 1,
    4: 2 ** 32 - 1,
    8: 2 ** 64 - 1
}



def toSigned (num, size):
    return INT_C_TYPES[size][0](num).value

def toUnsigned (num, size):
    return INT_C_TYPES[size][1](num).value

def toI8 (num):
    return toSigned(num, 1)

def toU8 (num):
    return toUnsigned(num, 1)

def toI16 (num):
    return toSigned(num, 2)

def toU16 (num):
    return toUnsigned(num, 2)

def toI32 (num):
    return toSigned(num, 4)

def toU32 (num):
    return toUnsigned(num, 4)

def toI64 (num):
    return toSigned(num, 8)

def toU64 (num):
    return toUnsigned(num, 8)

def mask8 (num):
    return num & (2 ** 8 - 1)

def mask16 (num):
    return num & (2 ** 16 - 1)

def mask32 (num):
    return num & (2 ** 32 - 1)

def imul16 (a8, b8):
    return toU16(toI8(a8) * toI8(b8))

def imul32 (eax, reg32):
    result = toU64(toI32(eax) * toI32(reg32))

    edx = mask32(result >> 32)
    eax = mask32(result)

    return edx, eax

def add8 (a8, b8):
    return mask8(a8 + b8)

def add16 (a16, b16):
    return mask16(a16 + b16)

def add32 (a32, b32):
    return mask32(a32 + b32)

def sub32 (a32, b32):
    return mask32(a32 - b32)

# Cyclic shift to left
def rol (num, shift, size):
    size *= 8
    mask = 2 ** size - 1
    shift %= size
    l = num << shift
    r = num >> (size - shift)

    return (l | r) & mask

def rol32 (num, shift):
    return rol(num, shift, 1)

# Signed divide
def sar (num, shift, size):
    num = toSigned(num, size)

    return toUnsigned(num // (2 ** shift), size)

def sar32 (num, shift):
    return sar(num, shift, 4)

KEY_1 = 0xB92143FB
KEY_2 = -1189002245

# function_4016b0
def decryptBuffer (data, size, key):
    data = bytearray(data)
    key  = key or 1

    for i in range(size):
        edx = ((KEY_2 * key) // 0x100000000) + key

        eax = (edx // 0x80) + int(edx < 0)
        eax = (eax * 0x763D) % 0x100000000

        ecx = (key * 0xAB) % 0x100000000

        key = toI32(ecx - eax)

        byte = data[i]
        byte = rol32(byte, i % 5)
        byte = ((byte ^ (18 + i * 6)) + key) % 0x100

        data[i] = byte

    # exit()

    return bytes(data)

def unpackRAS (filePath):
    print(filePath)

    with openFile(filePath, ReaderType.FS) as f:
        signature = f.read(4)

        if signature != SIGNATURE_RAS:
            print('Not a RAS file')
            return

        key = f.i32()
        size = 36
        data = f.ba(size)
        data = decryptBuffer(data, size, key)

        # signature.. decryptKey. entryCount. 05 00 00 00
        # tocSize.... pathsSize.. rasVersion. E3 01 A8 F9
        # A2 2E F1 86 C1 A1 A3 4E compatMark.   
        f2 = MemReader(data)

        entryCount = f2.u32()
        unk1       = f2.u32()
        tocSize    = f2.u32()
        pathsSize  = f2.u32()
        version    = f2.u32()
        unk3       = f2.u32()
        unk4       = f2.u32()
        unk5       = f2.u32()
        compatMark = f2.u32()

        # TODO:
        assert version == 0x3F99999A, 'Error: Archive <ras_path> version is <current_version>, expected version <expected_version>'
        assert compatMark == 4, 'Error: Incompatible archive <path>'

        # Entries
        # -----------------------------------------

        data2 = f.ba(tocSize)
        data2 = decryptBuffer(data2, tocSize, key)

        # Current f offset: 1505

        f3 = MemReader(data2)

        for i in range(entryCount):
            entryName = f3.string()
            unk6      = f3.u32()
            unk7      = f3.u32()
            unk8      = f3.u32()
            unk9      = f3.u32()
            unk10     = f3.u32()
            unk11     = f3.u32()
            unk12     = f3.u32()
            unk13     = f3.u32()
            unk14     = f3.u32()
            unk15     = f3.u32()

            if i: # == 2:
                _x = [ unk6, unk7, unk8, unk9, unk10, unk11, unk12, unk13, unk14, unk15 ]
                print(entryName, *[ hex(n) for n in _x ])

        # Paths
        # -----------------------------------------

        data3 = f.ba(pathsSize)
        data3 = decryptBuffer(data3, pathsSize, key)

        f4 = MemReader(data3)

        print(f.tell())

        # writeBin(filePath + '.decrypted2', data3)
        # print(f2.u32(), f2.u32(), f2.u32())

def unpackRASes (rootDir):
    for filePath in iterFiles(rootDir, True, [ '.ras', '.mp2m' ]):
        unpackRAS(filePath)
        print(' ')

if __name__ == '__main__':
    # unpackRASes(GAME_DIR)
    # unpackRAS(joinPath(GAME_DIR, 'Bonus Dead Man Walking Chapters.mp2m'))
    unpackRAS(joinPath(GAME_DIR, 'MP2_Init.ras'))
    # unpackRAS(joinPath(GAME_DIR, 'MP2_Levels_A.ras'))
    # unpackRAS(joinPath(GAME_DIR, 'MP2_Sounds.ras'))  # long list of files
    
    # 0x1ae976f
    # 04_Warehouse.ldb 0x2c66d08 0x1b31f57 0x0 0x1 0x0 0x1 0x907d3 0x120004 0x170014 0x3e7001e
    # 05_First_Vodka.ldb 0x2934aa3 0x1ae976f 0x0 0x1 0x0 0x1 0x907d3 0x160001 0x90009 0x220003b
    # 06_First_Dream.ldb 0x23cd34e 0x1ad0f2f 0x0 0x1 0x0 0x1 0x907d3 0x120004 0x35000f 0xf20031
    # 07_Maxs_Apartment.ldb 0x386c45b 0x26ffc58 0x0 0x1 0x0 0x1 0x907d3 0x130005 0x11000f 0x310002
    # 07_Maxs_Apartment_B.ldb 0x21ef0f8 0x1789f03 0x0 0x1 0x0 0x1 0x907d3 0x120004 0x170014 0x1670024
    # 08_First_Address_Unknown.ldb 0x35ff75e 0x2355550 0x0 0x1 0x0 0x1 0x907d3 0x160001 0xa0009 0x2300008
    # 09_Upper_East_Side.ldb 0x32f5c71 0x1e52c77 0x0 0x1 0x0 0x1 0x907d3 0x120004 0x36000f 0x19a0033