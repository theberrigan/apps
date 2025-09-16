import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *
from bfw.writer import *
from bfw.native.limits import MAX_U32, I16_BYTES
from bfw.native.base import *
from bfw.native.windows.types import HWND, BOOL, WCHAR, DWORD



CSFML_DLLS_DIR       = joinPath(BIN_DIR, 'csfml')
CSFML_AUDIO_DLL_PATH = joinPath(CSFML_DLLS_DIR, 'csfml-audio-2.dll')

NULL = 0

CSFML_STR_ENCODING = 'ansi'


class sfTime (CStruct):
    _fields_ = [
        ('microseconds', CI64),  # int64_t microseconds;
    ]

sfInt16  = CI16
psfInt16 = CPtr(sfInt16)
sfInt32  = CI32
sfUint32 = CU32
sInt64   = CI64
sfUint64 = CU64
sfBool   = CI32

sfTrue  = 1
sfFalse = 0


class Lib:
    _lib = None

    @classmethod
    def get (cls):
        if cls._lib is not None:
            return cls._lib

        cls._lib = lib = loadCDLL(CSFML_AUDIO_DLL_PATH)

        # Create a new sound buffer and load it from a file.
        # Here is a complete list of all the supported audio formats:
        # ogg, wav, flac, mp3, aiff, au, raw, paf, svx, nist, voc, ircam,
        # w64, mat4, mat5 pvf, htk, sds, avr, sd2, caf, wve, mpc2k, rf64.
        # ---
        # @arg1   filename - Path of the sound file to load
        # @return A new sfSoundBuffer object (NULL if failed)
        # ---
        # sfSoundBuffer* sfSoundBuffer_createFromFile(const char* filename);
        lib.sfSoundBuffer_createFromFile.restype  = CPtrVoid  # sfSoundBuffer*
        lib.sfSoundBuffer_createFromFile.argtypes = [
            CPtrChar,  # arg1: const char* filename
        ]

        # ---

        # Create a new sound buffer and load it from a file in memory.
        # Here is a complete list of all the supported audio formats:
        # ogg, wav, flac, mp3, aiff, au, raw, paf, svx, nist, voc, ircam,
        # w64, mat4, mat5 pvf, htk, sds, avr, sd2, caf, wve, mpc2k, rf64.
        # ---
        # @arg1   data        - Pointer to the file data in memory
        # @arg2   sizeInBytes - Size of the data to load, in bytes
        # @return A new sfSoundBuffer object (NULL if failed)
        # ---
        # sfSoundBuffer* sfSoundBuffer_createFromMemory(const void* data, size_t sizeInBytes);
        lib.sfSoundBuffer_createFromMemory.restype  = CPtrVoid  # sfSoundBuffer*
        lib.sfSoundBuffer_createFromMemory.argtypes = [
            CPtrVoid,  # arg1: const void* data
            CSize,     # arg2: size_t sizeInBytes
        ]

        # Create a new sound buffer and load it from a custom stream.
        # Here is a complete list of all the supported audio formats:
        # ogg, wav, flac, mp3, aiff, au, raw, paf, svx, nist, voc, ircam,
        # w64, mat4, mat5 pvf, htk, sds, avr, sd2, caf, wve, mpc2k, rf64.
        # ---
        # @arg1   stream - Source stream to read from
        # @return A new sfSoundBuffer object (NULL if failed)
        # ---
        # sfSoundBuffer* sfSoundBuffer_createFromStream(sfInputStream* stream);
        lib.sfSoundBuffer_createFromStream.restype  = CPtrVoid  # sfSoundBuffer*
        lib.sfSoundBuffer_createFromStream.argtypes = [
            CPtrVoid,  # arg1: sfInputStream* stream
        ]

        # Create a new sound buffer and load it from an array of samples in memory.
        # The assumed format of the audio samples is 16 bits signed integer (sfInt16).
        # ---
        # @arg1   samples      - Pointer to the array of samples in memory
        # @arg2   sampleCount  - Number of samples in the array
        # @arg3   channelCount - Number of channels (1 = mono, 2 = stereo, ...)
        # @arg4   sampleRate   - Sample rate (number of samples to play per second)
        # @return A new sfSoundBuffer object (NULL if failed)
        # ---
        # sfSoundBuffer* sfSoundBuffer_createFromSamples(const sfInt16* samples, sfUint64 sampleCount, unsigned int channelCount, unsigned int sampleRate);
        lib.sfSoundBuffer_createFromSamples.restype  = CPtrVoid  # sfSoundBuffer*
        lib.sfSoundBuffer_createFromSamples.argtypes = [
            psfInt16,  # arg1: const sfInt16* samples
            sfUint64,  # arg2: sfUint64 sampleCount
            sfUint32,  # arg3: unsigned int channelCount
            sfUint32,  # arg4: unsigned int sampleRate
        ]

        # Create a new sound buffer by copying an existing one
        # ---
        # @arg1   soundBuffer - Sound buffer to copy
        # @return A new sfSoundBuffer object which is a copy of a soundBuffer
        # ---
        # sfSoundBuffer* sfSoundBuffer_copy(const sfSoundBuffer* soundBuffer);
        lib.sfSoundBuffer_copy.restype  = CPtrVoid  # sfSoundBuffer*
        lib.sfSoundBuffer_copy.argtypes = [
            CPtrVoid,  # arg1: sfSoundBuffer* soundBuffer
        ]

        # Destroy a sound buffer
        # ---
        # @arg1 soundBuffer - Sound buffer to destroy
        # ---
        # void sfSoundBuffer_destroy(sfSoundBuffer* soundBuffer);
        lib.sfSoundBuffer_destroy.restype  = None  # void
        lib.sfSoundBuffer_destroy.argtypes = [
            CPtrVoid,  # arg1: sfSoundBuffer* soundBuffer
        ]

        # Save a sound buffer to an audio file
        # Here is a complete list of all the supported audio formats:
        # ogg, wav, flac, mp3, aiff, au, raw, paf, svx, nist, voc, ircam,
        # w64, mat4, mat5 pvf, htk, sds, avr, sd2, caf, wve, mpc2k, rf64.
        # ---
        # @arg1   soundBuffer - Sound buffer object
        # @arg2   filename    - Path of the sound file to write
        # @return sfTrue if saving succeeded, sfFalse if it failed
        # ---
        # sfBool sfSoundBuffer_saveToFile(const sfSoundBuffer* soundBuffer, const char* filename);
        lib.sfSoundBuffer_saveToFile.restype  = sfBool  # sfBool
        lib.sfSoundBuffer_saveToFile.argtypes = [
            CPtrVoid,  # arg1: const sfSoundBuffer* soundBuffer
            CPtrChar,  # arg2: const char* filename
        ]

        # Get the array of audio samples stored in a sound buffer
        # The format of the returned samples is 16 bits signed integer
        # (sfInt16). The total number of samples in this array
        # is given by the sfSoundBuffer_getSampleCount function.
        # ---
        # @arg1   soundBuffer - Sound buffer object
        # @return Read-only pointer to the array of sound samples
        # ---
        # const sfInt16* sfSoundBuffer_getSamples(const sfSoundBuffer* soundBuffer);
        lib.sfSoundBuffer_getSamples.restype  = CPtrVoid  # const sfInt16*
        lib.sfSoundBuffer_getSamples.argtypes = [
            CPtrVoid,  # arg1: const sfSoundBuffer* soundBuffer
        ]

        # Get the number of samples stored in a sound buffer.
        # The array of samples can be accessed with the
        # sfSoundBuffer_getSamples function.
        # ---
        # @arg1   soundBuffer - Sound buffer object
        # @return Number of samples
        # ---
        # sfUint64 sfSoundBuffer_getSampleCount(const sfSoundBuffer* soundBuffer);
        lib.sfSoundBuffer_getSampleCount.restype  = sfUint64  # sfUint64
        lib.sfSoundBuffer_getSampleCount.argtypes = [
            CPtrVoid,  # arg1: const sfSoundBuffer* soundBuffer
        ]

        # Get the sample rate of a sound buffer.
        # The sample rate is the number of samples played per second.
        # The higher, the better the quality (for example, 44100
        # samples/s is CD quality).
        # ---
        # @arg1   soundBuffer - Sound buffer object
        # @return Sample rate (number of samples per second)
        # ---
        # unsigned int sfSoundBuffer_getSampleRate(const sfSoundBuffer* soundBuffer);
        lib.sfSoundBuffer_getSampleRate.restype  = sfUint32  # unsigned int
        lib.sfSoundBuffer_getSampleRate.argtypes = [
            CPtrVoid,  # arg1: const sfSoundBuffer* soundBuffer
        ]

        # Get the number of channels used by a sound buffer
        # If the sound is mono then the number of channels will be 1, 2 for stereo...
        # ---
        # @arg1   soundBuffer - Sound buffer object
        # @return Number of channels
        # ---
        # unsigned int sfSoundBuffer_getChannelCount(const sfSoundBuffer* soundBuffer);
        lib.sfSoundBuffer_getChannelCount.restype  = sfUint32  # unsigned int
        lib.sfSoundBuffer_getChannelCount.argtypes = [
            CPtrVoid,  # arg1: const sfSoundBuffer* soundBuffer
        ]

        # Get the total duration of a sound buffer
        # ---
        # @arg1   soundBuffer - Sound buffer object
        # @return Sound duration
        # ---
        # sfTime sfSoundBuffer_getDuration(const sfSoundBuffer* soundBuffer);
        lib.sfSoundBuffer_getDuration.restype  = sfTime  # sfTime
        lib.sfSoundBuffer_getDuration.argtypes = [
            CPtrVoid,  # arg1: const sfSoundBuffer* soundBuffer
        ]

        return lib


