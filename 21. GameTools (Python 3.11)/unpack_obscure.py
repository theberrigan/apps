# Obscure Extractor

import os, sys, struct, json, ctypes, zlib
from collections import namedtuple

GAME_DIR = r'G:\Steam\steamapps\common\Obscure'
UNPACK_DIR = os.path.join(GAME_DIR, '.unpack')

SIGNATURE = b'HV PackFile\x00\x00\x03\x00\x01'
HEADER_SIZE = 40


def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])

def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items

def readNullString (descriptor):
    buff = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'\x00':
            break

        buff += byte

    return buff.decode('utf-8')

def decompressData (data):
    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


def getFileCRC32 (filePath, startPos=0):
    with open(filePath, 'rb') as f:
        checksum = 0

        f.seek(startPos)

        while True:
            data = f.read(8192)

            if not data:
                break

            checksum = zlib.crc32(data, checksum)

        return checksum


def readPackNode (f, unpackDir, files):
    nodeSize, isFile, zero1 = readStruct('>IBI', f)

    assert isFile == 0 or isFile == 1

    if isFile:
        compSize, decompSize, unk1, offset, fileNameSize = readStruct('>5I', f)
        fileName = f.read(fileNameSize).decode('ascii')
        filePath = os.path.join(unpackDir, fileName)
        files.append((filePath, unpackDir, offset, compSize, decompSize))

    else:
        itemCount, dirKeySize = readStruct('>II', f)
        dirName = f.read(dirKeySize).decode('ascii')

        for i in range(itemCount):
            readPackNode(f, os.path.join(unpackDir, dirName), files)

    return files


def unpackFiles (src, files):
    for filePath, unpackDir, offset, compSize, decompSize in files:
        print(filePath)
        
        src.seek(offset)
        data = src.read(compSize)

        if compSize != decompSize:
            data = decompressData(data)

        os.makedirs(unpackDir, exist_ok=True)

        with open(filePath, 'wb') as dst:
            dst.write(data)


def unpack (filePath, unpackDir):
    print(f'Unpacking { os.path.basename(filePath) }...')

    with open(filePath, 'rb') as f:
        signature = f.read(16)

        if signature != SIGNATURE:
            raise Exception('Signature check failed')

        rootNodeCount, nodeCount, itemCount, indexSize, unk1, indexCRC32 = readStruct('>6I', f)
        indexEnd = HEADER_SIZE + indexSize

        files = []

        for i in range(rootNodeCount):
            readPackNode(f, unpackDir, files)

        assert f.tell() == indexEnd

        unpackFiles(f, files)

    print('Done\n')


def unpackAll (gameDir, unpackDir):
    for item in os.listdir(gameDir):
        itemPath = os.path.join(gameDir, item)

        if item.lower().endswith('.hvp') and os.path.isfile(itemPath):                
            unpack(itemPath, unpackDir)


if __name__ == '__main__':
    # print(getFileCRC32('strmpack.ogg'))
    # unpack(os.path.join(GAME_DIR, 'strmpack.hvp'))
    unpackAll(GAME_DIR, UNPACK_DIR)

'''
8927 files / 2.39Gb / 3.11Gb / 1.3

# -----------------------------------------------

.zwo
.oom
.bmp
.tga
.it
.sav
.cre
.ipt
.ini
.map
.db
.txt
.sen
.txe
.rth
.rts
.coa
.hoe
.noe
.tm
.dip
.vcf
.lvl
.flo
.vso
.wav
.sub
.lng
.bik
.ogg

# -----------------------------------------------

cachpack.hvp
_common
--breakable
----chain1
----door1
----padlock
----win1
----win2
----win3
----win4
--invent
----objects
----weapons
------bar
------beat
------fgun
------flashlight
------grenade
------gun
------laser
------shotgun
--players
----boy1
------skin
------specific
----boy2
------skin
------specific
----boy3
------skin
------specific
----boy5
------skin
----boy6
------skin
----boy7
------skin
----gir1
------skin
------specific
----gir2
------skin
------specific
----gir3
------skin
----gir4
------skin
--pnj
----crab
------skin
------specific
----etdi1
------skin
------specific
----etdi2
------skin
----etdi3
------skin
----etdi4
------skin
----etdi5
------skin
----frie
------skin
------specific
----grim
------skin
------specific
----homm
------skin
------specific
----leon
------skin
----leonj000
------skin
----mord1
------skin
------specific
----mord2
------skin
----rein
------skin
----shom
------skin
----wald
------skin
----wick
------skin
------specific
----worm
------skin
------specific
--textures
 
datapack.hvp
_common
--chapters
--maps_pc
--menus_pc
--photos_pc
--scripts_fx
_kine
_levels
--a
----a000
----a001
----a002
----a003
----a004
--b
----b000
----b002
----b004
----b005
----b006
----b007
----b008
----b009
----b010
----b100
----b102
----b103
----b104
----b106
--c
----c000
----c003
----c004
----c006
----c009
----c010
----c011
----c100
----c101
----c104
----c105
----c109
--d
----d000
----d001
----d002
----d003
----d004
----d005
----d006
----d009
----d010
----d100
----d101
----d102
----d103
----d104
----d105
----d106
--e
----e000
----e001
----e002
----e003
----e100
----e101
----e102
----e103
--f
----f000
----f001
----f002
----f003
----f101
----f102
--g
----g000
----g001
----g002
----g003
----g004
----g005
----g006
----g007
----g008
----g009
----g010
----g012
----g013
----g014
----g015
----g016
----g100
----g103
----g104
----g105
----g106
----g107
--i
----i000
----i001
----i002
----i004
----i007
----i100
----i101
----i102
----i103
----i107
--j
----j000
----j001
--m
----m000
----m001
----m002
----m003
----m100
_shaders_pc
_sounds
--items
--menus
--monsters
--players
----en
--scene
--steps
--weapons
_sub
_texts
_voices
 
kinepack.hvp
_videopc
 
strmpack.hvp
_kine
--de
--en
--fr
--it
--sp
_sounds
_voices
--de
--en
--fr
--it
--sp
 
[Finished in 0.1s]
'''