from hashlib import md5
import re

# pip install Pillow
from PIL import Image as PILImage

from ...common import bfw
from ...common.types import *
from ...common.consts import *

# from ..dxt import DXT
from ..rw import RWStream, PluginId, Platform

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



class Texture:
    @classmethod
    def createKey (cls, name : str) -> str:
        return name.lower()

    def __init__ (self):
        self.name         : TStr    = None
        self.maskName     : TStr    = None
        self.hasAlpha     : TBool   = None
        self.width        : TInt    = None
        self.height       : TInt    = None
        self.pxFormat     : TInt    = None  # see TexturePxFormat
        self.depth        : TInt    = None  # 16 - DXT1/3, 24 - RGB, 32 - RGBA
        self.channelCount : TInt    = None
        self.filterType   : TInt    = None  # see TextureFilterType
        self.addrU        : TInt    = None  # see TextureAddressingType
        self.addrV        : TInt    = None  # see TextureAddressingType
        self.compType     : TInt    = None  # see TextureCompType
        self.pxCount      : TInt    = None
        self.isDXT        : TBool   = None  # if compType == DXT1 | DXT3
        self.data         : TBArray = None  # RGB(A) (24/32 bit)

        self.dataHash     : TStr    = None  # md5 hash of self.data
        self.texHash      : TStr    = None  # md5 hash of entire self object (mostly useless)

    def calcHashes (self):
        self.calcDataHash()
        self.calcTexHash()

    def calcDataHash (self):
        self.dataHash = md5(self.data).hexdigest().lower()

    def calcTexHash (self):
        if not self.dataHash:
            self.calcDataHash()

        key = ','.join([
            str(self.name),
            str(self.maskName),
            str(self.hasAlpha),
            str(self.width),
            str(self.height),
            str(self.pxFormat),
            str(self.depth),
            str(self.channelCount),
            str(self.filterType),
            str(self.addrU),
            str(self.addrV),
            str(self.compType),
            str(self.pxCount),
            str(self.isDXT),
            str(self.dataHash)
        ])

        key = key.lower().encode('utf-8')

        self.texHash = md5(key).hexdigest().lower()


class TXD:
    @classmethod
    def createKey (cls, path : str) -> str:
        return getAbsPath(path).lower()

    def __init__ (self):
        self.path     : TStr                    = None
        self.name     : TStr                    = None
        self.key      : TStr                    = None
        self.textures : Opt[Dict[str, Texture]] = {}

    def add (self, tex : Texture):
        self.textures[tex.name] = tex

    # DO NOT THROW!
    def getTexture (self, texName : str, silent : bool = False):
        texName = texName.lower()

        tex = self.textures.get(texName)

        if not tex and not silent:
            printW('Texture is not found:', texName)

        return tex

    def __iter__ (self):
        return iter(self.textures.values())


