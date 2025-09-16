import sys
import struct

from random import randint

import numpy

sys.path.insert(0, r'C:\Projects\PythonLib\python')

from bfw.utils import *
from bfw.reader import *
from bfw.writer import BinWriter
from bfw.native.limits import *

from _consts import *
from _math_types import *
from _voxels import VOXELS



# https://florianfe.github.io/vox-viewer/demo/
# https://drububu.com/miscellaneous/voxelizer/
# https://paulbourke.net/dataformats/vox/



KVX_COLOR_COUNT = 256



class KvxFlag:
    No    = 0 << 0
    FlipX = 1 << 0
    FlipY = 1 << 1
    FlipZ = 1 << 2


class VoxelData:
    def __init__ (self, size, voxels, palette):
        self.size    = size         # Vec3
        self.count   = len(voxels)  # int
        self.voxels  = voxels       # (x, y, z, i)[]
        self.palette = palette      # [r, g, b][]


def readKvx (kvxPath, flags=KvxFlag.No):
    assert isFile(kvxPath)

    voxSize = None
    voxels  = []
    palette = []

    with openFile(kvxPath) as f:
        # i32 mip1leng
        # vec3 voxSize
        # vec3 voxPivot
        # i32 xoffset[voxSize.x + 1]
        # u16 xyoffset[voxSize.x][voxSize.y + 1]

        _mipSize  = f.i32()
        voxSize   = Vec3(*f.vec3i32())
        _pivot    = f.vec3i32()
        _offsetsX = f.u32(voxSize.x + 1)
        offsetsXY = f.u16(voxSize.x * (voxSize.y + 1))

        for x in range(voxSize.x):
            for y in range(voxSize.y):
                offsetIdx = x * (voxSize.y + 1) + y
                chunkSize = offsetsXY[offsetIdx + 1] - offsetsXY[offsetIdx]
                chunkEnd  = f.tell() + chunkSize
                z1 = 0

                while f.tell() < chunkEnd:
                    z0       = f.u8()  # offset from top in voxels 
                    voxCount = f.u8()  # count of solid voxels
                    _flags   = f.u8()  # flags

                    z1 = z0 + voxCount

                    for z in range(z0, z1):
                        colorIndex = f.u8() + 1

                        assert colorIndex < 256

                        if flags & KvxFlag.FlipX:
                            x_ = voxSize.x - 1 - x
                        else:
                            x_ = x

                        if flags & KvxFlag.FlipY:
                            y_ = voxSize.y - 1 - y
                        else:
                            y_ = y

                        if flags & KvxFlag.FlipZ:
                            z_ = voxSize.z - 1 - z
                        else:
                            z_ = z

                        voxels.append((x_, y_, z_, colorIndex))

        f.fromEnd(-(3 * KVX_COLOR_COUNT))

        for _ in range(KVX_COLOR_COUNT):
            rgb = f.u8(3)

            rgb[0] = int(rgb[0] / 63 * 255)
            rgb[1] = int(rgb[1] / 63 * 255)
            rgb[2] = int(rgb[2] / 63 * 255)

            palette.append(rgb)

        assert not f.remaining()
        assert len(palette) == KVX_COLOR_COUNT

    return VoxelData(voxSize, voxels, palette)

