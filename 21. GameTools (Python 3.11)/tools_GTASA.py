# GTA San Andreas Tools

import sys
import subprocess

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR   = r'G:\Steam\steamapps\common\Grand Theft Auto San Andreas'
AUDIO_DIR  = joinPath(GAME_DIR, 'audio')
STREAM_DIR = joinPath(AUDIO_DIR, 'streams')
SFX_DIR    = joinPath(AUDIO_DIR, 'sfx')

TOOLS_DIR              = r'D:\Apps\_Categories\Game Tools\GTA San Andreas'
SAAT_STREAM_PATH       = joinPath(TOOLS_DIR, 'saat_stream.exe')
SAAT_SFX_PATH          = joinPath(TOOLS_DIR, 'saat_sfx.exe')
SAAT_META_GENERIC_PATH = joinPath(TOOLS_DIR, 'metadata-generic.ini')
SAAT_META_FULL_PATH    = joinPath(TOOLS_DIR, 'metadata-full.ini')

KNOWN_STREAMS = [
    {
        'name': 'aa',
        'description': 'Emergency',
        'type': 'emergency'
    },
    {
        'name': 'adverts',
        'description': 'Radio advertisement',
        'type': 'ads'
    },
    {
        'name': 'ambience',
        'description': 'Ambient',
        'type': 'ambience'
    },
    {
        'name': 'cutscene',
        'description': 'Cutscenes',
        'type': 'cutscenes'
    },
    {
        'name': 'beats',
        'description': 'Beats',
        'type': 'beats'
    },
    {
        'name': 'ch',
        'description': 'Playback FM',        
        'type': 'radio'
    },
    {
        'name': 'co',
        'description': 'K-Rose',
        'type': 'radio'
    },
    {
        'name': 'cr',
        'description': 'K-DST',
        'type': 'radio'
    },
    {
        'name': 'ds',
        'description': 'Bounce FM',
        'type': 'radio'
    },
    {
        'name': 'hc',
        'description': 'SF-UR',
        'type': 'radio'
    },
    {
        'name': 'mh',
        'description': 'Radio Los Santos',
        'type': 'radio'
    },
    {
        'name': 'mr',
        'description': 'Radio X',
        'type': 'radio'
    },
    {
        'name': 'nj',
        'description': 'CSR 103.9',
        'type': 'radio'
    },
    {
        'name': 're',
        'description': 'K-JAH West',
        'type': 'radio'
    },
    {
        'name': 'rg',
        'description': 'Master Sounds 98.3',
        'type': 'radio'
    },
    {
        'name': 'tk',
        'description': 'WCTR',
        'type': 'radio'
    }
]


def extractStream (streamPath, outputDir=None, metaPath=None):
    if not isFile(streamPath):
        raise Exception(f'Stream file does not exist: { streamPath }')

    if not outputDir:
        outputDir = streamPath + '_extracted'

    if checkPathExists(outputDir) and not isDir(outputDir):
        raise Exception(f'Output path exists, but it is not a directory: { outputDir }')        

    if metaPath and not isFile(metaPath):
        raise Exception(f'Meta file does not exist: { metaPath }')

    print(f'Extracting stream { streamPath } to { outputDir }')

    if metaPath:
        saatArgs = [ SAAT_STREAM_PATH, '-r', streamPath, outputDir, metaPath ]
    else:
        saatArgs = [ SAAT_STREAM_PATH, '-e', streamPath, outputDir ]

    proc = subprocess.run(saatArgs, stdout=sys.stdout, stderr=sys.stderr)

    if proc.returncode != 0:
        raise Exception(f'Failed to extract stream { streamPath }')

    print(' ')


def extractKnownStreams (streamDir, outputDir=None, streamTypes=None):
    for stream in KNOWN_STREAMS:
        if streamTypes and stream['type'] not in streamTypes:
            continue

        streamPath = joinPath(streamDir, stream['name'])

        extractStream(streamPath, outputDir, None)  # SAAT_META_FULL_PATH


def extractKnownMusicStreams (streamDir):
    outputDir = joinPath(streamDir, '.extracted')
    
    extractKnownStreams(streamDir, outputDir, [ 'ads', 'radio', 'beats' ])


def main ():
    extractKnownMusicStreams(STREAM_DIR)



if __name__ == '__main__':
    main()
