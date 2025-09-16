from ...common import bfw
from ...common.consts import GAME_DIR

from bfw.utils import joinPath



MODELS_DIR = joinPath(GAME_DIR, 'models')
MODEL_EXT  = '.mdl'



__all__ = [
    'MODELS_DIR',
    'MODEL_EXT',
]