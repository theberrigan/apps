from ...common import bfw
from ...common.types import *
from ...common.consts import *

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



class Quaternion:
    def __init__ (self, x : float, y : float, z : float, w : float):
        self.x : float = x
        self.y : float = y
        self.z : float = z
        self.w : float = w

    def __neg__ (self) -> Self:
        return Quaternion(-self.x, -self.y, -self.z, -self.w)

    # invert
    def conjugate (self) -> Self:
        self.x = -self.x
        self.y = -self.y
        self.z = -self.z

        return self

    def dot (self, q2 : Self) -> float:
        return self.x * q2.x + self.y * q2.y + self.z * q2.z + self.w * q2.w


class AnimKeyFrameFlag:
    Rotation    = 1
    Translation = 2


class AnimBlock:
    def __init__ (self):
        self.name        : TStr                          = None
        self.hierarchies : Dict[str, AnimBlendHierarchy] = {}

    def addHierarchy (self, hierarchy : 'AnimBlendHierarchy'):
        assert hierarchy.name
        assert hierarchy.name not in self.hierarchies

        self.hierarchies[hierarchy.name] = hierarchy


class KeyFrame:
    def __init__ (self):
        self.rotation  : Opt[Quaternion] = None  # CQuaternion rotation
        self.deltaTime : TFloat          = None  # float deltaTime -- relative to previous key frame


class KeyFrameTranslation (KeyFrame):
    def __init__ (self):
        super().__init__()

        self.translation : TVec3 = None  # CVector translation;


class AnimBlendSequence:
    def __init__ (self):
        self.name        : TStr                 = None
        self.prevSibling : TInt                 = None  # int16 boneTag
        self.nextSibling : TInt                 = None
        self._unk_44_4   : TInt                 = None  # TODO: unknown 4 bytes when size is 48 instead of 44
        self.frameCount  : TInt                 = None
        self.type        : int                  = 0     # int32 type (see AnimKeyFrameFlag)
        self.keyFrames   : Opt[List[KeyFrame]]  = None  # void *keyFrames

    def setFrameCount (self, frameCount : int, hasTranslation : bool):
        if hasTranslation:
            self.type      = self.type | AnimKeyFrameFlag.Rotation | AnimKeyFrameFlag.Translation
            self.keyFrames = Array(frameCount, KeyFrameTranslation)

        else:
            self.type      = self.type | AnimKeyFrameFlag.Rotation
            self.keyFrames = Array(frameCount, KeyFrame)

        self.frameCount = frameCount

    def getKeyFrame (self, index : int) -> Any:
        return self.keyFrames[index]

    def removeQuatFlips (self):
        if self.frameCount < 2:
            return

        prevRot = self.getKeyFrame(0).rotation

        for i in range(1, self.frameCount):
            frame = self.getKeyFrame(i)

            if prevRot.dot(frame.rotation) < 0:
                frame.rotation = -frame.rotation

            prevRot = frame.rotation


class AnimBlendHierarchy:
    def __init__ (self):
        self.name          : TStr                    = None
        self.sequenceCount : int                     = 0
        self.sequences     : List[AnimBlendSequence] = []
        self.totalDuration : int                     = 0  # float totalLength

    def removeQuatFlips (self):
        for seq in self.sequences:
            seq.removeQuatFlips()

    def calcTotalTime (self):
        self.totalDuration = 0

        for seq in self.sequences:
            if seq.frameCount == 0:
                continue

            self.totalDuration = max(self.totalDuration, seq.getKeyFrame(seq.frameCount - 1).deltaTime)

            for i in range(seq.frameCount - 1, 0, -1):
                kf1 = seq.getKeyFrame(i)
                kf2 = seq.getKeyFrame(i - 1)

                kf1.deltaTime -= kf2.deltaTime


def roundSize (value : int) -> int:
    if value & 3:
        value += (4 - (value & 3))

    return value


class IFPHeader:
    def __init__ (self):
        self.signature : TBytes = None
        self.size      : TInt   = None

    @classmethod
    def read (cls, f : Reader) -> Self:
        header = cls()

        assert f.remaining() >= 8

        header.signature = f.read(4)
        header.size      = roundSize(f.u32())

        return header


