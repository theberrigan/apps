import os
import json

from shutil import copy2 as copyFile
from stat import S_IREAD, S_IWRITE
from os.path import (
    exists as checkPathExists,
    isfile as isFile,
)



def readText (filePath, encoding='utf-8'):
    with open(filePath, 'r', encoding=encoding) as f:
        return f.read()


def writeText (filePath, text, encoding='utf-8'):
    with open(filePath, 'w', encoding=encoding) as f:
        f.write(text)


def readJson (filePath, encoding='utf-8'):
    text = readText(filePath, encoding)

    return json.loads(text.strip())


def parseJson (data):
    return json.loads(data.strip())


def writeJson (filePath, data, pretty=True, encoding='utf-8'):
    text = toJson(data, pretty=pretty)
    writeText(filePath, text, encoding)


def encodeJsonValue (obj):
    if hasattr(obj, '__dict__'):
        return vars(obj)

    return repr(obj)


def toJson (data, pretty=True):
    if pretty:
        indent = 4
        separators = (',', ': ')
    else:
        indent = None
        separators = (',', ':')

    return json.dumps(data, indent=indent, separators=separators, ensure_ascii=False, default=encodeJsonValue)


def setReadOnly (path, isReadOnly):
    if not checkPathExists(path):
        return 

    os.chmod(path, (S_IREAD if isReadOnly else S_IWRITE))


def removeFile (filePath):
    if not checkPathExists(filePath):
        return 

    if not isFile(filePath):
        raise Exception(f'Not a file: { filePath }')

    setReadOnly(filePath, False)

    os.remove(filePath)



__all__ = [
    'copyFile',
    'readText',
    'writeText',
    'readJson',
    'parseJson',
    'writeJson',
    'encodeJsonValue',
    'toJson',
    'setReadOnly',
    'removeFile',
]