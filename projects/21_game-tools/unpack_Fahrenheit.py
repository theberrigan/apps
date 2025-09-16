# Fahrenheit Extractor

import os, struct, math, sys, re
from pathlib import Path
from collections import namedtuple

GAME_DIR = r'G:\Games\Fahrenheit'
UNPACK_DIR = os.path.join(GAME_DIR, '.unpack')

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


def bytesToNullString (byteSeq):
    return ''.join([ chr(b) for b in byteSeq if b > 0 ])


def align (descriptor, boundry):
    descriptor.seek(math.ceil(descriptor.tell() / boundry) * boundry)


def findPattern (f, pattern, fromPos = 0, toPos = -1):
    maxBuffSize = 64 * 1024  # 64kb
    patternSize = len(pattern)
    wasPos = f.tell()
    fileSize = f.seek(0, 2)

    toPos = fileSize if toPos < 0 else min(toPos, fileSize)
    fromPos = min(toPos, max(fromPos, 0))

    if patternSize == 0 or (toPos - fromPos) < patternSize:
        f.seek(wasPos)
        return []

    f.seek(fromPos)

    offsets = []
    buffTail = b''

    while True:
        cursorPos = f.tell()
        tailSize = len(buffTail)
        buffBase = cursorPos - tailSize
        readSize = min(maxBuffSize - tailSize, toPos - cursorPos)
        buffSize = tailSize + readSize

        if buffSize <= patternSize:
            break

        buff = buffTail + f.read(readSize)
        buffTail = b''

        assert buffSize == len(buff), 'Expected buffer size is wrong'

        buffCursor = 0

        while True:
            try:
                foundIndex = buff.index(pattern, buffCursor)
                offsets.append(buffBase + foundIndex)
                buffCursor = foundIndex + patternSize
            except:
                buffCursor = buffSize

            if (buffSize - buffCursor) < patternSize:
                buffTail = buff[-(patternSize - 1):]
                break

    f.seek(wasPos)

    return offsets


def formatSize (size):
    if size >= (1024 ** 3):
        return '{:.1f}gb'.format(size / (1024 ** 3))
    elif size >= (1024 ** 2):
        return '{:.1f}mb'.format(size / (1024 ** 2))
    elif size >= 1024:
        return '{:.1f}kb'.format(size / 1024)
    else:
        return '{}b'.format(size)


# ------------------------------------------------------------------------------


def checkBigFile (filePath):
    return Path(filePath).stem.lower() == 'bigfile_pc'
    

def readDBRAW (f):
    _start = f.tell()
    itemCount, unk1, unk2, unk3 = readStruct('<4I', f)
    print(itemCount, unk1, unk2, unk3, _start, '\n')

    _contStart = f.tell() + itemCount * 8

    # print(_contStart)

    for i in range(itemCount):
        data = readStruct('<II', f)
        # print(data[0], _contStart + data[1])

    print(' ')
    print(itemCount, f.tell())
    

def unpack (filePath, unpackDir):
    print(f'Unpacking { os.path.basename(filePath) }...')

    if not os.path.isfile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    if not checkBigFile(filePath):
        raise Exception(f'File is not an archive: { filePath }')

    fileSize = os.path.getsize(filePath)

    with open(filePath, 'rb') as f:
        signature = f.read(20)

        if signature == b'QUANTICDREAMTABIDMEM':
            print('Unsupported')

        elif signature == b'QUANTICDREAMTABINDEX':
            unk1 = readStruct('<I', f)

            while f.tell() < fileSize:
                _start = f.tell()
                header = f.read(8)

                if header == b'--------':
                    print('--------')
                    align(f, 2048)
                    continue

                unk1, contentSize = readStruct('<II', f)

                if header == b'DB_IDX__':
                    # always: unk3 == 88
                    unk3, itemCount = readStruct('<2I', f)
                    for i in range(itemCount):
                        data = readStruct('<4I', f)
                        # print(data)
                    #print(header, unk1, unk2, unk3, itemCount, _start)
                # elif header == b'PARTOFFS':
                    # content = f.read(contentSize)
                    # print(header, unk1, _start)
                    # print(header, unk1, contentSize, _start)
                # elif header == b'SBSA_H__':
                    # content = f.read(contentSize)
                    # if contentSize > 7:
                    #     print(header, unk1, formatBytes(content), _start)
                    # print(header, unk1, contentSize, _start)
                else:
                    content = f.read(contentSize)
                    print(header, unk1, contentSize, _start)
        else:
            raise Exception('Unexpected signature')

    print('Done\n')



def unpackAll (gameDir, unpackDir):
    if not os.path.isdir(gameDir):
        raise Exception(f'Game directory does not exist: { gameDir }')

    for item in os.listdir(gameDir):
        itemPath = os.path.join(gameDir, item)

        if checkBigFile(item) and os.path.isfile(itemPath):
            unpack(itemPath, unpackDir)

