from typing import Annotated, Tuple, List, Union



# TODO: Python 3.12: type VecValue = Union[ int, float ]
VecValue = Union[ int, float ]
Vec      = List[ VecValue ]
Vec2     = Vec
Vec3     = Vec
Vec4     = Vec

# Doesn't work
# Vec3 = List[ VecValue, VecValue, VecValue ]
# Vec4 = List[ VecValue, VecValue, VecValue, VecValue ]

v : Vec3 = [1, 5.5, 6]


__all__ = [
    'VecValue',
    'Vec',
    'Vec2',
    'Vec3',
    'Vec4',
]



if __name__ == '__main__':
    pass
