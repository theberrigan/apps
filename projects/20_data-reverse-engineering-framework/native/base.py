import os

from ctypes import (
    c_bool                as CBool,       # _Bool    
    c_char                as CChar,       # char (use c_byte/CI8 instead)       
    c_wchar               as CWchar,      # wchar_t
    c_byte                as CI8,         # char
    c_ubyte               as CU8,         # unsigned char
    c_short               as CI16,        # short
    c_ushort              as CU16,        # unsigned short
    c_int                 as CI32,        # int
    c_uint                as CU32,        # unsigned int
    c_long                as CI32L,       # long
    c_ulong               as CU32L,       # unsigned long
    c_longlong            as CI64,        # __int64 or long long
    c_ulonglong           as CU64,        # unsigned __int64 or unsigned long long
    c_size_t              as CSize,       # size_t
    c_ssize_t             as CSSize,      # ssize_t or Py_ssize_t
    c_float               as CF32,        # float
    c_double              as CF64,        # double
    c_longdouble          as CF64L,       # long double
    c_char_p              as CPtrChar,    # char* (NULL terminated)
    c_wchar_p             as CPtrWChar,   # wchar_t* (NULL terminated)
    c_void_p              as CPtrVoid,    # void*
    POINTER               as CPtr,
    pointer               as cPtr,        # wrapper for CPtr
    byref                 as cRef,        # similar to cPtr, but faster; use if you don't need the pointer object in Python
    cast                  as cCast,
    resize                as cResize,     # resize memory block to greater size
    sizeof                as cSizeOf,
    addressof             as cAddrOf,
    Array                 as CArray,      # abstract class for type checking
    create_string_buffer  as CStr,        # mutable narrow string buffer (char*)
    create_unicode_buffer as CWStr,       # mutable wide string buffer (wchar_t*)
    Structure             as CStruct,     # struct with native byte order
    LittleEndianStructure as CLEStruct,   # struct with little endian byte order
    BigEndianStructure    as CBEStruct,   # struct with big endian byte order
    Union                 as CUnion,      # union with uses native byte order
    LittleEndianUnion     as CLEUnion,    # union with uses little endian byte order
    BigEndianUnion        as CBEUnion,    # union with uses big endian byte order
    CFUNCTYPE             as CFn,         # cdecl - c-standard calling convention; can be used as a decorator
    WINFUNCTYPE           as WinFn,       # stdcall - Windows API calling convention; can be used as a decorator
    CDLL                  as loadCDLL,    # load dll with cdecl functions
    WinDLL                as loadWinDLL,  # load dll with stdcall functions
)



BIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../bin'))



class CBuffer:
    @staticmethod
    def fromSource (source, offset=0, copy=False):
        if not isinstance(source, bytes) and not isinstance(source, bytearray) and not isCBuffer(source):
            raise Exception(f'Data must be of type bytes, bytearray or C array, { type(source).__name__ } given')

        sourceSize = len(source) - offset
        bufferType = CU8 * sourceSize

        # TODO: is copy compatible with bytearray?
        if copy:
            return bufferType.from_buffer_copy(source, offset)

        if isinstance(source, bytes):
            source = bytearray(source)

        return bufferType.from_buffer(source, offset)

    @staticmethod
    def create (size):
        return (CU8 * size)()


def isCBuffer (value):
    return isinstance(value, CArray)

def isCBufferType (dataType):
    return issubclass(dataType, CArray)

def toCStr (value, encoding='utf-8'):
    if isinstance(value, str):
        value = value.encode(encoding)

    assert isinstance(value, bytes)

    return CStr(value)

def toCWStr (value, terminate=False, encoding='utf-16le'):
    if isinstance(value, str):
        value = value.encode(encoding)

    assert isinstance(value, (bytes, bytearray))

    if terminate:
        value += '\x00'.encode(encoding)

    return value

def CZStr (string, terminate=False, encoding='utf-8'):
    if not isinstance(string, str):
        raise Exception('Expected string')

    if terminate and ('\0' not in string):
        string += '\0'

    return string.encode(encoding)

def toVoidPtr (ptr):
    return cCast(ptr, CPtrVoid).value



'''
https://docs.python.org/3/library/ctypes.html

- Assigning a new value to instances of the pointer types c_char_p, c_wchar_p, and c_void_p changes the memory location they point to, not the contents of the memory block
  Use create_string_buffer() (char) and create_unicode_buffer() (wchar_t) for mutable memory (var.value - as NT string; var.raw - raw memory bytes)
- As has been mentioned before, all Python types except integers, strings, and bytes objects have to be wrapped in their corresponding ctypes type
- You can set the argtypes attribute, and the argument will be converted from a Python type into a C type
- By default functions are assumed to return the C int type.

.native.base  # basic ctypes imports
.native.math  # c scalar types wrappers and math
.native.bind  # header parser and bind generator
.native.libs.opengl
.native.libs.glfw
.native.libs.glew
.native.libs.xaudio2
'''

'''
name = 'glfw'

----------------------

_dll = CDLL()

class glfwCLass:
    def __init__ (self, dll):
        self.dll = dll

        self._var1 = CU32.in_dll(dll, 'someDLLVar')

    # getter
    @property
    def someDLLVar (self):
        return self._var1.value

    # if not a const
    # setter
    @someDLLVar.setter
    def someDLLVar (self, value):
        self._var1.value = value

glfw = glfwCLass(_dll)

someDLLFn = _dll.someDLLFn

someDLLFn.restype = ...
someDLLFn.argtypes = [ ... ]

__all__ = [
    'glfw',
    'someDLLFn'
]
'''

__all__ = [
    'CBool',
    'CChar',
    'CWchar',
    'CI8',
    'CU8',
    'CI16',
    'CU16',
    'CI32',
    'CU32',
    'CI32L',
    'CU32L',
    'CI64',
    'CU64',
    'CSize',
    'CSSize',
    'CF32',
    'CF64',
    'CF64L',
    'CPtrChar',
    'CPtrWChar',
    'CPtrVoid',
    'CPtr',
    'cPtr',
    'cRef',
    'cCast',
    'cResize',
    'cSizeOf',
    'cAddrOf',
    'CArray',
    'CStr',
    'CWStr',
    'CStruct',
    'CLEStruct',
    'CBEStruct',
    'CUnion',
    'CLEUnion',
    'CBEUnion',
    'CFn',
    'WinFn',
    'loadCDLL',
    'loadWinDLL',
    'BIN_DIR',
    'CBuffer',
    'isCBuffer',
    'isCBufferType',
    'toCStr',
    'toCWStr',
    'CZStr',
    'toVoidPtr',
]