def kvxToVox (kvxPath, voxPath, flags=KvxFlag.No):
    kvx = readKvx(kvxPath, flags)

    createDirs(getDirPath(voxPath))

    palette = []

    for rgb in kvx.palette:
        palette += rgb + [ 255 ]

    with BinWriter() as f:
        f.write(b'VOX ')
        f.u32(150)

        f.write(b'MAIN')
        f.u32(0)

        mainChildrenSizeOffset = f.tell()

        f.u32(0)  # rewrite later

        mainChildrenStart = f.tell()

        f.write(b'SIZE')
        f.u32(U32_BYTES * 3)
        f.u32(0)
        f.u32(kvx.size.x)
        f.u32(kvx.size.y)
        f.u32(kvx.size.z)

        f.write(b'XYZI')
        f.u32(U32_BYTES + U8_BYTES * 4 * kvx.count)
        f.u32(0)
        f.u32(kvx.count)

        for x, y, z, colorIndex in kvx.voxels:
            f.u8(x)
            f.u8(y)
            f.u8(z)
            f.u8(colorIndex)

        f.write(b'RGBA')
        f.u32(U8_BYTES * 4 * KVX_COLOR_COUNT)
        f.u32(0)
        f.u8(*palette)

        f.seek(mainChildrenSizeOffset)
        f.u32(f.getSize() - mainChildrenStart)

        f.save(voxPath)

def kvxToVxl (kvxPath, vxlPath, flags=KvxFlag.No):
    kvx = readKvx(kvxPath, flags)

    createDirs(getDirPath(vxlPath))

    palette = sum(kvx.palette, [])

    with BinWriter() as f:
        f.write(b'VOXL')
        f.u16(1)  # version

        f.u16(kvx.size.x)
        f.u16(kvx.size.y)
        f.u16(kvx.size.z)

        f.u32(kvx.count)

        for x, y, z, colorIndex in kvx.voxels:
            f.u8(x)
            f.u8(y)
            f.u8(z)
            f.u8(colorIndex)

        assert len(palette) == (3 * KVX_COLOR_COUNT)

        f.u8(*palette)

        f.save(vxlPath)

# ----------------------------------------------------------------------------------------------------------------------

class Direction:
    NegativeZ = 0
    NegativeY = 1
    NegativeX = 2
    PositiveX = 3
    PositiveY = 4
    PositiveZ = 5

# Right-handed, +Z to up
ORTHOGONAL_DIRECTIONS = (
    (Direction.PositiveY, Direction.PositiveX),  # [Direction.NegativeZ]
    (Direction.PositiveX, Direction.PositiveZ),  # [Direction.NegativeY]
    (Direction.PositiveZ, Direction.PositiveY),  # [Direction.NegativeX]
    (Direction.PositiveZ, Direction.PositiveY),  # [Direction.PositiveX]
    (Direction.PositiveX, Direction.PositiveZ),  # [Direction.PositiveY]
    (Direction.PositiveY, Direction.PositiveX),  # [Direction.PositiveZ]
)

DIRECTION_VECTORS = (
    ( 0,  0, -1),  # [Direction.NegativeZ]
    ( 0, -1,  0),  # [Direction.NegativeY]
    (-1,  0,  0),  # [Direction.NegativeX]
    ( 1,  0,  0),  # [Direction.PositiveX]
    ( 0,  1,  0),  # [Direction.PositiveY]
    ( 0,  0,  1),  # [Direction.PositiveZ]
)

COMPASS_DIRECTION_VECTORS = (
    ( 0,  1),
    ( 1,  0),
    ( 0, -1),
    (-1,  0)
)

def expandVoxelSpace (voxels):
    shape  = [ d + 2 for d in voxels.shape ]
    result = numpy.zeros(shape, numpy.int32)
    
    for x in range(1, shape[0] - 1):
        for y in range(1, shape[1] - 1):
            for z in range(1, shape[2] - 1):
                result[x][y][z] = voxels[x - 1][y - 1][z - 1]
    
    return result

def markSolidVoxels (voxels):
    solids = numpy.zeros(voxels.shape, numpy.int8)

    sx, sy, sz = voxels.shape

    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                solids[x][y][z] = int(
                    0 < x < (sx - 1) and
                    0 < y < (sy - 1) and
                    0 < z < (sz - 1) and
                    voxels[x][y][z] > 0
                )

    return solids

def scaleVector (factor, vec):
    return [ c * factor for c in vec ]

