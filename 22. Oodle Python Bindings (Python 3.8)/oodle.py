import os
import re
from ctypes import (
    Structure, CDLL, WINFUNCTYPE, POINTER as PTR, byref, sizeof, windll, create_unicode_buffer, cast, Array as CArray,
    c_void_p, c_char_p, c_int, c_int8, c_uint8, c_int16, c_uint16, c_int32, c_uint32, c_int64, c_uint64, c_float, c_double,
)
from ctypes.wintypes import HANDLE, LPWSTR, DWORD
from typing import Union, List, Tuple, Type, Callable, Any
from enum import Enum


# -----------------------------------------------

# Requirements:
# - Windows 64-bit
# - Python 3.9 64-bit
# - oo2core_9_win64.dll

# Caveats:
# - ctypes callback functions only support fixed number of arguments

# TODO: create HL wrapper
# https://www.programcreek.com/python/?code=Hanjun-Dai%2Fpytorch_structure2vec%2Fpytorch_structure2vec-master%2Fharvard_cep%2Fmol_lib.py
# https://www.programcreek.com/python/?code=google%2Fmacops%2Fmacops-master%2Fgmacpyutil%2Fgmacpyutil%2Fgmacpyutil.py
# https://www.programcreek.com/python/example/3875/ctypes.c_uint32
# https://stackoverflow.com/a/40766849
# -----------------------------------------------


# Oodle version
# -----------------------------------------------

OODLE2_VERSION_STATIC = 2  # don't export
OODLE2_VERSION_MAJOR = 9
OODLE2_VERSION_MINOR = 0

OodleVersion = f'{ OODLE2_VERSION_STATIC }.{ OODLE2_VERSION_MAJOR }.{ OODLE2_VERSION_MINOR }'

# PyOodle definitions
# -----------------------------------------------

PYOODLE_VERSION            = f'{ OodleVersion }.1'
PYOODLE_ROOT_DIR           = os.path.dirname(os.path.abspath(__file__))
PYOODLE_LIB_REGEX          = re.compile(rf'^oo{ OODLE2_VERSION_STATIC }core_(\d+)_win64\.dll$', re.IGNORECASE)
PYOODLE_COMPAT_LIB_NAME    = f'oo{ OODLE2_VERSION_STATIC }core_{ OODLE2_VERSION_MAJOR }_win64.dll'
PYOODLE_COMPAT_LIB_VERSION = f'{ OODLE2_VERSION_STATIC }.{ OODLE2_VERSION_MAJOR }.x'
PYOODLE_ALIGNMENT          = 8
PYOODLE_LIB_TYPE           = CDLL
PYOODLE_CALLBACK_TYPE      = WINFUNCTYPE

c_int_p    = PTR(c_int)
c_int8_p   = PTR(c_int8)
c_uint8_p  = PTR(c_uint8)
c_int16_p  = PTR(c_int16)
c_uint16_p = PTR(c_uint16)
c_int32_p  = PTR(c_int32)
c_uint32_p = PTR(c_uint32)
c_int64_p  = PTR(c_int64)
c_uint64_p = PTR(c_uint64)
c_float_p  = PTR(c_float)
c_double_p = PTR(c_double)

# All Oodle enums must have c_int32 as base integer type
class PyOodleBaseEnum (c_int32):
    def __hash__ (self):
        return self.value

    def __eq__ (self, other):
        return (
            (isinstance(other, self.__class__) and self.value == other.value) or
            (isinstance(other, int) and self.value == other)
        )

    def __ne__ (self, other):
        return not self.__eq__(other)


# All Oodle structures must have alignment of 8 bytes
class PyOodleBaseStructure (Structure):
    _pack_ = PYOODLE_ALIGNMENT


# Oodle definitions
# -----------------------------------------------

OO_S8    = c_int8
OO_U8    = c_uint8
OO_S16   = c_int16
OO_U16   = c_uint16
OO_S32   = c_int32
OO_U32   = c_uint32
OO_S64   = c_int64
OO_U64   = c_uint64
OO_F32   = c_float
OO_F64   = c_double
OO_SINTa = c_int64
OO_UINTa = c_uint64
OO_BOOL  = c_int32

OODLELZ_SPACESPEEDTRADEOFFBYTES_DEFAULT = 256
OODLELZ_LOCALDICTIONARYSIZE_MAX         = 1 << 30
OODLELZ_BLOCK_LEN                       = 1 << 18
OODLELZ_BLOCK_MAXIMUM_EXPANSION         = 2
OODLELZ_BLOCK_MAX_COMPLEN               = OODLELZ_BLOCK_LEN + OODLELZ_BLOCK_MAXIMUM_EXPANSION
OODLELZ_QUANTUM_LEN                     = 1 << 14
OODLELZ_QUANTUM_MAXIMUM_EXPANSION       = 5
OODLELZ_QUANTUM_MAX_COMPLEN             = OODLELZ_QUANTUM_LEN + OODLELZ_QUANTUM_MAXIMUM_EXPANSION
OODLELZ_SEEKCHUNKLEN_MIN                = OODLELZ_BLOCK_LEN
OODLELZ_SEEKCHUNKLEN_MAX                = 1 << 29
OODLELZ_SEEKPOINTCOUNT_DEFAULT          = 16
OODLELZ_SCRATCH_MEM_NO_BOUND            = -1
OODLELZ_FAILED                          = 0
OODLE_MALLOC_MINIMUM_ALIGNMENT          = (sizeof(c_void_p) * 2)
OODLE_JOB_MAX_DEPENDENCIES              = 4
OODLE_ALLOW_DEPRECATED_COMPRESSORS      = 0
OODLECORE_PLUGIN_JOB_MAX_DEPENDENCIES   = OODLE_JOB_MAX_DEPENDENCIES


# Enums
# -----------------------------------------------

class OodleLZ_Verbosity (PyOodleBaseEnum):
    pass

OodleLZ_Verbosity.No      = OodleLZ_Verbosity(0)
OodleLZ_Verbosity.Minimal = OodleLZ_Verbosity(1)
OodleLZ_Verbosity.Some    = OodleLZ_Verbosity(2)
OodleLZ_Verbosity.Lots    = OodleLZ_Verbosity(3)


class OodleLZ_Compressor (PyOodleBaseEnum):
    pass

OodleLZ_Compressor.Invalid   = OodleLZ_Compressor(-1)
OodleLZ_Compressor.No        = OodleLZ_Compressor(3)

# New compressors
OodleLZ_Compressor.Kraken    = OodleLZ_Compressor(8)
OodleLZ_Compressor.Leviathan = OodleLZ_Compressor(13)
OodleLZ_Compressor.Mermaid   = OodleLZ_Compressor(9)
OodleLZ_Compressor.Selkie    = OodleLZ_Compressor(11)
OodleLZ_Compressor.Hydra     = OodleLZ_Compressor(12)

if OODLE_ALLOW_DEPRECATED_COMPRESSORS:
    OodleLZ_Compressor.BitKnit = OodleLZ_Compressor(10)
    OodleLZ_Compressor.LZB16   = OodleLZ_Compressor(4)
    OodleLZ_Compressor.LZNA    = OodleLZ_Compressor(7)
    OodleLZ_Compressor.LZH     = OodleLZ_Compressor(0)
    OodleLZ_Compressor.LZHLW   = OodleLZ_Compressor(1)
    OodleLZ_Compressor.LZNIB   = OodleLZ_Compressor(2)
    OodleLZ_Compressor.LZBLW   = OodleLZ_Compressor(5)
    OodleLZ_Compressor.LZA     = OodleLZ_Compressor(6)

OodleLZ_Compressor.Count     = OodleLZ_Compressor(14)


class OodleLZ_PackedRawOverlap (PyOodleBaseEnum):
    pass

OodleLZ_PackedRawOverlap.No  = OodleLZ_PackedRawOverlap(0)
OodleLZ_PackedRawOverlap.Yes = OodleLZ_PackedRawOverlap(1)


class OodleLZ_CheckCRC (PyOodleBaseEnum):
    pass

OodleLZ_CheckCRC.No  = OodleLZ_CheckCRC(0)
OodleLZ_CheckCRC.Yes = OodleLZ_CheckCRC(1)


class OodleLZ_Profile (PyOodleBaseEnum):
    pass

OodleLZ_Profile.Main    = OodleLZ_Profile(0)
OodleLZ_Profile.Reduced = OodleLZ_Profile(1)


class OodleDecompressCallbackRet (PyOodleBaseEnum):
    pass

OodleDecompressCallbackRet.Continue = OodleDecompressCallbackRet(0)
OodleDecompressCallbackRet.Cancel   = OodleDecompressCallbackRet(1)
OodleDecompressCallbackRet.Invalid  = OodleDecompressCallbackRet(2)


class OodleLZ_CompressionLevel (PyOodleBaseEnum):
    pass

OodleLZ_CompressionLevel.No         = OodleLZ_CompressionLevel(0)
OodleLZ_CompressionLevel.SuperFast  = OodleLZ_CompressionLevel(1)
OodleLZ_CompressionLevel.VeryFast   = OodleLZ_CompressionLevel(2)
OodleLZ_CompressionLevel.Fast       = OodleLZ_CompressionLevel(3)
OodleLZ_CompressionLevel.Normal     = OodleLZ_CompressionLevel(4)
OodleLZ_CompressionLevel.Optimal1   = OodleLZ_CompressionLevel(5)
OodleLZ_CompressionLevel.Optimal2   = OodleLZ_CompressionLevel(6)
OodleLZ_CompressionLevel.Optimal3   = OodleLZ_CompressionLevel(7)
OodleLZ_CompressionLevel.Optimal4   = OodleLZ_CompressionLevel(8)
OodleLZ_CompressionLevel.Optimal5   = OodleLZ_CompressionLevel(9)
OodleLZ_CompressionLevel.HyperFast1 = OodleLZ_CompressionLevel(-1)
OodleLZ_CompressionLevel.HyperFast2 = OodleLZ_CompressionLevel(-2)
OodleLZ_CompressionLevel.HyperFast3 = OodleLZ_CompressionLevel(-3)
OodleLZ_CompressionLevel.HyperFast4 = OodleLZ_CompressionLevel(-4)
OodleLZ_CompressionLevel.HyperFast  = OodleLZ_CompressionLevel(OodleLZ_CompressionLevel.HyperFast1.value)
OodleLZ_CompressionLevel.Optimal    = OodleLZ_CompressionLevel(OodleLZ_CompressionLevel.Optimal2.value)
OodleLZ_CompressionLevel.Max        = OodleLZ_CompressionLevel(OodleLZ_CompressionLevel.Optimal5.value)
OodleLZ_CompressionLevel.Min        = OodleLZ_CompressionLevel(OodleLZ_CompressionLevel.HyperFast4.value)
OodleLZ_CompressionLevel.Invalid    = OodleLZ_CompressionLevel(0x40000000)


class OodleLZ_Jobify (PyOodleBaseEnum):
    pass

OodleLZ_Jobify.Default    = OodleLZ_Jobify(0)
OodleLZ_Jobify.Disable    = OodleLZ_Jobify(1)
OodleLZ_Jobify.Normal     = OodleLZ_Jobify(2)
OodleLZ_Jobify.Aggressive = OodleLZ_Jobify(3)
OodleLZ_Jobify.Count      = OodleLZ_Jobify(4)


class OodleLZ_Decode_ThreadPhase (PyOodleBaseEnum):
    pass

