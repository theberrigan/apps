from ...common import bfw
from ...common.consts import SPRITES_DIR, HL_PALETTE_SIZE
from ...maths.vec3 import Vec3
from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



# msprite_t
class Sprite:
    def __init__ (self):
        # dsprite_hl_t
        self.version    = None  # int         version        -- current version 2
        self.angleType  = None  # angletype_t type           -- camera align (SpriteAngleType)
        self.texFormat  = None  # drawtype_t  texFormat      -- rendering mode (SpriteDrawType)
        self.radius     = None  # int         boundingradius -- quick face culling
        self.bounds     = None  # int         bounds[2]      -- mins/maxs
        self.frameCount = None  # int         numframes      -- including groups
        self.faceCull   = None  # facetype_t  facetype       -- cullface (Xash3D ext) (SpriteFaceType)
        self.syncType   = None  # synctype_t  synctype       -- animation synctype (SpriteSyncType)

        self.bbMin : Vec3 | None = None
        self.bbMax : Vec3 | None = None

        self.palette : bytes | None = None  # raw palette bytes of size HL_PALETTE_SIZE
        self.frames : list | None = None

    @classmethod
    def fromFile (cls, filePath : str) -> 'Sprite':
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._read(f)

    @classmethod
    def fromBuffer (cls, data : bytes, filePath : str | None = None) -> 'Sprite':
        return cls._read(MemReader(data, filePath))

    @classmethod
    def _read (cls, f : Reader) -> 'Sprite':
        # assert reader.getSize() >= 4 + Graph.SIZE
        sprite = Sprite()

        cls._readHeader(f, sprite)
        cls._readPalette(f, sprite)
        cls._readFrames(f, sprite)

        return sprite

    @classmethod
    def _readHeader (cls, f : Reader, sprite : 'Sprite') -> None:
        assert f.remaining() >= SPRITE_HEADER_SIZE

        signature = f.read(4)

        assert signature == SPRITE_SIGNATURE

        sprite.version = f.i32()

        assert sprite.version == SPRITE_VERSION

        sprite.angleType  = f.i32()  # SpriteAngleType
        sprite.texFormat  = f.i32()  # SpriteDrawType
        sprite.radius     = f.i32()
        sprite.bounds     = f.i32(2)
        sprite.frameCount = f.i32()
        sprite.faceCull   = f.i32()  # SpriteFaceType
        sprite.syncType   = f.i32()  # SpriteSyncType

        assert SpriteAngleType.hasValue(sprite.angleType)
        assert SpriteDrawType.hasValue(sprite.texFormat)
        assert SpriteFaceType.hasValue(sprite.faceCull)
        assert SpriteSyncType.hasValue(sprite.syncType)

        bounds = sprite.bounds

        sprite.bbMin = [
            -bounds[0] * 0.5,
            -bounds[0] * 0.5,
            -bounds[1] * 0.5
        ]

        sprite.bbMax = [
            bounds[0] * 0.5,
            bounds[0] * 0.5,
            bounds[1] * 0.5
        ]

        assert sprite.frameCount > 0
        assert f.tell() == SPRITE_HEADER_SIZE

    @classmethod
    def _readPalette (cls, f : Reader, sprite : 'Sprite') -> None:
        assert f.remaining() >= (2 + HL_PALETTE_SIZE)

        colorCount = f.i16()

        assert colorCount == 256

        # TODO: convert palette to ok format according to sprite.texFormat (engine/client/gl_sprite.c:249)
        sprite.palette = f.read(HL_PALETTE_SIZE)

    @classmethod
    def _readFrames (cls, f : Reader, sprite : 'Sprite') -> None:
        # assert f.remaining() >= (2 + HL_PALETTE_SIZE)
        frameType = f.i32()

        assert SpriteFrameType.hasValue(frameType)

        sprite.frames = frames = [ None ] * sprite.frameCount

        for i in range(sprite.frameCount):
            if frameType == SpriteFrameType.Single:
                frames[i] = cls._readFrame(f, sprite)
            else:
                pass

    @classmethod
    def _readFrame (cls, f : Reader, sprite : 'Sprite'):
        # dspriteframe_t
        origin = f.i32(2)  # int origin[2]
        width  = f.i32()   # int width
        height = f.i32()   # int height

        print(origin, width, height); exit()

        return None



# noinspection PyUnusedLocal
def _test_ ():
    for filePath in iterFiles(SPRITES_DIR, True, [ SPRITE_EXT ]):
        print(filePath, '\n')

        sprite = Sprite.fromFile(filePath)
        # sprite = Sprite.fromBuffer(readBin(filePath), filePath)

        print(' ')



__all__ = [
    'Sprite',

    '_test_',
]



if __name__ == '__main__':
    _test_()
