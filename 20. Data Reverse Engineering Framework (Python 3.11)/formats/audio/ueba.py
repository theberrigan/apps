import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *
from bfw.writer import *
from bfw.native.base import *



UEBA_DLL_PATH = joinPath(BIN_DIR, 'bfw.ueba.dll')



class UEBA:
    _lib = None

    @classmethod
    def _loadLib (cls):
        if cls._lib:
            return

        lib = cls._lib = loadCDLL(UEBA_DLL_PATH)

        lib.createDecoder.restype  = CPtrVoid  # DecompressBundle*
        lib.createDecoder.argtypes = [
            CPtr(CU8),  # arg1: U8* srcBuffer
            CU32,       # arg2: U32 srcBufferSize
        ]

        lib.destroyDecoder.restype  = None  # void
        lib.destroyDecoder.argtypes = [
            CPtrVoid,  # arg1: DecompressBundle*
        ]

        lib.hasError.restype  = CBool  # bool
        lib.hasError.argtypes = [
            CPtrVoid,  # arg1: DecompressBundle*
        ]

        lib.decompress.restype  = CBool  # bool
        lib.decompress.argtypes = [
            CPtrVoid,  # arg1: DecompressBundle*
        ]

        lib.getSampleRate.restype  = CU32  # U32
        lib.getSampleRate.argtypes = [
            CPtrVoid,  # arg1: DecompressBundle*
        ]

        lib.getChannelCount.restype  = CU8  # bool
        lib.getChannelCount.argtypes = [
            CPtrVoid,  # arg1: DecompressBundle*
        ]

        lib.getPCMSize.restype  = CU32  # U32
        lib.getPCMSize.argtypes = [
            CPtrVoid,  # arg1: DecompressBundle*
        ]

        lib.getPCMPointer.restype  = CPtr(CU8)  # U8*
        lib.getPCMPointer.argtypes = [
            CPtrVoid,  # arg1: DecompressBundle*
        ]

        '''
        # Amount of memory to pass to DecompressOpen
        lib.UEBinkAudioDecompressMemory.restype  = CU32  # uint32_t
        lib.UEBinkAudioDecompressMemory.argtypes = [
            CU32,  # arg1: uint32_t rate
            CU32,  # arg2: uint32_t chans
        ]

        # Open and initialize a decompression stream
        lib.UEBinkAudioDecompressOpen.restype  = CU32  # uint32_t
        lib.UEBinkAudioDecompressOpen.argtypes = [
            CPtrVoid,  # arg1: void * BinkAudioDecoderMemory
            CU32,      # arg2: uint32_t rate
            CU32,      # arg3: uint32_t chans
            CBool,     # arg4: bool interleave_output
            CBool,     # arg5: bool is_bink_audio_2
        ]

        # Do the decompression - supports linear or ringbuffers (outptr == outstart on non-ring), will clamp, if no room
        lib.UEBinkAudioDecompress.restype  = CU32  # uint32_t
        lib.UEBinkAudioDecompress.argtypes = [
            CPtrVoid,         # arg1: void * BinkAudioDecoderMemory
            CPtr(CU8),        # arg2: uint8_t* OutputBuffer
            CU32,             # arg3: uint32_t OutputBufferLen
            CPtr(CPtr(CU8)),  # arg4: uint8_t const** InputBuffer
            CPtr(CU8),        # arg5: uint8_t const* InputBufferEnd
        ]

        # Resets the start flag to prevent blending in the last decoded frame
        lib.UEBinkAudioDecompressResetStartFrame.restype  = None  # void
        lib.UEBinkAudioDecompressResetStartFrame.argtypes = [
            CPtrVoid,  # arg1: void * BinkAudioDecoderMemory
        ]
        '''

    @classmethod
    def createDecoder (cls, data):
        cls._loadLib()

        dataBuffer = CBuffer.fromSource(data)
        dataSize   = len(dataBuffer)

        return cls._lib.createDecoder(dataBuffer, dataSize)

    @classmethod
    def destroyDecoder (cls, handle):
        cls._loadLib()

        return cls._lib.destroyDecoder(handle)

    @classmethod
    def hasError (cls, handle):
        cls._loadLib()

        return cls._lib.hasError(handle)

    @classmethod
    def decompress (cls, handle):
        cls._loadLib()

        return cls._lib.decompress(handle)

    @classmethod
    def decompress2 (cls, data):
        cls._loadLib()

        dataBuffer = CBuffer.fromSource(data)
        dataSize   = len(dataBuffer)

        handle = cls._lib.createDecoder(dataBuffer, dataSize)

        if cls._lib.hasError(handle):
            print('ERROR:')
            exit()

        cls._lib.decompress(handle)

        if cls._lib.hasError(handle):
            print('ERROR:')
            exit()

        sampleRate   = cls._lib.getSampleRate(handle)
        channelCount = cls._lib.getChannelCount(handle)
        pcmSize      = cls._lib.getPCMSize(handle)
        pcmPointer   = cls._lib.getPCMPointer(handle)
        pcmAddress   = cCast(pcmPointer, CPtrVoid).value

        # UEBA.destroyDecoder(handle)

        pcmData = bytes((CU8 * pcmSize).from_address(pcmAddress))

        return sampleRate, channelCount, pcmData

    '''
    @classmethod
    def calcDecompressMemorySize (cls, sampleRate, channelCount):
        cls._loadLib()

        return cls._lib.UEBinkAudioDecompressMemory(sampleRate, channelCount)

    @classmethod
    def createDecompressStream (cls, mem, sampleRate, channelCount, interleaveOutput, isBA2):
        cls._loadLib()

        return cls._lib.UEBinkAudioDecompressOpen(mem, sampleRate, channelCount, interleaveOutput, isBA2)

    @classmethod
    def decompress (cls, mem, destBuffer, srcBuffer):
        cls._loadLib()

        return cls._lib.UEBinkAudioDecompress(mem, sampleRate, channelCount, interleaveOutput, isBA2)

    @classmethod
    def resetDecompressStartFrame (cls, mem):
        cls._loadLib()

        return cls._lib.UEBinkAudioDecompressResetStartFrame(mem)
    '''



        
def _test_ ():
    pass



__all__ = [
    'UEBA'
]



if __name__ == '__main__':
    _test_()
