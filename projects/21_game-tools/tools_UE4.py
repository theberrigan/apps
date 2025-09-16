# Unreal Engine 4 Tools

import sys

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR = r'G:\Steam\steamapps\common\POSTAL Redux'



class BlockMeta:
    def __init__ (self):
        self.offset = None
        self.size   = None


def unpackPak (filePath, unpackDir=None):    
    filePath = getAbsPath(filePath)

    if not isFile(filePath):
        raise Exception(f'File is not found: { filePath }')

    if not unpackDir:
        unpackDir = filePath + '.unpacked'

    # count = 13262 | 13259
    with openFile(filePath) as f:
        while f.remaining():
            print(f.tell())

            itemType = f.u64()  # 0

            assert itemType in [ 0, 34, 92, 116 ]

            if itemType == 0:
                payloadSize      = f.u64()     # total size of all compressed blocks or raw data
                decompBlocksSize = f.u64()     # size of original data
                hasBlocks        = f.u32()     # 0 | 1
                unk3             = f.read(20)  # guid
                blockCount       = f.u32()

                assert hasBlocks == 0 and blockCount == 0 or hasBlocks == 1 and blockCount > 0

                print(f'itemType         = { itemType }')
                print(f'payloadSize      = { payloadSize }')
                print(f'decompBlocksSize = { decompBlocksSize }')
                print(f'hasBlocks        = { hasBlocks }')
                print(f'unk3             = { formatHex(unk3) }')
                print(f'blockCount       = { blockCount }')

                blocks = None

                if hasBlocks:
                    print(' ')

                    blocks = [ BlockMeta() for i in range(blockCount) ]

                    _c = None

                    for i in range(blockCount):
                        block = blocks[i]

                        block.offset = f.u64()
                        blockEnd     = f.u64()
                        block.size   = blockEnd - block.offset

                        if _c is not None:
                            assert _c == block.offset

                        _c = block.offset + block.size

                        print('->', block.offset, block.size)

                    assert sum([ b.size for b in blocks ]) == payloadSize

                    print(' ')

                unk6 = f.u8()

                assert unk6 == 0, unk6

                if hasBlocks == 1:
                    compBufferSize = f.u32()

                # if itemType == 0:
                #     assert hasBlocks == 0 and compBufferSize == 2653586369 or hasBlocks == 1 and compBufferSize <= 65536, (hasBlocks, compBufferSize)

                print(f'unk6             = { unk6 }')

                if hasBlocks == 1:
                    print(f'compBufferSize   = { compBufferSize }')

                print(f.tell())

                blocksEnd = f.tell() + payloadSize

                if hasBlocks:
                    data       = bytearray(decompBlocksSize)
                    dataOffset = 0

                    for blockMeta in blocks:
                        f.seek(blockMeta.offset)

                        block = f.read(blockMeta.size)

                        assert block[:2] == b'\x78\x9C'

                        block     = decompressData(block)
                        blockSize = len(block)

                        data[dataOffset:dataOffset + blockSize] = block

                        dataOffset += blockSize

                    # if blockCount > 10:
                    #     writeBin(r'G:\Steam\steamapps\common\POSTAL Redux\PostalREDUX\Content\Paks\tmp.bin', data)
                    #     exit()

                else:
                    data = f.read(payloadSize)
                    print('UNCOMP+')

                assert f.tell() == blocksEnd, (f.tell(), blocksEnd)

                f.seek(blocksEnd)

            print(f.tell())

            f.align(2048)

            print(f.tell())

            print('-' * 100)       


def unpackAll ():
    for filePath in iterFiles(GAME_DIR, True, [ '.pak' ]):
        print(filePath)

        unpackPak(filePath)

        print(' ')


def main ():
    unpackAll()
    # unpackPack(joinPath(GAME_DIR, 'textures-s3.dat'))
    # unpackPack(joinPath(GAME_DIR, 'archives.dat'))



if __name__ == '__main__':
    main()
