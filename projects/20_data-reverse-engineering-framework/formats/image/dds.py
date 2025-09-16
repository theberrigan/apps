# https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) 

from bfw.utils import *
from bfw.reader import *

from bfw.fs.scan.collecting import GLOBAL_SAMPLES_DIR, collectSamplesInFile, iterSamplesInFile



DDS_SAMPLES_DIR  = joinPath(GLOBAL_SAMPLES_DIR, 'dds')
DDS_SAMPLES_PATH = joinPath(GLOBAL_SAMPLES_DIR, 'dds.bin')
DDS_EXT = '.dds'
DDS_SIGNATURE = b'DDS '
DDS_HEADER_SIZE = 124
DDS_PIXFMT_SIZE = 32


class DDSCompressionType:
    DXT1 = b'DXT1'
    DXT2 = b'DXT2'
    DXT3 = b'DXT3'
    DXT4 = b'DXT4'
    DXT5 = b'DXT5'
    DX10 = b'DX10'  # See DDS_HEADER_DXT10.dxgiFormat for actual format

    @classmethod
    def isSupported (cls, compType):
        return compType in [
            cls.DXT1,
            cls.DXT2,
            cls.DXT3,
            cls.DXT4,
            cls.DXT5,
            cls.DX10,
        ]


# DDPF_*
class DDSPxFmtFlag:
    AlphaPx   = 1 << 0   # Texture contains alpha data; dwRGBAlphaBitMask contains valid data
    Alpha     = 1 << 1   # Used in some older DDS files for alpha channel only uncompressed data (dwRGBBitCount contains the alpha channel bitcount; dwABitMask contains valid data)
    FourCC    = 1 << 2   # Texture contains compressed RGB data; dwFourCC contains valid data
    RGB       = 1 << 6   # Texture contains uncompressed RGB data; dwRGBBitCount and the RGB masks (dwRBitMask, dwGBitMask, dwBBitMask) contain valid data
    YUV       = 1 << 9   # Used in some older DDS files for YUV uncompressed data (dwRGBBitCount contains the YUV bit count; dwRBitMask contains the Y mask, dwGBitMask contains the U mask, dwBBitMask contains the V mask)
    Luminance = 1 << 17  # Used in some older DDS files for single channel color uncompressed data (dwRGBBitCount contains the luminance channel bit count; dwRBitMask contains the channel mask). Can be combined with DDPF_ALPHAPIXELS for a two channel DDS file


