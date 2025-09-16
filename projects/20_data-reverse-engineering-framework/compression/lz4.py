import os
import sys
import struct

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *
from bfw.writer import *
from bfw.native.base import *



LZ4_DLL_PATH = joinPath(BIN_DIR, 'liblz4.dll')


# CPtrChar = CPtr(CChar)


class LZ4:
    _lib = None
    _bindingVersion = (1, 9, 5)

    @classmethod
    def _loadLib (cls):
        if cls._lib:
            return

        lib = cls._lib = loadCDLL(LZ4_DLL_PATH)

        # v1.3.0+
        lib.LZ4_versionNumber.restype  = CI32  # int
        lib.LZ4_versionNumber.argtypes = None  # void

        cls._checkLibVersion()

        # v1.7.5+
        lib.LZ4_versionString.restype  = CPtrChar  # const char*
        lib.LZ4_versionString.argtypes = None      # void

        lib.LZ4_compressBound.restype  = CI32  # int
        lib.LZ4_compressBound.argtypes = [
            CI32,  # arg1: int inputSize
        ]

        lib.LZ4_compress_default.restype  = CI32  # int
        lib.LZ4_compress_default.argtypes = [
            CPtrVoid,  # arg1: const char* src
            CPtrVoid,  # arg2: char* dst
            CI32,      # arg3: int srcSize
            CI32,      # arg4: int dstCapacity
        ]

        lib.LZ4_decompress_safe.restype  = CI32  # int
        lib.LZ4_decompress_safe.argtypes = [
            CPtrVoid,  # arg1: const char* src
            CPtrVoid,  # arg2: char* dst
            CI32,      # arg3: int srcSize
            CI32,      # arg4: int dstCapacity
        ]

        lib.LZ4_compress_fast.restype  = CI32  # int
        lib.LZ4_compress_fast.argtypes = [
            CPtrVoid,  # arg1: const char* src
            CPtrVoid,  # arg2: char* dst
            CI32,      # arg3: int srcSize
            CI32,      # arg4: int dstCapacity
            CI32,      # arg5: int acceleration
        ]

        lib.LZ4_sizeofState.restype  = CI32  # int
        lib.LZ4_sizeofState.argtypes = None  # void

        lib.LZ4_compress_fast_extState.restype  = CI32  # int
        lib.LZ4_compress_fast_extState.argtypes = [
            CPtrVoid,  # arg1: void* state
            CPtrVoid,  # arg2: const char* src
            CPtrVoid,  # arg3: char* dst
            CI32,      # arg4: int srcSize
            CI32,      # arg5: int dstCapacity
            CI32,      # arg6: int acceleration
        ]

        lib.LZ4_compress_destSize.restype  = CI32  # int
        lib.LZ4_compress_destSize.argtypes = [
            CPtrVoid,  # arg1: const char* src
            CPtrVoid,  # arg2: char* dst
            CPtrVoid,  # arg3: int* srcSizePtr
            CI32,      # arg4: int targetDstSize
        ]

        lib.LZ4_decompress_safe_partial.restype  = CI32  # int
        lib.LZ4_decompress_safe_partial.argtypes = [
            CPtrVoid,  # arg1: const char* src
            CPtrVoid,  # arg2: char* dst
            CI32,      # arg3: int srcSize
            CI32,      # arg4: int targetOutputSize
            CI32,      # arg5: int dstCapacity
        ]

        lib.LZ4_createStream.restype  = CPtrVoid  # LZ4_stream_t*
        lib.LZ4_createStream.argtypes = None

        lib.LZ4_freeStream.restype  = CI32  # int
        lib.LZ4_freeStream.argtypes = [
            CPtrVoid,  # arg1: LZ4_stream_t* streamPtr
        ]

        # v1.9.0+
        lib.LZ4_resetStream_fast.restype  = None  # void
        lib.LZ4_resetStream_fast.argtypes = [
            CPtrVoid,  # arg1: LZ4_stream_t* streamPtr
        ]

        lib.LZ4_loadDict.restype  = CI32  # int
        lib.LZ4_loadDict.argtypes = [
            CPtrVoid,  # arg1: LZ4_stream_t* streamPtr
            CPtrVoid,  # arg2: const char* dictionary
            CI32,      # arg3: int dictSize
        ]

        # TODO: int LZ4_saveDict (LZ4_stream_t* streamPtr, char* safeBuffer, int maxDictSize);

        lib.LZ4_compress_fast_continue.restype  = CI32  # int
        lib.LZ4_compress_fast_continue.argtypes = [
            CPtrVoid,  # arg1: LZ4_stream_t* streamPtr
            CPtrVoid,  # arg2: const char* src
            CPtrVoid,  # arg3: char* dst
            CI32,      # arg4: int srcSize
            CI32,      # arg5: int dstCapacity
            CI32,      # arg6: int acceleration
        ]

        lib.LZ4_createStreamDecode.restype  = CPtrVoid  # LZ4_streamDecode_t*
        lib.LZ4_createStreamDecode.argtypes = None

        lib.LZ4_freeStreamDecode.restype  = CI32  # int
        lib.LZ4_freeStreamDecode.argtypes = [
            CPtrVoid,  # arg1: LZ4_streamDecode_t* LZ4_stream
        ]

        lib.LZ4_setStreamDecode.restype  = CI32  # int
        lib.LZ4_setStreamDecode.argtypes = [
            CPtrVoid,  # arg1: LZ4_streamDecode_t* LZ4_streamDecode
            CPtrVoid,  # arg2: const char* dictionary
            CI32,      # arg3: int dictSize
        ]

        # TODO: int LZ4_decoderRingBufferSize(int maxBlockSize);

        lib.LZ4_decompress_safe_continue.restype  = CI32  # int
        lib.LZ4_decompress_safe_continue.argtypes = [
            CPtrVoid,  # arg1: LZ4_streamDecode_t* LZ4_streamDecode
            CPtrVoid,  # arg2: const char* src
            CPtrVoid,  # arg3: char* dst
            CI32,      # arg4: int srcSize
            CI32,      # arg5: int dstCapacity
        ]

        # ---------------------

        lib.LZ4_decompress_fast_withPrefix64k.restype = CI32
        lib.LZ4_decompress_fast_withPrefix64k.argtypes = [
            CPtrVoid,  # arg1: src
            CPtrVoid,  # arg2: dst
            CI32,      # arg3: originalSize
        ]

    @classmethod
    def _checkLibVersion (cls):
        libVersion = cls.getVersion()

        if libVersion[0] != cls._bindingVersion[0]:
            raise Exception(f'DLL major version ({ libVersion[0] }) is incompatible with current bindings version ({ cls._bindingVersion[0] })')

    @classmethod
    def getVersion (cls):
        cls._loadLib()

        version = cls._lib.LZ4_versionNumber()

        major = version // 10000          # interface-breaking changes
        minor = (version % 10000) // 100  # new features (non-interface-breaking)
        patch = version % 100             # tweaks and fixes

        return major, minor, patch

    @classmethod
    def getVersionString (cls):
        cls._loadLib()

        version = cls._lib.LZ4_versionString()

        return version.decode('ascii')

    @classmethod
    def calcCompressBound (cls, sourceSize):
        cls._loadLib()

        result = cls._lib.LZ4_compressBound(sourceSize)

        if result == 0:
            raise Exception(f'Failed to calculate compress bound for source size { sourceSize }')

        return result

    # speed in [1-65537] - the higher the number, the faster and worse the compression
    @classmethod
    def compress (cls, source, speed=1, state=None, returnType=bytes):
        cls._loadLib()

        srcBuffer  = CBuffer.fromSource(source)
        srcSize    = len(srcBuffer)
        maxDstSize = cls.calcCompressBound(srcSize)
        dstBuffer  = CBuffer.create(maxDstSize)

        if state:
            compSize = cls._lib.LZ4_compress_fast_extState(state, srcBuffer, dstBuffer, srcSize, maxDstSize, speed)
        else:
            # LZ4_compress_default is same as LZ4_compress_fast with speed = 1
            compSize = cls._lib.LZ4_compress_fast(srcBuffer, dstBuffer, srcSize, maxDstSize, speed)
        
        if compSize <= 0:
            raise Exception('Failed to compress data')

        result = returnType(dstBuffer)[:compSize]

        return result

    # TODO: WTF fn?
    @classmethod
    def compressToFixedBuffer (cls, source, dstBuffer, dstSize, returnType=bytes):
        cls._loadLib()

        srcBuffer = CBuffer.fromSource(source)
        srcSize   = CI32(len(srcBuffer))

        # TODO: is cRef(srcSize) necessary?
        compSize = cls._lib.LZ4_compress_destSize(srcBuffer, dstBuffer, cRef(srcSize), dstSize)
        
        if compSize <= 0:
            raise Exception('Failed to compress data')

        return srcSize.value, compSize

    @classmethod
    def compressChainBlock (cls, pStream, srcBuffer, srcOffset, srcLimit, dstBuffer, dstSize, speed = 1):
        cls._loadLib()

        compSize = cls._lib.LZ4_compress_fast_continue(pStream, cRef(srcBuffer, srcOffset), dstBuffer, srcLimit, dstSize, speed)

        if compSize <= 0:
            raise Exception('Failed to compress data')

        return compSize

    @classmethod
    def decompress (cls, data, decompSize, returnType=bytes):
        cls._loadLib()

        srcBuffer = CBuffer.fromSource(data)
        dstBuffer = CBuffer.create(decompSize)

        resultSize = cls._lib.LZ4_decompress_safe(srcBuffer, dstBuffer, len(srcBuffer), decompSize)

        if resultSize < 0:
            raise Exception('Failed to decompress data')

        if resultSize != decompSize:
            raise Exception('Decompressed data is corrupted')

        result = returnType(dstBuffer)[:resultSize]

        return result

    # srcLimit - how many bytes to decompress, must be <= len(source)
    # dstLimit - max number of bytes to write to dstBuffer, must be <= dstSize
    # dstSize  - size of dstBuffer (used for backward compat.)
    # Function stops when srcLimit or dstLimit exceeded.
    # Returns the number of bytes written to the dstBuffer, always <= dstLimit.
    @classmethod
    def decompressPart (cls, source, srcLimit, dstBuffer, dstLimit, dstSize):
        cls._loadLib()

        srcBuffer = CBuffer.fromSource(source)

        decompSize = cls._lib.LZ4_decompress_safe_partial(srcBuffer, dstBuffer, srcLimit, dstLimit, dstSize)
        
        if decompSize < 0:
            raise Exception('Failed to decompress data block')

        return decompSize

    @classmethod
    def decompressChainBlock (cls, pStream, srcBuffer, srcOffset, srcLimit, dstBuffer, dstOffset, dstLimit):
        cls._loadLib()

        decompSize = cls._lib.LZ4_decompress_safe_continue(pStream, cRef(srcBuffer, srcOffset), cRef(dstBuffer, dstOffset), srcLimit, dstLimit)
        
        if decompSize < 0:
            raise Exception('Failed to decompress data block')

        return decompSize

    @classmethod
    def getStateSize (cls):
        cls._loadLib()

        return cls._lib.LZ4_sizeofState()

    @classmethod
    def createState (cls):
        stateSize = cls.getStateSize()

        return CBuffer.create(stateSize)

    @classmethod
    def createCompressionStream (cls):
        cls._loadLib()

        return cls._lib.LZ4_createStream()

    @classmethod
    def freeCompressionStream (cls, pStream):
        cls._loadLib()

        return cls._lib.LZ4_freeStream(pStream)

    @classmethod
    def resetCompressionStream (cls, pStream):
        cls._loadLib()
        cls._lib.LZ4_resetStream_fast(pStream)

    @classmethod
    def createDecompressionStream (cls):
        cls._loadLib()

        return cls._lib.LZ4_createStreamDecode()

    @classmethod
    def freeDecompressionStream (cls, pStream):
        cls._loadLib()

        return cls._lib.LZ4_freeStreamDecode(pStream)

    @classmethod
    def setDecompressionStream (cls, pStream, dictBuffer=None, dictSize=None):
        cls._loadLib()

        if dictSize is None:
            if dictBuffer:
                dictSize = len(dictBuffer)
            else:
                dictSize = 0

        result = cls._lib.LZ4_setStreamDecode(pStream, dictBuffer, dictSize)

        return result == 1

    @classmethod
    def createDict (cls, source):
        return CBuffer.fromSource(source)

    # dictBuffer - immutable buffer that must remain in memory until compression is complete
    @classmethod
    def loadDict (cls, pStream, dictBuffer):
        cls._loadLib()

        dictSize = len(dictBuffer)
        doneSize = cls._lib.LZ4_loadDict(pStream, dictBuffer, dictSize)

        if doneSize != dictSize:
            raise Exception('Failed to load dict')

    # ----------------------------

    @classmethod
    def decompressBlocked (cls, data, decompSize):
        cls._loadLib()

        if isinstance(data, bytes):
            data = bytearray(data)
        elif not isinstance(data, bytearray):
            raise Exception(f'Source data must be of type bytes or bytearray, { type(data).__name__ } given')

        srcBuffer = (CU8 * len(data)).from_buffer(data)
        srcSize   = len(srcBuffer)
        dstBuffer = (CU8 * decompSize)()

        srcCursor = 0
        dstCursor = 0

        while srcCursor < srcSize:
            blockSize, blockDecompSize = struct.unpack('<II', data[srcCursor:srcCursor + 8])

            srcCursor += 8

            bytesRead = cls._lib.LZ4_decompress_fast_withPrefix64k(
                cRef(srcBuffer, srcCursor),
                cRef(dstBuffer, dstCursor),
                blockDecompSize
            )

            bytesMustBeRead = blockSize - 8

            if bytesRead < bytesMustBeRead:
                raise Exception('Failed to decompress data')

            dstCursor += blockDecompSize
            srcCursor += bytesMustBeRead

        result = bytes(dstBuffer)[:dstCursor]

        return result



        '''
        size_t result = 0;

        MemStream stream(compressedData, compressedSize);
        char* dst = rcast<char*>(uncompressedData);

        size_t outCursor = 0;
        while (!stream.Ended()) {
            const size_t blockSize = stream.ReadTyped<uint32_t>();
            const size_t blockUncompressedSize = stream.ReadTyped<uint32_t>();

            const char* src = rcast<const char*>(stream.GetDataAtCursor());

            const int nbRead = LZ4_decompress_fast_withPrefix64k(src, dst + outCursor, scast<int>(blockUncompressedSize));
            const int nbCompressed = scast<int>(blockSize - 8);
            if (nbRead < scast<int>(nbCompressed)) {
                // ooops, error :(
                return 0;
            }

            outCursor += blockUncompressedSize;

            stream.SkipBytes(nbCompressed);
        }

        result = outCursor;

        return result;
        '''



        