class TXDStore:
    def __init__ (self):
        self.textureDicts   : Dict[str, TXD]     = {}
        self.textureCache   : Dict[str, Texture] = {}
        self.cachedTxdNames : List[str]          = []

    def add (self, txd : TXD) -> TXD:
        if not txd:
            return txd

        key = TXD.createKey(txd.path)

        if key not in self.textureDicts:
            self.textureDicts[key] = txd

        return self.textureDicts[key]

    def loadTxd (self, path : str, metaOnly : bool = False) -> TXD:
        txd = self.textureDicts.get(TXD.createKey(path))

        if not txd:
            txd = TXDReader.fromFile(path, metaOnly)

            if txd is None:
                raise Exception(f'Failed to load TXD: { path }')

            self.add(txd)

        return txd

    def loadAllTxd (self, rootDir : str, metaOnly : bool = False):
        for filePath in iterFiles(rootDir, True, [ TXD_EXT ]):
            self.loadTxd(filePath, metaOnly)

    def cacheTxdTextures (self, path : str, metaOnly : bool = False):
        txdKey = TXD.createKey(path)

        if txdKey in self.cachedTxdNames:
            return

        txd = self.loadTxd(path, metaOnly)

        self.cachedTxdNames.append(txdKey)

        for tex in txd:
            texKey = Texture.createKey(tex.name)

            if texKey in self.textureCache:
                printW(f'Texture with name "{ tex.name }" already cached')

            self.textureCache[texKey] = tex

    def getTexture (self, name : str) -> Texture:
        tex = self.textureCache.get(Texture.createKey(name))

        if tex is None:
            raise Exception(f'Texture "{ name }" is not found in cache')

        return tex

    # get texture from txd with textureCache fallback
    # txd = 'airport' | 'models/gta3/airport.txd' | r'C:/.../models/gta3/airport.txd' | TXD
    def getTextureFromTxd (self, txd : Union[str, TXD], texName : str, metaOnly : bool = False, allowFallback : bool = True) -> Texture:
        if isinstance(txd, str):
            if not txd.lower().endswith('.txd'):
                assert re.match(r'^[a-z_\d]+$', txd, flags=re.I)

                txd = f'models/gta3/{ txd }.txd'

            if not isAbsPath(txd):
                txd = joinPath(GAME_DIR, txd)

            txd = self.loadTxd(getAbsPath(txd), metaOnly=metaOnly)

        tex = txd.getTexture(texName)

        if not tex and allowFallback:
            tex = self.getTexture(texName)

        if tex is None:
            raise Exception(f'Texture "{ texName }" is not found in ether TXD or texture cache')

        return tex

    def loadImage (self, filePath : str, texName : Opt[str] = None) -> Texture:
        txdKey = TXD.createKey(filePath)

        if texName:
            texKey = texName.lower()
        else:
            texKey = '@' + getFileName(filePath).lower()

        if txdKey in self.cachedTxdNames:
            return self.textureCache[texKey]

        self.cachedTxdNames.append(txdKey)

        # --------------------------------------

        image = PILImage.open(filePath)

        resolution = image.width * image.height

        image = image.convert('RGBA')
        channelCount = 4

        extrema = image.getextrema()

        if extrema[3] == (255, 255):
            image = image.convert('RGB')
            channelCount = 3

        tex = Texture()

        tex.name         = texKey
        tex.maskName     = None
        tex.hasAlpha     = channelCount == 4
        tex.width        = image.width
        tex.height       = image.height
        tex.pxFormat     = TexturePxFormat.Default
        tex.depth        = 8 * channelCount
        tex.channelCount = channelCount
        tex.filterType   = TextureFilterType.Linear
        tex.addrU        = TextureAddressingType.Wrap
        tex.addrV        = TextureAddressingType.Wrap
        tex.compType     = TextureCompType.No
        tex.pxCount      = resolution
        tex.isDXT        = False
        tex.data         = image.tobytes()

        assert len(tex.data) == (resolution * channelCount)

        tex.calcHashes()

        # -------------------------

        assert texKey not in self.textureCache

        self.textureCache[texKey] = tex

        return tex