# DXGI_FORMAT
class DDSDXGIFormat:
    Unknown                = 0
    R32G32B32A32Typeless   = 1
    R32G32B32A32Float      = 2
    R32G32B32A32Uint       = 3
    R32G32B32A32Sint       = 4
    R32G32B32Typeless      = 5
    R32G32B32Float         = 6
    R32G32B32Uint          = 7
    R32G32B32Sint          = 8
    R16G16B16A16Typeless   = 9
    R16G16B16A16Float      = 10
    R16G16B16A16Unorm      = 11
    R16G16B16A16Uint       = 12
    R16G16B16A16Snorm      = 13
    R16G16B16A16Sint       = 14
    R32G32Typeless         = 15
    R32G32Float            = 16
    R32G32Uint             = 17
    R32G32Sint             = 18
    R32G8X24Typeless       = 19
    D32FloatS8X24Uint      = 20
    R32FloatX8X24Typeless  = 21
    X32TypelessG8X24Uint   = 22
    R10G10B10A2Typeless    = 23
    R10G10B10A2Unorm       = 24
    R10G10B10A2Uint        = 25
    R11G11B10Float         = 26
    R8G8B8A8Typeless       = 27
    R8G8B8A8Unorm          = 28
    R8G8B8A8UnormSRGB      = 29
    R8G8B8A8Uint           = 30
    R8G8B8A8Snorm          = 31
    R8G8B8A8Sint           = 32
    R16G16Typeless         = 33
    R16G16Float            = 34
    R16G16Unorm            = 35
    R16G16Uint             = 36
    R16G16Snorm            = 37
    R16G16Sint             = 38
    R32Typeless            = 39
    D32Float               = 40
    R32Float               = 41
    R32Uint                = 42
    R32Sint                = 43
    R24G8Typeless          = 44
    D24UnormS8Uint         = 45
    R24UnormX8Typeless     = 46
    X24TypelessG8Uint      = 47
    R8G8Typeless           = 48
    R8G8Unorm              = 49
    R8G8Uint               = 50
    R8G8Snorm              = 51
    R8G8Sint               = 52
    R16Typeless            = 53
    R16Float               = 54
    D16Unorm               = 55
    R16Unorm               = 56
    R16Uint                = 57
    R16Snorm               = 58
    R16Sint                = 59
    R8Typeless             = 60
    R8Unorm                = 61
    R8Uint                 = 62
    R8Snorm                = 63
    R8Sint                 = 64
    A8Unorm                = 65
    R1Unorm                = 66
    R9G9B9E5SharedExp      = 67
    R8G8B8G8Unorm          = 68
    G8R8G8B8Unorm          = 69
    BC1Typeless            = 70
    BC1Unorm               = 71
    BC1UnormSRGB           = 72
    BC2Typeless            = 73
    BC2Unorm               = 74
    BC2UnormSRGB           = 75
    BC3Typeless            = 76
    BC3Unorm               = 77
    BC3UnormSRGB           = 78
    BC4Typeless            = 79
    BC4Unorm               = 80
    BC4Snorm               = 81
    BC5Typeless            = 82
    BC5Unorm               = 83
    BC5Snorm               = 84
    B5G6R5Unorm            = 85
    B5G5R5A1Unorm          = 86
    B8G8R8A8Unorm          = 87
    B8G8R8X8Unorm          = 88
    R10G10B10XRBiasA2Unorm = 89
    B8G8R8A8Typeless       = 90
    B8G8R8A8UnormSRGB      = 91
    B8G8R8X8Typeless       = 92
    B8G8R8X8UnormSRGB      = 93
    BC6HTypeless           = 94
    BC6HUF16               = 95
    BC6HSF16               = 96
    BC7Typeless            = 97
    BC7Unorm               = 98
    BC7UnormSRGB           = 99
    AYUV                   = 100
    Y410                   = 101
    Y416                   = 102
    NV12                   = 103
    P010                   = 104
    P016                   = 105
    _420Opaque             = 106
    YUY2                   = 107
    Y210                   = 108
    Y216                   = 109
    NV11                   = 110
    AI44                   = 111
    IA44                   = 112
    P8                     = 113
    A8P8                   = 114
    B4G4R4A4Unorm          = 115
    P208                   = 130
    V208                   = 131
    V408                   = 132
    SFMMO                  = 133
    SFMRUO                 = 134
    ForceUint              = 0xFFFFFFFF


# D3D10_RESOURCE_DIMENSION
class DDSDX10ResDim:
    Unknown   = 0
    Buffer    = 1
    Texture1D = 2
    Texture2D = 3
    Texture3D = 4


def checkSignature (f):
    signature = f.read(4)

    if signature != DDS_SIGNATURE:
        raise Exception('Incorrect file signature')


# DDS_PIXELFORMAT 
# https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dds-pixelformat
def readPixFormat (f, dds):
    structSize = f.u32()       # DWORD     dwSize

    if structSize != DDS_PIXFMT_SIZE:
        raise Exception(f'Pixel format struct size is { structSize }, but expected { DDS_PIXFMT_SIZE }')

    dds.pxFmtFlags  = f.u32()       # DWORD dwFlags (DDSPxFmtFlag)
    dds.compType    = f.read(4)     # DWORD dwFourCC

    if not DDSCompressionType.isSupported(dds.compType):
        raise Exception(f'Unsupported compression type { dds.compType }')

    dds.rgbBitCount = f.u32()       # DWORD dwRGBBitCount
    dds.maskR       = f.u32()       # DWORD dwRBitMask
    dds.maskG       = f.u32()       # DWORD dwGBitMask
    dds.maskB       = f.u32()       # DWORD dwBBitMask
    dds.maskA       = f.u32()       # DWORD dwABitMask