# https://github.com/lz4/lz4/tree/dev/examples
def _test_ ():
    # print(LZ4.calcCompressBound(12))
    # print(LZ4.getVersionString())
    # print(LZ4.compress(b'123'))
    # print(LZ4.getStateSize())

    # -------------------

    sourceData = b'Below we will have a Compression and Decompression section to demonstrate.'

    # -------------------

    version = LZ4.getVersion()

    assert isinstance(version, tuple) and len(version) == 3

    version = LZ4.getVersionString()

    assert isinstance(version, str)

    compData = LZ4.compress(sourceData)

    assert isinstance(compData, bytes)

    decompData = LZ4.decompress(compData, len(sourceData))

    assert sourceData == decompData

    state = LZ4.createState()
    compData = LZ4.compress(sourceData, 8192, state)

    assert isinstance(compData, bytes)

    decompData = LZ4.decompress(compData, len(sourceData))

    assert sourceData == decompData

    # TODO: test LZ4.compressToFixedBuffer

    compData   = LZ4.compress(sourceData)
    dstBuffer  = CBuffer.create(len(sourceData) * 2)
    decompSize = LZ4.decompressPart(compData, len(compData), dstBuffer, len(sourceData), len(dstBuffer))

    assert decompSize == len(sourceData)
    assert bytes(dstBuffer)[:decompSize] == sourceData

    pStream = LZ4.createCompressionStream()

    assert pStream

    LZ4.resetCompressionStream(pStream)
    LZ4.freeCompressionStream(pStream)

    pStream = LZ4.createCompressionStream()
    compDict = LZ4.createDict(b'123456789') 

    LZ4.loadDict(pStream, compDict)
    LZ4.freeCompressionStream(pStream)

    pStream = LZ4.createDecompressionStream()
    dictBuffer = CBuffer.fromSource(b'123456789')
    isOk = LZ4.setDecompressionStream(pStream, dictBuffer)
    assert isOk
    LZ4.freeDecompressionStream(pStream)

    # ---------------------------------

    srcBlockSize = 1 * 1024 * 1024  # 1mb

    with BinWriter() as f:
        bigData   = readBin(r'C:\Projects\GameTools\steam_achievements\misc\apps.json')
        pStream   = LZ4.createCompressionStream()
        srcBuffer = CBuffer.fromSource(bigData)
        srcSize   = len(srcBuffer)
        srcOffset = 0

        while srcOffset < srcSize:
            srcLimit  = min(srcBlockSize, srcSize - srcOffset)
            dstSize   = LZ4.calcCompressBound(srcLimit)
            dstBuffer = CBuffer.create(dstSize)

            compSize = LZ4.compressChainBlock(pStream, srcBuffer, srcOffset, srcLimit, dstBuffer, dstSize)

            srcOffset += srcLimit

            f.u32(compSize)
            f.u32(srcLimit)  # decompSize
            f.write(bytes(dstBuffer)[:compSize])

        LZ4.freeCompressionStream(pStream)

        print(f'{ srcSize } bytes -> { f.getSize() } bytes')

        compData = f.getRaw()

    with BinWriter() as f:
        pStream   = LZ4.createDecompressionStream()
        srcSize   = len(compData)
        srcOffset = 0
        dstOffset = 0
        dstBuffer = CBuffer.create(16000000)

        # LZ4.setDecompressionStream(pStream)

        while srcOffset < srcSize:            
            blockCompSize, blockDecompSize = struct.unpack('<II', compData[srcOffset:srcOffset + 8])

            srcOffset += 8

            maxBlockDecompSize = LZ4.calcCompressBound(blockDecompSize)

            compDataBlock = compData[srcOffset:srcOffset + blockCompSize]
            compDataBlock += b'\x00' * (maxBlockDecompSize - len(compDataBlock))

            srcOffset += blockCompSize

            srcBuffer = CBuffer.fromSource(compDataBlock)

            # print(blockCompSize, blockDecompSize)

            # pStream, srcBuffer, srcOffset, srcLimit, dstBuffer, dstOffset, dstLimit
            decompSize = LZ4.decompressChainBlock(pStream, srcBuffer, 0, blockCompSize, dstBuffer, dstOffset, blockDecompSize)

            print(decompSize, blockDecompSize)

            assert decompSize == blockDecompSize

            dstOffset += blockDecompSize

            # f.write(bytes(dstBuffer)[:decompSize])

        LZ4.freeDecompressionStream(pStream)

        decompData = bytes(dstBuffer)[:dstOffset] # f.getRaw()

        assert decompData == bigData

    # -------------------

    # writeBin(r"C:\Users\Berrigan\Desktop\data.bin", bytes(state))

    # source = 'Below we will have a Compression and Decompression section to demonstrate.'
    # source = source.encode('utf-8')
    # sourceSize = len(source)

    # compData = LZ4.compress(source)
    # decompData = LZ4.decompress(compData, sourceSize)

    # assert decompData == source


