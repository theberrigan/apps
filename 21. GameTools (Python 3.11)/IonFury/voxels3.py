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

class Flags:
    Solid   = 1 << 0
    Outside = 1 << 1
    Queued  = 1 << 2
    Skip    = Solid | Outside | Queued

def createVoxelKey (x, y, z):
    return (x << 32) | (y << 16) | z

# TODO: add flooded voxels counter
def traverseOutsideVoxels (kvx, voxMap, coords):
    maxX = kvx.size.x - 1
    maxY = kvx.size.y - 1
    maxZ = kvx.size.z - 1

    chain = tail = [ coords, None ]

    while chain:
        x, y, z = chain[0]

        info = voxMap[createVoxelKey(x, y, z)]

        # mark current voxel as an outside one
        info['f'] = clearBit(info['f'], Flags.Queued) | Flags.Outside

        # ------------------------

        for side, dx, dy, dz in SIDE_NEIGHBOURS:
            nextX = x + dx
            nextY = y + dy
            nextZ = z + dz

            if 0 <= nextX <= maxX and 0 <= nextY <= maxY and 0 <= nextZ <= maxZ:
                info = voxMap[createVoxelKey(nextX, nextY, nextZ)]

                if info['f'] & Flags.Skip:
                    continue

                tail[1] = [ (nextX, nextY, nextZ), None ]
                tail = tail[1]

                info['f'] |= Flags.Queued

        # ------------------------

        # switch to next voxel in the chain
        chain = chain[1]

class VoxSide:
    PosX = 1 << 0
    NegX = 1 << 1
    PosY = 1 << 2
    NegY = 1 << 3
    PosZ = 1 << 4
    NegZ = 1 << 5

SIDE_NEIGHBOURS = [
    (VoxSide.PosX,  1,  0,  0),  # +X
    (VoxSide.NegX, -1,  0,  0),  # -X
    (VoxSide.PosY,  0,  1,  0),  # +Y
    (VoxSide.NegY,  0, -1,  0),  # -Y
    (VoxSide.PosZ,  0,  0,  1),  # +Z
    (VoxSide.NegZ,  0,  0, -1),  # -Z
]

def detectSurfaces (kvx, voxMap):
    solids = kvx.voxels

    sizeX = kvx.size.x
    sizeY = kvx.size.y
    sizeZ = kvx.size.z

    maxX = sizeX - 1
    maxY = sizeY - 1
    maxZ = sizeZ - 1

    solids = [ [ *v, 0 ] for v in solids ]

    for voxel in solids:
        x = voxel[0]
        y = voxel[1]
        z = voxel[2]

        for side, dx, dy, dz in SIDE_NEIGHBOURS:
            nextX = x + dx
            nextY = y + dy
            nextZ = z + dz

            if 0 <= nextX <= maxX and 0 <= nextY <= maxY and 0 <= nextZ <= maxZ:
                info = voxMap[createVoxelKey(nextX, nextY, nextZ)]

                if not (info['f'] & Flags.Outside):
                    continue

            voxel[4] |= side

    return solids

def processVoxel (kvxPath):
    kvx = readKvx(kvxPath)

    solids = kvx.voxels

    print('size =', kvx.size)

    sizeX = kvx.size.x
    sizeY = kvx.size.y
    sizeZ = kvx.size.z

    maxX = sizeX - 1
    maxY = sizeY - 1
    maxZ = sizeZ - 1

    voxMap = {}

    for x in range(sizeX):
        for y in range(sizeY):
            for z in range(sizeZ):
                voxMap[createVoxelKey(x, y, z)] = {
                    'f': 0,    # flags
                }

    for x, y, z, i in solids:
        info = voxMap[createVoxelKey(x, y, z)]
        info['f'] = Flags.Solid

    # Two XY sides
    for x in range(sizeX):
        for y in range(sizeY):
            for z in [ 0, maxZ ]:
                info = voxMap[createVoxelKey(x, y, z)]

                if info['f'] & Flags.Skip:
                    continue

                traverseOutsideVoxels(kvx, voxMap, (x, y, z))

    # Two YZ sides
    for y in range(sizeY):
        for z in range(sizeZ):
            for x in [ 0, maxX ]:
                info = voxMap[createVoxelKey(x, y, z)]

                if info['f'] & Flags.Skip:
                    continue

                traverseOutsideVoxels(kvx, voxMap, (x, y, z))

    # Two XZ sides
    for x in range(sizeX):
        for z in range(sizeZ):
            for y in [ 0, maxY ]:
                info = voxMap[createVoxelKey(x, y, z)]

                if info['f'] & Flags.Skip:
                    continue

                traverseOutsideVoxels(kvx, voxMap, (x, y, z))

    # TODO: discard solids with sides == 0
    solids = detectSurfaces(kvx, voxMap)

    # print(voxMap[createVoxelKey(2, 1, 27)]); sys.exit()

    area = 0

    for solid in solids:
        if solid[4] != 0:
            area += 6

    print(area)

    # for solid in solids:  # 2, 1, 27
    #     if solid[0] == 125 and solid[1] == 4 and solid[2] == 30:
    #     # if not solid[4]:
    #         print(solid)


def loadVoxels ():
    for voxel in VOXELS:
        kvxPath = voxel['path']
        kvxPath = getAbsPath(joinPath(GAME_DIR, kvxPath))

        print(kvxPath)

        processVoxel(kvxPath)

        print(' ')



if __name__ == '__main__':
    # loadVoxels()
    processVoxel(joinPath(GAME_DIR, 'voxels', '209_BATON.kvx'))
    # processVoxel(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))
    # loadVoxel(joinPath(GAME_DIR, 'voxels', '209_BATON.kvx'))
    # loadVoxel(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))