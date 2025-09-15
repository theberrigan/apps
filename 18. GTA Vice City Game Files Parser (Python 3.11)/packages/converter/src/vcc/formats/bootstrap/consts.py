from ...common import bfw
from ...common.consts import *

from bfw.utils import joinPath



BOOT_DEFAULT_FILE_PATH = joinPath(GAME_DIR, 'data', 'default.dat')
BOOT_GTA_VC_FILE_PATH  = joinPath(GAME_DIR, 'data', 'gta_vc.dat')

# NOTE: order is important!
BOOT_ALL_FILE_PATHS = (
    BOOT_DEFAULT_FILE_PATH,
    BOOT_GTA_VC_FILE_PATH,
)



__all__ = [
    'BOOT_DEFAULT_FILE_PATH',
    'BOOT_GTA_VC_FILE_PATH',
    'BOOT_ALL_FILE_PATHS',
]