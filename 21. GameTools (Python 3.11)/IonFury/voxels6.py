import sys
from typing import List, Any, Union

import cProfile, pstats, io
from pstats import SortKey

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

class VoxelFlags:
    Solid  = 1 << 0  # solid voxel
    Marked = 1 << 1  # any absent voxel accessible from outside

class VoxelState:
    Default = 1
    Marked  = 2

class VoxelSide:
    PosX = 1 << 0
    NegX = 1 << 1
    PosY = 1 << 2
    NegY = 1 << 3
    PosZ = 1 << 4
    NegZ = 1 << 5

SIDE_NEIGHBOURS = [
    (VoxelSide.PosX,  1,  0,  0),  # +X
    (VoxelSide.NegX, -1,  0,  0),  # -X
    (VoxelSide.PosY,  0,  1,  0),  # +Y
    (VoxelSide.NegY,  0, -1,  0),  # -Y
    (VoxelSide.PosZ,  0,  0,  1),  # +Z
    (VoxelSide.NegZ,  0,  0, -1),  # -Z
]

class KvxData:
    def __init__ (self, dims, pivot, voxels, palette):
        self.dims    : Vec3        = dims         # Vec3
        self.pivot   : Vec3        = pivot        # Vec3
        self.voxels  : List[Voxel] = voxels       # Voxel[]
        self.count   : int         = len(voxels)  # int
        self.palette : List[int]   = palette      # [r, g, b][]
        self.volume  : int         = dims.x * dims.y * dims.z

class Voxel:
    def __init__ (self):
        self.x     : int = 0
        self.y     : int = 0
        self.z     : int = 0
        self.value : int = 0  # color index
        self.sides : int = 0  # [VoxelSide] side presence flags
        self.used  : int = 0  # [VoxelSide] used side flags
        self.index : int = 0


def getVoxIndex (dimY, dimZ, x, y, z):
    return dimY * dimZ * x + dimZ * y + z

def readKvx (kvxPath, flags=KvxFlag.No):
    if not isFile(kvxPath):
        raise OSError(f'File does not exist: { kvxPath }')

    dims    = Vec3()
    pivot   = Vec3()
    voxels  = []
    palette = []

    with openFile(kvxPath) as f:
        _mipSize  = f.i32()

        dims.x = f.u32()
        dims.y = f.u32()
        dims.z = f.u32()

        # is not normalized (divide by 256.0)
        pivot.x = f.u32()
        pivot.y = f.u32()
        pivot.z = f.u32()

        _offsetsX = f.u32(dims.x + 1)
        offsetsXY = f.u16(dims.x * (dims.y + 1))

        for x in range(dims.x):
            for y in range(dims.y):
                offsetIdx = x * (dims.y + 1) + y
                chunkSize = offsetsXY[offsetIdx + 1] - offsetsXY[offsetIdx]
                chunkEnd  = f.tell() + chunkSize

                while f.tell() < chunkEnd:
                    z0     = f.u8()  # offset from top in voxels
                    count  = f.u8()  # count of solid voxels
                    _flags = f.u8()  # flags

                    z1 = z0 + count

                    for z in range(z0, z1):
                        voxel = Voxel()

                        voxel.value = f.u8() + 1

                        assert voxel.value < 256

                        if flags & KvxFlag.FlipX:
                            voxel.x = vx = dims.x - 1 - x
                        else:
                            voxel.x = vx = x

                        if flags & KvxFlag.FlipY:
                            voxel.y = vy = dims.y - 1 - y
                        else:
                            voxel.y = vy = y

                        if flags & KvxFlag.FlipZ:
                            voxel.z = vz = dims.z - 1 - z
                        else:
                            voxel.z = vz = z

                        voxel.index = getVoxIndex(dims.y, dims.z, vx, vy, vz)

                        voxels.append(voxel)

        f.fromEnd(-(3 * KVX_COLOR_COUNT))

        for _ in range(KVX_COLOR_COUNT):
            rgb = f.u8(3)

            rgb[0] = int(rgb[0] / 63 * 255)
            rgb[1] = int(rgb[1] / 63 * 255)
            rgb[2] = int(rgb[2] / 63 * 255)

            palette.append(rgb)

        assert not f.remaining()
        assert len(palette) == KVX_COLOR_COUNT

    return KvxData(dims, pivot, voxels, palette)

