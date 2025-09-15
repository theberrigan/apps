import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))) 

from bfw.utils import *
from bfw.writer import *
from bfw.native.limits import MAX_U32
from bfw.native.base import *
from bfw.native.windows.types import HWND, BOOL, WCHAR, DWORD


# Channel:
# - HCHANNEL - sample playback channel
# - HSTREAM  - sample stream
# - HMUSIC   - MOD music
# - HRECORD  - recording

BASS_DLLS_DIR = joinPath(BIN_DIR, 'bass')
BASS_DLL_PATH = joinPath(BASS_DLLS_DIR, 'bass.dll')


QWORD   = CI64
HSTREAM = DWORD

NULL = 0

BASS_SAMPLE_FLOAT = 256
BASS_UNICODE      = 0x80000000

BASS_DEVICE_ENABLED    = 1
BASS_DEVICE_DEFAULT    = 2
BASS_DEVICE_INIT       = 4
BASS_DEVICE_LOOPBACK   = 8
BASS_DEVICE_DEFAULTCOM = 128

BASS_DEVICE_TYPE_MASK        = 0xff000000
BASS_DEVICE_TYPE_NETWORK     = 0x01000000
BASS_DEVICE_TYPE_SPEAKERS    = 0x02000000
BASS_DEVICE_TYPE_LINE        = 0x03000000
BASS_DEVICE_TYPE_HEADPHONES  = 0x04000000
BASS_DEVICE_TYPE_MICROPHONE  = 0x05000000
BASS_DEVICE_TYPE_HEADSET     = 0x06000000
BASS_DEVICE_TYPE_HANDSET     = 0x07000000
BASS_DEVICE_TYPE_DIGITAL     = 0x08000000
BASS_DEVICE_TYPE_SPDIF       = 0x09000000
BASS_DEVICE_TYPE_HDMI        = 0x0a000000
BASS_DEVICE_TYPE_DISPLAYPORT = 0x40000000


class BASS_DEVICEINFO (CStruct):
    _fields_ = [
        ('name',   CPtrChar),  # const char *name
        ('driver', CPtrChar),  # const char *driver
        ('flags',  DWORD),     # DWORD flags
    ]


class DeviceInfo:
    def __init__ (self):
        self.id     = None
        self.name   = None
        self.driver = None
        self.flags  = None  # BASS_DEVICE_*
        self.type   = None  # BASS_DEVICE_TYPE_*

    @property
    def isEnabled (self):
        return bool(self.flags & BASS_DEVICE_ENABLED)

    @property
    def isDefault (self):
        return bool(self.flags & BASS_DEVICE_DEFAULT)

    @property
    def isDefaultCom (self):
        return bool(self.flags & BASS_DEVICE_DEFAULTCOM)

    @property
    def isInit (self):
        return bool(self.flags & BASS_DEVICE_INIT)

    @property
    def isLoopBack (self):
        return bool(self.flags & BASS_DEVICE_LOOPBACK)