# https://wiki.multimedia.cx/index.php/TXD
class TXDReader:
    @classmethod
    def fromFile (cls, filePath : str, metaOnly : bool = False) -> 'TXD':
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData = readBin(filePath)
        reader  = MemReader(rawData, filePath)
        stream  = RWStream(reader)

        return cls().read(stream, metaOnly)

    def __init__ (self):
        self.metaOnly : Opt[bool] = None

    def read (self, f : RWStream, metaOnly : bool) -> 'TXD':
        self.metaOnly = metaOnly

        txd = TXD()

        txd.path = f.getFilePath()
        txd.name = getFileName(f.getFilePath()).lower()
        txd.key  = TXD.createKey(txd.path)

        if not f.findChunk(PluginId.TextureDict):
            raise Exception('Failed to find texture dict chunk')

        if not f.findChunk(PluginId.Struct):
            raise Exception('Failed to find texture dict chunk struct')

        textureCount = f.i32()

        for i in range(textureCount):
            header = f.findChunk(PluginId.TextureNative)

            if not header:
                raise Exception('Failed to find native texture chunk')

            dataEnd = f.tell() + header.dataSize

            tex = self.readNativeTexture(f)

            if tex:
                txd.add(tex)

            f.seek(dataEnd)

        return txd

    def readNativeTexture (self, f : RWStream) -> Opt[Texture]:
        if not f.findChunk(PluginId.Struct):
            raise Exception('Failed to find native texture struct')

        platform = f.u32()

        # just skip unused intro.txd
        if platform == Platform.FourCCPS2:
            return None

        if platform != Platform.D3D8:
            raise Exception(f'Unsupported platform: { platform }')

        tex = Texture()

        info1        = f.u32()
        tex.name     = f.string(32).lower()  # TODO: replace spaces with "_"
        tex.maskName = f.string(32).lower() or None
        info2        = f.u32()        # uint32 format = stream->readU32();
        tex.hasAlpha = bool(f.i32())  # bool32 hasAlpha = stream->readI32();  # C888 - false, C8888 - true, DXT1 - both, DXT3 - true
        tex.width    = f.u16()        # int32 width = stream->readU16();
        tex.height   = f.u16()        # int32 height = stream->readU16();
        tex.depth    = f.u8()         # int32 depth = stream->readU8();     # 8 - Pal8[C888/C8888], 16 - DXT1/3, 32 - C888(BGRA)
        _mipCount    = f.u8()         # int32 numLevels = stream->readU8();
        _rasterType  = f.u8()         # int32 type = stream->readU8();  # Raster::Type::Texture = 4
        tex.compType = f.u8()         # int32 compression = stream->readU8();

        tex.filterType = info1 & 0xFF          # see TextureFilterType
        tex.addrU      = (info1 >> 8) & 0xF    # see TextureAddressingType
        tex.addrV      = (info1 >> 12) & 0xF   # see TextureAddressingType
        tex.isDXT      = False
        tex.pxCount    = tex.width * tex.height
        tex.pxFormat   = info2 & 0xF00         # see PixelFormat
        palFormat      = info2 & 0x6000
        _flags         = info2 & 0xF8          # always 0
        _hasMips       = bool(info2 & 0x8000)
        _autoMips      = bool(info2 & 0x1000)  # always False

        # Pal8[C888 | C8888]; depth: 8
        if tex.compType == TextureCompType.No and palFormat == 0x2000:
            self.readPAL8(f, tex)

        # BGRA (C888); depth: 32; hasAlpha: False
        elif tex.compType == TextureCompType.No and tex.pxFormat == TexturePxFormat.C888:
            self.readBGRA8(f, tex)

        # DXT1[C565 | C1555]; depth: 16; hasAlpha: True/False
        elif tex.compType == TextureCompType.DXT1:
            self.readDXT1(f, tex)

        # DXT3[C4444]; depth: 16; hasAlpha: True
        elif tex.compType == TextureCompType.DXT3:
            self.readDXT3(f, tex)

        else:
            raise Exception('Unknown texture format')

        if not self.metaOnly:
            tex.calcHashes()

        return tex

    def readMip1 (self, f : RWStream) -> bytearray:
        size = f.u32()

        return f.ba(size)

    # TODO: is this also BGRA?
    def readPAL8 (self, f : RWStream, tex : Texture) -> Texture:
        tex.isDXT = False

        if tex.pxFormat == TexturePxFormat.C888:
            tex.channelCount = 3
            tex.hasAlpha     = False
            tex.depth        = 24
        else:
            tex.channelCount = 4
            tex.hasAlpha     = True
            tex.depth        = 32

        if not self.metaOnly:
            tex.data = bytearray(tex.pxCount * tex.channelCount)

            palette = f.ba(256 * 4)  # 256 RGBA colors
            indices = self.readMip1(f)

            # C888/C8888 (drop alpha for C888)
            for i in range(tex.pxCount):
                index = indices[i]

                tex.data[i * tex.channelCount + 0] = palette[index * 4 + 0]
                tex.data[i * tex.channelCount + 1] = palette[index * 4 + 1]
                tex.data[i * tex.channelCount + 2] = palette[index * 4 + 2]

                if tex.channelCount == 4:
                    tex.data[i * tex.channelCount + 3] = palette[index * 4 + 3]

        return tex

    def readBGRA8 (self, f : RWStream, tex : Texture) -> Texture:
        tex.channelCount = 3
        tex.hasAlpha     = False
        tex.depth        = 24
        tex.isDXT        = False

        if not self.metaOnly:
            tex.data = bytearray(tex.pxCount * 3)  # RGB

            bgra = self.readMip1(f)

            # Drop alpha and convert BGR to RGB
            for i in range(tex.pxCount):
                tex.data[i * 3 + 0] = bgra[i * 4 + 2]
                tex.data[i * 3 + 1] = bgra[i * 4 + 1]
                tex.data[i * 3 + 2] = bgra[i * 4 + 0]

        return tex

    def readDXT1 (self, f: RWStream, tex: Texture) -> Texture:
        tex.isDXT = True

        if not self.metaOnly:
            tex.data = self.readMip1(f)
            # TODO: set channel count, hasAlpha

        return tex

    def readDXT3 (self, f: RWStream, tex: Texture) -> Texture:
        tex.isDXT = True

        if not self.metaOnly:
            tex.data = self.readMip1(f)
            # TODO: set channel count, hasAlpha

        return tex



# dxtX  -> keep dxt + raw deflate
# pal8  -> RGB/RGBA + raw deflate
# BGRA8 -> RGB/RGBA + raw deflate
# NOTE: may be dxt textures supported only on desktop browsers
# https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/Compressed_texture_formats
def _test_ ():
    for filePath in iterFiles(GAME_DIR, True, [ TXD_EXT ]):
        print(filePath)
        _txd = TXDReader.fromFile(filePath, False)
        print(' ')

    # totalCount  = 12267   | 12267
    # totalSize   = 184.7MB | 116.2MB
    # dupsCount   = 5625    | 5625
    # dupsSize    = 87.9MB  | 61.5MB
    # uniqueCount = 6642    | 6642
    # uniqueSize  = 96.8MB  | 54.6MB



__all__ = [
    'Texture',
    'TXD',
    'TXDStore',
    'TXDReader',

    '_test_',
]



if __name__ == '__main__':
    _test_()
