import os
import sys
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bfw.utils import *



FFPROBE_EXE_NAME = 'ffprobe.exe'


class FFProbeError (Exception):
    pass


class FFProbe:
    _exePath = None

    @classmethod
    def _getExe (cls):
        if not cls._exePath:
            cls._exePath = findFileInEnv(FFPROBE_EXE_NAME)

            if not cls._exePath:
                raise Exception(f'Failed to find { FFPROBE_EXE_NAME }')

        return cls._exePath

    @classmethod
    def getFormatTags (cls, filePath):
        tags = FFProbe.getMeta(filePath, entries='stream_tags:format_tags')

        return tags.get('format', {}).get('tags')

    # https://ffmpeg.org/ffprobe.html#Main-options
    @classmethod
    def getMeta (cls,
        filePath,
        streams          = None,    # -select_streams
        includeData      = False,   # -show_data
        includeDataHash  = False,   # -show_data_hash
        includeFormat    = False,   # -show_format
        entries          = None,    # -show_entries
        includePackets   = False,   # -show_packets
        includeFrames    = False,   # -show_frames
        includeLog       = False,   # -show_log
        includeStreams   = False,   # -show_streams
        includePrograms  = False,   # -show_programs
        includeChapters  = False,   # -show_chapters
        countFrames      = False,   # -count_frames
        countPackets     = False,   # -count_packets
        readIntervals    = None,    # -read_intervals
        includeProgVer   = False,   # -show_program_version
        includeLibVer    = False,   # -show_library_versions
        includePixFormat = False,   # -show_pixel_formats

    ):
        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        cmdArgs = []

        if streams is not None:
            cmdArgs.append('-select_streams')
            cmdArgs.append(streams)

        if includeData:
            cmdArgs.append('-show_data')

        if includeDataHash:
            cmdArgs.append('-show_data_hash')

        if includeFormat:
            cmdArgs.append('-show_format')

        if entries:
            cmdArgs.append('-show_entries')
            cmdArgs.append(entries)

        if includePackets:
            cmdArgs.append('-show_packets')

        if includeFrames:
            cmdArgs.append('-show_frames')

        if includeLog:
            cmdArgs.append('-show_log')

        if includeStreams:
            cmdArgs.append('-show_streams')

        if includePrograms:
            cmdArgs.append('-show_programs')

        if includeChapters:
            cmdArgs.append('-show_chapters')

        if countFrames:
            cmdArgs.append('-count_frames')

        if countPackets:
            cmdArgs.append('-count_packets')

        if readIntervals:
            cmdArgs.append('-read_intervals')
            cmdArgs.append(readIntervals)

        if includeProgVer:
            cmdArgs.append('-show_program_version')

        if includeLibVer:
            cmdArgs.append('-show_library_versions')

        if includePixFormat:
            cmdArgs.append('-show_pixel_formats')

        cmd = [
            cls._getExe(),
            '-v',
            'quiet',
            '-show_error',
            '-show_private_data',
            *cmdArgs,
            '-print_format',
            'json',
            filePath
        ]

        ffprobe = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        info = parseJsonSafe(ffprobe.stdout)

        if info is None:
            raise FFProbeError('Failed to parse ffprobe result as json')

        if ffprobe.returncode != 0:
            code    = info['error']['code']
            message = info['error']['string']

            raise FFProbeError(f'{ message } ({ code })')

        return info



def _test_ ():
    # print(findFileInEnv('ffmpeg.exe'))
    # print(toJson(FFProbe.getMeta(r"C:\Projects\PythonLib\python\v001\bfw\media\ffmpeg\ffprobe.py")))
    print(toJson(FFProbe.getFormatTags(r"D:\Documents\Музыка\Burito\Rab Kinoflo.flac")));
    print(toJson(FFProbe.getMeta(
        r"D:\Documents\Музыка\OST - Nick Brewer - Zombie Army 4\MUS_Battle_Track02_100BPM_4-4_Full.wav",
        # includeData      = True,   # -show_data
        # includeDataHash  = True,   # -show_data_hash
        includeFormat    = True,   # -show_format
        # includePackets   = True,   # -show_packets
        # includeFrames    = True,   # -show_frames
        # includeLog       = True,   # -show_log
        includeStreams   = True,   # -show_streams
        # includePrograms  = True,   # -show_programs
        # includeChapters  = True,   # -show_chapters
        # countFrames      = True,   # -count_frames
        # countPackets     = True,   # -count_packets
        # includeProgVer   = True,   # -show_program_version
        # includeLibVer    = True,   # -show_library_versions
        # includePixFormat = True,   # -show_pixel_formats
    )))



__all__ = [
    'FFProbe',
    'FFProbeError',
]



if __name__ == '__main__':
    _test_()