class Bass:
    _lib = None

    @classmethod
    def getLib (cls):
        if cls._lib is not None:
            return cls._lib

        lib = cls._lib = loadCDLL(BASS_DLL_PATH)

        lib.BASS_ErrorGetCode.restype  = CI32  # int
        lib.BASS_ErrorGetCode.argtypes = []

        lib.BASS_GetDeviceInfo.restype  = BOOL  # BOOL
        lib.BASS_GetDeviceInfo.argtypes = [
            DWORD,                  # arg1: DWORD device
            CPtr(BASS_DEVICEINFO),  # arg2: BASS_DEVICEINFO *info
        ]

        lib.BASS_Init.restype  = BOOL  # BOOL
        lib.BASS_Init.argtypes = [
            CI32,      # arg1: int device
            DWORD,     # arg2: DWORD freq
            DWORD,     # arg3: DWORD flags
            HWND,      # arg4: HWND win
            CPtrVoid,  # arg5: const void *dsguid
        ]

        lib.BASS_Free.restype  = BOOL  # BOOL
        lib.BASS_Free.argtypes = []

        lib.BASS_StreamCreateFile.restype  = HSTREAM  # HSTREAM
        lib.BASS_StreamCreateFile.argtypes = [
            BOOL,      # arg1: BOOL mem
            CPtrVoid,  # arg2: const WCHAR *file
            QWORD,     # arg3: QWORD offset
            QWORD,     # arg4: QWORD length
            DWORD,     # arg5: DWORD flags
        ]

        lib.BASS_StreamFree.restype  = BOOL  # BOOL
        lib.BASS_StreamFree.argtypes = [
            HSTREAM,      # arg1: HSTREAM handle
        ]

        lib.BASS_ChannelPlay.restype  = BOOL  # BOOL
        lib.BASS_ChannelPlay.argtypes = [
            HSTREAM,  # arg1: HSTREAM handle
            BOOL,     # arg1: BOOL restart
        ]

        lib.BASS_ChannelStop.restype  = BOOL  # BOOL
        lib.BASS_ChannelStop.argtypes = [
            HSTREAM,  # arg1: HSTREAM handle
        ]

        return cls._lib

    @classmethod
    def getErrorCode (cls):
        return cls.getLib().BASS_ErrorGetCode()

    @classmethod
    def getDeviceInfo (cls, deviceId):
        lib = cls.getLib()

        bassInfo = BASS_DEVICEINFO()

        if not lib.BASS_GetDeviceInfo(deviceId, bassInfo):
            return None

        info = DeviceInfo()

        info.id     = deviceId
        info.name   = bassInfo.name.decode('ansi')
        info.driver = bassInfo.driver.decode('ansi')
        info.flags  = bassInfo.flags & (BASS_DEVICE_TYPE_MASK ^ MAX_U32)
        info.type   = bassInfo.flags & BASS_DEVICE_TYPE_MASK

        return info

    @classmethod
    def getDevices (cls):
        devices = []
        deviceId = 1

        while True:
            device = cls.getDeviceInfo(deviceId)

            if not device:
                break

            devices.append(device)

            deviceId += 1

        return devices

    @classmethod
    def getDefaultDevice (cls):
        for device in cls.getDevices():
            if device.isDefault:
                return device

        return None

    @classmethod
    def init (cls, deviceId=-1, sampleRate=44100, flags=0):
        lib = cls.getLib()

        if not lib.BASS_Init(deviceId, sampleRate, flags, NULL, NULL):
            raise Exception(f'Failed to init BASS ({ cls.getErrorCode() })')

    @classmethod
    def free (cls):
        lib = cls.getLib()

        if not lib.BASS_Free():
            raise Exception(f'Failed to free BASS ({ cls.getErrorCode() })')

    @classmethod
    def openFileStream (cls, filePath):
        lib = cls.getLib()

        filePath = toCWStr(filePath, True)
        # filePath = CWStr(filePath.encode('utf-16le'))

        stream = lib.BASS_StreamCreateFile(False, filePath, 0, 0, BASS_UNICODE | BASS_SAMPLE_FLOAT)

        if not stream:
            raise Exception(f'Failed to create stream ({ cls.getErrorCode() })')

        return stream

    @classmethod
    def closeStream (cls, stream):
        lib = cls.getLib()

        if not lib.BASS_StreamFree(stream):
            raise Exception(f'Failed to close stream ({ cls.getErrorCode() })')

        return stream

    @classmethod
    def playStream (cls, stream, restart=False):
        lib = cls.getLib()

        if not lib.BASS_ChannelPlay(stream, restart):
            raise Exception(f'Failed to play stream ({ cls.getErrorCode() })')

        return stream

    @classmethod
    def stopStream (cls, stream):
        lib = cls.getLib()

        if not lib.BASS_ChannelStop(stream):
            raise Exception(f'Failed to stop stream ({ cls.getErrorCode() })')

        return stream


        
def _test_ ():
    device = Bass.getDefaultDevice()

    assert device

    pjp(device)

    import time

    Bass.init(device.id)

    # stream = Bass.openFileStream(r'D:\Documents\Музыка\OST - Michael McCann - Deus Ex Human Revolution\DLC The Missing Link\22. DLC RestrictedArea Music.mp3')
    stream = Bass.openFileStream(r'D:\Documents\Аудиобанк\GTA Vice City Radio Comedy (VCPR).mp3')

    Bass.playStream(stream, True)

    time.sleep(5)

    Bass.stopStream(stream)
    Bass.closeStream(stream)

    Bass.free()



__all__ = [
    'Bass'
]



if __name__ == '__main__':
    _test_()



# bass         - MP3, MP2, MP1, OGG, WAV, AIFF, MOD (XM, IT, S3M, MOD, MTM, UMX), MO3 (MP3/OGG compressed MODs), custom generated, and more via OS codecs, and recording functions
# bass_aac     - MP4, AAC, AAC+ Shoutcast
# bass_ac3     - AC3
# bass_adx     - ADX
# bass_aix     - AIX
# bass_alac    - ALAC
# bass_ape     - Monkey's Audio
# bass_cd      - Digital streaming and ripping of audio CDs
# bass_dsd     - DSD (Direct Stream Digital) data in DSDIFF and DSF containers, and WavPack when used with the BASSWV add-on
# bass_flac    - FLAC (including Ogg FLAC)
# bass_fx      - Effects, including reverse playback and tempo & pitch control
# bass_hls     - HLS (HTTP Live Streaming)
# bass_loud    - Loudness measurement
# bass_midi    - MIDI
# bass_mix     - Mix together multiple BASS channels, with resampling and matrix mixing features
# bass_mpc     - Musepack
# bass_ofr     - OptimFROG
# bass_opus    - Opus
# bass_spx     - Speex
# bass_ssl     - HTTPS support in BASS and BASSenc
# bass_tags    - Formatted text from the ID3v1/v2, OGG/FLAC, WMA, APE, MP4, and RIFF tags
# bass_tta     - TTA
# bass_vst     - VST effects and instruments
# bass_wasapi  - WASAPI input and output
# bass_webm    - WebM and MKV
# bass_wma     - Playback, encoding and broadcasting WMA
# bass_wv      - WavPack, including WavPack DSD files when used with the BASSDSD
# bassenc      - BASS channels to be encoded using command-line encoders with STDIN support, or ACM codecs (on Windows) or CoreAudio codecs (on macOS/iOS), or user-provided encoders. Streaming to clients directly or via Shoutcast and Icecast. PCM WAV/AIFF file writing.
# bassenc_flac - [BASSenc] FLAC encoding
# bassenc_mp3  - [BASSenc] MP3 encoding
# bassenc_ogg  - [BASSenc] Ogg Vorbis encoding
# bassenc_opus - [BASSenc] Opus encoding
