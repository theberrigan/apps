from .types import *

import re


def normResPath (resPath):
    resPath = resPath.strip()

    if resPath:
        resPath = re.sub(r'[\\/]+', '/', resPath.lower())

        if resPath[0] == '/':
            resPath = resPath[1:]

    return resPath

def splitSpaces (value : str) -> list[str]:
    return re.split(r'\s+', value)

def splitSeps (value : str) -> list[str]:
    """
    Splits string by whitespaces and commas
    :param value: String to split
    :return: List of strings
    """
    return re.split(r'[,\s]+', value)

def padList (array : list, size : int, value = None) -> list:
    size -= len(array)

    if size <= 0:
        return array

    return array + ([ value ] * size)

def isEmptyString (value : str) -> bool:
    r"""
    Checks if string is zero-length or contains only whitespace characters or \\x00
    :param value: String to check
    :return: True if string is empty
    """
    return not value.strip(' \r\t\n\x00')

def toFloats (values : list[str]) -> list[float]:
    return [ float(v) for v in values ]

def toInts (values : list[str], base : int = 10) -> list[int]:
    return [ int(v, base) for v in values ]


def saveImage (path : str, data : bytes | bytearray, channelCount : int, width, height : int):
    from PIL import Image as PILImage

    if channelCount == 3:
        pxFormat = 'RGB'
    elif channelCount == 4:
        pxFormat = 'RGBA'
    else:
        raise ValueError('Channel count must be 3 or 4')

    img = PILImage.frombytes(pxFormat, (width, height), data)

    img.save(path)

    return img


class EnumParser:
    def __init__ (self):
        self.prefixes = []
        self.evals    = {}
        self.members  = {}
        self.nextId   = 0
        self.name     = 0
        self.comments = []

    def identify (self):
        value = self.nextId

        self.nextId += 1

        return value

    def clearName (self, name):
        for prefix in self.prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]
                break

        if not name:
            raise Exception('Name is a prefix')

        return name

    def getVisValue (self, value):
        if re.match(r'-?\d+', value):
            return value

        items  = re.split(r'([\-+])', value)
        items2 = []

        for item in items:
            item = item.strip()

            if not item:
                continue

            if item not in '+-':
                item = self.clearName(item)

            items2.append(item)

        return ' '.join(items2)

    def evalVisValue (self, value):
        return eval(value, self.evals)

    def parseEnum (self, text : str, name : str = '__UNNAMED__', prefixes : List[str] = None, startValue : int = 0, comments : bool = False):
        self.prefixes = sorted(prefixes or [], key=lambda x: len(x), reverse=True)
        self.name = name
        self.nextId = startValue

        lines = text.split('\n')
        lines2 = []

        for line in lines:
            line = line.strip().split('//')[0]

            if not line:
                continue

            if '/*' in line:
                raise Exception('Unsupported')

            lines2.append(line)

        items = re.split(r'\s*,\s*', ' '.join(lines2))

        del lines
        del lines2
        del text

        maxNameSize = 0
        maxValueSize = 0

        for item in items:
            item = item.strip()

            if not item:
                continue

            item = re.split(r'\s*=\s*', item)

            assert len(item) <= 2, item

            name = item[0]

            if comments:
                self.comments.append(name)

            name = self.clearName(name)

            if len(item) == 1:
                value = self.identify()

                self.members[name] = value
                self.evals[name]   = value
            else:
                valueVis = self.getVisValue(item[1])
                valueInt = self.evalVisValue(valueVis)

                self.nextId = valueInt + 1

                self.members[name] = valueVis
                self.evals[name]   = valueInt

            maxNameSize  = max(maxNameSize, len(name))
            maxValueSize = max(maxValueSize, len(str(self.members[name])))

        print(f'class { self.name } (Enum):')

        for i, (k, v) in enumerate(self.members.items()):
            if comments:
                print(f'    {k:<{maxNameSize}} = {v:<{maxValueSize}}  # { self.comments[i] }')
            else:
                print(f'    {k:<{maxNameSize}} = { v }')

def parseEnum (text : str, name : str = '__UNNAMED__', prefixes : List[str] = None, startValue : int = 0, comments : bool = False):
    EnumParser().parseEnum(text, name, prefixes, startValue, comments)



def _test_ ():
    somePath1 = '\\\\DaTa\\//Res.Ext'
    somePath2 = 'data/res.ext'

    assert normResPath(somePath1) == somePath2



__all__ = [
    'normResPath',
    'splitSpaces',
    'splitSeps',
    'padList',
    'isEmptyString',
    'toFloats',
    'toInts',

    '_test_',
]



if __name__ == '__main__':
    _test_()
