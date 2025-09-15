# Space-separated values parser (usually these are *.txt files)

from ...common import bfw
from ...common.consts import GAME_DIR, HL_TEXT_ENCODING

from bfw.utils import isFile, readText



class SSV:
    def __init__ (self):
        self.line   = None
        self.size   = None
        self.cursor = None

    @classmethod
    def fromFile (cls, filePath : str, encoding=HL_TEXT_ENCODING):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding)

        return cls().parse(text)

    @classmethod
    def fromText (cls, text : str):
        if not isinstance(text, str):
            raise Exception(f'Expected str, given { type(text).__name__ }')

        return cls().parse(text)

    def parse (self, text : str):
        result = []
        lines  = text.split('\n')

        for line in lines:
            self.line   = line
            self.size   = len(line)
            self.cursor = 0

            tokens = []

            while self.cursor < self.size:
                char = self.peek()

                if char in ' \t\r':
                    self.cursor += 1
                elif char == self.peek(1) == '/':
                    break
                else:
                    tokens.append(self.readToken())

            if tokens:
                result.append(tokens)

        return result

    def peek (self, offset=0):
        offset += self.cursor

        if offset >= self.size:
            return None

        return self.line[offset]

    def readToken (self):
        tokenStart = self.cursor
        isQuoted   = False

        while self.cursor < self.size:
            char = self.peek()

            if self.cursor == tokenStart:
                self.cursor += 1
                isQuoted = char == '"'
            elif not isQuoted and char in ' \t\r':
                break
            elif isQuoted and char == '"':
                self.cursor += 1
                break
            else:
                self.cursor += 1

        if isQuoted:
            return self.line[tokenStart + 1:self.cursor - 1]

        return self.line[tokenStart:self.cursor]



def _test_ ():
    from ...common.consts import SPRITES_DIR, MATERIALS_PATH

    from bfw.utils import toJson, iterFiles, joinPath

    print(toJson(SSV.fromFile(MATERIALS_PATH)))
    print(toJson(SSV.fromFile(joinPath(GAME_DIR, 'gameinfo.txt'))))

    for filePath in iterFiles(SPRITES_DIR, False, [ '.txt' ]):
        print(toJson(SSV.fromText(readText(filePath, HL_TEXT_ENCODING))))



__all__ = [
    'SSV',

    '_test_',
]



if __name__ == '__main__':
    _test_()