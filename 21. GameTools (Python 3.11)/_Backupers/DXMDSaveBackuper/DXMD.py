import zlib, os, json, struct

def decompress ():
    decompressed = None

    with open('./DXNGsavegame0000.dat', 'rb') as f:
        f.seek(0x84)
        data = f.read(0x2929AC)
        decompressed = zlib.decompress(data)

    if not decompressed:
        return

    with open('./DXNGsavegame0000_decompressed.dat', 'wb') as f:
        f.write(decompressed)

prev = []

def readGameSave (filePath):
    with open(filePath, 'rb') as f:
        sign = f.read(4)

        if sign != b'SGD6':
            raise Exception('Wrong signature')

        uncompressedItemIndex, entryCount, compressedDataSize = struct.unpack('<HHI', f.read(8))

        itemList = []

        for i in range(entryCount):
            index, offset, size = struct.unpack('<I4xI4xI4x', f.read(24))

            if index != i:
                raise Exception('Wrong index')

            itemList.append((index, offset, size))

        for index, offset, size in itemList:            
            f.seek(offset)
            chunk = f.read(size)

            eq = ''

            if len(prev) > index:
                eq = prev[index] == chunk
            else:
                prev.append(chunk)

            print(index, offset, size, eq)

            if eq != True and index != uncompressedItemIndex:
                # print(index, offset, size, struct.unpack('<I', f.read(8))[0] )
                data = zlib.decompress(chunk)

                with open('{}_{}-{}-{}'.format(filePath, index, offset, size), 'wb') as f2:
                    f2.write(data)
                    # pass

# decompress()
readGameSave('./DXNGsavegame0020ok.dat')
print('-' * 20)
readGameSave('./DXNGsavegame0020.dat')