import os, struct, zlib, math
from collections import namedtuple

GAME_VC_DIR = r'G:\Steam\steamapps\common\Grand Theft Auto Vice City'
GAME_SA_DIR = r'G:\Steam\steamapps\common\Grand Theft Auto San Andreas'

FILE_EXT_IMG = '.img'
FILE_EXT_DIR = '.dir'

IMG_SECTOR_SIZE = 2048
IMG_DIR_ENTRY_SIZE = 32
IMG_V2_SIGNATURE = b'VER2'


def getIndex (sequence, item):
    try:
        return sequence.index(item)
    except:
        return -1


def bytesToNullString (buff):
    nullIndex = getIndex(buff, b'\x00')

    return (buff[:nullIndex] if nullIndex >= 0 else buff).decode('utf-8')


class IMGV1DirEntry:
    def __init__ (self, offsetInSectors, sizeInSectors, name):
        self.offsetInSectors = offsetInSectors
        self.sizeInSectors = sizeInSectors
        self.offset = offsetInSectors * IMG_SECTOR_SIZE
        self.size = sizeInSectors * IMG_SECTOR_SIZE
        self.name = name


class IMGV1:
    def __init__ (self, imgFilePath, dirFilePath):
        self.imgFilePath = imgFilePath
        self.dirFilePath = dirFilePath

    def readDir (self):
        with open(self.dirFilePath, 'rb') as f:
            data = f.read()

        dataSize = len(data)

        assert (dataSize % IMG_DIR_ENTRY_SIZE) == 0, 'Corrupted DIR file: {}'.format(dirFilePath)

        entryCount = dataSize // IMG_DIR_ENTRY_SIZE
        entries = []

        for i in range(entryCount):
            baseOffset = IMG_DIR_ENTRY_SIZE * i

            offset, size, name = struct.unpack('<II24s', data[baseOffset:baseOffset + IMG_DIR_ENTRY_SIZE])

            name = bytesToNullString(name)

            entries.append(IMGV1DirEntry(offset, size, name))

        return entries

    def extract (self):   
        entries = self.readDir()             
        basePath, ext = os.path.splitext(self.imgFilePath)
        extractDir = basePath + '_' + ext[1:]

        os.makedirs(extractDir, exist_ok=True)

        with open(self.imgFilePath, 'rb') as f:
            for entry in entries:
                f.seek(entry.offset)
                entryData = f.read(entry.size)
                entryPath = os.path.join(extractDir, entry.name)

                with open(entryPath, 'wb') as f2:
                    f2.write(entryData)



class IMGV2:
    def __init__ (self, imgFilePath):
        self.imgFilePath = imgFilePath

    def readDir (self):
        pass


def readIMG (filePath):
    basePath, ext = os.path.splitext(filePath)
    ext = ext.lower()

    if ext == FILE_EXT_IMG:
        dirFilePath = basePath + FILE_EXT_DIR
        imgFilePath = filePath
    elif ext == FILE_EXT_DIR:
        dirFilePath = filePath 
        imgFilePath = basePath + FILE_EXT_IMG
    else:
        raise Exception('Unsupported file')

    if not os.path.isfile(imgFilePath):
        raise Exception('IMG file doesn\'t exist: {}'.format(imgFilePath))

    with open(imgFilePath, 'rb') as f:
        isV2 = f.read(4) == IMG_V2_SIGNATURE

    if isV2:
        reader = IMGV2(imgFilePath)
    else:
        if not os.path.isfile(dirFilePath):
            raise Exception('DIR file doesn\'t exist: {}'.format(dirFilePath))

        reader = IMGV1(imgFilePath, dirFilePath)

    entries = reader.extract()


if __name__ == '__main__':
    readIMG(os.path.join(GAME_VC_DIR, 'models', 'gta3.img'))



