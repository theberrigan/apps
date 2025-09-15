import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from bfw.utils import *
from bfw.reader import *
from bfw.media.ffmpeg import FFProbe, FFMpeg



WAV_SAMPLES_DIR = r'C:\Projects\_Data_Samples\wav'



# https://en.wikipedia.org/wiki/WAV
# https://www.mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
# https://docs.fileformat.com/audio/wav/
# http://soundfile.sapp.org/doc/WaveFormat/
class WAV:
    def __init__ (self):
        pass

    @classmethod
    def ffprobe (cls, wavPath):
        return FFProbe.getMeta(wavPath, includeFormat=True, includeStreams=True)

    @classmethod
    def fromFile (cls, filePath):
        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._read(f)

    @classmethod
    def fromBuffer (cls, data):
        with MemReader(data) as f:
            return cls._read(f)

    @classmethod
    def _read (cls, f):
        wav = WAV()


def collectWav ():
    wavMap = {}

    for drive in getDrives(True):
        for wavPath in iterFiles(drive, True, [ '.wav' ]):
            if wavPath.lower().startswith(WAV_SAMPLES_DIR.lower()):
                continue

            print(wavPath)

            try:
                meta = FFProbe.getMeta(wavPath, includeFormat=True, includeStreams=True)
            except:
                continue

            # print(toJson(meta)); sys.exit()

            if not meta:
                continue

            streams = meta['streams']

            key = meta['format']['format_name']

            for stream in streams:
                key += (
                    '|' +
                    str(stream.get('codec_name', '?'))      + '|' +
                    str(stream.get('sample_fmt', '?'))      + '|' +
                    str(stream.get('sample_rate', '?'))     + '|' +
                    str(stream.get('channels', '?'))        + '|' +
                    str(stream.get('bits_per_sample', '?')) + '|' +
                    str(stream.get('r_frame_rate', '?'))    + '|' +
                    str(stream.get('time_base', '?'))
                )

            key = key.lower()

            fileSize = getFileSize(wavPath)

            old = wavMap.get(key)

            if not old or old['size'] > fileSize:
                wavMap[key] = {
                    'path': wavPath,
                    'size': fileSize
                }

                print(key, wavPath)

    for wav in wavMap.values():
        wavPath = wav['path']

        data = readBin(wavPath)
        crc  = calcCRC32(data)

        dstPath = joinPath(WAV_SAMPLES_DIR, '4', f'{getFileName(wavPath)}.{crc:08X}.wav')

        writeBin(dstPath, data)

    totalSize = sum([ wav['size'] for wav in wavMap.values() ])
    wavMap = [ wav['path'] for wav in wavMap.values() ]

    writeJson(joinPath(WAV_SAMPLES_DIR, '4', '.desc.json'), wavMap)

    print(toJson(wavMap))
    print(formatSize(totalSize))
    # sys.exit()


def createSamples ():
    codecs = [
        'adpcm_ima_wav',
        'adpcm_ms',
        'adpcm_swf',
        'adpcm_yamaha',
        'pcm_alaw',
        'pcm_f32le',
        'pcm_f64le',
        'pcm_mulaw',
        'pcm_s16le',
        'pcm_s24le',
        'pcm_s32le',
        'pcm_s64le',
        'pcm_u8'
    ]

    sampleRates = [
        8000,
        11025,
        16000,
        22050,
        24000,
        32000,
        44100,
        48000,
        88200,
        96000,
        176400,
        192000,
        352800,
        384000,
        768000
    ]

    srcPath = joinPath(WAV_SAMPLES_DIR, '4', 'bear_192kHz.1B6D9E9C.wav')

    for codec in codecs:
        for sampleRate in sampleRates:
            for channelCount, channels in [ (1, 'mono'), (2, 'stereo') ]:
                dstName = f'a_{ codec }_{ sampleRate }_{ channels }.wav'
                dstPath = joinPath(WAV_SAMPLES_DIR, '5', dstName)

                isOk = FFMpeg.convertAudio(srcPath, dstPath, codec, sampleRate, channelCount)

                if not isOk:
                    if isFile(dstPath):
                        removeFile(dstPath)

                    print('Failed to convert:', dstName)


def _test_ ():
    for wavPath in iterFiles(WAV_SAMPLES_DIR, True, [ '.wav' ]):
        WAV.fromFile(wavPath)


__all__ = [
    'WAV'
]



if __name__ == '__main__':
    _test_()