def getCoordPos (basePos, coords, orthoVecs):
    coords = [
        scaleVector(coords[1], orthoVecs[0]),
        scaleVector(coords[0], orthoVecs[1])
    ]

    return [
        basePos[0] + coords[0][0] + coords[1][0],
        basePos[1] + coords[0][1] + coords[1][1],
        basePos[2] + coords[0][2] + coords[1][2],
    ]

def extractSurface (voxels, solids, marks, voxPos, direction):
    # cur dir vec
    dirVec = DIRECTION_VECTORS[direction]

    # orthogonal vecs for cur dir vec
    orthoVecs = [ DIRECTION_VECTORS[d] for d in ORTHOGONAL_DIRECTIONS[direction] ]

    # voxel color
    voxelValue = voxels[*voxPos]

    stack1 = [ [ 0, 0 ] ]  # keeps next coords?
    stack2 = [ [ 0, 0 ] ]
    minCoords = [ 0, 0 ]
    maxCoords = [ 0, 0 ]

    while stack1:
        curCoords = stack1.pop()
        curPos = getCoordPos(voxPos, curCoords, orthoVecs)

        # if cur vox side is not used yet
        if marks[*curPos, direction] == 0:
            stack2.append(list(curCoords))  # push [0, 0] from stack1
            marks[*curPos, direction] = 1  # mark side as used

            if curCoords[0] < minCoords[0]:
                minCoords[0] = curCoords[0]

            if curCoords[1] < minCoords[1]:
                minCoords[1] = curCoords[1]

            if curCoords[0] > maxCoords[0]:
                maxCoords[0] = curCoords[0]

            if curCoords[1] > maxCoords[1]:
                maxCoords[1] = curCoords[1]

            for i, orthoVec in enumerate(orthoVecs):
                # curPos == [5, 1, 86]
                # npxyz  == [5, 1, 87] and [5, 2, 86]
                # popxyz == [4, 1, 87] and [4, 2, 86]

                # next position Vec3
                npx = curPos[0] + orthoVec[0]
                npy = curPos[1] + orthoVec[1]
                npz = curPos[2] + orthoVec[2]

                # potential occluding position Vec3
                popx = npx + dirVec[0]
                popy = npy + dirVec[1]
                popz = npz + dirVec[2]

                # if npxyz is solid and has same color, and popxyz is not solid
                if voxels[npx][npy][npz] == voxelValue and solids[npx][npy][npz] == 1 and solids[popx][popy][popz] == 0:
                    # clockwise | North - East - South - West
                    compDirVec = COMPASS_DIRECTION_VECTORS[i]

                    # next coordinates
                    stack1.append([
                        curCoords[0] + compDirVec[0],
                        curCoords[1] + compDirVec[1],
                    ])

    size = [  # [3, 3]
        maxCoords[0] - minCoords[0] + 3,
        maxCoords[1] - minCoords[1] + 3,
    ]

    field = numpy.zeros(size, numpy.uint32)  # [[0 0 0], [0 0 0], [0 0 0]]

    while stack2:
        curCoords = stack2.pop()

        x = curCoords[0] - minCoords[0] + 1
        y = curCoords[1] - minCoords[1] + 1

        if field[x][y] == 0:
            field[x][y] = 1

    return {
        'voxelValue': voxelValue,
        'direction': direction,
        'field': field,
        'fieldMinPosition': getCoordPos(voxPos, minCoords, orthoVecs)
    }

