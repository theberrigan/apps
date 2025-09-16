import sys
import struct

import cProfile, pstats, io
from pstats import SortKey

from random import randint

import numpy

sys.path.insert(0, r'C:\Projects\PythonLib\python')

from bfw.utils import *
from bfw.reader import *
from bfw.writer import BinWriter
from bfw.native.limits import *
from bfw.bitwise import BABitVec, BitVec, BinBitVec, BoolBitVec

from _consts import *
from _math_types import *
from _voxels import VOXELS



# https://www.david-colson.com/2020/03/10/exploring-rect-packing.html
# https://florianfe.github.io/vox-viewer/demo/
# https://drububu.com/miscellaneous/voxelizer/
# https://paulbourke.net/dataformats/vox/



POW2_M1 = [
    0, 1, 3, 7, 15, 31, 63, 127, 255,
    511, 1023, 2047, 4095, 8191, 16383,
    32767, 65535, 131071, 262143, 524287,
    1048575, 2097151, 4194303, 8388607,
    16777215, 33554431, 67108863, 134217727,
    268435455, 536870911, 1073741823, 2147483647, -1
]

VOXBORDWIDTH = 1
VOXBORDWIDTH_X2 = VOXBORDWIDTH * 2


# C++ rand
def rand ():
    return randint(0, 0x7fff)