__all__ = [
    'LZ4'
]


if __name__ == '__main__':
    _test_()


'''
int main(void) {
    /* Introduction */
    // Below we will have a Compression and Decompression section to demonstrate.
    // There are a few important notes before we start:
    //   1) The return codes of LZ4_ functions are important.
    //      Read lz4.h if you're unsure what a given code means.
    //   2) LZ4 uses char* pointers in all LZ4_ functions.
    //      This is baked into the API and not going to change, for consistency.
    //      If your program uses different pointer types,
    //      you may need to do some casting or set the right -Wno compiler flags to ignore those warnings (e.g.: -Wno-pointer-sign).
  
    /* Compression */
    // We'll store some text into a variable pointed to by *src to be compressed later.
    const char* const src = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Lorem ipsum dolor site amat.";
    // The compression function needs to know how many bytes exist.  Since we're using a string, we can use strlen() + 1 (for \0).
    const int src_size = (int)(strlen(src) + 1);
    // LZ4 provides a function that will tell you the maximum size of compressed output based on input data via LZ4_compressBound().
    const int max_dst_size = LZ4_compressBound(src_size);
    // We will use that size for our destination boundary when allocating space.
    char* compressed_data = (char*)malloc((size_t)max_dst_size);
    if (compressed_data == NULL)
      run_screaming("Failed to allocate memory for *compressed_data.", 1);
    // That's all the information and preparation LZ4 needs to compress *src into* compressed_data.
    // Invoke LZ4_compress_default now with our size values and pointers to our memory locations.
    // Save the return value for error checking.
    const int compressed_data_size = LZ4_compress_default(src, compressed_data, src_size, max_dst_size);
    // Check return_value to determine what happened.
    if (compressed_data_size <= 0)
      run_screaming("A 0 or negative result from LZ4_compress_default() indicates a failure trying to compress the data. ", 1);
    if (compressed_data_size > 0)
      printf("We successfully compressed some data! Ratio: %.2f\n",
          (float) compressed_data_size/src_size);
    // Not only does a positive return_value mean success, the value returned == the number of bytes required.
    // You can use this to realloc() *compress_data to free up memory, if desired.  We'll do so just to demonstrate the concept.
    compressed_data = (char *)realloc(compressed_data, (size_t)compressed_data_size);
    if (compressed_data == NULL)
      run_screaming("Failed to re-alloc memory for compressed_data.  Sad :(", 1);
  
  
    /* Decompression */
    // Now that we've successfully compressed the information from *src to *compressed_data, let's do the opposite!
    // The decompression will need to know the compressed size, and an upper bound of the decompressed size.
    // In this example, we just re-use this information from previous section,
    // but in a real-world scenario, metadata must be transmitted to the decompression side.
    // Each implementation is in charge of this part. Oftentimes, it adds some header of its own.
    // Sometimes, the metadata can be extracted from the local context.
  
    // First, let's create a *new_src location of size src_size since we know that value.
    char* const regen_buffer = (char*)malloc(src_size);
    if (regen_buffer == NULL)
      run_screaming("Failed to allocate memory for *regen_buffer.", 1);
    // The LZ4_decompress_safe function needs to know where the compressed data is, how many bytes long it is,
    // where the regen_buffer memory location is, and how large regen_buffer (uncompressed) output will be.
    // Again, save the return_value.
    const int decompressed_size = LZ4_decompress_safe(compressed_data, regen_buffer, compressed_data_size, src_size);
    free(compressed_data);   /* no longer useful */
    if (decompressed_size < 0)
      run_screaming("A negative result from LZ4_decompress_safe indicates a failure trying to decompress the data.  See exit code (echo $?) for value returned.", decompressed_size);
    if (decompressed_size >= 0)
      printf("We successfully decompressed some data!\n");
    // Not only does a positive return value mean success,
    // value returned == number of bytes regenerated from compressed_data stream.
    if (decompressed_size != src_size)
      run_screaming("Decompressed data is different from original! \n", 1);
  
    /* Validation */
    // We should be able to compare our original *src with our *new_src and be byte-for-byte identical.
    if (memcmp(src, regen_buffer, src_size) != 0)
      run_screaming("Validation failed.  *src and *new_src are not identical.", 1);
    printf("Validation done. The string we ended up with is:\n%s\n", regen_buffer);
    return 0;
}
'''