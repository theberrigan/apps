import os
from collections import namedtuple
from constants import GAME_DIR, GAME_FILES, BLACKLISTED_EXTENSIONS
from common import checkSamePaths, getPathExtension, formatSize, formatJson, walkDir
from img import readImg


ScanFile = namedtuple('ScanFile', ('inImg', 'type', 'filePath'))
ScanChunk = namedtuple('ScanChunk', ('inImg', 'type', 'imgPath', 'info'))


def scanImgFileExtensions (imgPath, items):
    for item in readImg(imgPath):
        ext = getPathExtension(item.name) or None

        if ext not in BLACKLISTED_EXTENSIONS:
            items.append(ScanChunk(True, ext, os.path.normpath(imgPath), item))

    return items


def scanGameFiles (gameDir):
    items = []

    def walk (directory):
        isGameDir = checkSamePaths(directory, gameDir)

        for item in os.listdir(directory):
            if isGameDir and item.lower() not in GAME_FILES:
                continue

            itemPath = os.path.join(directory, item)

            if os.path.isfile(itemPath):
                ext = getPathExtension(item) or None

                if ext not in BLACKLISTED_EXTENSIONS:
                    items.append(ScanFile(False, ext, itemPath))

                if ext == 'img':
                    scanImgFileExtensions(itemPath, items)

            elif os.path.isdir(itemPath):
                walk(itemPath)

    if not os.path.exists(gameDir):
        raise Exception('Game dir doesn\'t exist')

    if not os.path.isdir(gameDir):
        raise Exception('Game dir isn\'t a dir')

    walk(gameDir)

    return items


def scanDirByExtension (directory, extensions, isRecursive=True, rootItems=None):
    if type(extensions) == str:
        extensions = [ extensions ]

    def checkExtensions (path, isFile, isDir):
        return isFile and getPathExtension(path) in extensions

    return walkDir(directory, checkExtensions, isRecursive, rootItems)


if __name__ == '__main__':
    print(formatJson(scanGameFiles(GAME_DIR)))
    # print(collectIDE(GAME_DIR, GAME_FILES))