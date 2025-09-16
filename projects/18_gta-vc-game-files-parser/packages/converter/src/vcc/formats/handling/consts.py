from ...common import bfw
from ...common.consts import *

from bfw.utils import joinPath



HANDLING_FILE_PATH = joinPath(GAME_DIR, 'data', 'handling.cfg')



__all__ = [
    'HANDLING_FILE_PATH',
]