def extractSurfaces (voxels, solids):
    marks = numpy.zeros([ *voxels.shape, 6 ])
    surfaces = []

    sx, sy, sz = voxels.shape

    for y in range(sy):  # [0, 37)
        for z in range(sz):  # [0, 128)
            isPrevSolid = False

            for x in range(sx):  # [0, 12)
                isSolid = bool(solids[x][y][z])

                # if cur and prev voxels have different solidness along X axis
                if isPrevSolid != isSolid:
                    # if cur solid and prev not solid, and side of the voxel is not used yet
                    if isSolid and marks[x][y][z][Direction.NegativeX] == 0:
                        surfaces.append(extractSurface(voxels, solids, marks, [x, y, z], Direction.NegativeX))

                    if not isSolid and marks[x - 1][y][z][Direction.PositiveX] == 0:
                        surfaces.append(extractSurface(voxels, solids, marks, [x - 1, y, z], Direction.PositiveX))

                isPrevSolid = isSolid

    for x in range(sx):
        for z in range(sz):
            isPrevSolid = False

            for y in range(sy):
                isSolid = bool(solids[x][y][z])

                if isPrevSolid != isSolid:
                    if isSolid and marks[x][y][z][Direction.NegativeY] == 0:
                        surfaces.append(extractSurface(voxels, solids, marks, [x, y, z], Direction.NegativeY))

                    if not isSolid and marks[x][y - 1][z][Direction.PositiveY] == 0:
                        surfaces.append(extractSurface(voxels, solids, marks, [x, y - 1, z], Direction.PositiveY))

                isPrevSolid = isSolid

    for x in range(sx):
        for y in range(sy):
            isPrevSolid = False

            for z in range(sz):
                isSolid = bool(solids[x][y][z])

                if isPrevSolid != isSolid:
                    if isSolid and marks[x][y][z][Direction.NegativeZ] == 0:
                        surfaces.append(extractSurface(voxels, solids, marks, [x, y, z], Direction.NegativeZ))

                    if not isSolid and marks[x][y][z - 1][Direction.PositiveZ] == 0:
                        surfaces.append(extractSurface(voxels, solids, marks, [x, y, z - 1], Direction.PositiveZ))

                isPrevSolid = isSolid

    return surfaces

def kvxToMesh (kvxPath, flags=KvxFlag.No):
    kvx = readKvx(kvxPath, flags)

    voxels = numpy.zeros([ kvx.size.x, kvx.size.y, kvx.size.z ])

    for x, y, z, i in kvx.voxels:
        assert i > 0
        voxels[x][y][z] = i

    print('Shape before transpose:', voxels.shape)

    voxels = voxels.transpose((1, 2, 0))

    print('Shape after transpose:', voxels.shape)

    print('Expanding voxels...')
    expandedVoxels = expandVoxelSpace(voxels)    # create 1-voxel-width bounding box for the voxel model

    print('Mark solid voxels...')
    solidMarks = markSolidVoxels(expandedVoxels)  # mark all solid voxels as 1 and others as 0
    # 53874 - 0; 2958 - 1; 12x37x128

    print('Extracting surfaces...')
    surfaces = extractSurfaces(expandedVoxels, solidMarks)

    print(len(surfaces))

    # print(toJson([ int(i) for i in list(expVoxels.flatten('K')) ], pretty=False))


def loadVoxels ():
    voxDir = joinPath(GAME_DIR, 'voxels', 'vox')
    vxlDir = joinPath(GAME_DIR, 'voxels', 'vxl')

    kvxFlags = KvxFlag.FlipX | KvxFlag.FlipY | KvxFlag.FlipZ

    for voxel in VOXELS:
        kvxPath = voxel['path']
        kvxPath = getAbsPath(joinPath(GAME_DIR, kvxPath))

        print(kvxPath)

        # voxPath = getFileName(kvxPath) + '.vox'
        # voxPath = joinPath(voxDir, voxPath)

        # kvxToVox(kvxPath, voxPath, kvxFlags)

        vxlPath = getFileName(kvxPath) + '.vxl'
        vxlPath = joinPath(vxlDir, vxlPath)

        kvxToVxl(kvxPath, vxlPath, kvxFlags)

        print(' ')



if __name__ == '__main__':
    # loadVoxels()
    kvxToMesh(joinPath(GAME_DIR, 'voxels', '209_BATON.kvx'))
    # kvxToMesh(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))
    # loadVoxel(joinPath(GAME_DIR, 'voxels', '209_BATON.kvx'))
    # loadVoxel(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))