def parseDBRAW (filePath):
    with open(filePath, 'rb') as f:
        signature, unk1, sizeOfRest, itemCount, unk2, unk3, unk4 = readStruct('<8s6I', f)

        assert signature == b'DBRAW___'

        for i in range(itemCount):
            data = readStruct('<II', f)
            print(data)

def parseBytecode (filePath):
    unpackDir = os.path.join(os.path.dirname(filePath), '.unpack')
    groupsDir = os.path.join(unpackDir, 'groups')    
    os.makedirs(groupsDir, exist_ok=True)

    with open(filePath, 'rb') as f:
        bcpfStart, unk1, unk2, unk3, qd, unk4, bc, bbtc, unk5, bbtcSize = readStruct('<10sIII12sI8s8sII', f)
        bbtcContent = f.read(bbtcSize)
        eof, bcpfgi, infoGroupCount = readStruct('<8s16sI', f)

        groups = []

        for i in range(infoGroupCount):
            groups.append(readStruct('<III', f))

        # 365035 - groups start
        for groupId, offset, size in groups:
            f.seek(offset)

            with open(os.path.join(groupsDir, f'{groupId:08X}.bin'), 'wb') as f2:
                f2.write(f.read(size))

            # groupStart, unk1, itemCount = readStruct('<9sBI', f)
            # print(groupStart, itemCount)
            # for j in range(itemCount):
            #     item = readStruct('<I', f)
            #     print(item)
 
            # print(f.tell())
            # break

        # print(f.tell())

        # bcpfStart = readStruct('<8s', f)

        # BCPF_START | 4 ? | 4 ? | 4 ? | 
        #   QUANTICDREAM | &YA1 | 
        #   BYTECODE | BOOT_BTC | 4 ? | 4 BOOT_BTC_size | <BOOT_BTC_size> ? | ENDOFILE |
        #   BCPF_GROUP_INFOS
        # BCPF_END

        # QUANTICDREAM&YA1BYTECODE * 4947

        # BCG - byte code group

# BYTECODE
# ENDOFILE
# BCPF_GROUP_INFOS                                                                
# BCG_PACK_CLASSES_START
# BCG_CLASS_BTC_START
# BCG_CLASS_BTC_END
# BCG_PACK_CLASSES_END
# BCG_START
# BCG_END



if __name__ == '__main__':
    # unpackAll(GAME_DIR, UNPACK_DIR)
    unpack(os.path.join(GAME_DIR, 'BigFile_PC.dat'), UNPACK_DIR)
    # parseDBRAW(os.path.join(GAME_DIR, '_unpacked', 'dat', '00c.dbr'))
    # parseBytecode(os.path.join(GAME_DIR, 'obj', 'BYTECODE.BTC'))

    # for fileName, offset in [
    #     [ 'BigFile_PC.d01', 709177344 ],
    #     [ 'BigFile_PC.d02', 860342272 ],
    #     [ 'BigFile_PC.d01', 56551424  ],
    #     [ 'BigFile_PC.d01', 109492224 ],
    #     [ 'BigFile_PC.d01', 134332416 ],
    #     [ 'BigFile_PC.d01', 389408768 ],
    #     [ 'BigFile_PC.d01', 889550848 ],
    #     [ 'BigFile_PC.d01', 102895616 ],
    #     [ 'BigFile_PC.d02', 264140800 ],
    #     [ 'BigFile_PC.d02', 356311040 ],
    #     [ 'BigFile_PC.d02', 341501952 ],
    #     [ 'BigFile_PC.d02', 246960128 ],
    #     [ 'BigFile_PC.d02', 960294912 ],
    # ]:
    #     with open(os.path.join(GAME_DIR, fileName), 'rb') as f:
    #         f.seek(offset + 16)
    #         readDBRAW(f)

    # for k, v in _x.items():
    #     print(k)
    #     was = []
    #     for fileName, offset, contentSize in sorted(v, key=lambda item: item[2], reverse=True):
    #         if len(was) == 5:
    #             break
    #         if contentSize in was:
    #             continue
    #         was.append(contentSize)
    #         print('   ', fileName, offset, contentSize)