OodleLZ_Decode_ThreadPhase.One        = OodleLZ_Decode_ThreadPhase(1)
OodleLZ_Decode_ThreadPhase.Two        = OodleLZ_Decode_ThreadPhase(2)
OodleLZ_Decode_ThreadPhase.All        = OodleLZ_Decode_ThreadPhase(3)
OodleLZ_Decode_ThreadPhase.Unthreaded = OodleLZ_Decode_ThreadPhase(OodleLZ_Decode_ThreadPhase.All.value)


class OodleLZ_FuzzSafe (PyOodleBaseEnum):
    pass

OodleLZ_FuzzSafe.No  = OodleLZ_FuzzSafe(0)
OodleLZ_FuzzSafe.Yes = OodleLZ_FuzzSafe(1)


class OodleLZSeekTable_Flags (PyOodleBaseEnum):
    pass

OodleLZSeekTable_Flags.No          = OodleLZSeekTable_Flags(0)
OodleLZSeekTable_Flags.MakeRawCRCs = OodleLZSeekTable_Flags(1)


class Oodle_UsageWarnings (PyOodleBaseEnum):
    pass

Oodle_UsageWarnings.Enabled  = Oodle_UsageWarnings(0)
Oodle_UsageWarnings.Disabled = Oodle_UsageWarnings(1)


# Structures
# -----------------------------------------------

class OodleLZDecoder (PyOodleBaseStructure):
    _fields_ = []


class OodleLZ_CompressOptions (PyOodleBaseStructure):
    _fields_ = [
        ('unused_was_verbosity', OO_U32),
        ('minMatchLen', OO_S32),
        ('seekChunkReset', OO_BOOL),
        ('seekChunkLen', OO_S32),
        ('profile', OodleLZ_Profile),
        ('dictionarySize', OO_S32),
        ('spaceSpeedTradeoffBytes', OO_S32),
        ('unused_was_maxHuffmansPerChunk', OO_S32),
        ('sendQuantumCRCs', OO_BOOL),
        ('maxLocalDictionarySize', OO_S32),
        ('makeLongRangeMatcher', OO_BOOL),
        ('matchTableSizeLog2', OO_S32),
        ('jobify', OodleLZ_Jobify),
        ('jobifyUserPtr', c_void_p),
        ('farMatchMinLen', OO_S32),
        ('farMatchOffsetLog2', OO_S32),
        ('reserved', (OO_U32 * 4)),
    ]


class OodleLZ_DecodeSome_Out (PyOodleBaseStructure):
    _fields_ = [
        ('decodedCount', OO_S32),
        ('compBufUsed', OO_S32),
        ('curQuantumRawLen', OO_S32),
        ('curQuantumCompLen', OO_S32),
    ]


class OodleLZ_SeekTable (PyOodleBaseStructure):
    _fields_ = [
        ('compressor', OodleLZ_Compressor),
        ('seekChunksIndependent', OO_BOOL),
        ('totalRawLen', OO_S64),
        ('totalCompLen', OO_S64),
        ('numSeekChunks', OO_S32),
        ('seekChunkLen', OO_S32),
        ('seekChunkCompLens', PTR(OO_U32)),
        ('rawCRCs', PTR(OO_U32)),
    ]


class OodleConfigValues (PyOodleBaseStructure):
    _fields_ = [
        ('m_OodleLZ_LW_LRM_step', OO_S32),
        ('m_OodleLZ_LW_LRM_hashLength', OO_S32),
        ('m_OodleLZ_LW_LRM_jumpbits', OO_S32),
        ('m_OodleLZ_Decoder_Max_Stack_Size', OO_S32),
        ('m_OodleLZ_Small_Buffer_LZ_Fallback_Size_Unused', OO_S32),
        ('m_OodleLZ_BackwardsCompatible_MajorVersion', OO_S32),
        ('m_oodle_header_version', OO_U32),
    ]


# Used to check header/PyOodle-to-lib compatibility
OODLE_HEADER_VERSION = (
    (46 << 24) |
    (OODLE2_VERSION_MAJOR << 16) |
    (OODLE2_VERSION_MINOR << 8) |
    sizeof(OodleLZ_SeekTable)
)


# Pointers to callback functions
# -----------------------------------------------

OodleDecompressCallback = PYOODLE_CALLBACK_TYPE(
    OodleDecompressCallbackRet,  # return type
    c_void_p,                    # arg0: userdata
    PTR(OO_U8),                  # arg1: rawBuf
    OO_SINTa,                    # arg2: rawLen
    PTR(OO_U8),                  # arg3: compBuf
    OO_SINTa,                    # arg4: compBufferSize
    OO_SINTa,                    # arg5: rawDone
    OO_SINTa,                    # arg6: compUsed
)

t_fp_OodleCore_Plugin_MallocAligned = PYOODLE_CALLBACK_TYPE(
    c_void_p,  # return type
    OO_SINTa,  # arg0: bytes
    OO_S32,    # arg1: alignment
)

t_fp_OodleCore_Plugin_Free = PYOODLE_CALLBACK_TYPE(
    None,      # return type (void)
    c_void_p,  # arg0: ptr
)

t_OodleFPVoidVoid = PYOODLE_CALLBACK_TYPE(
    None,  # return type
)

t_OodleFPVoidVoidStar = PYOODLE_CALLBACK_TYPE(
    None,      # return type
    c_void_p,  # arg0: ptr
)

t_fp_Oodle_Job = t_OodleFPVoidVoidStar
t_fp_OodleCore_Plugin_Job = t_fp_Oodle_Job

t_fp_OodleCore_Plugin_RunJob = PYOODLE_CALLBACK_TYPE(
    OO_U64,          # return type
    t_fp_Oodle_Job,  # arg0: fp_job
    c_void_p,        # arg1: job_data
    PTR(OO_U64),     # arg2: dependencies
    c_int,           # arg3: num_dependencies
    c_void_p,        # arg4: user_ptr
)

t_fp_OodleCore_Plugin_WaitJob = PYOODLE_CALLBACK_TYPE(
    None,      # return type
    OO_U64,    # arg0: job_handle
    c_void_p,  # arg1: user_ptr
)

t_fp_OodleCore_Plugin_Printf = PYOODLE_CALLBACK_TYPE(
    None,      # return type
    c_int,     # arg0: verboseLevel
    c_char_p,  # arg1: file
    c_int,     # arg3: line
    c_char_p,  # arg4: fmt
    # TODO: va_list...
)

t_fp_OodleCore_Plugin_DisplayAssertion = PYOODLE_CALLBACK_TYPE(
    OO_BOOL,   # return type
    c_char_p,  # arg0: file
    c_int,     # arg1: line
    c_char_p,  # arg2: function
    c_char_p,  # arg3: message
)


# Code
# -----------------------------------------------

def formatVersion (version : Union[List, Tuple]) -> str:
    return '.'.join([ str(v) for v in version ])


def unmaskLibVersion (version : int) -> Tuple[int, int, int]:
    if not isinstance(version, int):
        return 0, 0, 0

    major = (version >> 16) & 0xFF
    minor = (version >> 8) & 0xFF

    return OODLE2_VERSION_STATIC, major, minor


def normPath (path : str) -> str:
    return os.path.normpath(os.path.abspath(path))


