from ...common import bfw
from ...common.consts import *

from bfw.utils import joinPath



SURFACE_FILE_PATH = joinPath(GAME_DIR, 'data', 'surface.dat')



__all__ = [
    'SURFACE_FILE_PATH',
]