from ...common import bfw
from ...common.consts import HL_TEXT_ENCODING
from .consts import *
from .types import *

from bfw.utils import *



class VDFToken:
    def __init__ (self, type_, value):
        self.type_ = type_
        self.value = value


def tokenize (data):
    tokens = []

    if not data:
        return tokens

    dataSize    = len(data)
    maxIndex    = dataSize - 1
    tokenStart  = None
    braceStack  = 0
    isInString  = False
    isInComment = False

    for i in range(dataSize):
        char = data[i]

        if isInString:
            if char == '"':
                tokens.append(VDFToken(
                    type_ = VDFTokenType.String,
                    value = data[tokenStart:i]
                ))

                isInString = False
                tokenStart = None

        elif isInComment:
            if char in '\n\x00':
                tokens.append(VDFToken(
                    type_ = VDFTokenType.Comment,
                    value = data[tokenStart:i - 1]
                ))

                isInComment = False
                tokenStart = None

        elif char == '"':
            isInString = True
            tokenStart = i + 1

        elif char == '/':
            if i < maxIndex and data[i + 1] == '/':
                isInComment = True
                tokenStart = i
            else:
                raise Exception('Comment expected')

        elif char == '{':
            tokens.append(VDFToken(
                type_ = VDFTokenType.BraceLeft,
                value = '{'
            ))

            braceStack += 1

        elif char == '}':
            tokens.append(VDFToken(
                type_ = VDFTokenType.BraceRight,
                value = '}'
            ))

            braceStack -= 1

            if braceStack < 0:
                raise Exception('Too many }')

        if char == '\x00':
            break

    assert not isInComment, 'Incomplete comment'

    if braceStack != 0:
        raise Exception('Unbalanced braces')

    if isInString:
        raise Exception('Incomplete string')

    return tokens


def construct (tokens):
    key     = None
    stack   = []
    current = None

    for i, token in enumerate(tokens):
        if token.type_ == VDFTokenType.String:
            if key:
                assert isinstance(current, dict)

                current[key] = token.value

                key = None
            else:
                if current is None:
                    current = {}
                elif not isinstance(current, dict):
                    raise Exception('Wrong current type')

                key = token.value

        elif token.type_ == VDFTokenType.BraceLeft:
            newCurrent = {}

            if key:
                if current is None:
                    current = {}
                elif not isinstance(current, dict):
                    raise Exception('Wrong current type')

                current[key] = newCurrent  

                key = None            
            else:
                if current is None:
                    current = []
                elif not isinstance(current, list):
                    raise Exception('Wrong current type')

                current.append(newCurrent)

            stack.append(current)

            current = newCurrent

        elif token.type_ == VDFTokenType.BraceRight:
            assert stack, 'Unbalanced braces'

            current = stack.pop()

    return current


def parse (text):
    return construct(tokenize(text))


class VDF:
    @classmethod
    def fromFile (cls, filePath : str, encoding=HL_TEXT_ENCODING) -> list[str] | None:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        return parse(readText(filePath, encoding))

    @classmethod
    def fromText (cls, text : str) -> list[str] | None:
        if not isinstance(text, str):
            raise Exception(f'Expected str, given { type(text).__name__ }')

        return parse(text)

    @classmethod
    def fromBuffer (cls, buffer : bytes | bytearray, encoding=HL_TEXT_ENCODING) -> list[str] | None:
        if not isinstance(buffer, (bytes, bytearray)):
            raise Exception(f'Expected bytes or bytearray, given { type(buffer).__name__ }')

        return parse(buffer.decode(encoding))



def _test_ ():
    rootDir = r'C:\Projects\HLW\packages\game\static\platform'

    for filePath in iterFiles(rootDir, True, [ '.vdf' ]):
        print(filePath, '\n')

        print(toJson(VDF.fromFile(filePath)))
        print(toJson(VDF.fromText(readText(filePath, HL_TEXT_ENCODING))))

        print('\n\n')



__all__ = [
    'VDF',

    '_test_',
]



if __name__ == '__main__':
    _test_()
