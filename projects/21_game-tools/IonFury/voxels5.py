import sys
from typing import List

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
    Solid   = 1 << 0  # solid voxel
    Outside = 1 << 1  # any absent voxel accessible from outside
    Queued  = 1 << 2  # queued for outsideness check
    Shell   = 1 << 3  # outside voxel adjacent to solid
    Skip    = Solid | Outside | Queued

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
        self.sides : int = 0  # side presence flags
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
        0           : '',
        VoxSide.PosX: 'right',
        VoxSide.NegX: 'left',
        VoxSide.PosY: 'near',
        VoxSide.NegY: 'far',
        VoxSide.PosZ: 'bottom',
        VoxSide.NegZ: 'top'
    }

    for voxel in voxels:
        sides = [ s for s in [
            SIDES[voxel.sides & VoxSide.PosX],
            SIDES[voxel.sides & VoxSide.NegX],
            SIDES[voxel.sides & VoxSide.PosY],
            SIDES[voxel.sides & VoxSide.NegY],
            SIDES[voxel.sides & VoxSide.PosZ],
            SIDES[voxel.sides & VoxSide.NegZ]
        ] if s ]

        sides = ' '.join(sides)
        coords = f'{ voxel.x } { voxel.y } { voxel.z }'

        print(f'{coords:<14} {sides}')

class VoxelConverter:
    def __init__ (self):
        self.kvxPath  : str | None       = None
        self.kvxData  : KvxData | None   = None
        self.outsides : List[int] | None = None

    @staticmethod
    def fromKvx (kvxPath):
        conv = VoxelConverter()

        conv.convertKvx(kvxPath)

        return conv

    def convertKvx (self, kvxPath):
        self.kvxPath = kvxPath
        self.kvxData = readKvx(self.kvxPath)

        self.markOutsideVoxels()
        self.markSurfaces()

        # _printVoxelSides(self.kvxData.voxels)

    class VoxSide:
        PosX = 1 << 0
        NegX = 1 << 1
        PosY = 1 << 2
        NegY = 1 << 3
        PosZ = 1 << 4
        NegZ = 1 << 5

    def markOutsideVoxels (self):
        kvx = self.kvxData

        voxels = kvx.voxels

        dimX = kvx.dims.x
        dimY = kvx.dims.y
        dimZ = kvx.dims.z

        maxX = dimX - 1
        maxY = dimY - 1
        maxZ = dimZ - 1

        voxMap = [ 0 ] * kvx.volume

        for vox in voxels:
            voxMap[vox.index] = VoxelFlags.Solid

        # Two XY sides
        for x in range(dimX):
            for y in range(dimY):
                for z in [ 0, maxZ ]:
                    i = getVoxIndex(dimY, dimZ, x, y, z)

                    if voxMap[i] & VoxelFlags.Skip:
                        continue

                    self.traverseOutsideVoxels(voxMap, dimX, dimY, dimZ, x, y, z)

        # Two YZ sides
        for y in range(dimY):
            for z in range(dimZ):
                for x in [ 0, maxX ]:
                    i = getVoxIndex(dimY, dimZ, x, y, z)

                    if voxMap[i] & VoxelFlags.Skip:
                        continue

                    self.traverseOutsideVoxels(voxMap, dimX, dimY, dimZ, x, y, z)

        # Two XZ sides
        for x in range(dimX):
            for z in range(dimZ):
                for y in [ 0, maxY ]:
                    i = getVoxIndex(dimY, dimZ, x, y, z)

                    if voxMap[i] & VoxelFlags.Skip:
                        continue

                    self.traverseOutsideVoxels(voxMap, dimX, dimY, dimZ, x, y, z)

        self.outsides = { i: True for i, f in enumerate(voxMap) if f & VoxelFlags.Shell }

    def traverseOutsideVoxels (self, voxMap, dimX, dimY, dimZ, x, y, z):
        maxX = dimX - 1
        maxY = dimY - 1
        maxZ = dimZ - 1

        chain = tail = [ x, y, z, None ]

        while chain:
            x, y, z, _ = chain

            isShellFlag = 0

            for side, dx, dy, dz in SIDE_NEIGHBOURS:
                nextX = x + dx
                nextY = y + dy
                nextZ = z + dz

                if 0 <= nextX <= maxX and 0 <= nextY <= maxY and 0 <= nextZ <= maxZ:
                    index = getVoxIndex(dimY, dimZ, nextX, nextY, nextZ)
                    flags = voxMap[index]

                    if flags & VoxelFlags.Solid:
                        isShellFlag = VoxelFlags.Shell

                    if flags & VoxelFlags.Skip:
                        continue

                    tail[3] = [ nextX, nextY, nextZ, None ]
                    tail = tail[3]

                    voxMap[index] |= VoxelFlags.Queued

            # ------------------------

            index = getVoxIndex(dimY, dimZ, x, y, z)

            # mark current voxel as an outside one
            voxMap[index] |= VoxelFlags.Outside | isShellFlag

            # ------------------------

            # switch to next voxel in the chain
            chain = chain[3]

    def markSurfaces (self):
        outsides = self.outsides

        solids = self.kvxData.voxels

        dimX = self.kvxData.dims.x
        dimY = self.kvxData.dims.y
        dimZ = self.kvxData.dims.z

        maxX = dimX - 1
        maxY = dimY - 1
        maxZ = dimZ - 1

        for solid in solids:
            x = solid.x
            y = solid.y
            z = solid.z

            solid.sides |= (
                (x == 0 and VoxSide.NegX)    |
                (y == 0 and VoxSide.NegY)    |
                (z == 0 and VoxSide.NegZ)    |
                (x == maxX and VoxSide.PosX) |
                (y == maxY and VoxSide.PosY) |
                (z == maxZ and VoxSide.PosZ)
            )

            for side, dx, dy, dz in SIDE_NEIGHBOURS:
                if solid.sides & side:
                    continue

                nextX = x + dx
                nextY = y + dy
                nextZ = z + dz

                if 0 <= nextX <= maxX and 0 <= nextY <= maxY and 0 <= nextZ <= maxZ:
                    index = getVoxIndex(dimY, dimZ, nextX, nextY, nextZ)

                    if index not in outsides:
                        continue

                solid.sides |= side

        return solids

def loadVoxels ():
    for voxel in VOXELS:
        kvxPath = voxel['path']
        kvxPath = getAbsPath(joinPath(GAME_DIR, kvxPath))

        print(kvxPath)

        VoxelConverter.fromKvx(kvxPath)

        print(' ')



if __name__ == '__main__':
    # loadVoxels()
    # VoxelConverter.fromKvx(joinPath(GAME_DIR, 'voxels', '209_BATON.kvx'))
    VoxelConverter.fromKvx(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))

    # pr = cProfile.Profile()
    # pr.enable()
    # VoxelConverter.fromKvx(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))
    # pr.disable()
    # s = io.StringIO()
    # sortby = SortKey.CUMULATIVE
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())