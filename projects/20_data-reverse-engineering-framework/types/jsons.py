import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bfw.utils import *
from bfw.types.enums import Enum2



class TokenType (Enum2):
    String       = 1   # ~
    Number       = 2
    BTrue        = 3   # ~
    BFalse       = 4   # ~
    Null         = 5   # ~
    BracketLeft  = 6   # +
    BracketRight = 7   # +
    BraceLeft    = 8   # +
    BraceRight   = 9   # +
    Colon        = 10  # +
    Comma        = 11  # +
    Comment      = 12  # ~


SAMPLES_DIR = r'C:\Projects\_Data_Samples\json'

'''
null
1.5
1
false
true
string
array
dict

'''

class Token:
    def __init__ (self, tokenType, offset, size, startLine, startColumn, endLine, endColumn, data):
        self.type        = tokenType
        self.offset      = offset
        self.size        = size
        self.startLine   = startLine
        self.startColumn = startColumn
        self.endLine     = endLine
        self.endColumn   = endColumn
        self.data        = data


class TokenStream:
    def __init__ (self):
        self.tokens = None
        self.size   = None
        self.cursor = None

    def read (self, tokens):
        self.tokens = [ t for t in tokens if t.type != TokenType.Comment ]
        self.size   = len(self.tokens)
        self.cursor = 0

        result = self.readValue()
        token  = self.advance()

        if token is not None:
            raise Exception(f'Unexpected token { TokenType.getKey(token.type) }, line { token.startLine }, column { token.startColumn }')

        return result

    def readValue (self):
        token = self.advance()

        if not token:
            raise Exception('Unexpected end of input')

        if token.type == TokenType.String:
            result = self.parseString(token.data)
        elif token.type in [
            TokenType.Number,
            TokenType.BTrue,
            TokenType.BFalse,
            TokenType.Null
        ]:
            result = token.data
        elif token.type == TokenType.BracketLeft:
            result = self.readArray()
        elif token.type == TokenType.BraceLeft:
            result = self.readDict()
        else:
            raise Exception(f'Unexpected token { TokenType.getKey(token.type) }, line { token.startLine }, column { token.startColumn }')

        return result

    def readArray (self):
        result = []

        isFirst  = True
        wasComma = False

        while True:
            token = self.peek()

            if not token:
                raise Exception('Unexpected end of input')

            if token.type == TokenType.BracketRight:
                self.cursor += 1
                break

            if token.type == TokenType.Comma:
                if wasComma:
                    raise Exception(f'Unexpected comma, line { token.startLine }, column { token.startColumn }')

                self.cursor += 1
                wasComma = True

                continue

            if not isFirst and not wasComma:
                raise Exception(f'Expected comma, { TokenType.getKey(token.type) } given, line { token.startLine }, column { token.startColumn }')

            result.append(self.readValue())

            wasComma = False
            isFirst  = False

        return result

    def readDict (self):
        result = {}

        wasComma = True

        while True:
            token = self.advance()

            if not token:
                raise Exception('Unexpected end of input')

            if token.type == TokenType.BraceRight:
                break

            if token.type == TokenType.Comma:
                if wasComma:
                    raise Exception(f'Unexpected comma, line { token.startLine }, column { token.startColumn }')

                wasComma = True

                continue
            elif not wasComma:
                raise Exception(f'Expected comma, { TokenType.getKey(token.type) } given, line { token.startLine }, column { token.startColumn }')

            if token.type != TokenType.String:
                raise Exception(f'Expected string, { TokenType.getKey(token.type) } given, line { token.startLine }, column { token.startColumn }')

            key = self.parseString(token.data)

            token = self.advance()

            if token.type != TokenType.Colon:
                raise Exception(f'Expected colon, { TokenType.getKey(token.type) } given, line { token.startLine }, column { token.startColumn }')

            result[key] = self.readValue()

            wasComma = False

        return result

    def parseString (self, string):
        assert len(string) >= 2
        assert string[0] == string[-1] == '"'

        return string[1:-1].replace('\\"', '"')

    def peek (self):
        if self.isEnd():
            return None

        return self.tokens[self.cursor]

    def advance (self):
        if self.isEnd():
            return None

        token = self.tokens[self.cursor]

        self.cursor += 1

        return token

    def isEnd (self):
        return self.cursor >= self.size