# DDS_HEADER
# https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
def readHeader (f, dds):
    structSize = f.u32()       # DWORD     dwSize

    if structSize != DDS_HEADER_SIZE:
        raise Exception(f'Header size is { structSize }, but expected { DDS_HEADER_SIZE }')

    dds.flags       = f.u32()  # DWORD     dwFlags
    dds.height      = f.u32()  # DWORD     dwHeight
    dds.width       = f.u32()  # DWORD     dwWidth
    dds.pitchOrSize = f.u32()  # DWORD     dwPitchOrLinearSize
    dds.depth       = f.u32()  # DWORD     dwDepth
    dds.mipCount    = f.u32()  # DWORD     dwMipMapCount

    f.skip(4 * 11)             # DWORD     dwReserved1[11]

    readPixFormat(f, dds)      # DDS_PXFMT ddspf

    dds.caps        = f.u32()  # DWORD     dwCaps
    dds.caps2       = f.u32()  # DWORD     dwCaps2

    f.skip(4)                  # DWORD     dwCaps3
    f.skip(4)                  # DWORD     dwCaps4
    f.skip(4)                  # DWORD     dwReserved2


# DDS_HEADER_DXT10
# https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dds-header-dxt10
def readHeaderDX10 (f, dds): 
    dds.dxgiFormat = f.u32()  # DXGI_FORMAT              dxgiFormat (DDSDXGIFormat)
    dds.resDim     = f.u32()  # D3D10_RESOURCE_DIMENSION resourceDimension (DDSDX10ResDim)
    dds.miscFlag   = f.u32()  # UINT                     miscFlag
    dds.arraySize  = f.u32()  # UINT                     arraySize
    dds.miscFlags2 = f.u32()  # UINT                     miscFlags2


class DDS:
    def __init__ (self):
        # Header and pixel format
        self.flags       = None
        self.height      = None
        self.width       = None
        self.pitchOrSize = None
        self.depth       = None
        self.mipCount    = None
        self.pxFmtFlags  = None  # DDSPxFmtFlag
        self.compType    = None
        self.rgbBitCount = None
        self.maskR       = None
        self.maskG       = None
        self.maskB       = None
        self.maskA       = None
        self.caps        = None
        self.caps2       = None

        # Header DXT10
        self.dxgiFormat  = None
        self.resDim      = None
        self.miscFlag    = None
        self.arraySize   = None
        self.miscFlags2  = None

    @classmethod
    def fromFile (cls, ddsPath):
        if not isFile(ddsPath):
            raise Exception(f'File does not exist: { ddsPath }')

        with openFile(ddsPath) as f:
            cls._read(f)

    @classmethod
    def fromBuffer (cls, data):
        with MemReader(data) as f:
            cls._read(f)

    @classmethod
    def _read (cls, f):
        dds = DDS()

        checkSignature(f)
        readHeader(f, dds)

        if dds.flags & DDSPxFmtFlag.FourCC and dds.compType == DDSCompressionType.DX10:
            readHeaderDX10(f, dds)
            print(dds.compType, dds.dxgiFormat, dds.arraySize); #sys.exit()






################################################
####               AUXILIARY                ####
################################################

_BLACKLISTED = [
    filePath.lower() for filePath in [

    ]
]

def _collectSamples ():
    def check (filePath, fileSize, fileCRC):
        print(filePath, fileSize, fileCRC)
        return _checkDDS(filePath)        

    collectSamplesInFile(
        rootDirs     = getDrives(True),
        destPath     = DDS_SAMPLES_PATH,
        exts         = [ DDS_EXT ], 
        isRecursive  = True, 
        minSize      = 1, 
        maxSize      = None,
        noDups       = True,
        checkFn      = check
    )

def _checkDDS (filePath):
    if filePath.lower() in _BLACKLISTED:
        return False

    return readBin(filePath, len(DDS_SIGNATURE)) == DDS_SIGNATURE

def _parseSample (ddsPath):
    if _checkDDS(ddsPath):
        print(ddsPath)

        try:
            DDS.fromFile(ddsPath)
        except Exception as e:
            # print('ERROR:', e)
            pass

        print(' ')

def _parseSamplesFromFile (filePath=DDS_SAMPLES_PATH):
    for ddsPath in iterSamplesInFile(filePath):
        _parseSample(ddsPath)

def _parseSamplesFromDir (rootDir=DDS_SAMPLES_DIR):
    for ddsPath in iterFiles(rootDir, True, [ DDS_EXT ]):
        _parseSample(ddsPath)


################################################
####                TESTING                 ####
################################################

def _test_ ():
    pass


################################################
####                 EXPORT                 ####
################################################

__all__ = [
    'DDS'
]



if __name__ == '__main__':
    # _test_()
    # _collectSamples()
    _parseSamplesFromFile()
    # _parseSamplesFromDir()