# https://gta.fandom.com/wiki/IFP
# https://web.archive.org/web/20220616154305/https://gtamodding.ru/wiki/IFP
class IFPReader:
    @classmethod
    def fromFile (cls, filePath : str):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData = readBin(filePath)
        reader  = MemReader(rawData, filePath)

        return cls().read(reader)

    def read (self, f : Reader) -> AnimBlock:
        packHeader = IFPHeader.read(f)

        assert packHeader.signature == b'ANPK'

        infoHeader = IFPHeader.read(f)

        assert infoHeader.signature == b'INFO'

        nameSize = infoHeader.size - 4  # 4 is animCount size

        animCount = f.i32()

        block = AnimBlock()

        block.name = f.string(size=nameSize).strip().lower()  # internal file name used in the script

        for i in range(animCount):
            hierarchy = AnimBlendHierarchy()

            nameHeader = IFPHeader.read(f)

            assert nameHeader.signature == b'NAME'

            hierarchy.name = f.string(size=nameHeader.size).strip().lower()

            dganHeader = IFPHeader.read(f)

            assert dganHeader.signature == b'DGAN'

            infoHeader = IFPHeader.read(f)

            assert infoHeader.signature == b'INFO'

            hierarchy.sequenceCount = f.i32()

            _unk = f.i32()

            hierarchy.sequences = Array(hierarchy.sequenceCount, AnimBlendSequence)

            for seq in hierarchy.sequences:
                cpanHeader = IFPHeader.read(f)

                assert cpanHeader.signature == b'CPAN'

                animHeader = IFPHeader.read(f)

                assert animHeader.signature == b'ANIM'

                # TODO: replace " " with "_"?
                seq.name = f.string(size=28).strip().lower()

                frameCount = f.i32()

                _unk = f.read(4)

                assert _unk == b'\x00\x00\x00\x00'

                seq.nextSibling = f.i32()
                seq.prevSibling = f.i32()

                # TODO: wtf? Maybe nextSibling and prevSibling are not they are when size is 48!
                if animHeader.size == 48:
                    seq._unk_44_4 = f.i32()

                if frameCount == 0:
                    continue

                hasScale       = False
                hasTranslation = False

                infoHeader = IFPHeader.read(f)

                match infoHeader.signature:
                    case b'KRTS':
                        hasScale = True
                        seq.setFrameCount(frameCount, True)

                    case b'KRT0':
                        hasTranslation = True
                        seq.setFrameCount(frameCount, True)

                    case b'KR00':
                        seq.setFrameCount(frameCount, False)

                    case _:
                        raise Exception('Unknown key frame type')

                for j in range(frameCount):
                    if hasScale:
                        kf : KeyFrameTranslation = seq.getKeyFrame(j)

                        kf.rotation    = Quaternion(*f.vec4()).conjugate()
                        kf.translation = f.vec3()
                        _scale         = f.vec3()  # ignored
                        kf.deltaTime   = f.f32()   # absolute time here

                    elif hasTranslation:
                        kf : KeyFrameTranslation = seq.getKeyFrame(j)

                        kf.rotation    = Quaternion(*f.vec4()).conjugate()
                        kf.translation = f.vec3()
                        kf.deltaTime   = f.f32()  # absolute time here

                    else:
                        kf : KeyFrame = seq.getKeyFrame(j)

                        kf.rotation    = Quaternion(*f.vec4()).conjugate()
                        kf.deltaTime   = f.f32()  # absolute time here

            hierarchy.removeQuatFlips()
            hierarchy.calcTotalTime()

            block.addHierarchy(hierarchy)

        return block



def _test_ ():
    for filePath in iterFiles(GAME_DIR, True, [ IFP_EXT ]):
        print(filePath)
        _ifp = IFPReader.fromFile(filePath)
        print(' ')



__all__ = [
    'IFPReader',
    'AnimBlock',

    '_test_',
]



if __name__ == '__main__':
    _test_()