'''
header         count    total size
--------------------------------------------
b'PARTITIO'    13745      1.9gb (2051590132)
b'DBRAW___'      794    803.5mb (842522208)
b'DATABANK'     1161    688.8mb (722218864)
b'STREAMAB'    13745      5.1mb (5302023)
b'DB_IDX__'     1164      2.3mb (2427728)
b'COM_CONT'     1165    474.8kb (486236)
b'PARTOFFS'    13745    214.8kb (219912)
b'HEADER__'    13744    114.1kb (116839)
b'DBANKIDX'        6     10.4kb (10672)
b'OCOMCONT'     1165      4.6kb (4660)
b'FONT____'        1      4.4kb (4480)
b'SBSA_H__'        1        12b (12)
b'LOADCONT'     1165         0b (0)

b'STREAMAB'
    BigFile_PC.d01 569376 1725
    BigFile_PC.d01 24397856 89
    BigFile_PC.d01 83376160 53
    BigFile_PC.d01 50995232 12
b'PARTITIO'
    BigFile_PC.d01 101771264 4080
    BigFile_PC.d01 489074688 4080
    BigFile_PC.d01 774297600 4080
    BigFile_PC.d02 974669824 4080
    BigFile_PC.d02 974675968 4080
    BigFile_PC.d01 67022848 6128
    BigFile_PC.d01 56567808 8176
    BigFile_PC.d01 56555520 10224
    BigFile_PC.d01 56596480 12272
    BigFile_PC.dat 1034344448 11911152
    BigFile_PC.d03 265715712 7577584
    BigFile_PC.dat 761798656 7559152
    BigFile_PC.d02 110092288 7391216
    BigFile_PC.d03 168660992 7272432
b'DATABANK'
    BigFile_PC.d01 54265856 2032
    BigFile_PC.d01 84922368 2032
    BigFile_PC.d01 133488640 2032
    BigFile_PC.d01 133492736 2032
    BigFile_PC.d01 133496832 2032
    BigFile_PC.d02 995899392 6128
    BigFile_PC.d02 767543296 8176
    BigFile_PC.d01 719761408 10224
    BigFile_PC.dat 1017444352 16871408
    BigFile_PC.d01 172636160 6727664
    BigFile_PC.dat 907427840 6074352
    BigFile_PC.d02 817580032 4829168
    BigFile_PC.dat 415082496 4483056
b'DBRAW___'
    BigFile_PC.d01 709177344 2032
    BigFile_PC.d02 860342272 2032
    BigFile_PC.d01 56551424 4080
    BigFile_PC.d01 109492224 4080
    BigFile_PC.d01 134332416 4080
    BigFile_PC.d01 389408768 6128
    BigFile_PC.d01 889550848 8176
    BigFile_PC.d01 102895616 10224
    BigFile_PC.d02 264140800 13686768
    BigFile_PC.d02 356311040 13682672
    BigFile_PC.d02 341501952 12834800
    BigFile_PC.d02 246960128 12421104
    BigFile_PC.d02 960294912 12298224
'''

'''
BaseType/OpcodeBool.cpp
BaseType/OpcodeChar.cpp
BaseType/OpcodeFloat.cpp
BaseType/OpcodeInt.cpp
BaseType/OpcodePointer.cpp
BaseType/OpcodeReference.cpp
BaseType/OpcodeString.cpp
ComObject/ComObjectLinkVM.cpp
ComObject/ComObjectVM.cpp
ComObject/ComObjectVM.cpp
ComObject/ComObjectVM.cpp
ComObject/DescLinkVM.cpp
ComObject/DescVM.cpp
ComObject/TypeRegistryVM.cpp
ComObject/VM_Descriptor.cpp
ComplexType/OpcodeAngle3d.cpp
ComplexType/OpcodeColor.cpp
ComplexType/OpcodeColorFloat.cpp
ComplexType/OpcodeComInstance.cpp
ComplexType/OpcodeObjectId.cpp
ComplexType/OpcodePoint2d.cpp
ComplexType/OpcodePoint3d.cpp
ComplexType/OpcodeQuaternion3d.cpp
ComplexType/OpcodeScale3d.cpp
ComplexType/OpcodeVector.cpp
Container/BreakPointData.cpp
Container/BreakPointManager.cpp
Container/BreakPointManager.cpp
Container/BreakPointManager.cpp
Container/BufferAllocator.cpp
Container/ByteCode.cpp
Container/ByteCodeAllocator.cpp
Container/ByteCodeAllocator.cpp
Container/ByteCodeGroup.cpp
Container/ByteCodeHtbl.cpp
Container/ByteCodePackedFile.cpp
Container/ClassVM.cpp
Container/ClassVMInfo.cpp
Container/ClassVMStatics.cpp
Container/ClassVMStatics.cpp
Container/DynamicAllocator.cpp
Container/DynamicAllocator.cpp
Container/InfoDebug.cpp
Container/InfoDebug.cpp
Container/Interpreter.cpp
Container/MapFile.cpp
Container/MethodVM.cpp
Container/ReadBCGroup.cpp
Container/Scheduler.cpp
Container/StaticAllocator.cpp
ModuleTypes/VmModuleTypes.cpp
ModuleTypes/VmObject.cpp
Opcode/MainOpcodes.cpp
Opcode/OpcodeCom.cpp
Opcode/OpcodeDebug.cpp
Opcode/OpcodeFlow.cpp
Opcode/OpcodeIVM.cpp
Opcode/OpcodeKernel.cpp
Opcode/OpcodeTable.cpp
Opcode/OpcodeVM.cpp
'''