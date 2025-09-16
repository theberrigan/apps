from ...common import bfw
from ...common.types import *
from ...common.consts import *

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *
from bfw.writer import BinWriter
from bfw.types.enums import Enum



# NOTE: all samples are mono
class SFXSample:
    def __init__ (self):
        self.id        : TInt = None  # see SampleId
        self.offset    : TInt = None  # uint32 nOffset     -- offset in .raw file
        self.size      : TInt = None  # uint32 nSize       -- size in .raw file
        self.freq      : TInt = None  # uint32 nFrequency  -- sample rate
        self.loopStart : TInt = None  # uint32 nLoopStart  -- loop start in bytes (0 <= loopStart <= size)
        self.loopEnd   : TInt = None  # int32 nLoopEnd     -- loop end in bytes (0 <= loopStart <= size) (-1 - from end)


# https://gtamods.com/wiki/SFX#GTA_III_and_Vice_City_(PC)
# Samples enum: src/audio/AudioSamples.h
class SFXReader:
    @classmethod
    def parseDefault (cls):
        return cls.fromFile(SFX_RAW_FILE_PATH, SFX_SDT_FILE_PATH)

    @classmethod
    def fromFile (cls, rawPath : str, sdtPath : str | None = None):
        if not isFile(rawPath):
            raise OSError(f'File does not exist: { rawPath }')

        if not sdtPath:
            sdtPath = replaceExt(sdtPath, SFX_SDT_EXT)

        if not isFile(sdtPath):
            raise OSError(f'File does not exist: { sdtPath }')

        rawFile = openFile(rawPath)
        sdtPath = openFile(sdtPath)

        return cls().read(rawFile, sdtPath)

    @classmethod
    def fromBuffer (cls, rawData : bytes, sdtData : bytes, rawPath : str | None = None, sdtPath : str | None = None):
        rawFile = MemReader(rawData, rawPath)
        sdtData = MemReader(sdtData, sdtPath)

        return cls().read(rawFile, sdtData)

    def read (self, rawFile : Reader, sdtFile : Reader):
        sdtSize = sdtFile.getSize()

        assert sdtSize % SFX_SAMPLE_STRUCT_SIZE == 0

        sampleCount = sdtSize // SFX_SAMPLE_STRUCT_SIZE

        samples = []

        for i in range(sampleCount):
            sample = SFXSample()

            sample.id        = i
            sample.offset    = sdtFile.u32()
            sample.size      = sdtFile.u32()
            sample.freq      = sdtFile.u32()
            sample.loopStart = sdtFile.u32()
            sample.loopEnd   = sdtFile.i32()

            assert SampleId.hasValue(sample.id), sample.id

            samples.append(sample)

        # TODO: load raw data and wrap to wav

        return samples

        # self.saveAsWav(rawFile, samples[0], r'G:\Steam\steamapps\common\Grand Theft Auto Vice City\.converter\original\sample.wav')
        # print(toJson(samples[0]))

    def saveAsRaw (self, rawFile : Reader, sample : SFXSample, outPath : str):
        rawFile.seek(sample.offset)

        data = rawFile.read(sample.size)

        writeBin(outPath, data)


    def saveAsWav (self, rawFile : Reader, sample : SFXSample, outPath : str):
        rawFile.seek(sample.offset)

        data = rawFile.read(sample.size)

        with BinWriter() as f:
            f.write(b'RIFF')         # 0x00  char[4]  ChunkID        "RIFF"
            f.u32(sample.size + 36)  # 0x04  dword    ChunkSize      size from SDT format + 36
            f.write(b'WAVE')         # 0x08  char[4]  Format         "WAVE"
            f.write(b'fmt ')         # 0x0C  char[4]  Subchunk1ID    "fmt "
            f.u32(16)                # 0x10  dword    SubchunkSize   16
            f.u16(1)                 # 0x14  word     AudioFormat    1 (PCM)
            f.u16(1)                 # 0x16  word     NumChannels    1 (mono)
            f.u32(sample.freq)       # 0x18  dword    SampleRate     sample rate from SDT format
            f.u32(sample.freq * 2)   # 0x1C  dword    ByteRate       sample rate from SDT format * 2
            f.u16(2)                 # 0x20  word     BlockAlign     2
            f.u16(16)                # 0x22  word     BitsPerSample  16
            f.write(b'data')         # 0x24  char[4]  Subchunk2ID    "data"
            f.u32(sample.size)       # 0x28  dword    Sunchunk2Size  size from SDT format
            f.write(data)            # 0x2C  -        Data           raw SFX data

            f.save(outPath)



def _test_ ():
    SFXReader.parseDefault()



__all__ = [
    'SFXReader',
    'SFXSample',

    '_test_',
]



if __name__ == '__main__':
    _test_()
