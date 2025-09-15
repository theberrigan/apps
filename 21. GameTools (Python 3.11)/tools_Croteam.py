# Croteam Tools

import sys
import struct

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *



def main ():
    decompressGzipFile(r"G:\Steam\userdata\108850163\564310\remote\PlayerProfile.dat")
    
def decodeStrings ():
    text = '''
    68 65 20 68 61 73 20 61 6C 6C 6F 77 65 64 20 68 69 6D 73 65 6C 66 20 74 6F 20 73 65 65 20 68 69 73 20 6F 77 6E 20 6C 69 74 74 6C 65 6E 65 73 73 2E
    D0 9D D0 B8 20 D0 BE D0 B4 D0 B8 D0 BD 20 D1 87 D0 B5 D0 BB D0 BE D0 B2 D0 B5 D0 BA
    D0 BE D1 81 D0 B2 D0 BE D0 B1 D0 BE D0 B4 D0 B8 D1 82 D1 8C D1 81 D1 8F 20 D0 BE D1 82 20 D1 81 D1 82 D1 80 D0 B0 D1 85 D0 B0 2C 20 D0 B5 D1 81 D0 BB D0 B8 20 D0 BE D0 BD 20 D0 BD D0 B5 20 D1 81 D0 BF D0 BE D1 81 D0 BE D0 B1 D0 B5 D0 BD 20 D1 83 D0 B2 D0 B8 D0 B4 D0 B5 D1 82 D1 8C 20 D1 81 D0 B2 D0 BE D0 B5 20
    20 D0 BC D0 B5 D1 81 D1 82 D0 BE 20 D0 B2 20 D0 BC D0 B8 D1 80 D0 B5 20 D1 82 D0 B0 D0 BA 2C 20 D0 BA D0 B0 D0 BA 20 D0 BE D0 BD D0 BE 20 D0 B5 D1 81 D1 82 D1 8C 3B 20 D0 BD D0 B8 20 D0 BE D0 B4 D0 B8 D0 BD 20 D1 87 D0 B5 D0 BB D0 BE D0 B2 D0 B5 D0 BA 20 D0 BD D0 B5 20 D0 BC D0 BE D0 B6 D0 B5 D1 82 20 D0 B4 D0 BE D1 81 D1 82 D0 B8 D0 B3 D0 BD D1 83 D1 82 D1 8C
    D0 B2 D0 B5 D0 BB D0 B8 D1 87 D0 B8 D1 8F 2C 20 D0 BD D0 B0 20 D0 BA D0 BE D1 82 D0 BE D1 80 D0 BE D0 B5 20 D0 BE D0 BD 20 D1 81 D0 BF D0 BE D1 81 D0 BE D0 B1 D0 B5 D0 BD 2C 20 D0 BF D0 BE D0 BA D0 B0 20 D0 BE D0 BD 20 D0 BD D0 B5
    36 38 20 36 35 20 32 30 20 36 38 20 36 31 20 37 33 20 32 30 20 36 31 20 36 43 20 36 43 20 36 46 20 37 37 20 36 35 20 36 34 20 32 30 20 36 38 20 36 39 20 36 44 20 37 33 20 36 35 20 36 43 20 36 36 20 32 30 20 37 34 20 36 46 20 32 30 20 37 33 20 36 35 20 36 35 20 32 30 20 36 38 20 36 39 20 37 33 20 32 30 20 36 46 20 37 37 20 36 45 20 32 30 20 36 43 20 36 39 20 37 34 20 37 34 20 36 43 20 36 35 20 36 45 20 36 35 20 37 33 20 37 33 20 32 45
    D0 AF 20 D0 A1 D0 9E D0 97 D0 94 D0 90 D0 AE 20 D0 9D D0 9E D0 92 D0 AB D0 99 20 D0 A0 D0 90 D0 99
    D0 98 D0 B1 D0 BE 20 D1 83 D0 B7 D1 80 D0 B8 2C 20 D1 8F 20 D1 81 D0 BE D0 B7 D0 B4 D0 B0 D1 8E 20 D0 BD D0 BE D0 B2 D1 8B D0 B9 20 D1 80 D0 B0 D0 B9 20 D0 B8 20 D0 BD D0 BE D0 B2 D1 83 D1 8E 20 D0 B7 D0 B5 D0 BC D0 BB D1 8E 3B
    D0 B8 20 D0 B4 D1 80 D1 83 D0 B3 D0 BE D0 B5 20 D0 BD D0 B5 20 D0 B4 D0 BE D0 BB D0 B6 D0 BD D0 BE 20 D0 BD D0 B8 20 D0 B2 D1 81 D0 BF D0 BE D0 BC D0 B8 D0 BD D0 B0 D1 82 D1 8C D1 81 D1 8F 2C 20 D0 BD D0 B8
    D0 B8 20 D0 B1 D1 8B D0 BB D0 BE D0 B5 20 D0 BD D0 B5 20 D0 B4
    D0 B6 D0 BD D0 BE 20 D0 BD D0 B8 20 D0 B2 D1 81 D0 BF D0 BE
    D0 BD D0 B8 20 D0 B2 D1 81 D0 BF D0 BE D0 BC D0 B8 D0 BD D0 B0 D1 82 D1 8C D1 81 D1 8F 2C 20 D0 BD D0 B8
    D0 BF D1 80 D0 B8 D1 85 D0 BE D0 B4 D0 B8 D1 82 D1 8C 20 D0 BD D0 B0 20 D1 83 D0 BC 2E
    d0 9f d1 80 d0 b0 d0 b2 d0 b4 d0 b0 20 d0 b1 d1 8b d0 bb d0 b0 20 d0 b4 d0 be d1 87 d0 b5 d1 80 d1 8c d1 8e 20 d0 92 d1 80 d0 b5 d0 bc d0 b5 d0 bd d0 b8 2e
    92 d0 95
    99 20 d0 a1 d0
    90 d0 94
    d0 9f d0 9e d0 94 d0 aa d0 95 d0 9c 20 d0 9d d0 90 20 d0 9e d0 9b d0 98 d0 9c d0 9f
    d0 94 d0 98 d0 a2 d0 af 20 d0 97 d0 95 d0 92 d0 a1 d0 90
    d0 a3 d0 b2 d0 b8 d0 b4 d0 b5 d1 82 d1 8c 20 d0 bc d0 b8 d1 80 20 d0 b2 20 d0 be d0 b4 d0 bd d0 be d0 b9 20 d0 bf d0 b5 d1 81 d1 87 d0 b8 d0 bd d0 ba d0 b5
    d0 98 20 d0 9a d0 be d1 81 d0 bc d0 be d1 81 20 d0 b2 d0 b5 d1 81 d1 8c 20 2d 20 d0 b2 20 d0 bb d0 b5 d1 81 d0 bd d0 be d0 b9 20 d1 82 d1 80 d0 b0 d0 b2 d0 b8 d0 bd d0 ba d0 b5 21
    d0 92 d0 bc d0 b5 d1 81 d1 82 d0 b8 d1 82 d1 8c 20 d0 b2 20 d0 bb d0 b0 d0 b4 d0 be d0 bd d0 b8 20 d0 b1 d0 b5 d1 81 d0 ba d0 be d0 bd d0 b5 d1 87 d0 bd d0 be d1 81 d1 82 d1 8c 0d 0a d0 98 20 d0 b2 20 d0 bc d0 b8 d0 b3 d0 b5 20 d0 bc d0 b8 d0 bc d0 be d0 bb d0 b5 d1 82 d0 bd d0 be d0 bc 20 d0 b2 d0 b5 d1 87 d0 bd d0 be d1 81 d1 82 d1 8c 21
    d0 a1 d1 82 d1 80 d0 b0 d1 81 d1 82 d0 b8 20 e2 80 94 20 d1 8d d1 82 d0 be
    d0 b2 d0 b5 d1 87 d0 bd d0 be d0 b5 20 d0 91 d0 bb d0 b0 d0 b6 d0 b5 d0 bd d1 81 d1 82 d0 b2 d0 be
    d0 9e d0 b4 d0 bd d0 b0 20 d0 bc d1 8b d1 81 d0 bb d1 8c
    d0 b7 d0 b0 d0 bf d0 be d0 bb d0 bd d1 8f d0 b5 d1 82 20 d0 bd d0 b5 d0 be d0 b1 d1 8a d1 8f d1 82 d0 bd d0 be d1 81 d1 82 d1 8c 2e
    d0 98 d1 81 d1 82 d0 b8 d0 bd d0 bd d1 8b d0 b9 20 d0 bc d0 b5 d1 82 d0 be d0 b4 20 d0 bf d0 be d0 b7 d0 bd d0 b0 d0 bd d0 b8 d1 8f
    d1 8d d1 82 d0 be 20 d0 be d0 bf d1 8b d1 82
    c1 d0 b8 20 d1 81 d0 bb d0 be d0 b2 d0 be
    d1 81 d1 82 d0 b0 d0 bb d0 be 20 d0 bf d0 bb d0 be d1 82 d1 8c d1 8e
    D0 B2 D1 81 D1 91 20 D0 BF D1 80 D0 B5 D0 B4 D1 81 D1 82 D0 B0 D0 BD D0 B5 D1 82 20 D1 87 D0 B5 D0 BB D0 BE D0 B2 D0 B5 D0 BA D1 83 20 D0 BA D0 B0 D0 BA 20 D0 B5 D1 81 D1 82 D1 8C
    d0 9b d1 8c d0 b2 d0 b8 d0 bd d1 8b d0 b9
    20 d0 b3 d0 bd d0 b5 d0 b2 20 d0 b8
    d0 b2 d0 be d0 bb d1 87 d1 8c d1 8f 20 d0 b7 d0 bb d0 be d0 b1 d0 b0
    d0 b4 d0 b0 d0 b1 d1 8b 20 d1 81 d0 ba d0 be d0 b2 d0 b0 d1 82 d1 8c 20 d0 b7 d0 be d0 bb d0 be d1 82 d1 83 d1 8e 20 d0 b1 d1 80 d0 be d0 bd d1 8e 20 d0 bd d0 b0 d1 83 d0 ba d0 b8
    66 61 63 65 62 6f 6f 6b 2e 63 6f 6d 2f 63 72 6f 74 65 61 6d
    d0 98 d0
    65 72 69 6f 75 73 20 45 6e 67 69 6e 65 20 37 2e 35 2c 20 d0 bb d1 8e d0 b1 d0 b5 d0 b7 d0 bd d0 be 20 d0 bf d1 80 d0 b5 d0 b4 d0 be d1 81 d1 82 d0 b0 d0 b2 d0 bb d0 b5 d0 bd d0 bd d1 8b d0 b9 20 43 72 6f 74 65 61 6d 2e
    d0 a7 d0 b5 d0 bb d0 be d0 b2 d0 b5 d1 87 d0 b8 d0
    b9 20 d0 b2 d0 b8 d0 b4 d0 b8 d1 82 20 d0 bb d0 b8 d0 ba 2e 20
    d1 81 d0 b2 d0 be d0 b8 d0 bc 20 d0 b1 d0 b5 d0 b7 d0 b4 d0 b5 d0 b9 d1 81 d1 82 d0 b2 d0 b8 d0 b5 d0 bc
    20 d0 b4 d0 be d0 bf d1 83 d1 81 d1 82 d0 b8 d1 82 d1 8c 2c 20 d1 87 d1 82 d0 be d0 b1 d1 8b 20 d1 87 d0 b5 d0 bb d0 be d0 b2 d0 b5 d0 ba d1 83 20 d0 b1 d1 8b d0 bb 20 d0 bf d1 80 d0 b8 d1 87 d0 b8 d0 bd d1 91 d0 bd 20 d0 b2 d1 80 d0 b5 d0 b4
    d0 92 d1 80 d0 b5 d0 bc d1 8f 20 d0 b5 d1 81 d1 82 d1 8c 20 d0 bc d0 b8 d0 bb d0 be d1 81 d1 82 d1 8c 20 d0 92 d0 b5 d1 87 d0 bd d0 be d1 81 d1 82 d0 b8 2e
    d0 92 d0 b5 d1 87 d0 bd d0 be d1 81 d1 82 d1 8c 20 d0 be d0 b1 d0 be d0 b6 d0 b0 d0 b5 d1 82 20 d1 82 d0 b2 d0 be d1 80 d0 b5 d0 bd d0 b8 d1 8f 20 d0 b1 d0 b5 d1 81 d0 ba d0 be d0 bd d0 b5 d1 87 d0 bd d0 be d0 b3 d0 be 20 d0 b2 d1 80 d0 b5 d0 bc d0 b5 d0 bd d0 b8 2e
    d0 ad d0 92 d0 9e d0 9b d0 ae d0 a6 d0 98 d0 af 20 d0 a7 d0 95 d0 a0 d0 95 d0 97 20 d0 a6 d0 98 d0 9a d0 9b 0d 0a d0 a6 d0 98 d0 9a d0 9b 20 d0 a7 d0 95 d0 a0 d0 95 d0 97 20 d0 98 d0 93 d0 a0 d0 a3 17
    d0 94 d0 be d1 80 d0 be d0 b3 d0 b0 20
    d0 bd d0 b5 d0 b2 d0 be d0 b7 d0 b4 d0 b5 d1 80 d0 b6 d0 b0 d0 bd d0 bd d0 be d1 81 d1 82 d0 b8 20 d0 b2 d0 b5 d0 b4 d0 b5 d1 82
    d0 ba 20 d1 85 d1 80 d0 b0 d0 bc d1 83
    d0 bc d1 83 d0 b4 d1 80 d0 be d1 81 d1 82 d0 b8 2e
    d0 ba 20 d1 85 d1 80
    d0 96 d0 98 d0 97 d0 9d d0 ac 20 d0 9f d0 9e d0 a1 d0 9b d0 95 20 d0 a1 d0 9c d0 95 d0 a0 d0 a2 d0 98 20 d0 9d d0 90 d0 a7 d0 9d d0 95 d0 a2 d0 a1 d0 af 20 d0 97 d0 90 d0 9d d0 9e d0 92 d0 9e
    d0 9d d0 b5 d0 b8 d0 b7 d1 83 d1 87 d0 b5 d0 bd d0 bd d0 b0 d1 8f 20 d0 b6 d0 b8 d0 b7 d0 bd d1 8c 20 d0 bd d0 b5 20 d1 81 d1 82 d0 be d0 b8 d1 82 20 d1 82 d0 be d0 b3 d0 be 2c 20 d1 87 d1 82 d0 be d0 b1 d1 8b 20 d0 b5 d0 b5 20 d0 bf d1 80 d0 be d0 b6 d0 b8 d1 82 d1 8c
    '''

    lines = text.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            continue

        line = [ int(n, 16) for n in line.split(' ') ]
        line = bytes(line)
        line = line.decode('utf-8', 'ignore')

        print(line)


if __name__ == '__main__':
    # decodeStrings()
    main()
    