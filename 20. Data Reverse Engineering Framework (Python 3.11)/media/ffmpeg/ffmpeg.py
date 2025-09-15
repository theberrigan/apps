import os
import sys
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bfw.utils import *



FFMPEG_EXE_NAME = 'ffmpeg.exe'


class FFMpegError (Exception):
    pass


class FFMpeg:
    _exePath = None

    @classmethod
    def _getExe (cls):
        if not cls._exePath:
            cls._exePath = findFileInEnv(FFMPEG_EXE_NAME)

            if not cls._exePath:
                raise Exception(f'Failed to find { FFMPEG_EXE_NAME }')

        return cls._exePath

    # https://ffmpeg.org/ffmpeg.html
    @classmethod
    def convertAudio (cls,
        srcPath,
        dstPath,
        codec,        # -acodec
        sampleRate,   # -ar
        channelCount  # -ac

    ):
        if not isFile(srcPath):
            raise Exception(f'File does not exist: { srcPath }')

        cmd = [
            cls._getExe(),
            '-hide_banner',
            '-y',
            '-i',
            srcPath,            
            '-acodec',
            codec,
            '-ar',
            str(sampleRate),
            '-ac',
            str(channelCount),
            '-progress',
            '-',
            dstPath
        ]

        # subprocess.PIPE
        ffmpeg = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr)

        return ffmpeg.returncode == 0



def _test_ ():
    codecs = [
        'aac',
        'ac3',
        'adpcm_adx',
        'adpcm_argo',
        'adpcm_g722',
        'adpcm_g726',
        'adpcm_g726le',
        'adpcm_ima_alp',
        'adpcm_ima_amv',
        'adpcm_ima_apm',
        'adpcm_ima_qt',
        'adpcm_ima_ssi',
        'adpcm_ima_wav',
        'adpcm_ima_ws',
        'adpcm_ms',
        'adpcm_swf',
        'adpcm_yamaha',
        'alac',
        'amr_nb',
        'anull',
        'aptx',
        'aptx_hd',
        'comfortnoise',
        'dfpwm',
        'dts',
        'eac3',
        'flac',
        'g723_1',
        'mlp',
        'mp2',
        'mp3',
        'nellymoser',
        'opus',
        'pcm_alaw',
        'pcm_bluray',
        'pcm_dvd',
        'pcm_f32be',
        'pcm_f32le',
        'pcm_f64be',
        'pcm_f64le',
        'pcm_mulaw',
        'pcm_s16be',
        'pcm_s16be_planar',
        'pcm_s16le',
        'pcm_s16le_planar',
        'pcm_s24be',
        'pcm_s24daud',
        'pcm_s24le',
        'pcm_s24le_planar',
        'pcm_s32be',
        'pcm_s32le',
        'pcm_s32le_planar',
        'pcm_s64be',
        'pcm_s64le',
        'pcm_s8',
        'pcm_s8_planar',
        'pcm_u16be',
        'pcm_u16le',
        'pcm_u24be',
        'pcm_u24le',
        'pcm_u32be',
        'pcm_u32le',
        'pcm_u8',
        'pcm_vidc',
        'ra_144',
        'roq_dpcm',
        's302m',
        'sbc',
        'sonic',
        'truehd',
        'tta',
        'vorbis',
        'wavpack',
        'wmav1',
        'wmav2'
    ]

    okCodecs = []

    for codec in codecs:
        if not codec.startswith('pcm_') and not codec.startswith('adpcm_'):
            continue

        result = FFMpeg.convertAudio(r"C:\Projects\_Data_Samples\wav\4\bear_192kHz.1B6D9E9C.wav", r"C:\Projects\_Data_Samples\wav\4\__bear_192kHz.1B6D9E9C.wav", codec, 44100, 2)  # 'pcm_s16le'

        if result:
            okCodecs.append(codec)

    print(toJson(okCodecs).replace('"', "'"))



__all__ = [
    'FFMpeg',
    'FFMpegError',
]



if __name__ == '__main__':
    _test_()