def _printVoxelSides (voxels):
    SIDES = {
        0             : '',
        VoxelSide.PosX: 'right',
        VoxelSide.NegX: 'left',
        VoxelSide.PosY: 'near',
        VoxelSide.NegY: 'far',
        VoxelSide.PosZ: 'bottom',
        VoxelSide.NegZ: 'top'
    }

    for voxel in voxels:
        sides = [ s for s in [
            SIDES[voxel.sides & VoxelSide.PosX],
            SIDES[voxel.sides & VoxelSide.NegX],
            SIDES[voxel.sides & VoxelSide.PosY],
            SIDES[voxel.sides & VoxelSide.NegY],
            SIDES[voxel.sides & VoxelSide.PosZ],
            SIDES[voxel.sides & VoxelSide.NegZ]
        ] if s ]

        sides = ' '.join(sides)
        coords = f'{ voxel.x } { voxel.y } { voxel.z }'

        print(f'{coords:<14} {sides}')

class VoxelConverter:
    def __init__ (self):
        self.kvxPath : str | None     = None
        self.kvxData : KvxData | None = None

    @staticmethod
    def fromKvx (kvxPath):
        conv = VoxelConverter()

        conv.convertKvx(kvxPath)

        return conv

    def convertKvx (self, kvxPath):
        self.kvxPath = kvxPath
        self.kvxData = readKvx(self.kvxPath)

        self.markSurfaces()
        # _printVoxelSides(self.kvxData.voxels)
        self.triangulate()

    def markSurfaces (self):
        kvx = self.kvxData

        dimX = kvx.dims.x
        dimY = kvx.dims.y
        dimZ = kvx.dims.z

        state : List[Union[int, Voxel]] = [ VoxelState.Default ] * kvx.volume

        for voxel in kvx.voxels:
            voxel.state = VoxelState.Default
            state[voxel.index] = voxel

        # Two XY sides
        for x in range(dimX):
            for y in range(dimY):
                for z in (0, dimZ - 1):
                    index = getVoxIndex(dimY, dimZ, x, y, z)
                    item  = state[index]

                    if item == VoxelState.Marked:
                        continue

                    if item == VoxelState.Default:
                        state[index] = VoxelState.Marked
                        self.traverseOutsideVoxels(state, dimX, dimY, dimZ, x, y, z)
                    elif z == 0:
                        item.sides |= VoxelSide.NegZ
                    else:
                        item.sides |= VoxelSide.PosZ

        # Two YZ sides
        for y in range(dimY):
            for z in range(dimZ):
                for x in (0, dimX - 1):
                    index = getVoxIndex(dimY, dimZ, x, y, z)
                    item  = state[index]

                    if item == VoxelState.Marked:
                        continue

                    if item == VoxelState.Default:
                        state[index] = VoxelState.Marked
                        self.traverseOutsideVoxels(state, dimX, dimY, dimZ, x, y, z)
                    elif x == 0:
                        item.sides |= VoxelSide.NegX
                    else:
                        item.sides |= VoxelSide.PosX

        # Two XZ sides
        for x in range(dimX):
            for z in range(dimZ):
                for y in (0, dimY - 1):
                    index = getVoxIndex(dimY, dimZ, x, y, z)
                    item  = state[index]

                    if item == VoxelState.Marked:
                        continue

                    if item == VoxelState.Default:
                        state[index] = VoxelState.Marked
                        self.traverseOutsideVoxels(state, dimX, dimY, dimZ, x, y, z)
                    elif y == 0:
                        item.sides |= VoxelSide.NegY
                    else:
                        item.sides |= VoxelSide.PosY

    def traverseOutsideVoxels (self, state, dimX, dimY, dimZ, x, y, z):
        maxX = dimX - 1
        maxY = dimY - 1
        maxZ = dimZ - 1

        chainIndex = 0
        chainLen = 1
        chain = {
            chainIndex: (x, y, z)
        }

        while chainIndex < chainLen:
            x, y, z = chain[chainIndex]
            chainIndex += 1

            for side, dx, dy, dz in SIDE_NEIGHBOURS:
                nextX = x + dx
                nextY = y + dy
                nextZ = z + dz

                if 0 <= nextX <= maxX and 0 <= nextY <= maxY and 0 <= nextZ <= maxZ:
                    index = getVoxIndex(dimY, dimZ, nextX, nextY, nextZ)
                    item  = state[index]

                    if item == VoxelState.Marked:
                        continue

                    if item == VoxelState.Default:
                        state[index] = VoxelState.Marked
                        chain[chainLen] = (nextX, nextY, nextZ)
                        chainLen += 1

                    else:
                        item.sides |= (
                            (dx == +1 and VoxelSide.NegX) |
                            (dx == -1 and VoxelSide.PosX) |
                            (dy == +1 and VoxelSide.NegY) |
                            (dy == -1 and VoxelSide.PosY) |
                            (dz == +1 and VoxelSide.NegZ) |
                            (dz == -1 and VoxelSide.PosZ)
                        )

    def triangulate (self):
        kvx = self.kvxData

        voxels = kvx.voxels

        dimX = kvx.dims.x
        dimY = kvx.dims.y
        dimZ = kvx.dims.z

        space : Any = [ [ [ None ] * dimZ for _ in range(dimY) ] for _ in range(dimX) ]

        for voxel in voxels:
            space[voxel.x][voxel.y][voxel.z] = voxel

        quads = {}
        quadCount = 0

        for x in range(dimX):
            for y in range(dimY):
                for z in range(dimZ):
                    vox1 = space[x][y][z]

                    if not vox1:
                        continue

                    for side in [ VoxelSide.NegX, VoxelSide.PosX ]:
                        if not (vox1.sides & side) or vox1.used & side:
                            continue

                        quadVoxels = {}
                        voxCount = 0
                        endZ = dimZ
                        rows = 0

                        for yy in range(y, dimY):
                            isFirstRow = yy == y
                            isRowOk = isFirstRow

                            for zz in range(z, endZ):
                                vox2 = space[x][yy][zz]

                                if not vox2 or not (vox2.sides & side) or vox2.used & side:
                                    break

                                quadVoxels[voxCount] = vox2
                                voxCount += 1

                                if isFirstRow:
                                    endZ = zz + 1
                                elif zz == (endZ - 1):
                                    isRowOk = True

                            if isRowOk:
                                rows += 1
                            else:
                                break

                        width = endZ - z

                        assert rows
                        assert width

                        quadLen = rows * width
                        quad = [ None ] * quadLen

                        for i in range(quadLen):
                            vox2 = quad[i] = quadVoxels[i]
                            vox2.used |= side

                        quads[quadCount] = (side, quad)
                        quadCount += 1







def loadVoxels ():
    for voxel in VOXELS:
        kvxPath = voxel['path']
        kvxPath = getAbsPath(joinPath(GAME_DIR, kvxPath))

        print(kvxPath)

        VoxelConverter.fromKvx(kvxPath)

        print(' ')



if __name__ == '__main__':
    # loadVoxels()
    VoxelConverter.fromKvx(joinPath(GAME_DIR, 'voxels', '209_BATON.kvx'))
    # VoxelConverter.fromKvx(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))

    # pr = cProfile.Profile()
    # pr.enable()
    # VoxelConverter.fromKvx(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))
    # pr.disable()
    # s = io.StringIO()
    # sortby = SortKey.CUMULATIVE
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())