# Call of Duty 2 Tools

import sys
import math

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.maths import *
from bfw.media.image.raw import RawImage, PILImage
from bfw.media.image.dxt1 import DXT1
from bfw.native.limits import MAX_I16, MAX_U16
from bfw.types.enums import Enum2



# NOTES:
# - Confirmed text file encoding - cp1252 (.gsc file at least)



GAME_DIR      = r'G:\Games\Call Of Duty 2'
RAW_DIR       = joinPath(GAME_DIR, 'raw')
MODELS_DIR    = joinPath(RAW_DIR, 'xmodel')
WEAPONS_DIR   = joinPath(RAW_DIR, 'weapons')
MATERIALS_DIR = joinPath(RAW_DIR, 'materials')
RES_UI_DIR    = joinPath(RAW_DIR, 'ui')



class TokenType (Enum2):
    Identifier = 1
    String     = 2
    Float      = 3
    Int        = 4
    BraceLeft  = 5
    BraceRight = 6
    Comment    = 7
    CommentML  = 8
    SemiColon  = 9
    Comma      = 10
    Macro      = 11



class MenuParser:
    def __init__ (self):
        self.tokenCount = None
        self.tokens     = None
        self.text       = None
        self.size       = None
        self.cursor     = None
        self.line       = None
        self.column     = None

    @classmethod
    def fromFile (cls, filePath, encoding='utf-8'):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        return cls.fromString(readText(filePath, encoding))

    @classmethod
    def fromString (cls, text):
        return cls().parse(text)

    def parse (self, text):
        self.tokenCount = 0
        self.tokens     = {}
        self.text       = text
        self.size       = len(text)
        self.cursor     = 0
        self.line       = 1
        self.column     = 1

        while not self.isEOF():
            char = self.peek()

            if char in ' \r\t':
                self.cursor += 1
                self.column += 1
            elif char == '\n':
                self.cursor += 1
                self.line   += 1
                self.column = 1
            elif char in '{':
                self.addToken(TokenType.BraceLeft, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char in '}':
                self.addToken(TokenType.BraceRight, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char in ';':
                self.addToken(TokenType.SemiColon, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char in ',':
                self.addToken(TokenType.Comma, self.cursor, 1, self.line, self.column, self.line, self.column)
                self.cursor += 1
                self.column += 1
            elif char == '#':
                self.readMacro()
            elif char == '"':
                self.readString()
            elif char in '-.' or char.isdigit():
                self.readNumber()
            elif char == '/' and self.peek(1) == '/' or \
                 char == '\\' and self.peek(1) == '\\':
                self.readComment(char)
            elif char == '/' and self.peek(1) == '*':
                self.readMLComment()
            elif char == '_' or char.isalpha():
                self.readIdentifier()
            else:
                raise Exception('Unexpected token')

        self.tokens = [ p[1] for p in sorted(self.tokens.items(), key=lambda p: p[0]) ]

        return self.tokens

    def readNumber (self):
        startOffset = self.cursor
        startColumn = self.column
        isFirstChar = True
        wasDot      = False
        wasDigit    = False

        while True:
            char = self.peek()
            isDigit = char.isdigit()

            if char is None or char not in '-.' and not isDigit:
                break

            if char == '-' and self.cursor != startOffset:
                raise Exception('Unexpected minus in number')

            if char == '.':
                if wasDot:
                    raise Exception('Unexpected dot in number')

                wasDot = True

            if isDigit:
                wasDigit = True

            self.cursor += 1
            self.column += 1

        endColumn = self.column - 1

        if not wasDigit:
            raise Exception(f'Invalid number { self.line }:{ startColumn }-{ endColumn }')

        num  = self.text[startOffset:self.cursor]
        size = len(num)

        if wasDot:
            tokenType = TokenType.Float
            num = float(num)
        else:
            tokenType = TokenType.Int
            num = int(num, 10)

        self.addToken(tokenType, startOffset, size, self.line, startColumn, self.line, endColumn, num)

    def readMacro (self):
        startOffset = self.cursor
        startColumn = self.column

        while True:
            char = self.peek()

            if self.cursor == startOffset and char != '#':
                raise Exception('Unexpected start of macro')                

            if char is None or char in ' \n\r\t':
                break

            self.cursor += 1
            self.column += 1

        macro = self.text[startOffset:self.cursor]

        self.addToken(TokenType.Macro, startOffset, len(macro), self.line, startColumn, self.line, self.column - 1, macro)

    def readIdentifier (self):
        startOffset = self.cursor
        startColumn = self.column

        # 0-9A-Za-z_
        while True:
            char = self.peek()

            if char is None:
                break

            isLetter = char == '_' or char.isalpha()

            if self.cursor == startOffset:
                if not isLetter:
                    raise Exception('Unexpected start of identifier')
            elif not isLetter and not char.isdigit():
                break

            self.cursor += 1
            self.column += 1

        if self.cursor == startOffset:
            raise Exception('Unexpected token')

        identifier = self.text[startOffset:self.cursor]

        self.addToken(TokenType.Identifier, startOffset, len(identifier), self.line, startColumn, self.line, self.column - 1, identifier)

    def readString (self):
        startOffset = self.cursor
        startColumn = self.column

        while True:
            char = self.peek()
            isStart = self.cursor == startOffset

            if isStart and char != '"':
                raise Exception('Unexpected start of string')

            if char is None or char == '\n':
                raise Exception('Unexpected end of string')

            self.cursor += 1
            self.column += 1

            if char == '"' and not isStart:
                break

        string = self.text[startOffset:self.cursor]

        self.addToken(TokenType.String, startOffset, len(string), self.line, startColumn, self.line, self.column - 1, string)  

    def readComment (self, slash):
        startOffset = self.cursor
        startColumn = self.column

        while True:
            char = self.peek()
            charCount = self.cursor - startOffset

            if char is None or char == '\n':
                break

            if charCount < 2 and char != slash:
                raise Exception('Unexpected start of one-line comment')

            self.cursor += 1
            self.column += 1

        comment = self.text[startOffset:self.cursor]

        # Fix broken backslash comment
        if slash == '\\':
            comment = '//' + comment[2:]

        self.addToken(TokenType.Comment, startOffset, len(comment), self.line, startColumn, self.line, self.column - 1, comment)

    def readMLComment (self):
        startOffset = self.cursor
        startLine   = self.line
        startColumn = self.column

        while True:
            char = self.peek()
            charCount = self.cursor - startOffset

            if char is None:
                raise Exception('Unexpected end of multiline comment')

            if charCount == 0 and char != '/':
                raise Exception('Unexpected multiline comment char')
            elif charCount == 1 and char != '*':
                raise Exception('Unexpected multiline comment char')

            if charCount >= 2 and char == '*' and self.peek(1) == '/':
                self.cursor += 2
                self.column += 2

                break

            if char == '\n':
                self.cursor += 1
                self.line   += 1
                self.column  = 1
            else:
                self.cursor += 1
                self.column += 1

        comment = self.text[startOffset:self.cursor]

        self.addToken(TokenType.CommentML, startOffset, len(comment), startLine, startColumn, self.line, self.column - 1, comment)

    def isEOF (self):
        return self.cursor >= self.size

    def peek (self, offset=0):
        offset += self.cursor

        if offset < self.size:
            return self.text[offset]

        return None

    def advance (self):
        if self.isEOF():
            return None

        self.cursor += 1

        return self.text[self.cursor - 1]

    def addToken (self, tokenType, offset, size, startLine, startColumn, endLine, endColumn, data=None):
        self.tokens[self.tokenCount] = (tokenType, offset, size, startLine, startColumn, endLine, endColumn, data)
        self.tokenCount += 1


def parseMenu (filePath):
    print(filePath)

    tokens = MenuParser.fromFile(filePath)

    for tokenType, offset, size, startLine, startColumn, endLine, endColumn, data in tokens:
        # if tokenType == TokenType.Identifier and data and '\\' in data:
        # if tokenType == TokenType.Comment and 'ANGUAGE RESTAR' in data:
        #     print(TokenType.getKey(tokenType), f'{offset}({size}) {startLine}:{startColumn}-{endLine}:{endColumn}', data)
        print(data)

    print(' ')


# -----------------------------------------------------------------------------


IWI_SIGNATURE = b'IWi'


class IWIVersion (Enum2):
    CoD2   = 0x05     # 2005
    CoDMW1 = 0x06     # 2007
    CoDWaW = CoDMW1   # 2008
    CoDMW2 = 0x08     # 2009
    CoDMW3 = CoDMW2   # 2011
    CoDBO1 = 0x0D     # 2010
    CoDBO2 = 0x1B     # 2012


class IWIFormat (Enum2):  #           | 2 | MW1 | WaW | MW2 | BO1 | MW3 | BO2 |
    ARGB32 = 0x01         # IWI_ARGB8 | + |  +  |  +  |  +  |  +  |  +  |  +  | ARGB32 is BGRA on little-endian platform (swap 0 and 2 channels to get RGBA)
    RGB24  = 0x02         # IWI_RGB8  | + |  +  |  +  |  +  |  +  |  +  |     |
    GA16   = 0x03         # IWI_ARGB4 | + |  +  |  +  |  +  |  +  |  +  |     |
    A8     = 0x04         # IWI_A8    |   |  +  |  +  |  +  |  +  |  +  |     |
    #      = 0x06         # ~not-mult | + |  +  |  +  |  +  |  +  |  +  |     |
    #      = 0x07         # ~IWI_JPG  | + |  +  |  +  |  +  |  +  |  +  |     |
    #      = 0x08         # ~not-mult |   |  +  |  +  |  +  |     |  +  |     |
    #      = 0x09         # ~not-mult |   |  +  |  +  |  +  |  +  |  +  |     |
    DXT1   = 0x0B         # IWI_DXT1  | + |  +  |  +  |  +  |  +  |  +  |  +  |
    DXT3   = 0x0C         # IWI_DXT3  | + |  +  |  +  |  +  |  +  |  +  |  +  |
    DXT5   = 0x0D         # IWI_DXT5  | + |  +  |  +  |  +  |  +  |  +  |  +  |
    #      = 0x0E         # ~8bpp     |   |     |     |     |     |     |  +  |
    #      = 0x17         # ~128bpp   |   |     |     |     |     |  +  |     |
    
# IWI Format:
# -----
# b'IWi'  - 3
# version - u8  - see IWIVersion
# ???     - u32 - MW2 & MW3 only
# format  - u8  - see IWIFormat
# flags?  - u8
# width   - u16
# height  - u16
# depth?  - u16
# ???     - 4   - BO1 only
# ???     - 20  - BO2 only

# Usage:
# -----
# CoD2   = 0 1 2 3 5
# CoDMW1 = 0 1 3 32 33 64 67 96 128 131 192 193 195 198
# CoDWaW = 0 1 3 32 64 67 128 131 192 193 195 196 224
# CoDMW2 = 0
# CoDBO1 = 0 1 3 6 10 16 17 32 48 67 128 144 192 193 195 198 199 202 208 209 240
# CoDMW3 = 0
# CoDBO2 = 0 1 2 3 5 16 17 20 64 80 128 130 131 144 192 193 194 195 196 198 208 209 212

# Depth:
# -----
# CoD2   = 1
# CoDMW1 = 1
# CoDWaW = 1
# CoDMW2 = 1
# CoDBO1 = 1 32 128
# CoDMW3 = 1
# CoDBO2 = 1

# CoDBO1/2[12:16]:
# -----
# 00 00 00 00
# 00 00 00 40
# 00 00 80 3F

# CoDBO2[16:32]:
# -----
# 4132 values


'''
0x3    | 0x0       | Contains the text 'IWi' in ASCII form
0x1    | 0x3       | The version of the IWI 0x5 = COD2, 0x6 = COD4, 0xD = BO (I think), 0x8 = MW2/MW3

0x1    | 0x4       | Unknown, not sure.
0x1    | 0x5       | The flags of the data [If (flags & 0x3) == 0x3, this image has mipmaps]
0x1    | 0x6       | The usage flag. [0x0 = Color image, 0x1 = Skybox collection, 0x4 = Normal Map, 0x09 = Skybox collection (w/ alpha)
0x1    | 0x7       | Unknown, not sure.

0x2    | 0x8       | True format. [0x1 = ARGB8, 0x2 = RGB8, 0x3 = ARGB4, 0x4 = A8, 0x7 = JPG, 0xB = DXT1, 0xC = DXT3, 0xD = DXT5] // Credits to Denton Woods
0x2    | 0xA       | The width of the image (in pixels)
0x2    | 0xC       | The height of the image (in pixels)
0x2    | 0xE       | Unknown, not sure.
0x4    | 0x10      | The file size of the of the file (including header)
0x4    | 0x14      | The offset to the texture
0x4    | 0x18      | Offset to the 1st mipmap
0x4    | 0x1B      | Offset to the 2nd mipmap
'''


def ARGB32ToRGBA32 (data):
    if isinstance(data, bytes):
        data = bytearray(data)

    pxCount = len(data)

    assert pxCount % 4 == 0
        
    pxCount //= 4

    for i in range(pxCount):
        i *= 4
        data[i + 0], data[i + 2] = data[i + 2], data[i + 0]

    return data


_c = {}

# https://www.khronos.org/opengl/wiki/S3_Texture_Compression
# https://en.wikipedia.org/wiki/S3_Texture_Compression
# https://github.com/dtzxporter/WraithXArchon/blob/master/src/WraithXCOD/CoDIWITranslator.cpp
class IWI:
    def __init__ (self):
        pass

    @classmethod
    def fromFile (cls, filePath):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._read(f)

    @classmethod
    def fromBuffer (cls, data, filePath=None):
        with MemReader(data, filePath=filePath) as f:
            return cls._read(f)

    @classmethod
    def _read (cls, f):
        # ---------------------------------------        
        _p = f.getFilePath()

        if 'Call Of Duty 2' in _p:
            gameKey = 'CoD2'
        elif 'World at War' in _p:
            gameKey = 'CoDWaW'
        elif 'Modern Warfare 3' in _p:
            gameKey = 'CoDMW3'
        elif 'Modern Warfare 2' in _p:
            gameKey = 'CoDMW2'
        elif 'Modern Warfare' in _p:
            gameKey = 'CoDMW1'
        elif 'Black Ops 2' in _p:
            gameKey = 'CoDBO2'
        elif 'Black Ops' in _p:
            gameKey = 'CoDBO1'
        else:
            assert 0, 'Unk game'
        # ---------------------------------------
        image = cls()

        signature = f.read(len(IWI_SIGNATURE))

        if signature != IWI_SIGNATURE:
            raise Exception(f'Invalid signature: { signature }')

        version = f.u8()

        if not IWIVersion.hasValue(version):
            raise Exception(f'Unsupported version: { version }')

        if version in [ IWIVersion.CoDMW2, IWIVersion.CoDMW3 ]:
            unk1 = f.u8()  # 0 1 3 8 9 [11](MW3) 16 24 32 40 48 49 51 56 64 65 67 80 83 96 99 112 113 114 115
            unk2 = f.u8()  # 0 1 3
            unk3 = f.u8()  # 0 1 4 [8 16 20 32 96](MW3) TODO: 9
            unk4 = f.u8()  # [0 8 16](MW3)

            assert unk1 in [ 0, 1, 3, 8, 9, 11, 16, 24, 32, 40, 48, 49, 51, 56, 64, 65, 67, 80, 83, 96, 99, 112, 113, 114, 115 ], unk1
            assert unk2 in [ 0, 1, 3 ], unk2
            assert unk3 in [ 0, 1, 4, 8, 9, 16, 20, 32, 96 ], unk3
            assert unk4 in [ 0, 8, 16 ], unk4

        pxFormat = f.u8()
        flags    = f.u8()  # (1 << 1) - no mips (mipOffsets[0] == fileSize)
        width    = f.u16()
        height   = f.u16()
        depth    = f.u16()

        assert version not in [ IWIVersion.CoDMW2, IWIVersion.CoDMW3 ] or flags == 0, flags
        assert version != IWIVersion.CoDBO1 and depth == 1 or version == IWIVersion.CoDBO1 and depth in [ 1, 32, 128 ], (version, depth)

        if version == IWIVersion.CoDBO1:
            unk5 = f.read(4)
            unk6 = None
            mipCount = 7
        elif version == IWIVersion.CoDBO2:
            unk5 = f.read(4)
            unk6 = f.read(16)
            mipCount = 7
        else:
            unk5 = None
            unk6 = None
            mipCount = 3

        assert unk5 in [ None, b'\x00\x00\x00\x00', b'\x00\x00\x00\x40', b'\x00\x00\x80\x3F' ], unk5

        prevOffset = f.u32()  # total file size
        mipOffsets = f.u32(mipCount)

        if gameKey not in [ 'CoDMW2', 'CoDMW3' ]:
            assert mipOffsets[0] == prevOffset and (flags & 2) or mipOffsets[0] != prevOffset and not (flags & 2)

        mips = [ None ] * mipCount

        mipWidth  = width
        mipHeight = height

        print(f'{ IWIFormat.getKey(pxFormat) } { flags } { width }x{ height } { depth }', mipOffsets, prevOffset, f.tell())

        for i, mipOffset in enumerate(mipOffsets):  
            if mipOffset == prevOffset:
                # assert i > 0
                break

            mipSize = prevOffset - mipOffset

            f.seek(mipOffset)

            data = f.read(mipSize)

            print(f'mipWidth={ mipWidth }, mipHeight={ mipHeight }, mipSize={ mipSize }, expectedSize={ mipWidth * mipHeight * 4 }')

            if pxFormat == IWIFormat.DXT1 and mipWidth >= 1024 and mipHeight >= 1024:
                _data = DXT1.toRGBA(data, mipWidth, mipHeight)
                _image = PILImage.frombytes('RGBA', (mipWidth, mipHeight), _data)
                _image.save(rf'G:\Games\_COD_IWI\image_DXT1.png')
                sys.exit()



            # if pxFormat == IWIFormat.ARGB32:
            #     assert mipSize == (mipWidth * mipHeight * 4), (mipSize, (mipWidth * mipHeight * 4))

            #     assert mipWidth == 1 or mipWidth % 2 == 0
            #     assert mipHeight == 1 or mipHeight % 2 == 0

            # do smth

            mipWidth  = math.ceil(mipWidth / 2)
            mipHeight = math.ceil(mipHeight / 2)

            prevOffset = mipOffset


        # _width  = width  // (2 ** (maxIndex - i))
        # _height = height // (2 ** (maxIndex - i))
        # _image = PILImage.frombytes('RGBA', (_width, _height), data)
        # _image.save(rf'G:\Games\_COD_IWI\image{ i }.png')


        return image

WEAPON_FILE_SIGNATURE = b'WEAPONFILE'

WEAPON_PARAMS = {
    'accuracy':                          [ float, None ],
    'aiSpread':                          [ float, None ],
    'playerSpread':                      [ float, None ],
    'fireTime':                          [ float, None ],
    'pitchConvergenceTime':              [ float, None ],
    'yawConvergenceTime':                [ float, None ],
    'horizViewJitter':                   [ float, None ],
    'vertViewJitter':                    [ float, None ],
    'locHelmet':                         [ float, None ],
    'locHead':                           [ float, None ],
    'locNeck':                           [ float, None ],
    'locTorsoUpper':                     [ float, None ],
    'locTorsoLower':                     [ float, None ],
    'locRightArmUpper':                  [ float, None ],
    'locRightArmLower':                  [ float, None ],
    'locRightHand':                      [ float, None ],
    'locLeftArmUpper':                   [ float, None ],
    'locLeftArmLower':                   [ float, None ],
    'locLeftHand':                       [ float, None ],
    'locRightLegUpper':                  [ float, None ],
    'locRightLegLower':                  [ float, None ],
    'locRightFoot':                      [ float, None ],
    'locLeftLegUpper':                   [ float, None ],
    'locLeftLegLower':                   [ float, None ],
    'locLeftFoot':                       [ float, None ],
    'destabilizationBaseTime':           [ float, None ],
    'destabilizationTimeReductionRatio': [ float, None ],
    'moveSpeedScale':                    [ float, None ],
    'fireDelay':                         [ float, None ],
    'meleeTime':                         [ float, None ],
    'meleeDelay':                        [ float, None ],
    'reloadTime':                        [ float, None ],
    'reloadEmptyTime':                   [ float, None ],
    'reloadStartTime':                   [ float, None ],
    'reloadEndTime':                     [ float, None ],
    'reloadAddTime':                     [ float, None ],
    'reloadStartAddTime':                [ float, None ],
    'rechamberTime':                     [ float, None ],
    'rechamberBoltTime':                 [ float, None ],
    'dropTime':                          [ float, None ],
    'raiseTime':                         [ float, None ],
    'altDropTime':                       [ float, None ],
    'altRaiseTime':                      [ float, None ],
    'quickDropTime':                     [ float, None ],
    'quickRaiseTime':                    [ float, None ],
    'standMoveF':                        [ float, None ],
    'standMoveR':                        [ float, None ],
    'standMoveU':                        [ float, None ],
    'posRotRate':                        [ float, None ],
    'duckedMoveR':                       [ float, None ],
    'duckedMoveU':                       [ float, None ],
    'duckedOfsF':                        [ float, None ],
    'duckedOfsR':                        [ float, None ],
    'duckedOfsU':                        [ float, None ],
    'proneMoveU':                        [ float, None ],
    'proneOfsF':                         [ float, None ],
    'proneOfsR':                         [ float, None ],
    'proneOfsU':                         [ float, None ],
    'adsIdleSpeed':                      [ float, None ],
    'idleCrouchFactor':                  [ float, None ],
    'idleProneFactor':                   [ float, None ],
    'adsSpread':                         [ float, None ],
    'adsTransInTime':                    [ float, None ],
    'adsTransOutTime':                   [ float, None ],
    'adsTransBlendTime':                 [ float, None ],
    'adsReloadTransTime':                [ float, None ],
    'adsCrosshairInFrac':                [ float, None ],
    'adsCrosshairOutFrac':               [ float, None ],
    'adsZoomInFrac':                     [ float, None ],
    'adsZoomOutFrac':                    [ float, None ],
    'adsBobFactor':                      [ float, None ],
    'adsViewBobMult':                    [ float, None ],
    'hipSpreadStandMin':                 [ float, None ],
    'hipSpreadDuckedMin':                [ float, None ],
    'hipSpreadProneMin':                 [ float, None ],
    'hipSpreadFireAdd':                  [ float, None ],
    'hipSpreadTurnAdd':                  [ float, None ],
    'hipSpreadMoveAdd':                  [ float, None ],
    'hipSpreadDecayRate':                [ float, None ],
    'hipSpreadDuckedDecay':              [ float, None ],
    'hipSpreadProneDecay':               [ float, None ],
    'swayLerpSpeed':                     [ float, None ],
    'swayPitchScale':                    [ float, None ],
    'swayYawScale':                      [ float, None ],
    'swayHorizScale':                    [ float, None ],
    'swayVertScale':                     [ float, None ],
    'adsSwayPitchScale':                 [ float, None ],
    'adsSwayYawScale':                   [ float, None ],
    'adsSwayHorizScale':                 [ float, None ],
    'adsSwayVertScale':                  [ float, None ],
    'holdFireTime':                      [ float, None ],
    'fuseTime':                          [ float, None ],
    'parallelDefaultBounce':             [ float, None ],
    'parallelBarkBounce':                [ float, None ],
    'parallelBrickBounce':               [ float, None ],
    'parallelCarpetBounce':              [ float, None ],
    'parallelClothBounce':               [ float, None ],
    'parallelConcreteBounce':            [ float, None ],
    'parallelDirtBounce':                [ float, None ],
    'parallelFleshBounce':               [ float, None ],
    'parallelFoliageBounce':             [ float, None ],
    'parallelGlassBounce':               [ float, None ],
    'parallelGrassBounce':               [ float, None ],
    'parallelGravelBounce':              [ float, None ],
    'parallelIceBounce':                 [ float, None ],
    'parallelMetalBounce':               [ float, None ],
    'parallelMudBounce':                 [ float, None ],
    'parallelPaperBounce':               [ float, None ],
    'parallelPlasterBounce':             [ float, None ],
    'parallelRockBounce':                [ float, None ],
    'parallelSandBounce':                [ float, None ],
    'parallelSnowBounce':                [ float, None ],
    'parallelWaterBounce':               [ float, None ],
    'parallelWoodBounce':                [ float, None ],
    'parallelAsphaltBounce':             [ float, None ],
    'perpendicularDefaultBounce':        [ float, None ],
    'perpendicularBarkBounce':           [ float, None ],
    'perpendicularBrickBounce':          [ float, None ],
    'perpendicularCarpetBounce':         [ float, None ],
    'perpendicularClothBounce':          [ float, None ],
    'perpendicularConcreteBounce':       [ float, None ],
    'perpendicularDirtBounce':           [ float, None ],
    'perpendicularFleshBounce':          [ float, None ],
    'perpendicularFoliageBounce':        [ float, None ],
    'perpendicularGlassBounce':          [ float, None ],
    'perpendicularGrassBounce':          [ float, None ],
    'perpendicularGravelBounce':         [ float, None ],
    'perpendicularIceBounce':            [ float, None ],
    'perpendicularMetalBounce':          [ float, None ],
    'perpendicularMudBounce':            [ float, None ],
    'perpendicularPaperBounce':          [ float, None ],
    'perpendicularPlasterBounce':        [ float, None ],
    'perpendicularRockBounce':           [ float, None ],
    'perpendicularSandBounce':           [ float, None ],
    'perpendicularSnowBounce':           [ float, None ],
    'perpendicularWaterBounce':          [ float, None ],
    'perpendicularWoodBounce':           [ float, None ],
    'perpendicularAsphaltBounce':        [ float, None ],
    'projectileRed':                     [ float, None ],
    'projectileGreen':                   [ float, None ],

    'projImpactExplode':                 [ int, None ],
    'projectileSpeed':                   [ int, None ],
    'explosionRadius':                   [ int, None ],
    'explosionInnerDamage':              [ int, None ],
    'explosionOuterDamage':              [ int, None ],
    'damage':                            [ int, None ],
    'playerDamage':                      [ int, None ],
    'minDamage':                         [ int, None ],
    'minPlayerDamage':                   [ int, None ],
    'maxDamageRange':                    [ int, None ],
    'minDamageRange':                    [ int, None ],
    'enemyCrosshairRange':               [ int, None ],
    'autoAimRange':                      [ int, None ],
    'slowdownAimRange':                  [ int, None ],
    'slowdownAimRangeAds':               [ int, None ],
    'lockonAimRange':                    [ int, None ],
    'lockonAimRangeAds':                 [ int, None ],
    'leftArc':                           [ int, None ],
    'rightArc':                          [ int, None ],
    'topArc':                            [ int, None ],
    'bottomArc':                         [ int, None ],
    'grabarc':                           [ int, None ],
    'animHorRotateInc':                  [ int, None ],
    'minHorTurnSpeed':                   [ int, None ],
    'minVertTurnSpeed':                  [ int, None ],
    'maxHorTurnSpeed':                   [ int, None ],
    'maxVertTurnSpeed':                  [ int, None ],
    'horTurnSpeed':                      [ int, None ],
    'vertTurnSpeed':                     [ int, None ],
    'suppressionTime':                   [ int, None ],
    'maxRange':                          [ int, None ],
    'rifleBullet':                       [ int, None ],
    'armorPiercing':                     [ int, None ],
    'reticleCenterSize':                 [ int, None ],
    'playerPositionDist':                [ int, None ],
    'wideListIcon':                      [ int, None ],
    'wideKillIcon':                      [ int, None ],
    'flipKillIcon':                      [ int, None ],
    'locNone':                           [ int, None ],
    'locGun':                            [ int, None ],
    'destabilizationAngleMax':           [ int, None ],
    'destabilizeDistance':               [ int, None ],
    'twoHanded':                         [ int, None ],
    'semiAuto':                          [ int, None ],
    'boltAction':                        [ int, None ],
    'aimDownSight':                      [ int, None ],
    'rechamberWhileAds':                 [ int, None ],
    'noPartialReload':                   [ int, None ],
    'segmentedReload':                   [ int, None ],
    'gunMaxPitch':                       [ int, None ],
    'gunMaxYaw':                         [ int, None ],
    'maxAmmo':                           [ int, None ],
    'startAmmo':                         [ int, None ],
    'clipSize':                          [ int, None ],
    'shotCount':                         [ int, None ],
    'dropAmmoMin':                       [ int, None ],
    'dropAmmoMax':                       [ int, None ],
    'reloadAmmoAdd':                     [ int, None ],
    'reloadStartAdd':                    [ int, None ],
    'meleeDamage':                       [ int, None ],
    'standRotP':                         [ int, None ],
    'standRotY':                         [ int, None ],
    'standRotR':                         [ int, None ],
    'standMoveMinSpeed':                 [ int, None ],
    'standRotMinSpeed':                  [ int, None ],
    'posMoveRate':                       [ int, None ],
    'duckedMoveF':                       [ int, None ],
    'duckedRotP':                        [ int, None ],
    'duckedRotY':                        [ int, None ],
    'duckedRotR':                        [ int, None ],
    'duckedMoveMinSpeed':                [ int, None ],
    'duckedRotMinSpeed':                 [ int, None ],
    'proneMoveF':                        [ int, None ],
    'proneMoveR':                        [ int, None ],
    'proneRotP':                         [ int, None ],
    'proneRotY':                         [ int, None ],
    'proneRotR':                         [ int, None ],
    'posProneMoveRate':                  [ int, None ],
    'posProneRotRate':                   [ int, None ],
    'proneMoveMinSpeed':                 [ int, None ],
    'proneRotMinSpeed':                  [ int, None ],
    'hipIdleAmount':                     [ int, None ],
    'adsIdleAmount':                     [ int, None ],
    'hipIdleSpeed':                      [ int, None ],
    'adsAimPitch':                       [ int, None ],
    'adsZoomFov':                        [ int, None ],
    'adsViewErrorMin':                   [ int, None ],
    'adsViewErrorMax':                   [ int, None ],
    'hipSpreadMax':                      [ int, None ],
    'hipSpreadDuckedMax':                [ int, None ],
    'hipSpreadProneMax':                 [ int, None ],
    'hipGunKickReducedKickBullets':      [ int, None ],
    'hipGunKickReducedKickPercent':      [ int, None ],
    'hipGunKickPitchMin':                [ int, None ],
    'hipGunKickPitchMax':                [ int, None ],
    'hipGunKickYawMin':                  [ int, None ],
    'hipGunKickYawMax':                  [ int, None ],
    'hipGunKickAccel':                   [ int, None ],
    'hipGunKickSpeedMax':                [ int, None ],
    'hipGunKickSpeedDecay':              [ int, None ],
    'hipGunKickStaticDecay':             [ int, None ],
    'adsGunKickReducedKickBullets':      [ int, None ],
    'adsGunKickReducedKickPercent':      [ int, None ],
    'adsGunKickPitchMin':                [ int, None ],
    'adsGunKickPitchMax':                [ int, None ],
    'adsGunKickYawMin':                  [ int, None ],
    'adsGunKickYawMax':                  [ int, None ],
    'adsGunKickAccel':                   [ int, None ],
    'adsGunKickSpeedMax':                [ int, None ],
    'adsGunKickSpeedDecay':              [ int, None ],
    'adsGunKickStaticDecay':             [ int, None ],
    'hipViewKickPitchMin':               [ int, None ],
    'hipViewKickPitchMax':               [ int, None ],
    'hipViewKickYawMin':                 [ int, None ],
    'hipViewKickYawMax':                 [ int, None ],
    'hipViewKickCenterSpeed':            [ int, None ],
    'adsViewKickPitchMin':               [ int, None ],
    'adsViewKickPitchMax':               [ int, None ],
    'adsViewKickYawMin':                 [ int, None ],
    'adsViewKickYawMax':                 [ int, None ],
    'adsViewKickCenterSpeed':            [ int, None ],
    'swayMaxAngle':                      [ int, None ],
    'swayShellShockScale':               [ int, None ],
    'adsSwayMaxAngle':                   [ int, None ],
    'adsSwayLerpSpeed':                  [ int, None ],
    'fightDist':                         [ int, None ],
    'maxDist':                           [ int, None ],
    'reticleSideSize':                   [ int, None ],
    'reticleMinOfs':                     [ int, None ],
    'hipReticleSidePos':                 [ int, None ],
    'adsOverlayWidth':                   [ int, None ],
    'adsOverlayHeight':                  [ int, None ],
    'isHandModelOverridable':            [ int, None ],
    'clipOnly':                          [ int, None ],
    'sharedAmmoCap':                     [ int, None ],
    'cookOffHold':                       [ int, None ],
    'projectileSpeedUp':                 [ int, None ],
    'projectileTrailTime':               [ int, None ],
    'projectileTrailRadius':             [ int, None ],
    'adsZoomGunFov':                     [ int, None ],
    'adsFire':                           [ int, None ],
    'projectileDLight':                  [ int, None ],
    'projectileBlue':                    [ int, None ],

    'modeName':                          [ None, None ],  # always empty string
    'altWeapon':                         [ None, None ],  # always empty string
    'meleeImpactRumble':                 [ None, None ],  # always empty string
    'projectileTrail':                   [ None, None ],
    'shellEject':                        [ None, None ],
    'adsOverlayReticle':                 [ None, None ],
    'playerAnimType':                    [ None, None ],
    'weaponClass':                       [ None, None ],
    'weaponSlot':                        [ None, None ],
    'stance':                            [ None, None ],
    'clipName':                          [ None, None ],
    'ammoName':                          [ None, None ],
    'weaponType':                        [ None, None ],
    'projExplosionType':                 [ None, None ],
    'offhandClass':                      [ None, None ],
    'displayName':                       [ None, None ],
    'useHintString':                     [ None, None ],
    'dropHintString':                    [ None, None ],
    'AIOverlayDescription':              [ None, None ],
    'sharedAmmoCapName':                 [ None, None ],
    
    # see soundaliases/iw_sound2.csv
    'rechamberSoundPlayer':              [ None, 'soundPlayers' ],  # always empty string
    'reloadSoundPlayer':                 [ None, 'soundPlayers' ],  # always empty string
    'reloadEmptySoundPlayer':            [ None, 'soundPlayers' ],  # always empty string
    'reloadStartSoundPlayer':            [ None, 'soundPlayers' ],  # always empty string
    'reloadEndSoundPlayer':              [ None, 'soundPlayers' ],  # always empty string
    'fireSoundPlayer':                   [ None, 'soundPlayers' ],
    'lastShotSoundPlayer':               [ None, 'soundPlayers' ],
    'loopFireSoundPlayer':               [ None, 'soundPlayers' ],
    'stopFireSoundPlayer':               [ None, 'soundPlayers' ],

    # see soundaliases/iw_sound2.csv
    'altSwitchSound':                    [ None, 'sounds' ],  # always empty string
    'noteTrackSoundA':                   [ None, 'sounds' ],  # always empty string
    'noteTrackSoundB':                   [ None, 'sounds' ],  # always empty string
    'noteTrackSoundC':                   [ None, 'sounds' ],  # always empty string
    'noteTrackSoundD':                   [ None, 'sounds' ],  # always empty string
    'fireSound':                         [ None, 'sounds' ],
    'loopFireSound':                     [ None, 'sounds' ],
    'stopFireSound':                     [ None, 'sounds' ],
    'pickupSound':                       [ None, 'sounds' ],
    'ammoPickupSound':                   [ None, 'sounds' ],
    'lastShotSound':                     [ None, 'sounds' ],
    'meleeSwipeSound':                   [ None, 'sounds' ],
    'rechamberSound':                    [ None, 'sounds' ],
    'reloadSound':                       [ None, 'sounds' ],
    'reloadEmptySound':                  [ None, 'sounds' ],
    'reloadStartSound':                  [ None, 'sounds' ],
    'reloadEndSound':                    [ None, 'sounds' ],
    'raiseSound':                        [ None, 'sounds' ],
    'putawaySound':                      [ None, 'sounds' ],
    'pullbackSound':                     [ None, 'sounds' ],
    'projExplosionSound':                [ None, 'sounds' ],
    'projectileSound':                   [ None, 'sounds' ],

    'fireRumble':                        [ None, None ],  # /rumble/<path>
    'script':                            [ None, None ],  # /animscripts/<path>.gsc

    # /accuracy/<type>/<path>
    'aiVsAiAccuracyGraph':               [ None, 'accuracy' ],  
    'aiVsPlayerAccuracyGraph':           [ None, 'accuracy' ],

    # /materials/<path>
    'adsOverlayShader':                  [ None, 'materials' ],
    'reticleCenter':                     [ None, 'materials' ],
    'hudIcon':                           [ None, 'materials' ],
    'killIcon':                          [ None, 'materials' ],
    'reticleSide':                       [ None, 'materials' ],
    'modeIcon':                          [ None, 'materials' ],

    # /xanim/<path>
    'idleAnim':                          [ None, 'anims' ],
    'fireAnim':                          [ None, 'anims' ],
    'emptyIdleAnim':                     [ None, 'anims' ],
    'lastShotAnim':                      [ None, 'anims' ],
    'rechamberAnim':                     [ None, 'anims' ],
    'meleeAnim':                         [ None, 'anims' ],
    'reloadAnim':                        [ None, 'anims' ],
    'reloadEmptyAnim':                   [ None, 'anims' ],
    'reloadStartAnim':                   [ None, 'anims' ],
    'reloadEndAnim':                     [ None, 'anims' ],
    'raiseAnim':                         [ None, 'anims' ],
    'dropAnim':                          [ None, 'anims' ],
    'altRaiseAnim':                      [ None, 'anims' ],
    'altDropAnim':                       [ None, 'anims' ],
    'quickRaiseAnim':                    [ None, 'anims' ],
    'quickDropAnim':                     [ None, 'anims' ],
    'adsFireAnim':                       [ None, 'anims' ],
    'adsLastShotAnim':                   [ None, 'anims' ],
    'adsRechamberAnim':                  [ None, 'anims' ],
    'adsUpAnim':                         [ None, 'anims' ],
    'adsDownAnim':                       [ None, 'anims' ],
    'holdFireAnim':                      [ None, 'anims' ],

    # /xmodel/<path>
    'gunModel':                          [ None, 'models' ],
    'handModel':                         [ None, 'models' ],
    'worldModel':                        [ None, 'models' ],
    'projectileModel':                   [ None, 'models' ],

    # /fx/<path>
    'viewFlashEffect':                   [ None, 'effects' ],
    'worldFlashEffect':                  [ None, 'effects' ],
    'projExplosionEffect':               [ None, 'effects' ],
    'projTrailEffect':                   [ None, 'effects' ],
    'shellEjectEffect':                  [ None, 'effects' ],
    'lastShotEjectEffect':               [ None, 'effects' ],
}


def parseInlineConfig (filePath, expectedType=None):
    lines = readText(filePath, encoding='cp1252')
    lines = lines.split('\\')

    if not lines:
        return None

    configType = lines[0]

    if expectedType is not None and configType != expectedType:
        raise Exception('Invalid config type')        

    lineCount = len(lines)

    assert lineCount % 2 == 1

    params = {}

    for i in range(1, lineCount, 2):
        key   = lines[i].strip()
        value = lines[i + 1].strip()

        params[key] = value

    return {
        'type': lines[0],
        'params': params
    }


def getResourcePath (*parts, ext=None):
    resPath = getAbsPath(joinPath(RAW_DIR, *parts))

    if ext is not None and getExt(resPath) != ext:
        resPath += ext

    return resPath

def getRumblePath (path):
    if not path:
        return None

    return getResourcePath('rumble', path)

def getAnimScriptPath (path):
    if not path:
        return None

    return getResourcePath('animscripts', path, ext='.gsc')

def getAccuracyPath (path, kind):
    if not path:
        return None

    return getResourcePath('accuracy', kind, path)

def getMaterialPath (path):
    if not path:
        return None

    return getResourcePath('materials', path)

def getAnimPath (path):
    if not path:
        return None

    return getResourcePath('xanim', path)

def getModelPath (path):
    if not path:
        return None

    path = path.lstrip('\\/')
    
    if path and not path.lower().startswith('xmodel'):
        return getResourcePath('xmodel', path)

    return getResourcePath(path)

def getModelSurfPath (path):
    if not path:
        return None

    return getResourcePath('xmodelsurfs', path)

def getModelPartsPath (path):
    if not path:
        return None

    return getResourcePath('xmodelparts', path)

def getFXPath (path):
    return getResourcePath(path)

def getImagePath (path):
    return getResourcePath('images', path, ext='.iwi')

def parseWeapon (filePath):
    expectedType = WEAPON_FILE_SIGNATURE.decode('cp1252')
    config = parseInlineConfig(filePath, expectedType)

    assert config

    params = {}

    for key, value in config['params'].items():
        if key not in WEAPON_PARAMS:
            raise Exception(f'Unknown weapon param: { key }')

        parseFn, sectionName = WEAPON_PARAMS[key]

        if parseFn:
            value = parseFn(value)

        if sectionName:
            if sectionName not in params:
                params[sectionName] = {}

            section = params[sectionName]
        else:
            section = params

        section[key] = value

    # print(toJson(params))

    gunModelPath   = getModelPath(params['models']['gunModel'])
    worldModelPath = getModelPath(params['models']['worldModel'])
    handModelPath  = getModelPath(params['models']['handModel'])

    for key, modelPath in params['models'].items():
        modelPath = getModelPath(modelPath)
        print(modelPath)
        parseModel(modelPath)
        print(' ')

    return params

MODEL_VERSION = 20

def readQuat (f, isSimple=False):
    x = 0
    y = 0
    z = 0
    w = 0

    if not isSimple:
        x = f.i16() / MAX_I16
        y = f.i16() / MAX_I16

    z = f.i16() / MAX_I16

    w = 1 - x * x - y * y - z * z

    if w > 0:
        w = math.sqrt(w)

    return [ w, x, y, z ]

MODEL_BONE_OFFSETS = {
    'tag_view':        [   0.000000,   0.000000,   0.000000 ],
    'tag_torso':       [ -11.764860,   0.000000,  -3.497466 ],
    'j_shoulder_le':   [   2.859542,  20.160720,  -4.597286 ],
    'j_elbow_le':      [  30.718500,  -0.000008,   0.000003 ],
    'j_wrist_le':      [  29.390600,   0.000019,  -0.000003 ],
    'j_thumb_le_0':    [   2.786345,   2.245192,   0.851610 ],
    'j_thumb_le_1':    [   4.806596,  -0.000001,   0.000003 ],
    'j_thumb_le_2':    [   2.433519,  -0.000002,   0.000001 ],
    'j_thumb_le_3':    [   3.000000,  -0.000001,  -0.000001 ],
    'j_flesh_le':      [   4.822557,   1.176307,  -0.110341 ],
    'j_index_le_0':    [  10.534350,   2.786251,  -0.000003 ],
    'j_index_le_1':    [   4.563000,  -0.000003,   0.000001 ],
    'j_index_le_2':    [   2.870304,   0.000003,  -0.000002 ],
    'j_index_le_3':    [   2.999999,   0.000004,   0.000001 ],
    'j_mid_le_0':      [  10.717680,   0.362385,  -0.386470 ],
    'j_mid_le_1':      [   4.842623,  -0.000001,  -0.000001 ],
    'j_mid_le_2':      [   2.957112,  -0.000001,  -0.000001 ],
    'j_mid_le_3':      [   3.000005,   0.000004,   0.000000 ],
    'j_ring_le_0':     [   9.843364,  -1.747671,  -0.401116 ],
    'j_ring_le_1':     [   4.842618,   0.000004,  -0.000003 ],
    'j_ring_le_2':     [   2.755294,  -0.000002,   0.000005 ],
    'j_ring_le_3':     [   2.999998,  -0.000002,  -0.000004 ],
    'j_pinky_le_0':    [   8.613766,  -3.707476,   0.168180 ],
    'j_pinky_le_1':    [   3.942609,   0.000001,   0.000001 ],
    'j_pinky_le_2':    [   1.794117,   0.000003,  -0.000003 ],
    'j_pinky_le_3':    [   2.839390,  -0.000001,   0.000004 ],
    'j_wristtwist_le': [  21.603790,   0.000012,  -0.000003 ],
    'j_shoulder_ri':   [   2.859542, -20.160720,  -4.597286 ],
    'j_elbow_ri':      [ -30.718520,   0.000004,  -0.000024 ],
    'j_wrist_ri':      [ -29.390670,   0.000044,   0.000022 ],
    'j_thumb_ri_0':    [  -2.786155,  -2.245166,  -0.851634 ],
    'j_thumb_ri_1':    [  -4.806832,  -0.000066,   0.000141 ],
    'j_thumb_ri_2':    [  -2.433458,  -0.000038,  -0.000053 ],
    'j_thumb_ri_3':    [  -3.000123,   0.000160,   0.000025 ],
    'j_flesh_ri':      [  -4.822577,  -1.176315,   0.110318 ],
    'j_index_ri_0':    [ -10.534320,  -2.786281,  -0.000007 ],
    'j_index_ri_1':    [  -4.562927,  -0.000058,   0.000054 ],
    'j_index_ri_2':    [  -2.870313,  -0.000065,   0.000100 ],
    'j_index_ri_3':    [  -2.999938,   0.000165,  -0.000065 ],
    'j_mid_ri_0':      [ -10.717520,  -0.362501,   0.386463 ],
    'j_mid_ri_1':      [  -4.842728,   0.000151,   0.000028 ],
    'j_mid_ri_2':      [  -2.957152,  -0.000087,  -0.000022 ],
    'j_mid_ri_3':      [  -3.000060,  -0.000068,  -0.000019 ],
    'j_ring_ri_0':     [  -9.843175,   1.747613,   0.401109 ],
    'j_ring_ri_1':     [  -4.842774,   0.000176,  -0.000063 ],
    'j_ring_ri_2':     [  -2.755269,  -0.000011,   0.000149 ],
    'j_ring_ri_3':     [  -3.000048,  -0.000041,  -0.000049 ],
    'j_pinky_ri_0':    [  -8.613756,   3.707438,  -0.168202 ],
    'j_pinky_ri_1':    [  -3.942537,  -0.000117,  -0.000065 ],
    'j_pinky_ri_2':    [  -1.794038,   0.000134,   0.000215 ],
    'j_pinky_ri_3':    [  -2.839375,   0.000056,  -0.000115 ],
    'j_wristtwist_ri': [ -21.603880,   0.000097,   0.000008 ],
    'tag_weapon':      [  38.505900,   0.000000, -17.151910 ],
    'tag_cambone':     [   0.000000,   0.000000,   0.000000 ],
    'tag_camera':      [   0.000000,   0.000000,   0.000000 ],
}


def loadModelParts (filePath, model):
    if not isFile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    with openFile(filePath) as f:
        version = f.u16()

        if version != MODEL_VERSION:
            raise Exception(f'Unsupported model version: { version }')

        relBoneCount = f.u16()
        absBoneCount = f.u16()

        totalBoneCount = relBoneCount + absBoneCount

        bones = [
            {
                'name':           None,
                'parent':         None,
                'translation':    None,
                'rotation':       None,
                'classification': None
            } for _ in range(totalBoneCount)
        ]

        # boneMap = {}

        for i in range(relBoneCount):
            bone = bones[absBoneCount + i]

            bone['parent']      = f.i8()
            bone['translation'] = f.vec3()
            bone['rotation']    = readQuat(f)

        for i in range(totalBoneCount):
            bone = bones[i]
            name = f.string()

            if not name:
                break

            bone['name']  = name
            # boneMap[name] = i

            if model['isHandsModel'] and i > 0:
                newBone = MODEL_BONE_OFFSETS.get(name.lower())

                if newBone:
                    divVec3(newBone, 2.54, bone['translation'])

        for i in range(totalBoneCount):
            bones[i]['classification'] = f.u8()

    model['parts'] = {
        'relBoneCount':   relBoneCount,
        'absBoneCount':   absBoneCount,
        'totalBoneCount': totalBoneCount,
        'bones':          bones
    }

    return model

def loadModelSurfs (filePath, model):
    if not isFile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    with openFile(filePath) as f:
        version = f.u16()

        if version != MODEL_VERSION:
            raise Exception(f'Unsupported model version: { version }')

        model['meshes']   = []
        model['vertices'] = []

        surfCount = f.u16()

        index = 0

        for i in range(surfCount):
            tileMode   = f.u8()
            vertCount  = f.u16()
            triCount   = f.u16()
            boneOffset = f.i16()

            if boneOffset == -1:
                unk1 = f.u16()

            vertices = [ None ] * vertCount

            for j in range(vertCount):
                vertex = vertices[j] = {
                    'boneWeights': [  0 ] * 4,
                    'boneIndices': [ -1 ] * 4
                }

                vertex['normal']   = scaleVec3(f.vec3(), -1)
                vertex['color']    = f.u32()
                vertex['u']        = f.f32()
                vertex['v']        = f.f32()
                vertex['binormal'] = f.vec3()
                vertex['tangent']  = f.vec3()

                if boneOffset == -1:
                    weightCount = f.u8()
                    boneIndex   = f.u16()
                else:
                    weightCount = 0
                    boneIndex   = boneOffset

                offset = f.vec3()

                vertex['weightCount'] = weightCount + 1

                vertex['boneWeights'][0] = 1
                vertex['boneIndices'][0] = boneIndex

                if weightCount > 0:
                    unk2 = f.u8()

                    for k in range(weightCount):
                        blendIndex  = f.u16()
                        blendOffset = f.vec3()
                        blendWeight = f.u16() / MAX_U16

                        vertex['boneWeights'][0] -= blendWeight
                        vertex['boneWeights'][k + 1] = blendWeight
                        vertex['boneIndices'][k + 1] = blendIndex

                # TODO:
                # auto transform = util::get_world_transform(parts.bones, boneindex);
                # vtx.pos = glm::rotate(transform.rotation, offset) + transform.translation;
                # vtx.normal = glm::rotate(transform.rotation, vtx.normal);

            mesh = {
                'indices': []
            }

            model['meshes'].append(mesh)

            for j in range(triCount):
                face = f.u16(3)

                for k in range(3):
                    model['vertices'].append(vertices[face[k]])
                    mesh['indices'].append(index)

                    index += 1

    return model

# ------------------------

def test ():
    import struct

    _c = {}

    for filePath in iterFiles(MATERIALS_DIR, True, excludeExts=[ '.tech', '.techset', '.hlsl', '.sm' ]):
        print(filePath)

        with openFile(filePath) as f:
            matOffset      = f.u32()  # [0]
            colorMapOffset = f.u32()  # [4]

            unk1 = f.u32()  # [8]

            assert unk1 == 0, unk1

            unk2 = f.u8()  # [12]

            # sort:
            # 03 - <default>
            # 00 - distortion
            # 01 - opaque water
            # 02 - boat hull
            # 03 - opaque (default)
            # 04 - sky
            # 05 - skybox - sky/moon
            # 06 - skybox - clouds
            # 07 - skybox - horizon
            # 08 - decal - bottom 1
            # 09 - decal - bottom 2
            # 0A - decal - bottom 3
            # 0B - decal - static
            # 0C - decal - middle 1
            # 0D - decal - middle 2
            # 0E - decal - middle 3
            # 0F - decal - weapon impact
            # 10 - decal - top 1
            # 11 - decal - top 2
            # 12 - decal - top 3
            # 13 - multiplicative
            # 14 - banner/curtain
            # 15 - hair
            # 16 - underwater
            # 17 - transparent water
            # 18 - corona
            # 19 - window inside
            # 1A - window outside
            # 1B - blend/additive
            # 1C - viewmodel effect
            sort = f.u8()  # [13]

            unk3 = f.u16()  # [14]
            unk4 = f.u32()  # [16]
            unk5 = f.u8()   # [20]

            # usage:
            # 00 - <not in editor>
            # 01 - case
            # 02 - tools
            # 03 - door
            # 04 - floor
            # 05 - ceiling
            # 06 - root
            # 07 - interior wall
            # 08 - interior trim
            # 09 - exterior wall
            # 0A - exterior trim
            # 0B - window
            # 0C - poster
            # 0D - sign
            # 0E - core
            # 0F - damage
            # 10 - trench
            # 11 - fence
            # 12 - background
            # 13 - foliage
            # 14 - ground
            # 15 - liquid
            # 16 - road
            # 17 - rock
            # 18 - sky
            # 19 - barrel
            # 1A - crate
            usage = f.u8()  # [21]

            # 90 - no tile
            # 10 - tile both
            # 90 - horizontal
            # 90 - vertical
            colorMapTile = f.u8()  # [22]

            unk5_2 = f.u8()  # [23]

            # locales (flags):
            # 01 00 00 00 - case
            # 02 00 00 00 - test
            # 04 00 00 00 - tools
            # 08 00 00 00 - decal
            # 10 00 00 00 - Stalingrad
            # 20 00 00 00 - Stalingrad Winter
            # 40 00 00 00 - Kiev
            # 80 00 00 00 - IwoJima
            # 00 01 00 00 - Tinian
            # 00 02 00 00 - Tarawa
            # 00 04 00 00 - Hill 400
            # 00 08 00 00 - Normandy
            # 00 10 00 00 - Duhoc
            # 00 20 00 00 - Villers
            # 00 40 00 00 - Egypt
            # 00 80 00 00 - Libya
            # 00 00 01 00 - Tunisia
            # 00 00 02 00 - Industrial
            # 00 00 04 00 - Poland
            locales = f.u32()  # [24]
            width   = f.u16()   # [28]  (w and h?)
            height  = f.u16()  # [30]  (w and h?)

            unk8 = f.u32()  # [32]
            unk9 = f.u16()  # [36]

            # surfaceType:
            # 00 00 - <none>
            # 60 01 - asphalt
            # 10 00 - bark
            # 20 00 - brick
            # 30 00 - carpet
            # 40 00 - cloth
            # 50 00 - concrete
            # 60 00 - dirt
            # 70 00 - flesh
            # 80 00 - foliage
            # 90 00 - glass
            # A0 00 - grass
            # B0 00 - gravel
            # C0 00 - ice
            # D0 00 - metal
            # E0 00 - mud
            # F0 00 - paper
            # 00 01 - plaster
            # 10 01 - rock
            # 20 01 - sand
            # 30 01 - show
            # 40 01 - water
            # 50 01 - wood
            surfaceType = f.u16()  # [38]

            unk10 = f.read(7)  # [40]

            # platform:
            # 28 - <none>
            # 38 - PC/Xenon
            # ---
            # 28 - 0b101000 - <none>
            # 38 - 0b111000 - PC/Xenon, RGB enabled, alpha enabled
            # 30 - 0b110000 - PC/Xenon, RGB disabled, alpha enabled
            # 20 - 0b100000 - PC/Xenon, RGB disabled, alpha disabled
            # 28 - 0b101000 - PC/Xenon, RGB enabled, alpha disabled
            platform = f.u8()

            unk11 = f.read(8)  # [40]

            # see [50(4)] for detail map

            # ?  - color map*
            # 32 - [detail map]
            # ?  - norm map*
            # 12 - [spec map]
            # 12 - [cospow map]


            # 02 00 00 00 - cm only
            # 03 00 01 00 - cm + dm

            # 104: D9 - no norm map
            # 104: DB - norm map

            # offset to "colorMap"
            # cmUnk1 = f.u8():
            #     30 - no tile
            #     00 - both*
            #     20 - horizontal
            #     10 - vertical
            #     ---
            #     00 - auto filter*
            #     07 - anisotropic
            #     06 - bilinear
            #     02 - linear
            #     01 - nearest
            #     0A - trilinear
            # cmUnk2 = f.u8()
            # cmUnk3 = f.u8()
            # cmUnk4 = f.u8()
            # offset to "weapon_ppsh_c[.iwi]"

            # -------------

            techSetOffset = f.u32()  # [56]

            # ----------------

            f.seek(matOffset)

            matName = f.string()

            f.seek(colorMapOffset)

            cmName = f.string()

            f.seek(techSetOffset)

            techSet = f.string()

            # -----

            _minStringOffset = min(matOffset, colorMapOffset, techSetOffset)

            # if techSetId not in _c:
            #     _c[techSetId] = []

            # if techSet not in _c[techSetId]:
            #     _c[techSetId].append(techSet)

            # -----

            cmPath = getImagePath(cmName)

            assert isFile(cmPath), cmPath

            with openFile(cmPath) as f2:
                f2.skip(6)

                imageWidth  = f2.u16()
                imageHeight = f2.u16()

            assert imageWidth == width and imageHeight == height, (imageWidth, imageHeight, width, height)

            assert areSamePaths(getMaterialPath(matName), filePath), matName

            print('matName =', matName)
            print('cmName  =', cmName)
            print('techSet =', techSet)
            # print('unk1+2  =', formatHex(unk1 + unk2))
            print('_mso    =', _minStringOffset)

        print(' ')

    # print(toJson(_c))

    exit()

    with openFile(r"G:\Games\Call Of Duty 2\raw\materials\mtl_weapon_ppsh") as f:
        strsStart = 136

        nums = f.u32(strsStart // 4)

        raw = []

        for i, offset in enumerate(nums):
            offsetOffset = i * 4

            if offset < strsStart or offset >= f.getSize():
                raw.append(offset)
                continue

            f.seek(offset - 1)

            if f.u8() != 0:
                raw.append(offset)
                continue

            name = f.string()

            if raw:
                print(formatHex(struct.pack(f'<{ len(raw) }I', *raw)))
                raw = []

            print(offsetOffset, offset, name)

# test()

'''
54 00 00 00 - matOffset
65 00 00 00 - colorMapOffset

00 00 00 00 00 1B 01 01 00 00 00 00 00 00 60 00 00 00 00 00 04 00 04 00 00 00 00 00 00 00 00 00 01 00 00 00 22 51 12 28 04 00 00 00 01 00 00 00
00 00 00 00 0C 04 01 01 00 00 00 00 00 18 90 00 00 10 00 00 00 04 00 04 00 00 00 00 34 00 00 00 00 08 00 00 12 88 12 28 05 00 00 00 01 00 00 00 
50 00 00 00 - techSetOffset
44 00 00 00 50 00 00 00 

75 00 00 00 - "colorMap" offset
30 02 00 00
65 00 00 00 - image offset


0 162 mtl_weapon_ppsh
4 178 weapon_ppsh_c
00 00 00 00 03 03 01 01 00 00 00 00 00 00 10 00 00 00 00 00 00 02 00 02 00 00 00 00 00 00 D0 00 01 00 00 00 12 88 12 28 05 00 00 00 04 00 01 00
56 136 phong_replace_spec_detail
44 00 00 00 74 00 00 00

68 192 colorMap
00 02 00 00
76 178 weapon_ppsh_c

80 201 detailMap
00 02 00 00
88 211 metal_01

92 220 normalMap
00 03 00 00
100 230 ~weapon_ppsh_n-gggr

104 250 specularMap
00 04 00 00
112 262 ~weapon_ppsh_s-rgb&weapon_ppsh_cp-l-11

116 301 detailScale
'''

# ------------------------

def loadModelMaterial (filePath, model):
    if not isFile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    with openFile(filePath) as f:
        matOffset      = f.u32()
        colorMapOffset = f.u32()
        print(filePath, matOffset, colorMapOffset)

def parseModel (filePath):
    if not isFile(filePath):
        raise Exception(f'File does not exist: { filePath }')

    with openFile(filePath) as f:
        version = f.u16()

        if version != MODEL_VERSION:
            raise Exception(f'Unsupported model version: { version }')

        model = {
            'isHandsModel': getFileName(filePath).lower().startswith('viewmodel_hands'),
            'flags': f.u8(),
            'mins':  f.vec3(),
            'maxs':  f.vec3(),
        }

        lods = model['lods'] = []

        for _ in range(4):
            dist = f.f32()
            name = f.string()

            if not name:
                continue

            lods.append({
                'dist': dist,
                'name': name
            })

        model['colLod'] = f.i32()

        colSurfCount = max(0, f.i32())

        model['colSurfs'] = colSurfs = [ None ] * colSurfCount

        for i in range(colSurfCount):
            colTriCount = max(0, f.i32())

            colTris = [
                {
                    'normal': f.vec3(),
                    'dist':   f.f32(),
                    'sVec':   f.vec4(),
                    'tVec':   f.vec4()
                } for _ in range(colTriCount)
            ]

            colSurfs[i] = {
                'mins':      f.vec3(),
                'maxs':      f.vec3(),
                'boneIndex': f.i32(),
                'contents':  f.i32(),
                'surfFlags': f.i32(),
                'colTris':   colTris
            }

        matCount = f.u16()

        mats = []  # model['materials'] = 

        for i in range(matCount):
            mat = f.string()

            if not mat:
                break

            mats.append(mat)

        if not lods:
            raise Exception('Model does not have any lods')

        loadModelParts(getModelPartsPath(lods[0]['name']), model)

        for lod in lods:
            loadModelSurfs(getModelSurfPath(lod['name']), model)

        for mat in mats:
            loadModelMaterial(getMaterialPath(mat), model)

        # ignore bones' bbox
        for bone in model['parts']['bones']:
            mins = f.vec3()
            maxs = f.vec3()

        # print(toJson(model))
        # print(toJson(parts))

        return model

# weapons/<weapon>
# |-- xmodel/<modelPath>
# |   |-- xmodelparts/<model.lods[0]['name']>
# |   |-- materials/<model.materials[i]>
# |   |   |-- images/<imageName>.iwi
# |   |-- xmodelsurfs/<model.lods[i]['name']>
# |-- xanim/<animPath>


'''
- accuracy       - *.accu text file with \x00 byte at the end
- aitype         - *.gsc text files
- animscripts    - *.gsc text files
- animtrees      - *.atr structured text files
- character      - *.gsc text files
- codescripts    - *.gsc text files
- fonts          - bin files
- fx             - *.csv, *.efx structured text files
- images         - *.iwi files
- info           - inline config text files (LOCDMGTABLE)
- lights         - bin files
- maps           - *.d3dbsp, *.gsc, *.csv files
- materials      - a lot of custom files including *.hlsl
- materials_dx7  - *.tech, *.techset text files (gsc or HLSL?)
- mptype         - *.gsc text files
- radiant        - *.txt specific text file
- rumble         - inline config text files (RUMBLE)
- scriptdebugger - nevermind
- shock          - *.shock text files with list of cvars
- sound          - *.wav, *.mp3 files
- soundaliases   - *.spkrmap, *.def, *.csv text files
- sun            - *.sun text files with list of cvars
- ui             - *.menu, *.txt, *.h, *.cfg text files
- vehicles       - inline config text files (VEHICLEFILE)
- video          - *.roq bin files
- weapons        - inline config text files (WEAPONFILE)
- xanim          - bin files
- xmodel         - bin files
- xmodelalias    - *.gsc text files
- xmodelparts    - bin files
- xmodelsurfs    - bin files
'''
def parseWeapons (rootDir):
    weaponsDir = joinPath(rootDir, 'weapons')

    for filePath in iterFiles(weaponsDir, True):
        signature = readBin(filePath, len(WEAPON_FILE_SIGNATURE))

        if signature != WEAPON_FILE_SIGNATURE:
            continue

        print(filePath)
        parseWeapon(filePath)
        print(' ')

    print(toJson(_c))

def main ():
    # for filePath in iterFiles(MODELS_DIR, True):
    #     print(filePath)
    #     print('-' * 20)
    #     parseModel(filePath)
    #     print(' ')

    # exit()

    parseWeapon(joinPath(WEAPONS_DIR, 'sp', 'ppsh'))
    # parseWeapons(RAW_DIR)
    exit()

    if 1:
        for gameDir in [
            r'G:\Games\Call Of Duty 2',
            r'G:\Games\_COD_IWI\04. Call of Duty - Modern Warfare',
            r'G:\Games\_COD_IWI\05. Call of Duty - World at War',
            r'G:\Games\_COD_IWI\06. Call of Duty - Modern Warfare 2',
            r'G:\Games\_COD_IWI\07. Call of Duty - Black Ops',
            r'G:\Games\_COD_IWI\08. Call Of Duty - Modern Warfare 3',
            r'G:\Games\_COD_IWI\09. Call of Duty - Black Ops 2',
        ]:
            for filePath in iterFiles(gameDir, includeExts=[ '.iwi' ]):
                print(filePath)

                image = IWI.fromFile(filePath)

                print(' ')

                # sys.exit()
    else:
        # image = IWI.fromFile(r'G:\Games\_COD_IWI\09. Call of Duty - Black Ops 2\base\c522e74b.iwi')
        # image = IWI.fromFile(r'G:\Games\Call Of Duty 2\raw\images\popups_goldline.iwi')
        # image = IWI.fromFile(r'G:\Games\Call Of Duty 2\raw\images\logo_cod2_sm.iwi')
        image = IWI.fromFile(r'G:\Games\_COD_IWI\04. Call of Duty - Modern Warfare\falloff_center.iwi')
        # image = IWI.fromFile(r'G:\Games\Call Of Duty 2\raw\images\~zbrushtest_corner_normal01-gggr.iwi')
    


if __name__ == '__main__':
    main()



'''

G:\Games\_COD_IWI\05. Call of Duty - World at War\cod.iwi
GA16 195 722x304 1 [439004, 439004, 439004, 439004] [0, 0, 0, 438976] 439004

hasOdd
hasNPO2
hasOneMip

LittleEndian();

typedef float f32;
typedef double f64;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef char i8;
typedef short i16;
typedef int i32;

local int DXTVERSION = 0;



typedef struct
{
    u8 start_I;
    u8 start_W;
    u8 start_i;
    u8 version;
    u8 DXTformat; //0x0b -> DXT1? | 0x0d -> DXT5?
    u8 flag;
    u16 width;
    u16 height;
    u16 u3;
    u32 lol[4];

    if( start_I != 73 || start_W != 87 || start_i != 105 )
        return 0;
    else if( version != 0x05 )
        return -2;
    
    if( DXTformat == 0x0b )
        DXTVERSION = 1;
    else if( DXTformat == 0x0d )
        DXTVERSION = 5;
    else
        return -3;

    if( u3 != 1 )
        return -4;
    else if( flag != 1 && flag != 0 )
        return -5;
} HEADER;

typedef struct
{
    u16 color0;
    u16 color1;
    u8 index[4];
} COLORBLOCK;

typedef struct
{
    COLORBLOCK cb;
} DXT1;

typedef struct
{
    u8 alpha[8];
    COLORBLOCK cb;
} DXT3;

typedef struct
{
    u8 alpha1;
    u8 alpha2;
    u8 alpha_indices[6];
    COLORBLOCK cb;
} DXT5;

local int getSize( local int width , local int height , local int depth )
{
    return ( ( width + 3 ) / 4 ) * ( ( height + 3 ) / 4 );// * ( DXTVERSION == 0 ? 8 : 16 );   
}

local int getMipmapCount( local int width , local int height )
{
    local int max = width > height ? width : height;
    local int count = 0;
    local int i = 0;

    for( i = 0 ; max >> i > 0 ; i++ )
    {
        count++;
    }

    return count;
}

void readMipmap( local int count )
{
    if( DXTVERSION == 1 )
        DXT1 blocks[count] <optimize=false>;
    else if( DXTVERSION == 3 )
        DXT3 blocks[count] <optimize=false>;
    else if( DXTVERSION == 5 )
        DXT5 blocks[count] <optimize=false>;
}

typedef struct
{
    HEADER header;

    local int numMipmaps = getMipmapCount( header.width , header.height );
    
    Printf( "numMipmaps: %d\n" , numMipmaps );

    while( numMipmaps > 0 )
    {
        numMipmaps--;

        readMipmap( getSize( header.width >> numMipmaps , header.height >> numMipmaps , 4 ) );
    }
} IWI;

IWI x; 


struct IWIHeader{
    BYTE DTX_Type;
    BYTE flags;
    short x;
    short y;
    short misc;
    int blockoffsets[4];
};

struct IWIHeader_MW2{ // mw3 also
    short dunno;
    short dunno1;
    BYTE DTX_Type;
    BYTE flags;
    short x;
    short y;
    short misc;
    int blockoffsets[5];
    int dunno2;
};


'''