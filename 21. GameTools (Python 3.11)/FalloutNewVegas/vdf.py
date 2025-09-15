from utils import *


VDF_TOKEN_LBRACE  = 1
VDF_TOKEN_RBRACE  = 2
VDF_TOKEN_STRING  = 3
VDF_TOKEN_COMMENT = 4


VDFToken = createNamedTuple('VDFToken', ('type', 'value'))


# noinspection PyArgumentList
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
                    type  = VDF_TOKEN_STRING,
                    value = data[tokenStart:i]
                ))

                isInString = False
                tokenStart = None

        elif isInComment:
            if char in '\n\x00':
                tokens.append(VDFToken(
                    type  = VDF_TOKEN_COMMENT,
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
                type  = VDF_TOKEN_LBRACE,
                value = '{'
            ))

            braceStack += 1

        elif char == '}':
            tokens.append(VDFToken(
                type  = VDF_TOKEN_RBRACE,
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
        if token.type == VDF_TOKEN_STRING:
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

        elif token.type == VDF_TOKEN_LBRACE:
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

        elif token.type == VDF_TOKEN_RBRACE:
            assert stack, 'Unbalanced braces'

            current = stack.pop()

    return current


def parseVDF (filePath):
    if not isFile(filePath):
        return None

    with open(filePath, 'r', encoding='cp1252') as f:
        data = f.read()

    return construct(tokenize(data))


def __test__ ():
    rootDir = r'G:\Steam\steamapps'

    for filePath in iterFiles(rootDir, isRecursive=False, includeExts=[ '.vdf', '.acf' ]):
        print(filePath, '\n')
        print(toJson(parseVDF(filePath)))
        print('\n\n')


__all__ = [ 'parseVDF' ]


if __name__ == '__main__':
    __test__()
