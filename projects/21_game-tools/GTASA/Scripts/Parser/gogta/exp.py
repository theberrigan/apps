import os
from common import GAME_DIR, checkSamePaths, getPathExtension, formatSize
from img import readImg
# from fxp import readFxp
from audio import AudioReader

BLACKLISTED_EXTENSIONS = tuple(ext.lower() for ext in [ '.dll', '.exe', '.asi', '.ini', '.mpg', '.ico' ])
GAME_FILES = tuple(file.lower() for file in [
    'anim', 
    'audio', 
    'data', 
    'models', 
    'movies', 
    'text', 
    'eax.dll', 
    'gta-sa.exe', 
    'ogg.dll', 
    'stream.ini', 
    'vorbis.dll', 
    'vorbisFile.dll'
])


def addExtensions (extensions, filePath, size):
    ext = getPathExtension(filePath)

    if not ext:
        ext = '.___'

    if ext in BLACKLISTED_EXTENSIONS:
        return None

    if ext not in extensions:
        extensions[ext] = {
            'itemCount': 0,
            'totalSize': 0
        }

    # if ext == '.txt':
    #     print(itemPath)

    extensions[ext]['itemCount'] += 1
    extensions[ext]['totalSize'] += size    

    return ext



def scanImgFileExtensions (imgPath, extensions):
    items = readImg(imgPath)

    for item in items:
        if 'landstal' in item.name.lower():
            print(imgPath, item.name)
        addExtensions(extensions, item.name, item.size)

    return extensions


def scanExtensions (gameDir):
    extensions = {}

    def walk (directory):
        isGameDir = checkSamePaths(directory, gameDir)

        for item in os.listdir(directory):
            if isGameDir and item.lower() not in GAME_FILES:
                continue

            itemPath = os.path.join(directory, item)

            if os.path.isfile(itemPath):
                ext = addExtensions(extensions, item, os.path.getsize(itemPath))

                if ext == '.img':
                    # print(itemPath)
                    scanImgFileExtensions(itemPath, extensions)

            elif os.path.isdir(itemPath):
                walk(itemPath)

    if not os.path.exists(gameDir):
        raise Exception('Game dir doesn\'t exist')

    if not os.path.isdir(gameDir):
        raise Exception('Game dir isn\'t a dir')

    walk(gameDir)

    return extensions 


def scanGameDir (gameDir):
    extensions = scanExtensions(gameDir)
    extensions = sorted(extensions.items(), key=lambda item: item[1]['itemCount'], reverse=True)

    lengths = [ 0, 0, 0 ]  
    items = []  

    for key, data in extensions:
        itemCount = str(data['itemCount'])
        totalSize = formatSize(data['totalSize'])

        lengths[0] = max(lengths[0], len(key))
        lengths[1] = max(lengths[1], len(itemCount))
        lengths[2] = max(lengths[2], len(totalSize))

        items.append((key, itemCount, totalSize))

    for key, itemCount, totalSize in items:
        print('  '.join((
            key.ljust(lengths[0]),
            itemCount.rjust(lengths[1]),
            totalSize.rjust(lengths[2]),
        )))




if __name__ == '__main__':
    scanGameDir(GAME_DIR)
    # ----------------------------------------------
    # reader = AudioReader.create(GAME_DIR)
    # reader.unpack()
    # ----------------------------------------------
    # readFxp(os.path.join(GAME_DIR, 'models', 'effects.fxp'))