class PyOodleCore:
    _libCache = {}

    def __init__ (self, libPathOrDir : Union[str, None] = None):
        self._cls : Type[PyOodleCore] = self.__class__
        self._callbacks : List[PYOODLE_CALLBACK_TYPE] = []
        self._lib : PYOODLE_LIB_TYPE = self._cls._loadLib(libPathOrDir)

    # Class methods
    # ---------------------------------------------------------------------------

    @classmethod
    def _initLib (cls, lib : PYOODLE_LIB_TYPE) -> PYOODLE_LIB_TYPE:
        # Oodle_GetConfigValues
        # -------------------------------------------------
        lib.Oodle_GetConfigValues.restype = None
        lib.Oodle_GetConfigValues.argtypes = [
            PTR(OodleConfigValues),  # arg0: ptr
        ]

        # Oodle_SetConfigValues
        # -------------------------------------------------
        lib.Oodle_SetConfigValues.restype = None
        lib.Oodle_SetConfigValues.argtypes = [
            PTR(OodleConfigValues),  # arg0: ptr
        ]

        # Oodle_SetUsageWarnings
        # -------------------------------------------------
        lib.Oodle_SetUsageWarnings.restype = None
        lib.Oodle_SetUsageWarnings.argtypes = [
            Oodle_UsageWarnings,  # arg0: state
        ]

        # OodleCore_Plugins_SetAllocators
        # -------------------------------------------------
        lib.OodleCore_Plugins_SetAllocators.restype = None
        lib.OodleCore_Plugins_SetAllocators.argtypes = [
            t_fp_OodleCore_Plugin_MallocAligned,  # arg0: fp_OodleMallocAligned
            t_fp_OodleCore_Plugin_Free,           # arg1: fp_OodleFree
        ]

        # OodleCore_Plugins_SetJobSystem
        # -------------------------------------------------
        lib.OodleCore_Plugins_SetJobSystem.restype = None
        lib.OodleCore_Plugins_SetJobSystem.argtypes = [
            t_fp_OodleCore_Plugin_RunJob,   # arg0: fp_RunJob
            t_fp_OodleCore_Plugin_WaitJob,   # arg1: fp_WaitJob
        ]

        # OodleCore_Plugins_SetJobSystemAndCount
        # -------------------------------------------------
        lib.OodleCore_Plugins_SetJobSystemAndCount.restype = None
        lib.OodleCore_Plugins_SetJobSystemAndCount.argtypes = [
            t_fp_OodleCore_Plugin_RunJob,   # arg0: fp_RunJob
            t_fp_OodleCore_Plugin_WaitJob,  # arg1: fp_WaitJob
            c_int,                          # arg2: target_parallelism
        ]

        # OodleCore_Plugins_SetPrintf
        # -------------------------------------------------
        lib.OodleCore_Plugins_SetPrintf.restype = t_fp_OodleCore_Plugin_Printf
        lib.OodleCore_Plugins_SetPrintf.argtypes = [
            t_fp_OodleCore_Plugin_Printf,   # arg0: fp_rrRawPrintf
        ]

        # OodleCore_Plugins_SetAssertion
        # -------------------------------------------------
        lib.OodleCore_Plugins_SetAssertion.restype = t_fp_OodleCore_Plugin_DisplayAssertion
        lib.OodleCore_Plugins_SetAssertion.argtypes = [
            t_fp_OodleCore_Plugin_DisplayAssertion,   # arg0: fp_rrDisplayAssertion
        ]

        # OodleCore_Plugin_MallocAligned_Default
        # -------------------------------------------------
        lib.OodleCore_Plugin_MallocAligned_Default.restype = c_void_p
        lib.OodleCore_Plugin_MallocAligned_Default.argtypes = [
            OO_SINTa,   # arg0: size
            OO_S32,     # arg1: alignment
        ]

        # OodleCore_Plugin_Free_Default
        # -------------------------------------------------
        lib.OodleCore_Plugin_Free_Default.restype = None
        lib.OodleCore_Plugin_Free_Default.argtypes = [
            c_void_p,   # arg0: ptr
        ]

        # OodleCore_Plugin_Printf_Default
        # -------------------------------------------------
        lib.OodleCore_Plugin_Printf_Default.restype = None
        lib.OodleCore_Plugin_Printf_Default.argtypes = [
            c_int,      # arg0: verboseLevel
            c_char_p,   # arg1: file
            c_int,      # arg2: line
            c_char_p,   # arg3: fmt
            # TODO: va_list?
        ]

        # OodleCore_Plugin_Printf_Verbose
        # -------------------------------------------------
        lib.OodleCore_Plugin_Printf_Verbose.restype = None
        lib.OodleCore_Plugin_Printf_Verbose.argtypes = [
            c_int,      # arg0: verboseLevel
            c_char_p,   # arg1: file
            c_int,      # arg2: line
            c_char_p,   # arg3: fmt
            # TODO: va_list?
        ]

        # OodleCore_Plugin_DisplayAssertion_Default
        # -------------------------------------------------
        lib.OodleCore_Plugin_DisplayAssertion_Default.restype = OO_BOOL
        lib.OodleCore_Plugin_DisplayAssertion_Default.argtypes = [
            c_char_p,   # arg0: file
            c_int,      # arg1: line
            c_char_p,   # arg2: function
            c_char_p,   # arg3: message
        ]

        # OodleCore_Plugin_RunJob_Default
        # -------------------------------------------------
        lib.OodleCore_Plugin_RunJob_Default.restype = OO_U64
        lib.OodleCore_Plugin_RunJob_Default.argtypes = [
            t_fp_Oodle_Job,  # arg0: fp_job
            c_void_p,        # arg1: job_data
            PTR(OO_U64),     # arg2: dependencies
            c_int,           # arg3: num_dependencies
            c_void_p,        # arg4: user_ptr
        ]

        # OodleCore_Plugin_WaitJob_Default
        # -------------------------------------------------
        lib.OodleCore_Plugin_WaitJob_Default.restype = None
        lib.OodleCore_Plugin_WaitJob_Default.argtypes = [
            OO_U64,    # arg0: job_handle
            c_void_p,  # arg1: user_ptr
        ]

        # OodleLZ_Compress
        # -------------------------------------------------
        lib.OodleLZ_Compress.restype = OO_SINTa
        lib.OodleLZ_Compress.argtypes = [
            OodleLZ_Compressor,            # arg0: compressor
            c_void_p,                      # arg1: rawBuf
            OO_SINTa,                      # arg2: rawLen
            c_void_p,                      # arg3: compBuf
            OodleLZ_CompressionLevel,      # arg4: level
            PTR(OodleLZ_CompressOptions),  # arg5: pOptions
            c_void_p,                      # arg6: dictionaryBase
            c_void_p,                      # arg7: lrm
            c_void_p,                      # arg8: scratchMem
            OO_SINTa,                      # arg9: scratchSize
        ]

        # OodleLZ_Decompress
        # -------------------------------------------------
        lib.OodleLZ_Decompress.restype = OO_SINTa
        lib.OodleLZ_Decompress.argtypes = [
            c_void_p,                    # arg0:  compBuf
            OO_SINTa,                    # arg1:  compBufSize
            c_void_p,                    # arg2:  rawBuf
            OO_SINTa,                    # arg3:  rawLen
            OodleLZ_FuzzSafe,            # arg4:  fuzzSafe
            OodleLZ_CheckCRC,            # arg5:  checkCRC
            OodleLZ_Verbosity,           # arg6:  verbosity
            c_void_p,                    # arg7:  decBufBase
            OO_SINTa,                    # arg8:  decBufSize
            OodleDecompressCallback,     # arg9:  fpCallback
            c_void_p,                    # arg10: callbackUserData
            c_void_p,                    # arg11: decoderMemory
            OO_SINTa,                    # arg12: decoderMemorySize
            OodleLZ_Decode_ThreadPhase,  # arg13: threadPhase
        ]

        # OodleLZDecoder_Create
        # -------------------------------------------------
        lib.OodleLZDecoder_Create.restype = PTR(OodleLZDecoder)
        lib.OodleLZDecoder_Create.argtypes = [
            OodleLZ_Compressor,  # arg0: compressor
            OO_S64,              # arg1: rawLen
            c_void_p,            # arg2: memory
            OO_SINTa,            # arg3: memorySize
        ]

        # OodleLZDecoder_MemorySizeNeeded
        # -------------------------------------------------
        lib.OodleLZDecoder_MemorySizeNeeded.restype = OO_S32
        lib.OodleLZDecoder_MemorySizeNeeded.argtypes = [
            OodleLZ_Compressor,  # arg0: compressor
            OO_SINTa,            # arg1: rawLen
        ]

        # OodleLZ_ThreadPhased_BlockDecoderMemorySizeNeeded
        # -------------------------------------------------
        lib.OodleLZ_ThreadPhased_BlockDecoderMemorySizeNeeded.restype = OO_S32
        lib.OodleLZ_ThreadPhased_BlockDecoderMemorySizeNeeded.argtypes = []

        # OodleLZDecoder_Destroy
        # -------------------------------------------------
        lib.OodleLZDecoder_Destroy.restype = None
        lib.OodleLZDecoder_Destroy.argtypes = [
            PTR(OodleLZDecoder),  # arg0: decoder
        ]

        # OodleLZDecoder_Reset
        # -------------------------------------------------
        lib.OodleLZDecoder_Reset.restype = OO_BOOL
        lib.OodleLZDecoder_Reset.argtypes = [
            PTR(OodleLZDecoder),  # arg0: decoder
            OO_SINTa,             # arg1: decPos
            OO_SINTa,             # arg2: decLen
        ]

        # OodleLZDecoder_DecodeSome
        # -------------------------------------------------
        lib.OodleLZDecoder_DecodeSome.restype = OO_BOOL
        lib.OodleLZDecoder_DecodeSome.argtypes = [
            PTR(OodleLZDecoder),          # arg0:  decoder
            PTR(OodleLZ_DecodeSome_Out),  # arg1:  out
            c_void_p,                     # arg2:  decBuf
            OO_SINTa,                     # arg3:  decBufPos
            OO_SINTa,                     # arg4:  decBufferSize
            OO_SINTa,                     # arg5:  decBufAvail
            c_void_p,                     # arg6:  compPtr
            OO_SINTa,                     # arg7:  compAvail
            OodleLZ_FuzzSafe,             # arg8:  fuzzSafe
            OodleLZ_CheckCRC,             # arg9: checkCRC
            OodleLZ_Verbosity,            # arg10: verbosity
            OodleLZ_Decode_ThreadPhase,   # arg11: threadPhase
        ]

        # OodleLZDecoder_MakeValidCircularWindowSize
        # -------------------------------------------------
        lib.OodleLZDecoder_MakeValidCircularWindowSize.restype = OO_S32
        lib.OodleLZDecoder_MakeValidCircularWindowSize.argtypes = [
            OodleLZ_Compressor,  # arg0: compressor
            OO_S32,              # arg1: minWindowSize
        ]

        # OodleLZ_MakeSeekChunkLen
        # -------------------------------------------------
        lib.OodleLZ_MakeSeekChunkLen.restype = OO_S32
        lib.OodleLZ_MakeSeekChunkLen.argtypes = [
            OO_S64,  # arg0: rawLen
            OO_S32,  # arg1: desiredSeekPointCount
        ]

        # OodleLZ_GetNumSeekChunks
        # -------------------------------------------------
        lib.OodleLZ_GetNumSeekChunks.restype = OO_S32
        lib.OodleLZ_GetNumSeekChunks.argtypes = [
            OO_S64,  # arg0: rawLen
            OO_S32,  # arg1: seekChunkLen
        ]

        # OodleLZ_GetSeekTableMemorySizeNeeded
        # -------------------------------------------------
        lib.OodleLZ_GetSeekTableMemorySizeNeeded.restype = OO_SINTa
        lib.OodleLZ_GetSeekTableMemorySizeNeeded.argtypes = [
            OO_S32,                  # arg0: numSeekChunks
            OodleLZSeekTable_Flags,  # arg1: flags
        ]

        # OodleLZ_FillSeekTable
        # -------------------------------------------------
        lib.OodleLZ_FillSeekTable.restype = OO_BOOL
        lib.OodleLZ_FillSeekTable.argtypes = [
            PTR(OodleLZ_SeekTable),  # arg0: pTable
            OodleLZSeekTable_Flags,  # arg1: flags
            OO_S32,                  # arg2: seekChunkLen
            c_void_p,                # arg3: rawBuf
            OO_SINTa,                # arg4: rawLen
            c_void_p,                # arg5: compBuf
            OO_SINTa,                # arg6: compLen
        ]

        # OodleLZ_CreateSeekTable
        # -------------------------------------------------
        lib.OodleLZ_CreateSeekTable.restype = PTR(OodleLZ_SeekTable)
        lib.OodleLZ_CreateSeekTable.argtypes = [
            OodleLZSeekTable_Flags,  # arg0: flags
            OO_S32,                  # arg1: seekChunkLen
            c_void_p,                # arg2: rawBuf
            OO_SINTa,                # arg3: rawLen
            c_void_p,                # arg4: compBuf
            OO_SINTa,                # arg5: compLen
        ]

        # OodleLZ_FreeSeekTable
        # -------------------------------------------------
        lib.OodleLZ_FreeSeekTable.restype = None
        lib.OodleLZ_FreeSeekTable.argtypes = [
            PTR(OodleLZ_SeekTable),  # arg0: pTable
        ]

        # OodleLZ_CheckSeekTableCRCs
        # -------------------------------------------------
        lib.OodleLZ_CheckSeekTableCRCs.restype = OO_BOOL
        lib.OodleLZ_CheckSeekTableCRCs.argtypes = [
            c_void_p,                # arg0: rawBuf
            OO_SINTa,                # arg1: rawLen
            PTR(OodleLZ_SeekTable),  # arg2: seekTable
        ]

        # OodleLZ_FindSeekEntry
        # -------------------------------------------------
        lib.OodleLZ_FindSeekEntry.restype = OO_S32
        lib.OodleLZ_FindSeekEntry.argtypes = [
            OO_S64,                  # arg0: rawPos
            PTR(OodleLZ_SeekTable),  # arg1: seekTable
        ]

        # OodleLZ_GetSeekEntryPackedPos
        # -------------------------------------------------
        lib.OodleLZ_GetSeekEntryPackedPos.restype = OO_S64
        lib.OodleLZ_GetSeekEntryPackedPos.argtypes = [
            OO_S32,                  # arg0: seekI
            PTR(OodleLZ_SeekTable),  # arg1: seekTable
        ]

        # OodleLZ_CompressionLevel_GetName
        # -------------------------------------------------
        lib.OodleLZ_CompressionLevel_GetName.restype = c_char_p
        lib.OodleLZ_CompressionLevel_GetName.argtypes = [
            OodleLZ_CompressionLevel,  # arg0: compressSelect
        ]

        # OodleLZ_Compressor_GetName
        # -------------------------------------------------
        lib.OodleLZ_Compressor_GetName.restype = c_char_p
        lib.OodleLZ_Compressor_GetName.argtypes = [
            OodleLZ_Compressor,  # arg0: compressor
        ]

        # OodleLZ_Jobify_GetName
        # -------------------------------------------------
        lib.OodleLZ_Jobify_GetName.restype = c_char_p
        lib.OodleLZ_Jobify_GetName.argtypes = [
            OodleLZ_Jobify,  # arg0: jobify
        ]

        # OodleLZ_CompressOptions_GetDefault
        # -------------------------------------------------
        lib.OodleLZ_CompressOptions_GetDefault.restype = PTR(OodleLZ_CompressOptions)
        lib.OodleLZ_CompressOptions_GetDefault.argtypes = [
            OodleLZ_Compressor,        # arg0: compressor
            OodleLZ_CompressionLevel,  # arg1: lzLevel
        ]

        # OodleLZ_CompressOptions_Validate
        # -------------------------------------------------
        lib.OodleLZ_CompressOptions_Validate.restype = None
        lib.OodleLZ_CompressOptions_Validate.argtypes = [
            PTR(OodleLZ_CompressOptions),  # arg0: pOptions
        ]

        # OodleLZ_GetCompressScratchMemBound
        # -------------------------------------------------
        lib.OodleLZ_GetCompressScratchMemBound.restype = OO_SINTa
        lib.OodleLZ_GetCompressScratchMemBound.argtypes = [
            OodleLZ_Compressor,            # arg0: compressor
            OodleLZ_CompressionLevel,      # arg1: level
            OO_SINTa,                      # arg2: rawLen
            PTR(OodleLZ_CompressOptions),  # arg3: pOptions
        ]

        # OodleLZ_GetCompressedBufferSizeNeeded
        # -------------------------------------------------
        lib.OodleLZ_GetCompressedBufferSizeNeeded.restype = OO_SINTa
        lib.OodleLZ_GetCompressedBufferSizeNeeded.argtypes = [
            OodleLZ_Compressor,  # arg0: compressor
            OO_SINTa,            # arg1: rawSize
        ]

        # OodleLZ_GetDecodeBufferSize
        # -------------------------------------------------
        lib.OodleLZ_GetDecodeBufferSize.restype = OO_SINTa
        lib.OodleLZ_GetDecodeBufferSize.argtypes = [
            OodleLZ_Compressor,  # arg0: compressor
            OO_SINTa,            # arg1: rawSize
            OO_BOOL,             # arg2: corruptionPossible
        ]

        # OodleLZ_GetInPlaceDecodeBufferSize
        # -------------------------------------------------
        lib.OodleLZ_GetInPlaceDecodeBufferSize.restype = OO_SINTa
        lib.OodleLZ_GetInPlaceDecodeBufferSize.argtypes = [
            OodleLZ_Compressor,  # arg0: compressor
            OO_SINTa,            # arg1: compLen
            OO_SINTa,            # arg2: rawLen
        ]

        # OodleLZ_GetCompressedStepForRawStep
        # -------------------------------------------------
        lib.OodleLZ_GetCompressedStepForRawStep.restype = OO_SINTa
        lib.OodleLZ_GetCompressedStepForRawStep.argtypes = [
            c_void_p,       # arg0: compPtr
            OO_SINTa,       # arg1: compAvail
            OO_SINTa,       # arg2: startRawPos
            OO_SINTa,       # arg3: rawSeekBytes
            PTR(OO_SINTa),  # arg4: pEndRawPos
            PTR(OO_BOOL),   # arg5: pIndependent
        ]

        # OodleLZ_GetAllChunksCompressor
        # -------------------------------------------------
        lib.OodleLZ_GetAllChunksCompressor.restype = OodleLZ_Compressor
        lib.OodleLZ_GetAllChunksCompressor.argtypes = [
            c_void_p,  # arg0: compBuf
            OO_SINTa,  # arg1: compBufSize
            OO_SINTa,  # arg2: rawLen
        ]

        # OodleLZ_GetFirstChunkCompressor
        # -------------------------------------------------
        lib.OodleLZ_GetFirstChunkCompressor.restype = OodleLZ_Compressor
        lib.OodleLZ_GetFirstChunkCompressor.argtypes = [
            c_void_p,      # arg0: compChunkPtr
            OO_SINTa,      # arg1: compBufAvail
            PTR(OO_BOOL),  # arg2: pIndependent
        ]

        # OodleLZ_GetChunkCompressor
        # -------------------------------------------------
        lib.OodleLZ_GetChunkCompressor.restype = OodleLZ_Compressor
        lib.OodleLZ_GetChunkCompressor.argtypes = [
            c_void_p,      # arg0: compChunkPtr
            OO_SINTa,      # arg1: compBufAvail
            PTR(OO_BOOL),  # arg2: pIndependent
        ]

        # Oodle_CheckVersion
        # -------------------------------------------------
        lib.Oodle_CheckVersion.restype = OO_BOOL
        lib.Oodle_CheckVersion.argtypes = [
            OO_U32,       # arg0: oodle_header_version
            PTR(OO_U32),  # atg1: pOodleLibVersion
        ]

        # Oodle_LogHeader
        # -------------------------------------------------
        lib.Oodle_LogHeader.restype = None
        lib.Oodle_LogHeader.argtypes = []

        return lib

    @classmethod
    def _loadLib (cls, libPathOrDir : Union[str, None]) -> PYOODLE_LIB_TYPE:
        # Try to find lib in provided path
        if libPathOrDir:
            if not isinstance(libPathOrDir, str):
                raise Exception('Lib path/directory must be a string or None')

            libPathOrDir = normPath(libPathOrDir)

            if os.path.isfile(libPathOrDir):
                lib = cls._tryLoadLibByPath(libPathOrDir)

                if isinstance(lib, Exception):
                    raise lib

                return cls._initLib(lib)

            elif os.path.isdir(libPathOrDir):
                for item in os.listdir(libPathOrDir):
                    lib = cls._tryLoadLibByPath(os.path.join(libPathOrDir, item))

                    if isinstance(lib, Exception):
                        continue

                    return cls._initLib(lib)

                raise Exception('Compatible library is not found in provided directory')

            raise Exception(f'Provided path is not a file or directory: { libPathOrDir }')

        # Try to find lib in special directories
        directories = [ PYOODLE_ROOT_DIR, os.getcwd() ]

        for directory in directories:
            for item in os.listdir(directory):
                lib = cls._tryLoadLibByPath(os.path.join(directory, item))

                if isinstance(lib, Exception):
                    continue

                return cls._initLib(lib)

        # Try to load lib by name
        lib = cls._tryLoadLibByName(PYOODLE_COMPAT_LIB_NAME)

        if isinstance(lib, Exception):
            raise lib

        return cls._initLib(lib)

    @classmethod
    def _tryLoadLibByPath (cls, libPath : str) -> Union[PYOODLE_LIB_TYPE, Exception]:
        if not os.path.isfile(libPath):
            return Exception(f'Provided path is not a file: { libPath }')

        majorVersion = cls._getLibMajorVersionFromFilePath(libPath)

        if majorVersion is None:
            return Exception(f'Not an Oodle library: { libPath }')

        if majorVersion != OODLE2_VERSION_MAJOR:
            return Exception(f'Major version of library ({ majorVersion }) doesn\'t match major version supported by PyOodle ({ OODLE2_VERSION_MAJOR })')

        cachedLib = cls._getCachedLib(libPath)

        if cachedLib:
            return cachedLib

        lib = cls._instantiateLib(libPath)

        if isinstance(lib, Exception):
            return lib

        return cls._getLibCompatError(lib) or cls._cacheLib(libPath, lib)

    @classmethod
    def _tryLoadLibByName (cls, libName : str) -> Union[PYOODLE_LIB_TYPE, Exception]:
        lib = cls._instantiateLib(libName)

        if isinstance(lib, Exception):
            return lib

        return cls._getLibCompatError(lib) or cls._cacheLib(cls._getLibPathFromModule(lib), lib)

    @classmethod
    def _instantiateLib (cls, libPathOrName : str) -> Union[PYOODLE_LIB_TYPE, Exception]:
        try:
            return PYOODLE_LIB_TYPE(libPathOrName)
        except Exception as e:
            return e

    @classmethod
    def _getCachedLib (cls, libPath : str) -> Union[PYOODLE_LIB_TYPE, None]:
        cacheKey = cls._pathToCacheKey(libPath)

        if cacheKey in cls._libCache:
            return cls._libCache[cacheKey]

        return None

    @classmethod
    def _cacheLib (cls, libPath : str, lib : PYOODLE_LIB_TYPE) -> PYOODLE_LIB_TYPE:
        cacheKey = cls._pathToCacheKey(libPath)

        cls._libCache[cacheKey] = lib

        return lib

    @classmethod
    def _pathToCacheKey (cls, path : str) -> str:
        return normPath(path).strip().lower()

    @classmethod
    def _getLibMajorVersionFromFilePath (cls, filePath : str) -> Union[int, None]:
        if isinstance(filePath, str):
            matches = re.match(PYOODLE_LIB_REGEX, os.path.basename(filePath))

            if matches:
                return int(matches.group(1))

        return None

    @classmethod
    def _getLibCompatError (cls, lib : PYOODLE_LIB_TYPE) -> Union[None, Exception]:
        isCompat, libVersion = cls._getLibCompat(lib)
        formattedLibVersion = formatVersion(unmaskLibVersion(libVersion))

        if not isCompat:
            return Exception(
                f'Current version of PyOodle is only compatible with library version { PYOODLE_COMPAT_LIB_VERSION }, '
                f'but version of the provided library is { formattedLibVersion }'
            )

        return None

    @classmethod
    def _getLibCompat (cls, lib : PYOODLE_LIB_TYPE) -> Tuple[bool, int]:
        if not lib or not hasattr(lib, 'Oodle_CheckVersion'):
            return False, 0

        lib.Oodle_CheckVersion.restype = OO_BOOL
        lib.Oodle_CheckVersion.argtypes = OO_U32, PTR(OO_U32)
        libVersion = OO_U32(0)

        result = lib.Oodle_CheckVersion(OO_U32(OODLE_HEADER_VERSION), byref(libVersion))

        return bool(result), libVersion.value

    @classmethod
    def _getLibPathFromModule (cls, lib : PYOODLE_LIB_TYPE) -> str:
        GetModuleFileName = windll.kernel32.GetModuleFileNameW

        GetModuleFileName.restype = DWORD
        GetModuleFileName.argtypes = HANDLE, LPWSTR, DWORD

        maxPathLength = 260  # see MAX_PATH in windows.h
        pathBuffer = create_unicode_buffer(maxPathLength)

        # noinspection PyProtectedMember
        pathLength = GetModuleFileName(lib._handle, pathBuffer, maxPathLength)

        # noinspection PyProtectedMember
        return pathBuffer.value if pathLength else lib._name

    # Private methods
    # ---------------------------------------------------------------------------

    def _cacheCallback (self, callback : PYOODLE_CALLBACK_TYPE) -> PYOODLE_CALLBACK_TYPE:
        self._callbacks.append(callback)
        return callback

    # Oodle API functions
    # ---------------------------------------------------------------------------

    def Oodle_GetConfigValues (self, ptr : OodleConfigValues) -> None:
        return self._lib.Oodle_GetConfigValues(ptr)

    def Oodle_SetConfigValues (self, ptr : OodleConfigValues) -> None:
        return self._lib.Oodle_SetConfigValues(ptr)

    def Oodle_SetUsageWarnings (self, state : Oodle_UsageWarnings) -> None:
        return self._lib.Oodle_SetUsageWarnings(state)

    def OodleCore_Plugins_SetAllocators (
        self,
        fp_OodleMallocAligned : t_fp_OodleCore_Plugin_MallocAligned,
        fp_OodleFree : t_fp_OodleCore_Plugin_Free
    ) -> None:
        return self._lib.OodleCore_Plugins_SetAllocators(
            self._cacheCallback(fp_OodleMallocAligned),
            self._cacheCallback(fp_OodleFree)
        )

    def OodleCore_Plugins_SetJobSystem (
        self,
        fp_RunJob : t_fp_OodleCore_Plugin_RunJob,
        fp_WaitJob : t_fp_OodleCore_Plugin_WaitJob
    ) -> None:
        return self._lib.OodleCore_Plugins_SetJobSystem(
            self._cacheCallback(fp_RunJob),
            self._cacheCallback(fp_WaitJob)
        )

    def OodleCore_Plugins_SetJobSystemAndCount (
        self,
        fp_RunJob : t_fp_OodleCore_Plugin_RunJob,
        fp_WaitJob : t_fp_OodleCore_Plugin_WaitJob,
        target_parallelism : c_int
    ) -> None:
        return self._lib.OodleCore_Plugins_SetJobSystemAndCount(
            self._cacheCallback(fp_RunJob),
            self._cacheCallback(fp_WaitJob),
            target_parallelism
        )

    def OodleCore_Plugins_SetPrintf (
        self,
        fp_rrRawPrintf : t_fp_OodleCore_Plugin_Printf
    ) -> t_fp_OodleCore_Plugin_Printf:
        return self._lib.OodleCore_Plugins_SetPrintf(self._cacheCallback(fp_rrRawPrintf))

    def OodleCore_Plugins_SetAssertion (
        self,
        fp_rrDisplayAssertion : t_fp_OodleCore_Plugin_DisplayAssertion
    ) -> t_fp_OodleCore_Plugin_DisplayAssertion:
        return self._lib.OodleCore_Plugins_SetAssertion(self._cacheCallback(fp_rrDisplayAssertion))

    def OodleCore_Plugin_MallocAligned_Default (self, size : OO_SINTa, alignment : OO_S32) -> c_void_p:
        return c_void_p(self._lib.OodleCore_Plugin_MallocAligned_Default(size, alignment))

    def OodleCore_Plugin_Free_Default (self, ptr : c_void_p) -> None:
        return self._lib.OodleCore_Plugin_Free_Default(ptr)

    def OodleCore_Plugin_Printf_Default (
        self,
        verboseLevel : c_int,
        file : c_char_p,
        line : c_int,
        fmt : c_char_p,
        *args  # TODO: test ...
    ) -> None:
        return self._lib.OodleCore_Plugin_Printf_Default(verboseLevel, file, line, fmt, *args)

    def OodleCore_Plugin_Printf_Verbose (
        self,
        verboseLevel : c_int,
        file : c_char_p,
        line : c_int,
        fmt : c_char_p,
        *args  # TODO: test ...
    ) -> None:
        return self._lib.OodleCore_Plugin_Printf_Verbose(verboseLevel, file, line, fmt, *args)

    def OodleCore_Plugin_DisplayAssertion_Default (
        self,
        file : c_char_p,
        line : c_int,
        function : c_char_p,
        message : c_char_p
    ) -> OO_BOOL:
        return OO_BOOL(self._lib.OodleCore_Plugin_DisplayAssertion_Default(file, line, function, message))

    def OodleCore_Plugin_RunJob_Default (
        self,
        fp_job : t_fp_Oodle_Job,
        job_data : c_void_p,
        dependencies : PTR(OO_U64),
        num_dependencies : c_int,
        user_ptr : c_void_p
    ) -> OO_U64:
        return OO_U64(self._lib.OodleCore_Plugin_RunJob_Default(
            fp_job,
            job_data,
            dependencies,
            num_dependencies,
            user_ptr
        ))

    def OodleCore_Plugin_WaitJob_Default (self, job_handle : OO_U64, user_ptr : c_void_p) -> None:
        return self._lib.OodleCore_Plugin_WaitJob_Default(job_handle, user_ptr)

    def OodleLZ_Compress (
        self,
        compressor : OodleLZ_Compressor,
        rawBuf : c_void_p,
        rawLen : OO_SINTa,
        compBuf : c_void_p,
        level : OodleLZ_CompressionLevel,
        pOptions : PTR(OodleLZ_CompressOptions) = None,
        dictionaryBase : c_void_p = None,
        lrm : c_void_p = None,
        scratchMem : c_void_p = None,
        scratchSize : OO_SINTa = None
    ) -> OO_SINTa:
        if scratchSize is None:
            scratchSize = OO_SINTa(0)

        return OO_SINTa(self._lib.OodleLZ_Compress(
            compressor,
            rawBuf,
            rawLen,
            compBuf,
            level,
            pOptions,
            dictionaryBase,
            lrm,
            scratchMem,
            scratchSize
        ))

    def OodleLZ_Decompress (
        self,
        compBuf : c_void_p,
        compBufSize : OO_SINTa,
        rawBuf : c_void_p,
        rawLen : OO_SINTa,
        fuzzSafe : OodleLZ_FuzzSafe = None,
        checkCRC : OodleLZ_CheckCRC = None,
        verbosity : OodleLZ_Verbosity = None,
        decBufBase : c_void_p = None,
        decBufSize : OO_SINTa = None,
        fpCallback : OodleDecompressCallback = None,
        callbackUserData : c_void_p = None,
        decoderMemory : c_void_p = None,
        decoderMemorySize : OO_SINTa = None,
        threadPhase : OodleLZ_Decode_ThreadPhase = None
    ) -> OO_SINTa:
        if fuzzSafe is None:
            fuzzSafe = OodleLZ_FuzzSafe.Yes

        if checkCRC is None:
            checkCRC = OodleLZ_CheckCRC.No

        if verbosity is None:
            verbosity = OodleLZ_Verbosity.No

        if decBufSize is None:
            decBufSize = OO_SINTa(0)

        if fpCallback is None:
            fpCallback = OodleDecompressCallback(0)

        if decoderMemorySize is None:
            decoderMemorySize = OO_SINTa(0)

        if threadPhase is None:
            threadPhase = OodleLZ_Decode_ThreadPhase.Unthreaded

        return OO_SINTa(self._lib.OodleLZ_Decompress(
            compBuf,
            compBufSize,
            rawBuf,
            rawLen,
            fuzzSafe,
            checkCRC,
            verbosity,
            decBufBase,
            decBufSize,
            fpCallback,
            callbackUserData,
            decoderMemory,
            decoderMemorySize,
            threadPhase
        ))

    def OodleLZDecoder_Create (
        self,
        compressor : OodleLZ_Compressor,
        rawLen : OO_S64,
        memory : c_void_p,
        memorySize : OO_SINTa
    ) -> PTR(OodleLZDecoder):
        return self._lib.OodleLZDecoder_Create(compressor, rawLen, memory, memorySize)

    def OodleLZDecoder_MemorySizeNeeded (
        self,
        compressor : OodleLZ_Compressor = None,
        rawLen : OO_SINTa = None
    ) -> OO_S32:
        if compressor is None:
            compressor = OodleLZ_Compressor.Invalid

        if rawLen is None:
            rawLen = OO_SINTa(-1)

        return OO_S32(self._lib.OodleLZDecoder_MemorySizeNeeded(compressor, rawLen))

    def OodleLZ_ThreadPhased_BlockDecoderMemorySizeNeeded (self) -> OO_S32:
        return OO_S32(self._lib.OodleLZ_ThreadPhased_BlockDecoderMemorySizeNeeded())

    def OodleLZDecoder_Destroy (self, decoder : PTR(OodleLZDecoder)) -> None:
        return self._lib.OodleLZDecoder_Destroy(decoder)

    def OodleLZDecoder_Reset (
        self,
        decoder : PTR(OodleLZDecoder),
        decPos : OO_SINTa,
        decLen : OO_SINTa = None
    ) -> OO_BOOL:
        if decLen is None:
            decLen = OO_SINTa(0)

        return OO_BOOL(self._lib.OodleLZDecoder_Reset(decoder, decPos, decLen))

    def OodleLZDecoder_DecodeSome (
        self,
        decoder : PTR(OodleLZDecoder),
        out : PTR(OodleLZ_DecodeSome_Out),
        decBuf : c_void_p,
        decBufPos : OO_SINTa,
        decBufferSize : OO_SINTa,
        decBufAvail : OO_SINTa,
        compPtr : c_void_p,
        compAvail : OO_SINTa,
        fuzzSafe : OodleLZ_FuzzSafe = None,
        checkCRC : OodleLZ_CheckCRC = None,
        verbosity : OodleLZ_Verbosity = None,
        threadPhase : OodleLZ_Decode_ThreadPhase = None
    ) -> OO_BOOL:
        if fuzzSafe is None:
            fuzzSafe = OodleLZ_FuzzSafe.No

        if checkCRC is None:
            checkCRC = OodleLZ_CheckCRC.No

        if verbosity is None:
            verbosity = OodleLZ_Verbosity.No

        if threadPhase is None:
            threadPhase = OodleLZ_Decode_ThreadPhase.Unthreaded

        return OO_BOOL(self._lib.OodleLZDecoder_DecodeSome(
            decoder,
            out,
            decBuf,
            decBufPos,
            decBufferSize,
            decBufAvail,
            compPtr,
            compAvail,
            fuzzSafe,
            checkCRC,
            verbosity,
            threadPhase,
        ))

    def OodleLZDecoder_MakeValidCircularWindowSize (
        self,
        compressor : OodleLZ_Compressor,
        minWindowSize : OO_S32 = None
    ) -> OO_S32:
        if minWindowSize is None:
            minWindowSize = OO_S32(0)

        return OO_S32(self._lib.OodleLZDecoder_MakeValidCircularWindowSize(compressor, minWindowSize))

    def OodleLZ_MakeSeekChunkLen (self, rawLen : OO_S64, desiredSeekPointCount : OO_S32) -> OO_S32:
        return OO_S32(self._lib.OodleLZ_MakeSeekChunkLen(rawLen, desiredSeekPointCount))

    def OodleLZ_GetNumSeekChunks (self, rawLen : OO_S64, seekChunkLen : OO_S32) -> OO_S32:
        return OO_S32(self._lib.OodleLZ_GetNumSeekChunks(rawLen, seekChunkLen))

    def OodleLZ_GetSeekTableMemorySizeNeeded (self, numSeekChunks : OO_S32, flags : OodleLZSeekTable_Flags) -> OO_SINTa:
        return OO_SINTa(self._lib.OodleLZ_GetSeekTableMemorySizeNeeded(numSeekChunks, flags))

    def OodleLZ_FillSeekTable (
        self,
        pTable : PTR(OodleLZ_SeekTable),
        flags : OodleLZSeekTable_Flags,
        seekChunkLen : OO_S32,
        rawBuf : c_void_p,
        rawLen : OO_SINTa,
        compBuf : c_void_p,
        compLen : OO_SINTa
    ) -> OO_BOOL:
        return OO_BOOL(self._lib.OodleLZ_FillSeekTable(pTable, flags, seekChunkLen, rawBuf, rawLen, compBuf, compLen))

    def OodleLZ_CreateSeekTable (
        self,
        flags : OodleLZSeekTable_Flags,
        seekChunkLen : OO_S32,
        rawBuf : c_void_p,
        rawLen : OO_SINTa,
        compBuf : c_void_p,
        compLen : OO_SINTa
    ) -> PTR(OodleLZ_SeekTable):
        return self._lib.OodleLZ_CreateSeekTable(flags, seekChunkLen, rawBuf, rawLen, compBuf, compLen)

    def OodleLZ_FreeSeekTable (self, pTable : PTR(OodleLZ_SeekTable)) -> None:
        return self._lib.OodleLZ_FreeSeekTable(pTable)

    def OodleLZ_CheckSeekTableCRCs (
        self,
        rawBuf : c_void_p,
        rawLen : OO_SINTa,
        seekTable : PTR(OodleLZ_SeekTable)
    ) -> OO_BOOL:
        return OO_BOOL(self._lib.OodleLZ_CheckSeekTableCRCs(rawBuf, rawLen, seekTable))

    def OodleLZ_FindSeekEntry (
        self,
        rawPos : OO_S64,
        seekTable : PTR(OodleLZ_SeekTable)
    ) -> OO_S32:
        return OO_S32(self._lib.OodleLZ_FindSeekEntry(rawPos, seekTable))

    def OodleLZ_GetSeekEntryPackedPos (
        self,
        seekI : OO_S32,
        seekTable : PTR(OodleLZ_SeekTable)
    ) -> OO_S64:
        return OO_S64(self._lib.OodleLZ_GetSeekEntryPackedPos(seekI, seekTable))

    def OodleLZ_CompressionLevel_GetName (self, compressSelect : OodleLZ_CompressionLevel) -> c_char_p:
        return c_char_p(self._lib.OodleLZ_CompressionLevel_GetName(compressSelect))

    def OodleLZ_Compressor_GetName (self, compressor : OodleLZ_Compressor) -> c_char_p:
        return c_char_p(self._lib.OodleLZ_Compressor_GetName(compressor))

    def OodleLZ_Jobify_GetName (self, jobify : OodleLZ_Jobify) -> c_char_p:
        return c_char_p(self._lib.OodleLZ_Jobify_GetName(jobify))

    def OodleLZ_CompressOptions_GetDefault (
        self,
        compressor : OodleLZ_Compressor = None,
        lzLevel : OodleLZ_CompressionLevel = None
    ) -> PTR(OodleLZ_CompressOptions):
        if compressor is None:
            compressor = OodleLZ_Compressor.Invalid

        if lzLevel is None:
            lzLevel = OodleLZ_CompressionLevel.Normal

        return self._lib.OodleLZ_CompressOptions_GetDefault(compressor, lzLevel)

    def OodleLZ_CompressOptions_Validate (self, pOptions : PTR(OodleLZ_CompressOptions)) -> None:
        return self._lib.OodleLZ_CompressOptions_Validate(pOptions)

    def OodleLZ_Compressor_UsesWholeBlockQuantum (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        return self.OodleLZ_Compressor_IsNewLZFamily(compressor)

    def OodleLZ_Compressor_UsesLargeWindow (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        return OO_BOOL(not self.OodleLZ_Compressor_CanDecodeInCircularWindow(compressor).value)

    # noinspection PyMethodMayBeStatic
    def OodleLZ_Compressor_CanDecodeInCircularWindow (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        if OODLE_ALLOW_DEPRECATED_COMPRESSORS:
            return OO_BOOL(compressor in [
                OodleLZ_Compressor.LZH,
                OodleLZ_Compressor.LZB16,
            ])

        return OO_BOOL(0)

    def OodleLZ_Compressor_CanDecodeThreadPhased (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        return self.OodleLZ_Compressor_IsNewLZFamily(compressor)

    # noinspection PyMethodMayBeStatic
    def OodleLZ_Compressor_CanDecodeInPlace (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        return OO_BOOL(compressor != OodleLZ_Compressor.Invalid)

    # noinspection PyMethodMayBeStatic
    def OodleLZ_Compressor_MustDecodeWithoutResets (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        if OODLE_ALLOW_DEPRECATED_COMPRESSORS:
            return OO_BOOL(compressor in [
                OodleLZ_Compressor.BitKnit,
                OodleLZ_Compressor.LZA,
                OodleLZ_Compressor.LZNA,
            ])

        return OO_BOOL(0)

    # noinspection PyMethodMayBeStatic
    def OodleLZ_Compressor_IsNewLZFamily (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        return OO_BOOL(compressor in [
            OodleLZ_Compressor.Kraken,
            OodleLZ_Compressor.Leviathan,
            OodleLZ_Compressor.Mermaid,
            OodleLZ_Compressor.Selkie,
            OodleLZ_Compressor.Hydra,
        ])

    # noinspection PyMethodMayBeStatic
    def OodleLZ_Compressor_CanDecodeFuzzSafe (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        if OODLE_ALLOW_DEPRECATED_COMPRESSORS:
            return OO_BOOL(compressor in [
                OodleLZ_Compressor.Kraken,
                OodleLZ_Compressor.Leviathan,
                OodleLZ_Compressor.Mermaid,
                OodleLZ_Compressor.Selkie,
                OodleLZ_Compressor.Hydra,
                OodleLZ_Compressor.BitKnit,
                OodleLZ_Compressor.LZB16,
            ])

        return OO_BOOL(compressor != OodleLZ_Compressor.Invalid)

    # noinspection PyMethodMayBeStatic
    def OodleLZ_Compressor_RespectsDictionarySize (self, compressor : OodleLZ_Compressor) -> OO_BOOL:
        if OODLE_ALLOW_DEPRECATED_COMPRESSORS:
            return OO_BOOL(compressor in [
                OodleLZ_Compressor.Kraken,
                OodleLZ_Compressor.Leviathan,
                OodleLZ_Compressor.Mermaid,
                OodleLZ_Compressor.Selkie,
                OodleLZ_Compressor.Hydra,
                OodleLZ_Compressor.LZNA,
                OodleLZ_Compressor.BitKnit,
            ])

        return OO_BOOL(compressor != OodleLZ_Compressor.Invalid)

    def OodleLZ_GetCompressScratchMemBound (
        self,
        compressor : OodleLZ_Compressor,
        level : OodleLZ_CompressionLevel,
        rawLen : OO_SINTa,
        pOptions : PTR(OodleLZ_CompressOptions) = None
    ) -> OO_SINTa:
        return OO_SINTa(self._lib.OodleLZ_GetCompressScratchMemBound(compressor, level, rawLen, pOptions))

    def OodleLZ_GetCompressedBufferSizeNeeded (self, compressor : OodleLZ_Compressor, rawSize : OO_SINTa) -> OO_SINTa:
        return OO_SINTa(self._lib.OodleLZ_GetCompressedBufferSizeNeeded(compressor, rawSize))

    def OodleLZ_GetDecodeBufferSize (
        self,
        compressor : OodleLZ_Compressor,
        rawSize : OO_SINTa,
        corruptionPossible : OO_BOOL
    ) -> OO_SINTa:
        return OO_SINTa(self._lib.OodleLZ_GetDecodeBufferSize(compressor, rawSize, corruptionPossible))

    def OodleLZ_GetInPlaceDecodeBufferSize (
        self,
        compressor : OodleLZ_Compressor,
        compLen : OO_SINTa,
        rawLen : OO_SINTa
    ) -> OO_SINTa:
        return OO_SINTa(self._lib.OodleLZ_GetInPlaceDecodeBufferSize(compressor, compLen, rawLen))

    def OodleLZ_GetCompressedStepForRawStep (
        self,
        compPtr : c_void_p,
        compAvail : OO_SINTa,
        startRawPos : OO_SINTa,
        rawSeekBytes : OO_SINTa,
        pEndRawPos : PTR(OO_SINTa) = None,
        pIndependent : PTR(OO_BOOL) = None
    ) -> OO_SINTa:
        return OO_SINTa(self._lib.OodleLZ_GetCompressedStepForRawStep(
            compPtr,
            compAvail,
            startRawPos,
            rawSeekBytes,
            pEndRawPos,
            pIndependent
        ))

    def OodleLZ_GetAllChunksCompressor (
        self,
        compBuf : c_void_p,
        compBufSize : OO_SINTa,
        rawLen : OO_SINTa
    ) -> OodleLZ_Compressor:
        return self._lib.OodleLZ_GetAllChunksCompressor(compBuf, compBufSize, rawLen)

    def OodleLZ_GetFirstChunkCompressor (
        self,
        compChunkPtr : c_void_p,
        compBufAvail : OO_SINTa,
        pIndependent : PTR(OO_BOOL)
    ) -> OodleLZ_Compressor:
        return self._lib.OodleLZ_GetFirstChunkCompressor(compChunkPtr, compBufAvail, pIndependent)

    def OodleLZ_GetChunkCompressor (
        self,
        compChunkPtr : c_void_p,
        compBufAvail : OO_SINTa,
        pIndependent : PTR(OO_BOOL)
    ) -> OodleLZ_Compressor:
        return self._lib.OodleLZ_GetChunkCompressor(compChunkPtr, compBufAvail, pIndependent)

    def Oodle_CheckVersion (
        self,
        oodle_header_version : OO_U32,
        pOodleLibVersion : PTR(OO_U32) = None
    ) -> OO_BOOL:
        return OO_BOOL(self._lib.Oodle_CheckVersion(oodle_header_version, pOodleLibVersion))

    def Oodle_LogHeader (self) -> None:
        return self._lib.Oodle_LogHeader()


# ----------------------------------------------------------------------------------------------------------------------

# Enums
# -----------------------------------------------

class Verbosity (Enum):
    No      = OodleLZ_Verbosity.No.value
    Minimal = OodleLZ_Verbosity.Minimal.value
    Some    = OodleLZ_Verbosity.Some.value
    Lots    = OodleLZ_Verbosity.Lots.value


class Compressor (Enum):
    Invalid    = OodleLZ_Compressor.Invalid.value
    No         = OodleLZ_Compressor.No.value
    Kraken     = OodleLZ_Compressor.Kraken.value
    Leviathan  = OodleLZ_Compressor.Leviathan.value
    Mermaid    = OodleLZ_Compressor.Mermaid.value
    Selkie     = OodleLZ_Compressor.Selkie.value
    Hydra      = OodleLZ_Compressor.Hydra.value

    if OODLE_ALLOW_DEPRECATED_COMPRESSORS:
        BitKnit = OodleLZ_Compressor.BitKnit.value
        LZB16   = OodleLZ_Compressor.LZB16.value
        LZNA    = OodleLZ_Compressor.LZNA.value
        LZH     = OodleLZ_Compressor.LZH.value
        LZHLW   = OodleLZ_Compressor.LZHLW.value
        LZNIB   = OodleLZ_Compressor.LZNIB.value
        LZBLW   = OodleLZ_Compressor.LZBLW.value
        LZA     = OodleLZ_Compressor.LZA.value

    Count = OodleLZ_Compressor.Count.value


class PackedRawOverlap (Enum):
    No  = OodleLZ_PackedRawOverlap.No.value
    Yes = OodleLZ_PackedRawOverlap.Yes.value


class CheckCRC (Enum):
    No  = OodleLZ_CheckCRC.No.value
    Yes = OodleLZ_CheckCRC.Yes.value


class Profile (Enum):
    Main    = OodleLZ_Profile.Main.value
    Reduced = OodleLZ_Profile.Reduced.value


class DecompressCallbackRet (Enum):
    Continue = OodleDecompressCallbackRet.Continue.value
    Cancel   = OodleDecompressCallbackRet.Cancel.value
    Invalid  = OodleDecompressCallbackRet.Invalid.value


class CompressionLevel (Enum):
    No         = OodleLZ_CompressionLevel.No.value
    SuperFast  = OodleLZ_CompressionLevel.SuperFast.value
    VeryFast   = OodleLZ_CompressionLevel.VeryFast.value
    Fast       = OodleLZ_CompressionLevel.Fast.value
    Normal     = OodleLZ_CompressionLevel.Normal.value
    Optimal1   = OodleLZ_CompressionLevel.Optimal1.value
    Optimal2   = OodleLZ_CompressionLevel.Optimal2.value
    Optimal3   = OodleLZ_CompressionLevel.Optimal3.value
    Optimal4   = OodleLZ_CompressionLevel.Optimal4.value
    Optimal5   = OodleLZ_CompressionLevel.Optimal5.value
    HyperFast1 = OodleLZ_CompressionLevel.HyperFast1.value
    HyperFast2 = OodleLZ_CompressionLevel.HyperFast2.value
    HyperFast3 = OodleLZ_CompressionLevel.HyperFast3.value
    HyperFast4 = OodleLZ_CompressionLevel.HyperFast4.value
    HyperFast  = OodleLZ_CompressionLevel.HyperFast.value
    Optimal    = OodleLZ_CompressionLevel.Optimal.value
    Max        = OodleLZ_CompressionLevel.Max.value
    Min        = OodleLZ_CompressionLevel.Min.value
    Invalid    = OodleLZ_CompressionLevel.Invalid.value


class Jobify (Enum):
    Default    = OodleLZ_Jobify.Default.value
    Disable    = OodleLZ_Jobify.Disable.value
    Normal     = OodleLZ_Jobify.Normal.value
    Aggressive = OodleLZ_Jobify.Aggressive.value
    Count      = OodleLZ_Jobify.Count.value


class DecodeThreadPhase (Enum):
    One        = OodleLZ_Decode_ThreadPhase.One.value
    Two        = OodleLZ_Decode_ThreadPhase.Two.value
    All        = OodleLZ_Decode_ThreadPhase.All.value
    Unthreaded = OodleLZ_Decode_ThreadPhase.Unthreaded.value


class FuzzSafe (Enum):
    No  = OodleLZ_FuzzSafe.No.value
    Yes = OodleLZ_FuzzSafe.Yes.value


class SeekTableFlags (Enum):
    No          = OodleLZSeekTable_Flags.No.value
    MakeRawCRCs = OodleLZSeekTable_Flags.MakeRawCRCs.value


class UsageWarnings (Enum):
    Enabled  = Oodle_UsageWarnings.Enabled.value
    Disabled = Oodle_UsageWarnings.Disabled.value


# Structures
# -----------------------------------------------

class Decoder:
    pass


class CompressOptions:
    def __init__ (self):
        self.minMatchLen : int             = 0
        self.seekChunkReset : bool         = False
        self.seekChunkLen : int            = 0
        self.profile : Profile             = Profile.Main
        self.dictionarySize : int          = 0
        self.spaceSpeedTradeoffBytes : int = OODLELZ_SPACESPEEDTRADEOFFBYTES_DEFAULT
        self.sendQuantumCRCs : bool        = False
        self.maxLocalDictionarySize : int  = 0
        self.makeLongRangeMatcher : bool   = False
        self.matchTableSizeLog2 : int      = 0
        self.jobify : Jobify               = Jobify.Default
        self.jobifyUserPtr : None          = None  # TODO
        self.farMatchMinLen : int          = 0
        self.farMatchOffsetLog2 : int      = 0

    @staticmethod
    def fromOodle (options : OodleLZ_CompressOptions) -> 'CompressOptions':
        newOptions = CompressOptions()

        newOptions.minMatchLen             = options.minMatchLen
        newOptions.seekChunkReset          = bool(options.seekChunkReset)
        newOptions.seekChunkLen            = options.seekChunkLen
        newOptions.profile                 = Profile(options.profile.value)
        newOptions.dictionarySize          = options.dictionarySize
        newOptions.spaceSpeedTradeoffBytes = options.spaceSpeedTradeoffBytes
        newOptions.sendQuantumCRCs         = bool(options.sendQuantumCRCs)
        newOptions.maxLocalDictionarySize  = options.maxLocalDictionarySize
        newOptions.makeLongRangeMatcher    = bool(options.makeLongRangeMatcher)
        newOptions.matchTableSizeLog2      = options.matchTableSizeLog2
        newOptions.jobify                  = Jobify(options.jobify.value)
        newOptions.jobifyUserPtr           = None  # TODO
        newOptions.farMatchMinLen          = options.farMatchMinLen
        newOptions.farMatchOffsetLog2      = options.farMatchOffsetLog2

        return newOptions

    def toOodle (self) -> OodleLZ_CompressOptions:
        options = OodleLZ_CompressOptions()

        options.unused_was_verbosity    = OO_U32(0)
        options.minMatchLen             = OO_S32(self.minMatchLen)
        options.seekChunkReset          = OO_BOOL(self.seekChunkReset)
        options.seekChunkLen            = OO_S32(self.seekChunkLen)
        options.profile                 = OodleLZ_Profile(self.profile.value)
        options.dictionarySize          = OO_S32(self.dictionarySize)
        options.spaceSpeedTradeoffBytes = OO_S32(self.spaceSpeedTradeoffBytes)
        options.unused_was_maxHuffmansPerChunk = OO_S32(0)
        options.sendQuantumCRCs         = OO_BOOL(self.sendQuantumCRCs)
        options.maxLocalDictionarySize  = OO_S32(self.maxLocalDictionarySize)
        options.makeLongRangeMatcher    = OO_BOOL(self.makeLongRangeMatcher)
        options.matchTableSizeLog2      = OO_S32(self.matchTableSizeLog2)
        options.jobify                  = OodleLZ_Jobify(self.jobify.value)
        options.jobifyUserPtr           = None  # TODO
        options.farMatchMinLen          = OO_S32(self.farMatchMinLen)
        options.farMatchOffsetLog2      = OO_S32(self.farMatchOffsetLog2)
        options.reserved                = (OO_U32 * 4)()

        return options


class DecodeSomeOut:
    def __init__ (self):
        self.decodedCount : int      = 0
        self.compBufUsed : int       = 0
        self.curQuantumRawLen : int  = 0
        self.curQuantumCompLen : int = 0

    @staticmethod
    def fromOodle (out : OodleLZ_DecodeSome_Out) -> 'DecodeSomeOut':
        newOut = DecodeSomeOut()

        newOut.decodedCount      = out.decodedCount
        newOut.compBufUsed       = out.compBufUsed
        newOut.curQuantumRawLen  = out.curQuantumRawLen
        newOut.curQuantumCompLen = out.curQuantumCompLen

        return newOut

    def toOodle (self) -> OodleLZ_DecodeSome_Out:
        out = OodleLZ_DecodeSome_Out()

        out.decodedCount      = OO_S32(self.decodedCount)
        out.compBufUsed       = OO_S32(self.compBufUsed)
        out.curQuantumRawLen  = OO_S32(self.curQuantumRawLen)
        out.curQuantumCompLen = OO_S32(self.curQuantumCompLen)

        return out


class SeekTable:
    def __init__ (self):
        self.compressor : Compressor      = Compressor.No
        self.seekChunksIndependent : bool = False
        self.totalRawLen : int            = 0
        self.totalCompLen : int           = 0
        self.numSeekChunks : int          = 0
        self.seekChunkLen : int           = 0
        self.seekChunkCompLens : None     = None  # TODO
        self.rawCRCs : None               = None  # TODO

    @staticmethod
    def fromOodle (seekTable : OodleLZ_SeekTable) -> 'SeekTable':
        newSeekTable = SeekTable()

        newSeekTable.compressor            = Compressor(seekTable.compressor.value)
        newSeekTable.seekChunksIndependent = bool(seekTable.seekChunksIndependent)
        newSeekTable.totalRawLen           = seekTable.totalRawLen
        newSeekTable.totalCompLen          = seekTable.totalCompLen
        newSeekTable.numSeekChunks         = seekTable.numSeekChunks
        newSeekTable.seekChunkLen          = seekTable.seekChunkLen
        newSeekTable.seekChunkCompLens     = seekTable.seekChunkCompLens  # TODO
        newSeekTable.rawCRCs               = seekTable.rawCRCs            # TODO

        return newSeekTable

    def toOodle (self) -> OodleLZ_SeekTable:
        seekTable = OodleLZ_SeekTable()

        seekTable.compressor            = OodleLZ_Compressor(self.compressor.value)
        seekTable.seekChunksIndependent = OO_BOOL(self.seekChunksIndependent)
        seekTable.totalRawLen           = OO_S64(self.totalRawLen)
        seekTable.totalCompLen          = OO_S64(self.totalCompLen)
        seekTable.numSeekChunks         = OO_S32(self.numSeekChunks)
        seekTable.seekChunkLen          = OO_S32(self.seekChunkLen)
        seekTable.seekChunkCompLens     = self.seekChunkCompLens  # TODO PTR(OO_U32)
        seekTable.rawCRCs               = self.rawCRCs            # TODO PTR(OO_U32)

        return seekTable


class ConfigValues:
    def __init__ (self):
        self.LWLRMStep : int                       = 0
        self.LWLRMHashLength : int                 = 0
        self.LWLRMJumpBits : int                   = 0
        self.decoderMaxStackSize : int             = 0
        self.smallBufferLZFallbackSizeUnused : int = 0
        self.backwardsCompatibleMajorVersion : int = 0
        self.headerVersion : int                   = 0

    @staticmethod
    def fromOodle (config : OodleConfigValues) -> 'ConfigValues':
        newConfig = ConfigValues()

        newConfig.LWLRMStep                       = config.m_OodleLZ_LW_LRM_step
        newConfig.LWLRMHashLength                 = config.m_OodleLZ_LW_LRM_hashLength
        newConfig.LWLRMJumpBits                   = config.m_OodleLZ_LW_LRM_jumpbits
        newConfig.decoderMaxStackSize             = config.m_OodleLZ_Decoder_Max_Stack_Size
        newConfig.smallBufferLZFallbackSizeUnused = config.m_OodleLZ_Small_Buffer_LZ_Fallback_Size_Unused
        newConfig.backwardsCompatibleMajorVersion = config.m_OodleLZ_BackwardsCompatible_MajorVersion
        newConfig.headerVersion                   = config.m_oodle_header_version

        return newConfig

    def toOodle (self) -> OodleConfigValues:
        config = OodleConfigValues()

        config.m_OodleLZ_LW_LRM_step                          = OO_S32(self.LWLRMStep)
        config.m_OodleLZ_LW_LRM_hashLength                    = OO_S32(self.LWLRMHashLength)
        config.m_OodleLZ_LW_LRM_jumpbits                      = OO_S32(self.LWLRMJumpBits)
        config.m_OodleLZ_Decoder_Max_Stack_Size               = OO_S32(self.decoderMaxStackSize)
        config.m_OodleLZ_Small_Buffer_LZ_Fallback_Size_Unused = OO_S32(self.smallBufferLZFallbackSizeUnused)
        config.m_OodleLZ_BackwardsCompatible_MajorVersion     = OO_S32(self.backwardsCompatibleMajorVersion)
        config.m_oodle_header_version                         = OO_U32(self.headerVersion)

        return config



BufferType = CArray[c_uint8]

def createBuffer (
    size : Union[int, None] = None,
    data : Union[bytes, bytearray, None] = None
) -> BufferType:
    if isinstance(data, bytes):
        data = bytearray(data)

    if not isinstance(size, int) and not isinstance(data, bytearray):
        raise Exception('Neither data nor buffer size is specified')

    bufferSize = size if isinstance(size, int) else len(data)
    bufferType = c_uint8 * bufferSize

    if isinstance(data, bytearray):
        return bufferType.from_buffer(data)
    else:
        return bufferType()


class PyOodleWrap:
    def __init__ (self, libPathOrDir : Union[str, None] = None):
        self._lib : PyOodleCore = PyOodleCore(libPathOrDir)

    def getLib (self) -> PyOodleCore:
        return self._lib

    def getConfig (self) -> ConfigValues:
        _config = OodleConfigValues()

        self._lib.Oodle_GetConfigValues(_config)

        return ConfigValues.fromOodle(_config)

    def setConfig (self, config : ConfigValues) -> None:
        return self._lib.Oodle_SetConfigValues(config.toOodle())

    def setUsageWarnings (self, state : UsageWarnings) -> None:
        return self._lib.Oodle_SetUsageWarnings(Oodle_UsageWarnings(state.value))

    # OodleCore_Plugins_SetAllocators
    # OodleCore_Plugins_SetJobSystem
    # OodleCore_Plugins_SetJobSystemAndCount

    # TODO: deal with va_list...
    def setPrintF (
        self,
        fn : Callable[[int, str, int, str], None]
    ) -> Callable[[int, str, int, str], None]:
        def fnWrap (verboseLevel : int, file : bytes, line : int, fmt : bytes, *args) -> None:
            return fn(verboseLevel, file.decode('utf-8'), line, fmt.decode('utf-8'), *args)  # TODO

        prevFn = self._lib.OodleCore_Plugins_SetPrintf(t_fp_OodleCore_Plugin_Printf(fnWrap))

        def prevFnWrap (verboseLevel : int, file : str, line : int, fmt : str, *args) -> None:
            return prevFn(
                c_int(verboseLevel),
                c_char_p(file.encode('utf-8')),
                c_int(line),
                c_char_p(fmt.encode('utf-8')),
                *args
            )

        return prevFnWrap

    # OodleCore_Plugins_SetAssertion
    # OodleCore_Plugin_MallocAligned_Default
    # OodleCore_Plugin_Free_Default

    def printFDefault (self, verboseLevel : int, file : str, line : int, fmt : str, *args) -> None:  # TODO: test ...
        return self._lib.OodleCore_Plugin_Printf_Default(
            c_int(verboseLevel),
            c_char_p(file.encode('utf-8')),
            c_int(line),
            c_char_p(fmt.encode('utf-8')),
            *args
        )

    def printFVerbose (self, verboseLevel : int, file : str, line : int, fmt : str, *args) -> None:  # TODO: test ...
        return self._lib.OodleCore_Plugin_Printf_Verbose(
            c_int(verboseLevel),
            c_char_p(file.encode('utf-8')),
            c_int(line),
            c_char_p(fmt.encode('utf-8')),
            *args
        )

    def displayAssertDefault (
        self,
        file : str,
        line : int,
        function : str,
        message : str
    ) -> bool:
        return bool(self._lib.OodleCore_Plugin_DisplayAssertion_Default(
            c_char_p(file.encode('utf-8')),
            c_int(line),
            c_char_p(function.encode('utf-8')),
            c_char_p(message.encode('utf-8'))
        ))

    # OodleCore_Plugin_RunJob_Default
    # OodleCore_Plugin_WaitJob_Default

    def compress (
        self,
        compressor : Compressor,
        data : bytes,
        level : CompressionLevel,
        options : CompressOptions = None,
        dictionaryBase : c_void_p = None,  # TODO
        lrm : c_void_p = None,             # TODO
        scratchBuffer : Union[BufferType, None] = None,
    ) -> Union[bytes, None]:
        _compressor = OodleLZ_Compressor(compressor.value)

        _rawLen = OO_SINTa(len(data))
        _rawBuf = cast(createBuffer(_rawLen.value, data), c_void_p)

        compBufferSize = self._lib.OodleLZ_GetCompressedBufferSizeNeeded(_compressor, _rawLen)
        compBuffer = createBuffer(compBufferSize.value)
        _compBuf = cast(compBuffer, c_void_p)

        _level = OodleLZ_CompressionLevel(level.value)
        _pOptions = options.toOodle() if options else None
        # TODO: dictionaryBase
        # TODO: lrm

        if scratchBuffer:
            _scratchSize = OO_SINTa(len(scratchBuffer))
            _scratchMem = cast(scratchBuffer, c_void_p)
        else:
            _scratchSize = OO_SINTa(0)
            _scratchMem = None

        compDataSize = self._lib.OodleLZ_Compress(
            _compressor,
            _rawBuf,
            _rawLen,
            _compBuf,
            _level,
            _pOptions,
            dictionaryBase,  # TODO
            lrm,             # TODO
            _scratchMem,
            _scratchSize
        ).value

        if compDataSize == OODLELZ_FAILED:
            return None
        else:
            # noinspection PyTypeChecker
            return bytes(compBuffer[:compDataSize])

    def decompress (
        self,
        compData : Union[bytes, bytearray],
        rawDataSize : int,
        fuzzSafe : FuzzSafe = FuzzSafe.Yes,
        checkCRC : CheckCRC = CheckCRC.No,
        verbosity : Verbosity = Verbosity.No,
        decBufBase : c_void_p = None,  # TODO
        decBufSize : int = 0,          # TODO
        callback : Callable[[], DecompressCallbackRet] = None,
        callbackUserData : Union[bytes, bytearray, None] = None,
        decoderMemory : Union[bytes, bytearray, None] = None,
        threadPhase : DecodeThreadPhase = DecodeThreadPhase.Unthreaded
    ) -> Union[bytearray, None]:
        _compBuf = cast(createBuffer(data = compData), c_void_p)
        _compBufSize = OO_SINTa(len(compData))

        rawBuffer = createBuffer(size = rawDataSize)

        _rawBuf = cast(rawBuffer, c_void_p)
        _rawLen = OO_SINTa(rawDataSize)

        _fuzzSafe = OodleLZ_FuzzSafe(fuzzSafe.value)
        _checkCRC = OodleLZ_CheckCRC(checkCRC.value)
        _verbosity = OodleLZ_Verbosity(verbosity.value)

        _decBufBase = None                  # TODO: decBufBase
        _decBufSize = OO_SINTa(decBufSize)  # TODO: decBufSize

        if callback:
            def fn (
                userdata : c_void_p,
                rawBuf : PTR(OO_U8),
                rawLen : OO_SINTa,
                compBuf : PTR(OO_U8),
                compBufferSize : OO_SINTa,
                rawDone : OO_SINTa,
                compUsed : OO_SINTa,
            ) -> int:
                result = callback(rawBuf.contents)
                return OodleDecompressCallbackRet(result.value).value

            _fpCallback = OodleDecompressCallback(fn)
        else:
            _fpCallback = None

        # TODO: pass Any data
        if isinstance(callbackUserData, bytes) or isinstance(callbackUserData, bytearray):
            _callbackUserData = cast(createBuffer(data = callbackUserData), c_void_p)
        else:
            _callbackUserData = None

        if decoderMemory:
            _decoderMemory = cast(createBuffer(data = decoderMemory), c_void_p)
            _decoderMemorySize = OO_SINTa(len(decoderMemory))
        else:
            _decoderMemory = None
            _decoderMemorySize = OO_SINTa(0)

        _threadPhase = OodleLZ_Decode_ThreadPhase(threadPhase.value)

        decompDataSize = self._lib.OodleLZ_Decompress(
            _compBuf,
            _compBufSize,
            _rawBuf,
            _rawLen,
            _fuzzSafe,
            _checkCRC,
            _verbosity,
            _decBufBase,
            _decBufSize,
            _fpCallback,
            _callbackUserData,
            _decoderMemory,
            _decoderMemorySize,
            _threadPhase
        ).value

        if decompDataSize == OODLELZ_FAILED:
            return None
        else:
            # noinspection PyTypeChecker
            return bytearray(rawBuffer[:decompDataSize])



    '''
    OodleDecompressCallback = PYOODLE_CALLBACK_TYPE(
        OodleDecompressCallbackRet,  # return type
        c_void_p,                    # arg0: userdata
        PTR(OO_U8),                  # arg1: rawBuf
        OO_SINTa,                    # arg2: rawLen
        PTR(OO_U8),                  # arg3: compBuf
        OO_SINTa,                    # arg4: compBufferSize
        OO_SINTa,                    # arg5: rawDone
        OO_SINTa,                    # arg6: compUsed
    )
    '''

    def getCompressBufferSize (self, compressor : Compressor, rawDataSize : int) -> int:
        _compressor = OodleLZ_Compressor(compressor.value)
        _rawSize = OO_SINTa(rawDataSize)

        return self._lib.OodleLZ_GetCompressedBufferSizeNeeded(_compressor, _rawSize).value

    def getDefaultCompressOptions (
        self,
        compressor : Union[Compressor, None] = None,
        level : Union[CompressionLevel, None] = None
    ) -> CompressOptions:
        if compressor is None:
            _compressor = OodleLZ_Compressor.Invalid
        else:
            _compressor = OodleLZ_Compressor(compressor.value)

        if level is None:
            _lzLevel = OodleLZ_CompressionLevel.Normal
        else:
            _lzLevel = OodleLZ_CompressionLevel(level.value)

        _compOptions = self._lib.OodleLZ_CompressOptions_GetDefault(_compressor, _lzLevel)

        return CompressOptions.fromOodle(_compOptions.contents)



def _test_ ():
    lib = PyOodleWrap(r'C:\Projects\DataCoding\compressors\oo2core_9_win64.dll')

    def printF (verboseLevel : int, file : str, line : int, fmt : str, *args) -> None:
        print(verboseLevel, file, line, fmt, *args)

    lib.setPrintF(printF)    

    with open(r"C:\Projects\HLW\static\game.zip", 'rb') as f:
        data = f.read()

    dataSize = len(data)

    import time

    _start = time.time()

    print('Compressing')

    compData = lib.compress(Compressor.Kraken, data, CompressionLevel.Optimal5, CompressOptions())
    compDataSize = len(compData)
    percent = round(compDataSize / dataSize * 100)

    print(dataSize, compDataSize, f'{percent:d}%')

    def cb (*args) -> DecompressCallbackRet:
        print('msg:', *args)
        return DecompressCallbackRet.Continue   

    print(time.time() - _start)     

    print('Decompressing')

    _start = time.time()

    decompData = lib.decompress(compData, dataSize, callback = cb, verbosity = Verbosity.No)

    print(time.time() - _start)  

    return 

    # with open('./sample_data/core.js', 'rb') as f:
    #     data = f.read()
    #     # 1276441 216983
    #     compData = lib.compress(Compressor.Leviathan, data, CompressionLevel.Optimal5, CompressOptions())
    #     print(len(data), len(compData))

    def printF (verboseLevel : int, file : str, line : int, fmt : str, *args) -> None:
        print(verboseLevel, file, line, fmt, *args)

    lib.setPrintF(printF)
    lib.setPrintF(printF)
    lib.getLib().Oodle_LogHeader()
    lib.printFDefault(1, 'A', 2, 'B')
    lib.displayAssertDefault('file', 1, 'function', 'message')

    def cb (*args) -> DecompressCallbackRet:
        print(*args)
        return DecompressCallbackRet.Continue

    data = bytes(range(256)) * 4000
    dataSize = len(data)
    compData = lib.compress(Compressor.Leviathan, data, CompressionLevel.Optimal5, CompressOptions())
    print(dataSize, len(compData))
    decompData = lib.decompress(compData, dataSize, callback = cb, verbosity = Verbosity.No)
    print(len(decompData), data == decompData)



if __name__ == '__main__':
    _test_()
