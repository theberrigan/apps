import sys

sys.path.insert(0, r'C:\Projects\GameTools')

from deps.utils import *
from deps.reader import *

STEAM_CLIENT_64_PATH = r'G:\Steam\steamclient64.dll'


def isASCIIStringChar (charCode):
    return 1 <= charCode <= 127


def isIdentifierChar (charCode, isFirstChar):
    return (not isFirstChar and 48 <= charCode <= 57) or (65 <= charCode <= 90) or (97 <= charCode <= 122) or (charCode in [ 95 ])


def findIdentifiers ():
    with openFile(STEAM_CLIENT_64_PATH) as f:
        data = f.read()

    lastIndex = len(data) - 1
    identifiers = []
    identifier = ''
    identifierStart = -1
    lastAsciiIndex = -2

    for i, charCode in enumerate(data):        
        isASCII = isASCIIStringChar(charCode)
        isIdChar = isIdentifierChar(charCode, len(identifier) == 0)
        isNull = charCode == 0
        isPrevAscii = lastAsciiIndex == (i - 1)

        # if 17170383 <= i <= (17170384 + 16):
        #     print(i, hex(charCode), isIdChar)

        if isIdChar:
            if identifier or not isPrevAscii:
                if not identifier:
                    identifierStart = i

                identifier += chr(charCode)
        else:
            if isNull and len(identifier) >= 3:
                identifiers.append((identifierStart, identifier))
                print(identifiers[-1])

            identifierStart = -1
            identifier = ''         

        if isASCII:
            lastAsciiIndex = i

'''
var client = new API.Client();

client.Initialize(0):
    

new GamePicker(client);

'''


if __name__ == '__main__':
    findIdentifiers()
