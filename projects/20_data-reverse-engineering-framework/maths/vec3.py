import os
import sys

from math import sqrt, floor, ceil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.maths.types import Vec3, Vec4



VEC3_ORIGIN = [ 0, 0, 0 ]



def dotVec3 (v1 : Vec3 | Vec4, v2 : Vec3 | Vec4) -> float | int:
    assert len(v1) >= 3 and len(v2) >= 3

    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def lenVec3 (v : Vec3 | Vec4) -> float | int:
    assert len(v) >= 3

    return sqrt(dotVec3(v, v))


def scaleVec3 (v : Vec3 | Vec4, scalar : float | int, out : Vec3 | Vec4 = None) -> None:
    assert len(v) >= 3

    if out is None:
        out = v

    out[0] = v[0] * scalar
    out[1] = v[1] * scalar
    out[2] = v[2] * scalar

    if v != out and len(v) == 4:
        out[3] = v[3]

    return out


def subVec3 (v1 : Vec3 | Vec4, v2 : Vec3 | Vec4, out : Vec3 | Vec4 = None) -> None:
    if out is None:
        out = v1

    assert len(v1) >= 3 and len(v2) >= 3 and len(out) >= 3

    out[0] = v1[0] - v2[0]
    out[1] = v1[1] - v2[1]
    out[2] = v1[2] - v2[2]

    return out


def divVec3 (v : Vec3 | Vec4, scalar : float | int, out : Vec3 | Vec4 = None) -> None:
    assert len(v) >= 3

    return scaleVec3(v, 1 / scalar, out)


def avgVec3 (v : Vec3 | Vec4) -> float | int:
    assert len(v) >= 3

    return (v[0] + v[1] + v[2]) / 3


def averageVec3 (v1 : Vec3 | Vec4, v2 : Vec3 | Vec4, out : Vec3 | Vec4 = None) -> None:
    if out is None:
        out = v1
        
    assert len(v1) >= 3 and len(v2) >= 3 and len(out) >= 3

    out[0] = (v1[0] + v2[0]) * 0.5
    out[1] = (v1[1] + v2[1]) * 0.5
    out[2] = (v1[2] + v2[2]) * 0.5

    return out


def normVec3 (v : Vec3 | Vec4):
    assert len(v) >= 3

    vLen = lenVec3(v)

    if vLen:
        vLen = 1 / vLen

    v[0] *= vLen
    v[1] *= vLen
    v[2] *= vLen

    return v


def copyVec3 (src : Vec3 | Vec4, dst : Vec3 | Vec4):
    assert len(src) >= 3 and len(dst) >= 3

    dst[0] = src[0]
    dst[1] = src[1]
    dst[2] = src[2]

    return dst


def areEqVec3 (v1 : Vec3 | Vec4, v2 : Vec3 | Vec4) -> bool:
    assert len(v1) >= 3 and len(v2) >= 3

    return v1[0] == v2[0] and v1[1] == v2[1] and v1[2] == v2[2]



def _test_ ():
    print(lenVec3([3, 3, 3]))
    v = [ 1, 2, 3, 4 ]
    scaleVec3(v, 2, v)
    print(v)
    print(avgVec3([2, 3, 4]))
    v1 = [ 1, 2, 3 ]
    v2 = [ 3, 4, 5 ]
    v3 = [ 0, 0, 0 ]
    averageVec3(v1, v2, v3)
    print(v3)



__all__ = [
    'VEC3_ORIGIN',
    'sqrt',
    'floor',
    'ceil',
    'dotVec3',
    'lenVec3',
    'scaleVec3',
    'subVec3',
    'divVec3',
    'avgVec3',
    'averageVec3',
    'normVec3',
    'copyVec3',
    'areEqVec3',
]



if __name__ == '__main__':
    _test_()
