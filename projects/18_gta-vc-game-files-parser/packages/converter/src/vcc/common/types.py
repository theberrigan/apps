from typing import Optional as Opt, Iterator, Self, Type, Union, Tuple, Dict, List, Callable, Any, TypeVar



TInt      = Opt[int]
TFloat    = Opt[float]
TBool     = Opt[bool]
TStr      = Opt[str]
TVec      = Opt[List[float]]
TVec2     = TVec
TVec3     = TVec
TVec4     = TVec
TRGB      = Opt[List[int]]
TRGBA     = Opt[List[int]]
TUV       = Opt[List[int]]
TBytes    = Opt[bytes | bytearray]
TBArray   = Opt[bytearray]
TTuple    = Opt[Tuple]
TDict     = Opt[Dict]
TList     = Opt[List]
TCallable = Opt[Callable]


class Sphere:
    def __init__ (self):
        self.center : Opt[List[float]] = None
        self.radius : TInt             = None

    def set (self, radius : float, center : List[float]):
        self.center = center
        self.radius = radius


class Box:
    def __init__ (self):
        self.min : Opt[List[float]] = None
        self.max : Opt[List[float]] = None

    def set (self, boxMin : List[float], boxMax : List[float]):
        self.min = boxMin
        self.max = boxMax



__all__ = [
    'Opt',
    'Iterator',
    'Self',
    'Type',
    'Union',
    'Tuple',
    'Dict',
    'List',
    'Callable',
    'Any',
    'TypeVar',
    'TInt',
    'TFloat',
    'TBool',
    'TStr',
    'TVec',
    'TVec2',
    'TVec3',
    'TVec4',
    'TRGB',
    'TRGBA',
    'TUV',
    'TBytes',
    'TBArray',
    'TTuple',
    'TDict',
    'TList',
    'TCallable',
    'Sphere',
    'Box',
]