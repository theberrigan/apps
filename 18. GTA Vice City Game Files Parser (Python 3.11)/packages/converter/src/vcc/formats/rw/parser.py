from ...common import bfw
from ...common.types import *

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum

# https://gta.fandom.com/wiki/RenderWare_binary_stream_file



# TODO: Check alwaysCallbacks for each plugin
class RWStreamPluginManager:
    @classmethod
    def create (cls, plugins : Opt[Any] = None) -> Self:
        manager = cls()

        if plugins:
            for objectClass, pluginClass in plugins:
                manager.add(objectClass, pluginClass)

        return manager

    def __init__ (self):
        self.map : List[Tuple[Tuple[Any, int], Any]] = []

    def add (self, objClass : Any, pluginClass : Any) -> Opt[Any]:
        return self.map.append(((objClass, pluginClass.Id), pluginClass))

    def get (self, objClass : Any, pluginId : int) -> Opt[Any]:
        # compound key
        key = (objClass, pluginId)

        for k, pluginClass in self.map:
            if k == key:
                return pluginClass

        return None



class RWStream:
    def __init__ (self, f : Reader, consumer : Opt[Any] = None, plugins : Opt[Any] = None):
        self.f        : Reader                = f
        self.consumer : Any                   = consumer
        self.plugins  : RWStreamPluginManager = RWStreamPluginManager.create(plugins)

    def decodeVersion (self, version : int) -> int:
        if version & 0xFFFF0000:
            return ((version >> 14 & 0x3FF00) + 0x30000) | (version >> 16 & 0x3F)

        return version << 8

    def decodeBuild (self, version : int) -> int:
        if version & 0xFFFF0000:
            return version & 0xFFFF

        return 0

    # RwStreamFindChunk
    def findChunk (self, kind : int) -> RWStreamHeader | None:
        while True:
            header = self.readHeader()

            if not header or header.kind == PluginId.NA:
                return None

            if header.kind == kind:
                return header

            self.f.skip(header.dataSize)

    # readChunkHeaderInfo
    def readHeader (self) -> RWStreamHeader | None:
        if self.remaining() < 12:
            return None

        kind    = self.i32()  # int32 type
        size    = self.i32()  # int32 size
        version = self.u32()  # uint32 id

        header = RWStreamHeader()

        header.kind      = kind
        header.dataSize  = size
        header.version   = self.decodeVersion(version)
        header.build     = self.decodeBuild(version)
        header.dataStart = self.tell()
        header.dataEnd   = header.dataStart + size

        return header

    def readExtension (self, obj : Any) -> bool:
        extensionHeader = self.findChunk(PluginId.Extension)

        if not extensionHeader:
            return False

        while self.tell() < extensionHeader.dataEnd:
            pluginHeader = self.readHeader()

            if not pluginHeader:
                return False

            plugin = self.plugins.get(obj.__class__, pluginHeader.kind)

            if plugin:
                readFn : Callable[[RWStream, int, Any], bool] = plugin.read

                if not readFn(self, pluginHeader.dataSize, obj):
                    raise Exception('Failed to read plugin data')

                if self.tell() != pluginHeader.dataEnd:
                    raise Exception(f'Plugin must read every single byte from its buffer: { plugin.__name__ }')

                if hasattr(plugin, 'alwaysCallback'):
                    alwaysCallbackFn : Callable[[RWStream, Any], bool] = plugin.alwaysCallback

                    if alwaysCallbackFn and not alwaysCallbackFn(self, obj):
                        raise Exception(f'Failed to run always callback: { plugin.__name__ }.alwaysCallback')
            else:
                # -----------------------------------------------------------------
                assert pluginHeader.kind != 0x105 or pluginHeader.dataSize == 4
                # -----------------------------------------------------------------
                if PluginId.hasValue(pluginHeader.kind):
                    pluginName = PluginId.getKey(pluginHeader.kind)
                    pluginName = f'{PluginId.__name__}.{pluginName} = '
                else:
                    pluginName = ''

                objType = type(obj).__name__

                raise Exception(
                    f'Plugin not found: { pluginName }0x{pluginHeader.kind:X} ' +
                    f'(data size: { pluginHeader.dataSize }; obj type: { objType })'
                )

            self.seek(pluginHeader.dataEnd)

        if self.tell() != extensionHeader.dataEnd:
            raise Exception('Extension must be read completely')

        return True

    def i8 (self, *args, **kwargs) -> Union[int, List[int]]:
        return self.f.i8(*args, **kwargs)

    def u8 (self, *args, **kwargs) -> Union[int, List[int]]:
        return self.f.u8(*args, **kwargs)

    def i16 (self, *args, **kwargs) -> Union[int, List[int]]:
        return self.f.i16(*args, **kwargs)

    def u16 (self, *args, **kwargs) -> Union[int, List[int]]:
        return self.f.u16(*args, **kwargs)

    def i32 (self, *args, **kwargs) -> Union[int, List[int]]:
        return self.f.i32(*args, **kwargs)

    def u32 (self, *args, **kwargs) -> Union[int, List[int]]:
        return self.f.u32(*args, **kwargs)

    def i64 (self, *args, **kwargs) -> Union[int, List[int]]:
        return self.f.i64(*args, **kwargs)

    def u64 (self, *args, **kwargs) -> Union[int, List[int]]:
        return self.f.u64(*args, **kwargs)

    def f32 (self, *args, **kwargs) -> Union[float, List[float]]:
        return self.f.f32(*args, **kwargs)

    def f64 (self, *args, **kwargs) -> Union[float, List[float]]:
        return self.f.f64(*args, **kwargs)

    def vec2 (self, *args, **kwargs) -> List[float]:
        return self.f.vec2(*args, **kwargs)

    def vec3 (self, *args, **kwargs) -> List[float]:
        return self.f.vec3(*args, **kwargs)

    def vec4 (self, *args, **kwargs) -> List[float]:
        return self.f.vec4(*args, **kwargs)

    def vec2i32 (self, *args, **kwargs) -> List[int]:
        return self.f.vec2i32(*args, **kwargs)

    def vec3i32 (self, *args, **kwargs) -> List[int]:
        return self.f.vec3i32(*args, **kwargs)

    def vec4i32 (self, *args, **kwargs) -> List[int]:
        return self.f.vec4i32(*args, **kwargs)

    def ba (self, *args, **kwargs) -> bytearray:
        return self.f.ba(*args, **kwargs)

    def string (self, *args, **kwargs) -> str:
        return self.f.string(*args, **kwargs)

    def fixedString (self, *args, **kwargs) -> str:
        return self.f.fixedString(*args, **kwargs)

    def alignedString (self, *args, **kwargs) -> str:
        return self.f.alignedString(*args, **kwargs)

    def skip (self, *args, **kwargs):
        return self.f.skip(*args, **kwargs)

    def remaining (self) -> int:
        return self.f.remaining()

    def peek (self, *args, **kwargs) -> bytes:
        return self.f.peek(*args, **kwargs)

    def fromStart (self, *args, **kwargs):
        return self.f.fromStart(*args, **kwargs)

    def fromCurrent (self, *args, **kwargs):
        return self.f.fromCurrent(*args, **kwargs)

    def fromEnd (self, *args, **kwargs):
        return self.f.fromEnd(*args, **kwargs)

    def read (self, *args, **kwargs) -> bytes:
        return self.f.read(*args, **kwargs)

    def tell (self) -> int:
        return self.f.tell()

    def seek (self, *args, **kwargs):
        return self.f.seek(*args, **kwargs)

    def close (self):
        return self.f.close()

    def getSize (self) -> int:
        return self.f.getSize()

    def getFilePath (self) -> Opt[str]:
        return self.f.getFilePath()



def _test_ ():
    pass



__all__ = [
    'RWStream',
    'RWStreamPluginManager',

    '_test_',
]



if __name__ == '__main__':
    _test_()
