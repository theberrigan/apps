import zlib, os, json, struct
from enum import Enum, IntEnum, unique

ROOT_DIR = r'C:\Program Files (x86)\Steam\steamapps\common\Zombie Army Trilogy'

@unique
class Signature(Enum):
    Plain = b'Asura   '
    Zlib  = b'AsuraZlb'
    Cmp   = b'AsuraCmp'

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_

@unique
class EncodingType(IntEnum):
    ASTS = 0x53545341

    @classmethod
    def hasValue(cls, value):
        return value in cls.__members__.values()


ARCH_TYPE_0000 = b'\x00\x00\x00\x00'  # used in case of ARCH_COMPRESSION_ZLIB
ARCH_TYPE_RSCF = b'RSCF'
ARCH_TYPE_RSFL = b'RSFL'
ARCH_TYPE_FNFO = b'FNFO'
ARCH_TYPE_ASTS = b'ASTS'
ARCH_TYPE_HTXT = b'HTXT'
ARCH_TYPE_TXST = b'TXST'
ARCH_TYPE_UIAU = b'UIAU'
ARCH_TYPE_UIAN = b'UIAN'

'''
A = 8 bytes = "AsuraZlb" | "AsuraCmp" | "Asura   "
B = 4 bytes = "ASTS" | ...
C = 12 bytes = 4 bytes (size of the rest w/o alignment) + 4 bytes (0x2 compare to 0x2)
D = 4 bytes = 
E = 1 byte = 

F = 0x4844 - 0x10 = 0x4834 (0x4844 - size from header, 0x10 - hardcoded for ASTS)
G = F (0x4834) + cursor pos after read 12 bytes (0x18) = 0x484C

if (C[3rd dword] == 0x2) {
    
}
'''

def dec():
    decompressed = None

    with open('./GmSndMeta.asr', 'rb') as f:
        data = f.read()[20:]
        decompressed = zlib.decompress(data)

    with open('./GmSndMeta_dec.asr', 'wb') as f:
        f.write(decompressed)

   # print(decompressed)

def c():
    data = zlib.compress('test'.encode('utf-8'))
    with open('./zlb.bin', 'wb') as f:
        f.write(data)

info = {}

def deasr (filepath):
    with open(filepath, 'rb') as f:
        signature = f.read(8)

        if not Signature.hasValue(signature):
            return

        if signature == Signature.Zlib:
            basepath, ext = os.path.splitext(filepath)
            decompFilename = basepath + '_decompressed' + ext

            if not os.path.isfile(decompFilename):
                decompressed = zlib.decompress(f.read())

                with open(decompFilename, 'wb') as f2:
                    f2.write(decompressed)

                deasr(decompFilename)

            return

        archType = f.read(4)
        archTypeKey = '0000' if archType == ARCH_TYPE_0000 else archType.decode('utf-8')

        if archTypeKey not in info:
            info[archTypeKey] = []

        archSize = struct.unpack('<I', f.read(4))[0]

        unk = f.read(4)

        actualSize = os.path.getsize(filepath)

        info[archTypeKey].append({
            'filepath': os.path.relpath(filepath, ROOT_DIR),
            'sizebyte': str(archSize),
            'size': str(actualSize),
            'sizediff': str(actualSize - archSize),
            'sizefmt': '{:.2f}mb'.format(actualSize / 1024 / 1024)
        })

        # print(header)

def scan(dir):
    if not os.path.isdir(dir):
        print('Is not a path:', dir)
        return

    for item in os.listdir(dir):
        path = os.path.join(dir, item)

        if os.path.isdir(path):
            scan(path)
            continue

        if os.path.isfile(path):
            deasr(path)


def readASR (filepath):
    if not os.path.isfile(filepath):
        print('Not a file:', filepath)
        return

    with open(filepath, 'rb') as f:
        signature = f.read(8)

        if not Signature.hasValue(signature):
            print('Incorrect signature')
            return

        encodingSize = 4
        encodingType = struct.unpack('<I', f.read(encodingSize))[0]

        if not EncodingType.hasValue(encodingType):
            print('Unknown encoding type')
            return

        if encodingType == EncodingType.ASTS:
            buffSize = 0x10
            buffSizeWithoutEncodingType = buffSize - encodingSize
            afterEncodingType = f.read(buffSizeWithoutEncodingType)  # read 0xC (12) bytes
            # dword1 - size of file w/o signature and alignment bytes
            dword1, dword2, dword3 = struct.unpack('<III', afterEncodingType) 
            cursorPos = f.tell()
            dword1 -= buffSize
            dword1 += cursorPos

            if dword2 > 0x2:
                print('dword2 must be less or equal 0x2')
                return

            entiresCount = struct.unpack('<I', f.read(4))[0]
            unk2 = 0

            if dword2 < 0x2:
                pass # see read_next_header_bytes
            else:
                unk2 = struct.unpack('B', f.read(1))[0]

                if unk2 != 0:
                    unk2 = 1

                if entiresCount <= 0:
                    pass # see read_next_header_bytes
                else:
                    entries = []

                    for i in range(entiresCount):
                        path = ''

                        while True:
                            chars = struct.unpack('<4B', f.read(4))
                            isNullFound = False

                            for char in chars:
                                if char:
                                    path += chr(char)
                                else:
                                    isNullFound = True
                                    break

                            if isNullFound:
                                break

                        byte1, contentSize, contentOffset = struct.unpack('<BII', f.read(9))

                        if dword2 < 1:
                            pass  # see read_next_header_bytes
                        else:
                            pass # continue here

                        entries.append((path, contentOffset, contentSize))

                    EXTRACT_ROOT = os.path.join(ROOT_DIR, '_ex') 

                    for entry in entries:
                        path, contentOffset, contentSize = entry
                        print(path)
                        path = os.path.join(EXTRACT_ROOT, path)
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        with open(path, 'wb') as outputFile:
                            f.seek(contentOffset)
                            data = f.read(contentSize)
                            outputFile.write(data)

                        # read 1 byte



            
            # print(hex(dword1), hex(dword2), hex(dword3), hex(entiresCount))

        print('OK')



readASR(os.path.join(ROOT_DIR, 'Sounds', 'StreamingSounds.asr'))

# deasr('./StreamingSounds.asr')
# --------------------------------------
# scan(ROOT_DIR)

# keyToLength = {}

# for archType, archTypeItems in info.items():
#     for arch in archTypeItems:
#         for key, value in arch.items():
#             keyToLength[key] = max(len(value), keyToLength[key] if key in keyToLength else len(key))

# for archType, archTypeItems in info.items():   
#     print(' ')
#     for i, arch in enumerate(archTypeItems):
#         if i == 0:
#             row = '    '
#             for key in arch:
#                 row += key.rjust(keyToLength[key] + 1, ' ')
#             print(row)
#             print('-' * len(row))

#         row = archType if i == 0 else '    '

#         for key, value in arch.items():
#             row += value.rjust(keyToLength[key] + 1, ' ')

#         print(row)




# --------------------------------------
#print(hex(zlib.crc32(b'Rebellion') & 0xffffffff))