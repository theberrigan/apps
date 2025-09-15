import math

from ..common import bfw
from ..common.consts import *

from .consts import *
from .types import *



def degToRad (deg : float) -> float:
    return deg * math.pi / 180

def radToDeg (rad : float) -> float:
    return rad * 180 / math.pi



def _test_ ():
    pass



__all__ = [
    'degToRad',
    'radToDeg',

    '_test_',
]



if __name__ == '__main__':
    _test_()
