import os
from collections import namedtuple
from common import readStruct, bytesToNullString

IMG_SIGNATURE = b'VER2'
IMG_HEADER_SIZE = 8
IMG_INDEX_ITEM_SIZE = 32
IMG_SECTOR_SIZE = 2048

IMGHeader = namedtuple('IMGHeader', ('offsetInSectors', 'sizeInSectors', 'sizeInArchive', 'offset', 'size', 'name'))

def readImg (imgPath):
    if not os.path.isfile(imgPath):
        raise Exception('IMG file {} doesn\'t exist'.format(imgPath))

    fileSize = os.path.getsize(imgPath)

    assert fileSize >= IMG_HEADER_SIZE, 'Corrupted IMG file: {}'.format(imgPath)

    items = []

    with open(imgPath, 'rb') as f:
        signature = f.read(4)

        if signature != IMG_SIGNATURE:
            raise Exception('IMG file signature check failed: {}'.format(imgPath))

        itemCount = readStruct('<I', f)

        assert (fileSize >= (IMG_HEADER_SIZE + (IMG_INDEX_ITEM_SIZE * itemCount))), 'Corrupted IMG file: {}'.format(imgPath)

        for i in range(itemCount):
            offsetInSectors, sizeInSectors, sizeInArchive = readStruct('<IHH', f)
            offset = offsetInSectors * IMG_SECTOR_SIZE
            size = sizeInArchive if sizeInSectors == 0 else (sizeInSectors * IMG_SECTOR_SIZE)
            name = bytesToNullString(f.read(24))

            items.append(IMGHeader(
                offsetInSectors,
                sizeInSectors,
                sizeInArchive,
                offset,
                size,
                name
            ))

    return items


if __name__ == '__main__':
    pass