class SFMLSoundBuffer:
    @classmethod
    def getLib (cls):
        return Lib.get()

    @classmethod
    def fromFile (cls, filePath):
        lib = cls.getLib()

        filePath = CZStr(filePath, True, CSFML_STR_ENCODING)

        pBuffer = lib.sfSoundBuffer_createFromFile(filePath)

        if pBuffer == NULL:
            raise Exception('Failed to open file')

        return cls(pBuffer)

    @classmethod
    def fromBuffer (cls, data):
        lib = cls.getLib()

        dataSize = len(data)
        data     = CBuffer.fromSource(data)

        pBuffer = lib.sfSoundBuffer_createFromMemory(data, dataSize)

        if pBuffer == NULL:
            raise Exception('Failed to create sound buffer from raw buffer')

        return cls(pBuffer)

    @classmethod
    def fromStream (cls, pStream):
        lib = cls.getLib()

        pBuffer = lib.sfSoundBuffer_createFromStream(pStream)

        if pBuffer == NULL:
            raise Exception('Failed to create sound buffer from input stream')

        return cls(pBuffer)

    @classmethod
    def fromSamples (cls, pSamples, sampleCount, channelCount, sampleRate):
        lib = cls.getLib()

        pBuffer = lib.sfSoundBuffer_createFromSamples(pSamples, sampleCount, channelCount, sampleRate)

        if pBuffer == NULL:
            raise Exception('Failed to create sound buffer from samples')

        return cls(pBuffer)

    @classmethod
    def copyBuffer (cls, pBuffer):
        lib = cls.getLib()

        pBuffer2 = lib.sfSoundBuffer_copy(pBuffer)

        if pBuffer2 == NULL:
            raise Exception('Failed to copy sound buffer')

        return pBuffer2

    @classmethod
    def saveBuffer (cls, pBuffer, filePath):
        lib = cls.getLib()

        filePath = CZStr(filePath, True, CSFML_STR_ENCODING)

        result = lib.sfSoundBuffer_saveToFile(pBuffer, filePath)

        if result == sfFalse:
            raise Exception('Failed to save file')

    @classmethod
    def closeBuffer (cls, pBuffer):
        cls.getLib().sfSoundBuffer_destroy(pBuffer)

    @classmethod
    def getBufferChannelCount (cls, pBuffer):
        return cls.getLib().sfSoundBuffer_getChannelCount(pBuffer)

    @classmethod
    def getBufferSampleRate (cls, pBuffer):
        return cls.getLib().sfSoundBuffer_getSampleRate(pBuffer)

    @classmethod
    def getBufferSampleCount (cls, pBuffer):
        return cls.getLib().sfSoundBuffer_getSampleCount(pBuffer)

    @classmethod
    def getBufferSamples (cls, pBuffer):
        lib = cls.getLib()

        # TODO: need to free?
        pSamples = lib.sfSoundBuffer_getSamples(pBuffer)

        if pSamples == NULL:
            raise Exception('Failed to get samples')

        return pSamples

    @classmethod
    def getBufferDuration (cls, pBuffer):
        lib = cls.getLib()

        result = lib.sfSoundBuffer_getDuration(pBuffer)

        return result.microseconds

    # -------------------------

    @property
    def channelCount (self):
        self._ensureOpen()

        return self.cls.getBufferChannelCount(self.pBuffer)

    @property
    def sampleRate (self):
        self._ensureOpen()

        return self.cls.getBufferSampleRate(self.pBuffer)

    @property
    def sampleCount (self):
        self._ensureOpen()

        return self.cls.getBufferSampleCount(self.pBuffer)

    @property
    def samples (self, bufferType=bytes):
        self._ensureOpen()

        pSamples = self.cls.getBufferSamples(self.pBuffer)

        samples = (CI16 * self.sampleCount).from_address(pSamples)

        return bufferType(samples)

    # microseconds
    @property
    def duration (self):
        self._ensureOpen()

        return self.cls.getBufferDuration(self.pBuffer)

    def __init__ (self, pBuffer):
        if pBuffer == 0:
            raise Exception('Cannot create sound buffer from null pointer')

        self.pBuffer = pBuffer
        self.isOpen  = True
        self.cls     = self.__class__

    def __del__ (self):
        self.close()

    def _ensureOpen (self):
        if not self.isOpen:
            raise Exception('Sound buffer is closed')

    def close (self):
        if self.isOpen:
            self.cls.closeBuffer(self.pBuffer)

            self.pBuffer = None
            self.isOpen  = False

    def save (self, filePath):
        self._ensureOpen()

        self.cls.saveBuffer(self.pBuffer, filePath)

    def copy (self):
        self._ensureOpen()

        pBuffer = self.cls.copyBuffer(self.pBuffer)

        return self.cls(pBuffer)


        