'''
IMG_SIGNATURE = b'VER2'
IMG_HEADER_SIZE = 8
IMG_INDEX_ITEM_SIZE = 32
IMG_SECTOR_SIZE = 2048


class IMGIndexItem:
    def __init__ (self, offsetInSectors, sizeInSectors, sizeInArchive, offset, size, name):
        self.offsetInSectors = offsetInSectors
        self.sizeInSectors = sizeInSectors
        self.sizeInArchive = sizeInArchive
        self.offset = offset
        self.size = size
        self.name = name


def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items


def getIndex (sequence, item):
    try:
        return sequence.index(item)
    except:
        return -1


def bytesToNullString (buff):
    nullIndex = getIndex(buff, b'\x00')

    return (buff[:nullIndex] if nullIndex >= 0 else buff).decode('utf-8')


def align (value, boundry):
    return math.ceil(value / boundry) * boundry


def readImgIndex (imgPath):
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

            items.append(IMGIndexItem(
                offsetInSectors,
                sizeInSectors,
                sizeInArchive,
                offset,
                size,
                name
            ))

    return items


def compareCount (myNames, v1Names):
    countDiff = len(myNames) - len(v1Names) 

    if countDiff == 0:
        print(f'Same count of names')
    else:
        print(f'Count diff: {countDiff:+d} item(s)')


def compareCount (myNames, v1Names):
    countDiff = len(myNames) - len(v1Names) 

    if countDiff == 0:
        print(f'Same count of names')
    else:
        print(f'Different count: {countDiff:+d} item(s)')

    return countDiff


def compareNames (myNames, v1Names):
    myNameCount = len(myNames)
    v1NameCount = len(v1Names)
    minNameCount = min(myNameCount, v1NameCount)
    maxNameCount = max(myNameCount, v1NameCount)
    nameDiff = maxNameCount - minNameCount

    for i in range(minNameCount):
        if getIndex(v1Names, myNames[i]) < 0:
            nameDiff += 1

    if nameDiff == 0:
        print(f'Same names')
    else:
        print(f'Different names: { nameDiff }')

    return nameDiff


def comparePositions (myNames, v1Names):
    posDiff = 0

    for i in range(min(len(myNames), len(v1Names))):
        if myNames[i] != v1Names[i]:
            posDiff += 1

    if posDiff == 0:
        print(f'Same order of items')
    else:
        print(f'Different positions: { posDiff }')

    return posDiff


def compareChecksum (myImgPath, v1ImgPath, myItems, v1Items):
    with open(myImgPath, 'rb') as myFile, \
         open(v1ImgPath, 'rb') as v1File:

        for myItem in myItems:
            v1Item = None

            for item in v1Items:
                if myItem.name.lower() == item.name.lower():
                    v1Item = item
                    break

            if not v1Item:
                continue

            myFile.seek(myItem.offset)
            myCrc32 = zlib.crc32(myFile.read(myItem.size))

            v1File.seek(v1Item.offset)
            v1Crc32 = zlib.crc32(v1File.read(v1Item.size))

            if myCrc32 != v1Crc32:
                print(v1Item.name)

def cloneImgIndexItem (item):
    return IMGIndexItem(
        item.offsetInSectors,
        item.sizeInSectors,
        item.sizeInArchive,
        item.offset,
        item.size,
        item.name,
    )

def rebuildImg (mySrcImgPath, myItems, v1Items):
    myDstImgPath = mySrcImgPath + '.tmp'
    myBkpImgPath = mySrcImgPath + '.orig'
    myItemCount = len(myItems)

    metaSize = IMG_HEADER_SIZE + (IMG_INDEX_ITEM_SIZE * myItemCount) 
    contentOffset = align(metaSize, IMG_SECTOR_SIZE)

    myItemsDict = { item.name.lower(): item for item in myItems }
    indexItems = []
    contentItems = []

    # Sort index items in original order
    for v1Item in v1Items:
        myItem = myItemsDict[v1Item.name.lower()]
        indexItems.append(myItem)

    # Sort content items in original order
    for v1Item in sorted(v1Items, key=lambda item: item.offset):
        myItem = myItemsDict[v1Item.name.lower()]
        contentItems.append(myItem)

    # Add custom files if any exists
    for item in myItems:
        if item not in indexItems:
            indexItems.append(item)

        if item not in contentItems:
            contentItems.append(item)

    assert len(indexItems) == len(contentItems)

    contentItemOffsetInSectors = contentOffset // IMG_SECTOR_SIZE

    # Update offsets in index items
    for contentItem in contentItems:
        indexItemIndex = indexItems.index(contentItem)
        indexItem = cloneImgIndexItem(indexItems[indexItemIndex])
        indexItems[indexItemIndex] = indexItem

        indexItem.offsetInSectors = contentItemOffsetInSectors
        indexItem.offset = indexItem.offsetInSectors * IMG_SECTOR_SIZE

        if contentItem.sizeInSectors == 0:
            contentItemOffsetInSectors += contentItem.sizeInArchive // IMG_SECTOR_SIZE
        else:
            contentItemOffsetInSectors += contentItem.sizeInSectors

    headerData = struct.pack('<4sI', IMG_SIGNATURE, myItemCount)
    indexData = b''.join([ 
        struct.pack(
            '<IHH24s',
            item.offsetInSectors, 
            item.sizeInSectors, 
            item.sizeInArchive,
            item.name.encode('ascii')
        ) for item in indexItems 
    ])

    metaData = (headerData + indexData).ljust(contentOffset, b'\x00')

    assert len(metaData) == contentOffset

    with open(myDstImgPath, 'wb') as myDstFile, \
         open(mySrcImgPath, 'rb') as mySrcFile:

        myDstFile.write(metaData)

        for contentItem in contentItems:
            mySrcFile.seek(contentItem.offset)
            data = mySrcFile.read(contentItem.size)
            myDstFile.write(data)

    os.rename(mySrcImgPath, myBkpImgPath)
    os.rename(myDstImgPath, mySrcImgPath)
'''