class Json:
    def __init__ (self):
        self.tokenCount = None
        self.tokens     = None
        self.text       = None
        self.size       = None
        self.cursor     = None
        self.line       = None
        self.column     = None

    @classmethod
    def parseFile (cls, filePath, encoding='utf-8'):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        return cls.parseString(readText(filePath, encoding))

    @classmethod
    def parseString (cls, text):
        return cls().parse(text)

    def parse (self, text):
        self.tokens = []
        self.text   = text
        self.size   = len(text)
        self.cursor = 0
        self.line   = 1
        self.column = 1

        while not self.isEnd():
            char = self.peek()

            if char in ' \t\r':
                self.cursor += 1
                self.column += 1
            elif char == '\n':
                self.cursor += 1
                self.line   += 1
                self.column = 1
            elif char in '[':
                self.addToken(TokenType.BracketLeft, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char in ']':
                self.addToken(TokenType.BracketRight, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char in '{':
                self.addToken(TokenType.BraceLeft, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char in '}':
                self.addToken(TokenType.BraceRight, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char in ',':
                self.addToken(TokenType.Comma, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char in ':':
                self.addToken(TokenType.Colon, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char == '/' and self.peek(1) == '/':
                self.readComment()
            elif char == '"':
                self.readString()
            elif char.isalpha():
                self.readKeyword()  # null / true / false
            elif char == '-' or char.isdigit():
                self.readNumber()
            else:
                raise Exception(f'Unexpected token "{ char }", line { self.line }, column { self.column }')

        if not self.tokens:
            raise Exception('Input is empty')

        return TokenStream().read(self.tokens)

    def isEnd (self):
        return self.cursor >= self.size

    def peek (self, offset=0):
        offset += self.cursor

        if offset >= self.size:
            return None

        return self.text[offset]

    def addToken (self, tokenType, offset, size, startLine, startColumn, endLine, endColumn, data=None):
        self.tokens.append(Token(
            tokenType   = tokenType,
            offset      = offset,
            size        = size,
            startLine   = startLine,
            startColumn = startColumn,
            endLine     = endLine,
            endColumn   = endColumn,
            data        = data
        ))

    def readComment (self):
        startOffset = self.cursor
        startColumn = self.column

        while True:
            char = self.peek()
            charCount = self.cursor - startOffset

            if char is None or char == '\n':
                break

            if charCount < 2 and char != '/':
                raise Exception('Unexpected start of one-line comment')

            self.cursor += 1
            self.column += 1

        comment = self.text[startOffset:self.cursor]

        self.addToken(TokenType.Comment, startOffset, len(comment), self.line, startColumn, self.line, self.column - 1, comment)

    def readString (self):
        startOffset = self.cursor
        startColumn = self.column
        isEscaped   = False

        while True:
            char = self.peek()
            isStart = self.cursor == startOffset

            if isStart and char != '"':
                raise Exception('Unexpected start of string')

            if char is None or char == '\n':
                raise Exception('Unexpected end of string')

            self.cursor += 1
            self.column += 1

            if isEscaped:
                isEscaped = False
            elif char == '\\':
                isEscaped = True
            elif char == '"' and not isStart:
                break

        string = self.text[startOffset:self.cursor]

        self.addToken(TokenType.String, startOffset, len(string), self.line, startColumn, self.line, self.column - 1, string) 

    def readKeyword (self):
        startOffset = self.cursor
        startColumn = self.column

        while True:
            char = self.peek()

            if char is None or not char.isdigit() and not char.isalpha():
                break

            self.cursor += 1
            self.column += 1

        keyword = self.text[startOffset:self.cursor]

        tokenMap = {
            'null':  (TokenType.Null,   None ),
            'true':  (TokenType.BTrue,  True ),
            'false': (TokenType.BFalse, False),
        }

        tokenInfo = tokenMap.get(keyword)

        if tokenInfo is None:
            raise Exception(f'Unexpected token "{ keyword }", line { self.line }, column { startColumn }')

        self.addToken(tokenInfo[0], startOffset, len(keyword), self.line, startColumn, self.line, self.column - 1, tokenInfo[1]) 

    def readNumber (self):
        startOffset = self.cursor
        startColumn = self.column
        isFirstChar = True
        wasDot      = False
        wasDigit    = False
        isPrevE     = False
        wasE        = False

        while True:
            char = self.peek().lower()
            isDigit = char.isdigit()

            if char is None or char not in '-.e+' and not isDigit:
                break

            if char == '-' and self.cursor != startOffset and not isPrevE:
                raise Exception('Unexpected minus')

            if char == '+' and not isPrevE:
                raise Exception('Unexpected plus')

            if char == '.':
                if not wasDigit:
                    raise Exception('Unexpected dot before digit')

                if wasDot:
                    raise Exception('Unexpected second dot in the number')

                wasDot = True

            if char == 'e':
                if wasE:
                    raise Exception('Unexpected second E in the number')

                isPrevE = True
                wasE    = True
            else:
                isPrevE = False

            if isDigit:
                wasDigit = True

            self.cursor += 1
            self.column += 1

        endColumn = self.column - 1

        if isPrevE:
            raise Exception('Unexpected end after number exponent')            

        if not wasDigit:
            raise Exception(f'Invalid number { self.line }:{ startColumn }-{ endColumn }')

        num  = self.text[startOffset:self.cursor]
        size = len(num)

        if wasDot or wasE:
            num = float(num)
        else:
            num = int(num, 10)

        self.addToken(TokenType.Number, startOffset, size, self.line, startColumn, self.line, endColumn, num)

# .sublime-theme
# .hidden-color-scheme


def _test_ ():
    import traceback

    for filePath in iterFiles(r'C:\Users\Berrigan\Desktop\Sublime Text 4\Misc\Themes', includeExts=[ '.sublime-theme', '.hidden-color-scheme' ]):
        print(filePath)

        obj = Json.parseFile(filePath)

        writeJson(filePath, obj)

        print(' ')

    exit()

    tokens = Json.parseFile(r"C:\Users\Berrigan\Desktop\Sublime Text 4\Misc\Themes\Theme - Default (ST3)\Default.sublime-theme")
    print(toJson(tokens))
    exit()

    tokens = Json.parseFile(joinPath(SAMPLES_DIR, 'pass1.json'))
    print(toJson(tokens))
    print(toJson(readJson(joinPath(SAMPLES_DIR, 'pass1.json'))))
    exit()

    # tokens = Json.parseFile(joinPath(SAMPLES_DIR, 'my_all.json'))
    # print(toJson(tokens))
    # exit()

    for filePath in iterFiles(SAMPLES_DIR, includeExts=[ '.json' ]):
        print(filePath)

        try:
            obj = Json.parseFile(filePath)
        except Exception:
            traceback.print_exc()

        print(' ')



__all__ = [
    'Json'
]



if __name__ == '__main__':
    _test_()