def _test_ ():
    # buffer = SFMLSoundBuffer.fromFile(r'D:\Documents\Музыка\OST - Michael McCann - Deus Ex Human Revolution\DLC The Missing Link\22. DLC RestrictedArea Music.mp3')
    buffer = SFMLSoundBuffer.fromFile(r'D:\Documents\Аудиобанк\GTA Vice City Radio Comedy (VCPR).mp3')
    print(buffer.duration)
    # buffer = SFMLSoundBuffer.fromBuffer(readBin(r'D:\Documents\Музыка\OST - Michael McCann - Deus Ex Human Revolution\DLC The Missing Link\22. DLC RestrictedArea Music.mp3'))

    # channelCount = SFMLAudio.getSoundBufferChannelCount(buffer)
    # sampleRate   = SFMLAudio.getSoundBufferSampleRate(buffer)
    # pcmData      = SFMLAudio.getSoundBufferSamples(buffer)

    # saveAsWave(r'C:\Users\Berrigan\Desktop\sample.wav', buffer.samples, buffer.channelCount, buffer.sampleRate)
    # buffer.save(r'C:\Users\Berrigan\Desktop\sample2.wav')

    # print(buffer.copy())

    # SFMLAudio.closeSoundBuffer(buffer)



__all__ = [
    'SFMLSoundBuffer'
]



if __name__ == '__main__':
    _test_()