class VoxelMesh:
    def __init__ (self, kvxPath):
        self.kvxPath = kvxPath

        self.mipSize = None  # first mip size
        self.dims    = None  # [Vec3] voxel dimensions
        self.pivot   = None  # [Vec3] pivot point
        self.palette = None  # [int32[]] 6-bit colors with its indices
        self.vbit    = None  # [BoolBitVec] 1s - surface and interior voxels, 0s - absent outside voxels
        self.voxels  = None

        self.vcol = None
        self.vnum = 0
        self.vmax = 0

        self.vcolhashsizm1 = None  # color hash table?
        self.vcolhashead   = None

        self.maxAxis  = None  # shcntp - largest axis value (max(126, 10, 35) == 126); partially uset to point into shcntmal
        self.shcntmal = None  # plane of voxels with size <first_largest_axis> * <second_largest_axis> (int32_t[x * y])
        self.basePtr1 = None  # shcnt - pointer to subpart of shcntmal; usage: shcntmal[self.basePtr1 + N]
        self.maxX     = None  # gmaxx - max quad length by x?
        self.maxY     = None  # gmaxy - max quad length by y?
        self.area     = None  # garea - total area of all quads
        self.gqfacind = None  # quad face indices? keeps gvox.qcnt
        self.qcnt     = None  # quad count?
        self.shp      = None  # ?
        self.texX     = None  # mytexx - texture size x
        self.texY     = None  # mytexy - texture size y
        self.mytexo5  = None  # self.texX >> 5
        self.zbit     = None  # [BoolBitVec]
        self.quad     = None  # [voxrect_t[]]
        self.tex      = None  # [int32_t[]]
        self.vertex   = None
        self.index    = None

        self.readKvx()
        self.toMesh()

        assert len(self.vertex) % 5 == 0
        assert len(self.index) % 3 == 0

        print(len(self.vertex) // 5)
        print(len(self.index) // 3)

        with BinWriter() as f:
            f.u32(len(self.vertex) * 4)
            f.f32(*self.vertex)
            f.u32(len(self.index) * 4)
            f.u32(*self.index)

            data = f.getRaw()

            f.save('./trash/000_verts_py.bin')

        data2 = readBin('./trash/000_verts.bin')

        assert data == data2

        '''
        lines = []

        for i in range(0, len(self.vertex), 5):
            x = self.vertex[i + 0]
            y = self.vertex[i + 1]
            z = self.vertex[i + 2]

            lines.append(f'v {x:.5f} {y:.5f} {z:.5f}')

        for i in range(0, len(self.index), 3):
            i1 = self.index[i + 0] + 1
            i2 = self.index[i + 1] + 1
            i3 = self.index[i + 2] + 1

            lines.append(f'f {i1} {i2} {i3}')

        writeText('./trash/model2.obj', '\n'.join(lines))
        '''

    def setupPalette (self, raw):
        self.palette = palette = [ 0 ] * 256

        for i in range(256):
            r, g, b = raw[i * 3:i * 3 + 3]

            color = (
                ((i & MAX_U8) << 24) |  # 8-bit index
                ((r & MAX_U8) << 18) |  # 6-bit r
                ((g & MAX_U8) << 10) |  # 6-bit g
                ((b & MAX_U8) << 2)     # 6-bit b
            )

            color &= MAX_U32

            palette[i] = color

    def _createColorHashTable (self, mipSize):
        tableSize = 4096

        while tableSize < (mipSize >> 1):
            tableSize <<= 1

        self.vcolhashsizm1 = tableSize - 1
        self.vcolhashead   = [ -1 ] * tableSize

    def _setVbitRange (self, start, end):
        for i in range(start, end):
            self.vbit.setIndex(i)

    def readKvx (self):
        assert isFile(self.kvxPath)

        with openFile(self.kvxPath) as f:
            # i32 mip1leng
            # vec3 voxSize
            # vec3 voxPivot
            # i32 xoffset[voxSize.x + 1]
            # u16 xyoffset[voxSize.x][voxSize.y + 1]

            self.voxels = voxels = []

            self.mipSize = mipSize = f.i32()

            self._createColorHashTable(mipSize)

            dimX = f.i32()
            dimY = f.i32()
            dimZ = f.i32()

            self.dims = Vec3(dimX, dimY, dimZ)

            self.vbit = BoolBitVec(dimX * dimY * dimZ)
            # self.vbit = [  ]

            pivX = f.i32() / 256.0
            pivY = f.i32() / 256.0
            pivZ = f.i32() / 256.0

            self.pivot = Vec3(pivX, pivY, pivZ)

            _offsetsX = f.u32(dimX + 1)
            offsetsXY = f.u16(dimX * (dimY + 1))

            for x in range(dimX):
                j = x * dimY * dimZ

                for y in range(dimY):
                    offsetIdx = x * (dimY + 1) + y
                    chunkSize = offsetsXY[offsetIdx + 1] - offsetsXY[offsetIdx]
                    chunkEnd  = f.tell() + chunkSize
                    z1 = 0

                    while f.tell() < chunkEnd:
                        z0       = f.u8()  # offset from top in voxels
                        voxCount = f.u8()  # count of solid voxels
                        flags    = f.u8()  # flags

                        # voxels inside on the object (not surface)
                        if not (flags & 16):
                            self._setVbitRange(j + z1, j + z0)

                        z1 = z0 + voxCount

                        self._setVbitRange(j + z0, j + z1)

                        for z in range(z0, z1):
                            colorIndex = f.u8() + 1

                            assert colorIndex < 256

                            voxels.append((x, y, z, colorIndex))
                            self.putVoxel(x, y, z, colorIndex)

                    j += dimZ

            f.fromEnd(-768)

            palette = f.read(768)

            self.setupPalette(palette)

            assert not f.remaining()

    def checkSolid (self, x, y, z):
        dimX, dimY, dimZ = self.dims

        if x < 0 or x >= dimX or y < 0 or y >= dimY or z < 0 or z >= dimZ:
            return False

        voxIndex = dimY * dimZ * x + dimZ * y + z

        return self.vbit.checkIndex(voxIndex)

    def cntquad (self, x0, y0, z0, x1, y1, z1, x2, y2, z2, face):
        x = abs(x2 - x0)
        y = abs(y2 - y0)
        z = abs(z2 - z0)

        x, y = sorted([ x or z, y or z ], reverse=True)

        self.shcntmal[self.basePtr1 + self.maxAxis * y + x] += 1

        self.maxX = max(self.maxX, x)
        self.maxY = max(self.maxY, y)

        self.area += (x + VOXBORDWIDTH_X2) * (y + VOXBORDWIDTH_X2)
        self.qcnt += 1

    def addquad (self, x0, y0, z0, x1, y1, z1, x2, y2, z2, face):
        i = 0
        x = abs(x2 - x0)
        y = abs(y2 - y0)
        z = abs(z2 - z0)

        if x == 0:
            x = y
            y = z
            i = 0
        elif y == 0:
            y = z
            i = 1
        else:
            i = 2

        if x < y:
            z = x
            x = y
            y = z
            i += 3

        z = self.shcntmal[self.basePtr1 + self.maxAxis * y + x]

        self.shcntmal[self.basePtr1 + self.maxAxis * y + x] += 1

        # int32_t *lptr = &gvox->mytex[(self.shp[z].y + VOXBORDWIDTH) * self.texX + (self.shp[z].x + VOXBORDWIDTH)]
        lptr = (self.shp[z].y + VOXBORDWIDTH) * self.texX + (self.shp[z].x + VOXBORDWIDTH)

        nx = 0
        ny = 0
        nz = 0

        match face:
            case 0:
                ny = y1
                x2 = x0
                x0 = x1
                x1 = x2
            case 1:
                ny = y0
                y0 += 1
                y1 += 1
                y2 += 1
            case 2:
                nz = z1
                y0 = y2
                y2 = y1
                y1 = y0
                z0 += 1
                z1 += 1
                z2 += 1
            case 3:
                nz = z0
            case 4:
                nx = x1
                y2 = y0
                y0 = y1
                y1 = y2
                x0 += 1
                x1 += 1
                x2 += 1
            case 5:
                nx = x0

        for yy in range(y):
            for xx in range(x):
                match face:
                    case 0:
                        if i < 3:  # back
                            nx = x1 + x - 1 - xx
                            nz = z1 + yy
                        else:
                            nx = x1 + y - 1 - yy
                            nz = z1 + xx
                    case 1:
                        if i < 3:  # front
                            nx = x0 + xx
                            nz = z0 + yy
                        else:
                            nx = x0 + yy
                            nz = z0 + xx
                    case 2:
                        if i < 3:  # bottom
                            nx = x1 - x + xx
                            ny = y1 - 1 - yy
                        else:
                            nx = x1 - 1 - yy
                            ny = y1 - 1 - xx
                    case 3:
                        if i < 3:  # top
                            nx = x0 + xx
                            ny = y0 + yy
                        else:
                            nx = x0 + yy
                            ny = y0 + xx
                    case 4:
                        if i < 3:  # right
                            ny = y1 + x - 1 - xx
                            nz = z1 + yy
                        else:
                            ny = y1 + y - 1 - yy
                            nz = z1 + xx
                    case 5:
                        if i < 3:  # left
                            ny = y0 + xx
                            nz = z0 + yy
                        else:
                            ny = y0 + yy
                            nz = z0 + xx

                self.tex[lptr + xx] = self.getVoxel(nx, ny, nz)

            lptr += self.texX

        # Extend borders horizontally
        for xx in range(VOXBORDWIDTH):
            for yy in range(VOXBORDWIDTH, y + VOXBORDWIDTH):
                lptr = (self.shp[z].y + yy) * self.texX + self.shp[z].x
                self.tex[lptr + xx] = self.tex[lptr + VOXBORDWIDTH]
                self.tex[lptr + xx + x + VOXBORDWIDTH] = self.tex[lptr + x - 1 + VOXBORDWIDTH]

        # Extend borders vertically
        for yy in range(VOXBORDWIDTH):
            dst = (self.shp[z].y + yy) * self.texX + self.shp[z].x
            src = (self.shp[z].y + VOXBORDWIDTH) * self.texX + self.shp[z].x
            cnt = (x + VOXBORDWIDTH_X2) << 2

            for jj in range(cnt):
                self.tex[dst + jj] = self.tex[src + jj]

            dst = (self.shp[z].y + y + yy + VOXBORDWIDTH) * self.texX + self.shp[z].x
            src = (self.shp[z].y + y - 1 + VOXBORDWIDTH) * self.texX + self.shp[z].x
            cnt = (x + VOXBORDWIDTH_X2) << 2

            for jj in range(cnt):
                self.tex[dst + jj] = self.tex[src + jj]

        qptr = self.quad[self.qcnt]

        qptr.v[0].x = x0
        qptr.v[0].y = y0
        qptr.v[0].z = z0

        qptr.v[1].x = x1
        qptr.v[1].y = y1
        qptr.v[1].z = z1

        qptr.v[2].x = x2
        qptr.v[2].y = y2
        qptr.v[2].z = z2

        for j in range(3):
            qptr.v[j].u = self.shp[z].x + VOXBORDWIDTH
            qptr.v[j].v = self.shp[z].y + VOXBORDWIDTH

        if i < 3:
            qptr.v[1].u += x
        else:
            qptr.v[1].v += y

        qptr.v[2].u += x
        qptr.v[2].v += y

        qptr.v[3].u = qptr.v[0].u - qptr.v[1].u + qptr.v[2].u
        qptr.v[3].v = qptr.v[0].v - qptr.v[1].v + qptr.v[2].v

        qptr.v[3].x = qptr.v[0].x - qptr.v[1].x + qptr.v[2].x
        qptr.v[3].y = qptr.v[0].y - qptr.v[1].y + qptr.v[2].y
        qptr.v[3].z = qptr.v[0].z - qptr.v[1].z + qptr.v[2].z

        if self.gqfacind[face] < 0:
            self.gqfacind[face] = self.qcnt

        self.qcnt += 1

    def checkRectFree (self, x0, y0, dx, dy):
        i = y0 * self.mytexo5 + (x0 >> 5)
        dx += x0 - 1

        c = (dx >> 5) - (x0 >> 5)

        m  = POW2_M1[x0 & 31] ^ 0xFFFFFFFF  # inverse bits u32
        m1 = POW2_M1[(dx & 31) + 1]

        if not c:
            m &= m1

            while dy:
                if self.zbit[i] & m:
                    return 0

                dy -= 1
                i += self.mytexo5
        else:
            while dy:
                if self.zbit[i] & m:
                    return 0

                xxx = 0

                for x in range(1, c):
                    if self.zbit[i + x]:
                        return 0

                xxx += 1

                if self.zbit[i + xxx] & m1:
                    return 0

                dy -= 1
                i += self.mytexo5

        return 1

    def setRect (self, x0, y0, dx, dy):
        i = y0 * self.mytexo5 + (x0 >> 5)

        dx += x0 - 1

        c = (dx >> 5) - (x0 >> 5)

        m  = POW2_M1[x0 & 31] ^ 0xFFFFFFFF  # inverse bits u32
        m1 = POW2_M1[(dx & 31) + 1]

        if not c:
            m &= m1

            while dy:
                self.zbit[i] |= m
                dy -= 1
                i += self.mytexo5
        else:
            while dy:
                self.zbit[i] |= m

                xxx = 0

                for x in range(1, c):
                    self.zbit[i + x] = -1
                    xxx = x

                xxx += 1

                self.zbit[i + xxx] |= m1

                dy -= 1
                i += self.mytexo5

    def putVoxel (self, x, y, z, col):
        # voxcol_t
        if self.vnum >= self.vmax:
            self.vmax = max(self.vmax << 1, 4096)
            self.vcol = self.vcol or []
            self.vcol = self.vcol + [ voxcol_t() for _ in range(self.vmax - len(self.vcol)) ]

        z = self.dims.y * self.dims.z * x + self.dims.z * y + z

        self.vcol[self.vnum].p = z

        z = (z * 214013) & self.vcolhashsizm1

        self.vcol[self.vnum].c = col
        self.vcol[self.vnum].n = self.vcolhashead[z]

        self.vcolhashead[z] = self.vnum

        self.vnum += 1

    def getVoxel (self, x, y, z):
        z = self.dims.y * self.dims.z * x + self.dims.z * y + z

        x = self.vcolhashead[(z * 214013) & self.vcolhashsizm1]

        while x >= 0:
            if self.vcol[x].p == z:
                return self.vcol[x].c

            x = self.vcol[x].n

        return 0x808080

    def toMesh (self):
        # x - 1st largest, y - 2nd largest, z - unused
        x, y, _ = sorted(self.dims, reverse=True)
        dimX, dimY, dimZ = self.dims

        self.maxAxis  = x  # shcntp
        self.shcntmal = [ 0 ] * (x * y)
        self.basePtr1 = -self.maxAxis - 1  # shcnt
        self.maxX     = 0
        self.maxY     = 0
        self.area     = 0
        self.gqfacind = [ -1 ] * 7

        i = max(dimY, dimZ) + 1

        bx0 = [ 0 ] * i
        by0 = [ 0 ] * i

        ov = 0
        oz = 0

        for cnt in [ 0, 1 ]:
            daquad = [ self.cntquad, self.addquad ][cnt]

            self.qcnt = 0

            for i in range(len(by0)):
                by0[i] = -1

            v = 0

            for i in [ -1, 1 ]:
                for y in range(dimY):
                    for x in range(dimX + 1):
                        for z in range(dimZ + 1):
                            ov = v
                            v = self.checkSolid(x, y, z) and not self.checkSolid(x, y + i, z)

                            if by0[z] >= 0 and (by0[z] != oz or v >= ov):
                                daquad(bx0[z], y, by0[z], x, y, by0[z], x, y, z, int(i >= 0))
                                by0[z] = -1

                            if v > ov:
                                oz = z
                            elif v < ov and by0[z] != oz:
                                bx0[z] = x
                                by0[z] = oz

            for i in [ -1, 1 ]:
                for z in range(dimZ):
                    for x in range(dimX + 1):
                        for y in range(dimY + 1):
                            ov = v
                            v = self.checkSolid(x, y, z) and not self.checkSolid(x, y, z - i)

                            if by0[y] >= 0 and (by0[y] != oz or v >= ov):
                                daquad(bx0[y], by0[y], z, x, by0[y], z, x, y, z, int(i >= 0) + 2)
                                by0[y] = -1

                            if v > ov:
                                oz = y
                            elif v < ov and by0[y] != oz:
                                bx0[y] = x
                                by0[y] = oz

            for i in [ -1, 1 ]:
                for x in range(dimX):
                    for y in range(dimY + 1):
                        for z in range(dimZ + 1):
                            ov = v
                            v = self.checkSolid(x, y, z) and not self.checkSolid(x - i, y, z)

                            if by0[z] >= 0 and (by0[z] != oz or v >= ov):
                                daquad(x, bx0[z], by0[z], x, y, by0[z], x, y, z, int(i >= 0) + 4)
                                by0[z] = -1

                            if v > ov:
                                oz = z
                            elif v < ov and by0[z] != oz:
                                bx0[z] = y
                                by0[z] = oz

            if not cnt:
                self.shp = [ Vec2() for _ in range(self.qcnt) ]

                sc = 0

                for y in range(self.maxY, 0, -1):
                    for x in range(self.maxX, y - 1, -1):
                        i = self.shcntmal[self.basePtr1 + self.maxAxis * y + x]

                        self.shcntmal[self.basePtr1 + self.maxAxis * y + x] = sc  # shcnt changes from counter to head index

                        for i in range(i, 0, -1):
                            self.shp[sc].x = x
                            self.shp[sc].y = y
                            sc += 1

                self.texX = 32

                while self.texX < (self.maxX + VOXBORDWIDTH_X2):
                    self.texX <<= 1

                self.texY = 32

                while self.texY < (self.maxY + VOXBORDWIDTH_X2):
                    self.texY <<= 1

                while (self.texX * self.texY * 8) < (self.area * 9):  # This should be sufficient to fit most skins...
                    if self.texX <= self.texY:
                        self.texX <<= 1
                    else:
                        self.texY <<= 1

                self.mytexo5 = self.texX >> 5

                # self.zbit = BoolBitVec(self.texX * self.texY)
                # TODO: wrong num count
                self.zbit = [ 0 ] * ((self.texX * self.texY + 7) >> 3)

                v = self.texX * self.texY

                vbw = Vec2(VOXBORDWIDTH_X2, VOXBORDWIDTH_X2)

                for z in range(sc):
                    d = self.shp[z] + vbw
                    i = v

                    while True:
                        x0 = ((rand() & 32767) * (self.texX + 1 - d.x)) >> 15
                        y0 = ((rand() & 32767) * (self.texY + 1 - d.y)) >> 15

                        i -= 1

                        assert i >= 0, 'Time-out! Very slow if this happens... but at least it still works :P'

                        if self.checkRectFree(x0, y0, d.x, d.y):
                            break

                    while y0 and self.checkRectFree(x0, y0 - 1, d.x, 1):
                        y0 -= 1

                    while x0 and self.checkRectFree(x0 - 1, y0, 1, d.y):
                        x0 -= 1

                    self.setRect(x0, y0, d.x, d.y)

                    # Overwrite size with top-left location
                    self.shp[z].x = x0
                    self.shp[z].y = y0

                self.quad = self.quad or []
                self.quad = self.quad + [ voxrect_t() for _ in range(self.qcnt - len(self.quad)) ]

                self.tex = [ 0 ] * (self.texX * self.texY)

        self.shp  = None
        self.zbit = None

        phack = [ 0, 1.0 / 256.0 ]

        self.vertex = [ 0 ] * (5 * 4 * self.qcnt)  # GLfloat[]
        self.index  = [ 0 ] * (3 * 2 * self.qcnt)  # GLuint[]

        # units per texture pixel
        ru = 1.0 / self.texX
        rv = 1.0 / self.texY

        for i in range(self.qcnt):
            vptr = self.quad[i].v
            vsum = Vec3(
                vptr[0].x + vptr[2].x,
                vptr[0].y + vptr[2].y,
                vptr[0].z + vptr[2].z,
            )

            for j in range(4):
                baseIndex = ((i << 2) + j) * 5
                vert = vptr[j]

                self.vertex[baseIndex + 0] = vert.x - phack[vsum.x > (vert.x << 1)] + phack[vsum.x < (vert.x << 1)]
                self.vertex[baseIndex + 1] = vert.y - phack[vsum.y > (vert.y << 1)] + phack[vsum.y < (vert.y << 1)]
                self.vertex[baseIndex + 2] = vert.z - phack[vsum.z > (vert.z << 1)] + phack[vsum.z < (vert.z << 1)]
                self.vertex[baseIndex + 3] = vert.u * ru
                self.vertex[baseIndex + 4] = vert.v * rv

            self.index[(i << 1) * 3 + 0] = (i << 2) + 0
            self.index[(i << 1) * 3 + 1] = (i << 2) + 1
            self.index[(i << 1) * 3 + 2] = (i << 2) + 2

            self.index[((i << 1) + 1) * 3 + 0] = (i << 2) + 0
            self.index[((i << 1) + 1) * 3 + 1] = (i << 2) + 2
            self.index[((i << 1) + 1) * 3 + 2] = (i << 2) + 3

        self.quad = None

class vert_t:
    def __init__ (self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.u = 0
        self.v = 0

class voxrect_t:
    def __init__ (self):
        self.v = [ vert_t() for _ in range(4) ]

class voxcol_t:
    def __init__ (self):
        self.p = None
        self.c = None
        self.n = None

def loadVoxels ():
    for voxel in VOXELS:
        kvxPath = getAbsPath(joinPath(GAME_DIR, voxel['path']))

        print(kvxPath)

        VoxelMesh(kvxPath)

        print(' ')

def _conv ():
    with openFile(r"C:\Projects\GameTools\ion_fury\trash\000_verts.bin") as f:
        size = f.u32()
        count = size // 4 // 5
        lines = []

        for i in range(count):
            x = f.f32()
            y = f.f32()
            z = f.f32()
            u = f.f32()
            v = f.f32()

            lines.append(f'v {x:.5f} {y:.5f} {z:.5f}')

        size = f.u32()
        count = size // 4 // 3

        for i in range(count):
            i1 = f.u32() + 1
            i2 = f.u32() + 1
            i3 = f.u32() + 1

            lines.append(f'f {i1} {i2} {i3}')

        writeText('./trash/model9999.obj', '\n'.join(lines))


if __name__ == '__main__':
    # loadVoxels()
    VoxelMesh(joinPath(GAME_DIR, 'voxels', '209_BATON.kvx'))
    # pr = cProfile.Profile()
    # pr.enable()
    # VoxelMesh(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx'))
    # pr.disable()
    # s = io.StringIO()
    # sortby = SortKey.CUMULATIVE
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())

