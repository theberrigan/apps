from ...common import bfw
from ...common.consts import *

from bfw.utils import joinPath


SFX_RAW_EXT = '.raw'
SFX_SDT_EXT = '.sdt'

SFX_RAW_FILE_PATH = joinPath(GAME_DIR, 'audio', f'sfx{ SFX_RAW_EXT }')
SFX_SDT_FILE_PATH = joinPath(GAME_DIR, 'audio', f'sfx{ SFX_SDT_EXT }')

SFX_SAMPLE_STRUCT_SIZE = 20



__all__ = [
    'SFX_RAW_EXT',
    'SFX_SDT_EXT',
    'SFX_RAW_FILE_PATH',
    'SFX_SDT_FILE_PATH',
    'SFX_SAMPLE_STRUCT_SIZE',
]
