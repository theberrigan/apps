import sys

from random import randint

sys.path.insert(0, r'C:\Projects\PythonLib\python')

from bfw.utils import *
from bfw.reader import *
from bfw.native.limits import *

from _consts import *
from _math_types import *
from _voxels import VOXELS



VOXBORDWIDTH = 1
VOXBORDWIDTH_X2 = VOXBORDWIDTH * 2

voxSize       = None    # vec3_t voxsiz
voxPiv        = Vec3()  # vec3f_t voxpiv
vbit          = None    # bool[]; vbit: 1 bit per voxel: 0=air, 1=solid
vcolhashsizm1 = 0       # int32_t
vcolhashead   = None    # int32_t[]
vnum          = 0       # int32_t
vmax          = 0       # int32_t
vcol          = []      # voxcol_t*
gvox          = None    # voxmodel_t*
shcntp        = 0       # int32_t
shcntmal      = None    # int32_t*
shcnt         = 0       # int32_t*
gmaxx         = 0       # int32_t
gmaxy         = 0       # int32_t
garea         = 0       # int32_t
pow2m1        = [ 0 ] * 33  # int32_t[33]
gqfacind      = [ 0 ] * 7   # int32_t[7]
shp           = None    # vec2_u16_t[]
gquad         = None    # voxrect_t*
mytexo5       = None
zbit          = None

# yzsiz = voxSize.y * voxSize.z


class voxcol_t:
    size = 12

    def __init__ (self, p=0, c=0, n=0):
        self.p = p  # int32_t
        self.c = c  # int32_t
        self.n = n  # int32_t


def read_pal (f):
    f.fromEnd(-768)

    assert f.remaining() == 768

    pal = []

    for i in range(256):
        rgb = f.u8(3)

        assert rgb[0] < 2 ** 6

        color = (
            ((i      & MAX_U8) << 24) +
            ((rgb[0] & MAX_U8) << 18) +
            ((rgb[1] & MAX_U8) << 10) + 
            ((rgb[2] & MAX_U8) << 2)
        )

        color &= MAX_U32

        pal.append(color)

    assert f.remaining() == 0

    return pal

def alloc_vbit ():
    global voxSize, vbit

    bitCount = voxSize.x * voxSize.y * voxSize.z

    vbit = [ False ] * bitCount

def alloc_vcolhashead ():
    global vcolhashead

    vcolhashead = [ -1 ] * (vcolhashsizm1 + 1)

def SHIFTMOD32 (a):
    return a

# Set all bits in vbit from (x,y,z0) to (x,y,z1-1) to 0's
def setzrange0 (flags, z0, z1):
    for i in range(z0, z1):
        flags[i] = False

# Set all bits in vbit from (x,y,z0) to (x,y,z1-1) to 1's
def setzrange1 (flags, z0, z1):
    for i in range(z0, z1):
        flags[i] = True

def putvox (x, y, z, col):
    global voxSize, vnum, vmax, vcol

    if vnum >= vmax:
        vmax = max(vmax << 1, 4096)
        vadd = vmax - len(vcol)
        vcol += [ voxcol_t() for _ in range(vadd) ]

    # convert z to abs?
    z += x * voxSize.y * voxSize.z + y * voxSize.z

    vcol[vnum].p = z  # prev?

    z = (z * 214013) & vcolhashsizm1
    
    vcol[vnum].c = col
    vcol[vnum].n = vcolhashead[z]  # next?

    vcolhashead[z] = vnum

    vnum += 1

class voxmodel_t:
    def __init__ (self):
        self.mdnum     = None  # int32_t
        self.shadeoff  = None  # int32_t
        self.scale     = None  # float
        self.bscale    = None  # float
        self.zadd      = None  # float
        self.yoffset   = None  # float
        self.texid     = None  # GLuint *
        self.flags     = None  # int32_t
        self.vertex    = None  # GLfloat *
        self.index     = None  # GLuint *
        self.qcnt      = None  # int32_t
        self.mytex     = None  # int32_t *
        self.mytexx    = None  # int32_t
        self.mytexy    = None  # int32_t
        self.siz       = None  # vec3_t
        self.piv       = None  # vec3f_t
        self.is8bit    = None  # int32_t
        self.texid8bit = None  # uint32_t
        self.vbo       = None  # GLuint
        self.vboindex  = None  # GLuint

# modifies shcntmal, gmaxx, gmaxy, garea, gvox.qcnt
def cntquad (x0, y0, z0, x1, y1, z1, x2, y2, z2, face):
    global gvox, shcnt, shcntp, gmaxx, gmaxy, garea

    # x0, y0, z0 -- start
    # x1, y1, z1 -- end in same plane as start (???) -- UNUSED
    # x2, y2, z2 -- end [start, end)
    # face -- 1 - renderable face, 0 - non-renderable outer adjacent surface -- UNUSED

    print(x0, y0, z0)
    print(x1, y1, z1)
    print(x2, y2, z2)
    print(face)
    # sys.exit()

    x = abs(x2 - x0)  # length x
    y = abs(y2 - y0)  # length y
    z = abs(z2 - z0)  # length z

    # Find two axis defining area and assign their values to x and y
    if x == 0:
        x = z
    elif y == 0:
        y = z

    if x < y:
        # swap x and y
        x, y = y, x

    # are shcnt and shcntp related to largest voxSize axis?
    shcntmalIndex = shcnt + y * shcntp + x

    assert shcntmalIndex >= 0

    shcntmal[shcntmalIndex] += 1

    # remember largest x and y
    gmaxx = max(gmaxx, x)
    gmaxy = max(gmaxy, y)

    # add are of added quad including border
    garea += (x + VOXBORDWIDTH_X2) * (y + VOXBORDWIDTH_X2)

    # increment quad count
    gvox.qcnt += 1

    print('---')

def getvox (x, y, z):
    global voxSize, vcol, vcolhashead, vcolhashsizm1

    z += x * voxSize.y * voxSize.z + y * voxSize.z

    x = vcolhashead[(z * 214013) & vcolhashsizm1]

    while x >= 0:
        if vcol[x].p == z:
            return vcol[x].c

        x = vcol[x].n

    return 0x808080

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
 
def addquad (x0, y0, z0, x1, y1, z1, x2, y2, z2, face):
    global gvox, shcnt, shcntp, shp, gmaxx, gmaxy, garea, gquad, gqfacind

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

    z = shcnt[y * shcntp + x]

    shcnt[y * shcntp + x] += 1

    # int32_t *lptr = &gvox.mytex[(shp[z].y + VOXBORDWIDTH) * gvox.mytexx + (shp[z].x + VOXBORDWIDTH)]
    lptr = (shp[z].y + VOXBORDWIDTH) * gvox.mytexx + (shp[z].x + VOXBORDWIDTH)  # ptr into gvox.mytex

    # int32_t
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

            # lptr[xx] = getvox(nx, ny, nz);
            gvox.mytex[lptr + xx] = getvox(nx, ny, nz)

        lptr += gvox.mytexx

    # Extend borders horizontally
    for xx in range(VOXBORDWIDTH):
        for yy in range(y + VOXBORDWIDTH):
            lptr = (shp[z].y + yy) * gvox.mytexx + shp[z].x
            gvox.mytex[lptr + xx] = gvox.mytex[lptr + VOXBORDWIDTH]
            gvox.mytex[lptr + xx + x + VOXBORDWIDTH] = gvox.mytex[lptr + x - 1 + VOXBORDWIDTH]

    # Extend borders vertically
    for yy in range(VOXBORDWIDTH):
        dst = (shp[z].y + yy) * gvox.mytexx + shp[z].x
        src = (shp[z].y + VOXBORDWIDTH) * gvox.mytexx + shp[z].x
        cnt = x + VOXBORDWIDTH_X2

        for jj in range(cnt):
            gvox.mytex[dst + jj] = gvox.mytex[src + jj]

        dst = (shp[z].y + y + yy + VOXBORDWIDTH) * gvox.mytexx + shp[z].x
        src = (shp[z].y + y - 1 + VOXBORDWIDTH) * gvox.mytexx + shp[z].x
        cnt = x + VOXBORDWIDTH_X2

        for jj in range(cnt):
            gvox.mytex[dst + jj] = gvox.mytex[src + jj]

    # qptr = &gquad[gvox.qcnt];
    qptr = gvox.qcnt

    gquad[qptr].v[0].x = x0
    gquad[qptr].v[0].y = y0
    gquad[qptr].v[0].z = z0

    gquad[qptr].v[1].x = x1
    gquad[qptr].v[1].y = y1
    gquad[qptr].v[1].z = z1

    gquad[qptr].v[2].x = x2
    gquad[qptr].v[2].y = y2
    gquad[qptr].v[2].z = z2

    # constexpr vec2_u16_t vbw = { VOXBORDWIDTH, VOXBORDWIDTH };
    # vbw = Vec2(VOXBORDWIDTH, VOXBORDWIDTH)
    
    for j in range(3):
        gquad[qptr].v[j].u = shp[z].x + VOXBORDWIDTH
        gquad[qptr].v[j].v = shp[z].y + VOXBORDWIDTH

    if i < 3:
        gquad[qptr].v[1].u += x
    else:
        gquad[qptr].v[1].v += y

    gquad[qptr].v[2].u += x
    gquad[qptr].v[2].v += y

    gquad[qptr].v[3].u = gquad[qptr].v[0].u - gquad[qptr].v[1].u + gquad[qptr].v[2].u
    gquad[qptr].v[3].v = gquad[qptr].v[0].v - gquad[qptr].v[1].v + gquad[qptr].v[2].v

    gquad[qptr].v[3].x = gquad[qptr].v[0].x - gquad[qptr].v[1].x + gquad[qptr].v[2].x
    gquad[qptr].v[3].y = gquad[qptr].v[0].y - gquad[qptr].v[1].y + gquad[qptr].v[2].y
    gquad[qptr].v[3].z = gquad[qptr].v[0].z - gquad[qptr].v[1].z + gquad[qptr].v[2].z

    if gqfacind[face] < 0:
        gqfacind[face] = gvox.qcnt

    gvox.qcnt += 1

# return 0 or 1
def isolid (x, y, z):
    global voxSize, vbit

    if x < 0 or x >= voxSize.x or y < 0 or y >= voxSize.y or z < 0 or z >= voxSize.z:
        return 0

    # calc abs voxel index
    # scan along x left-to-right, along y ?-to-?, along z top-to-bottom
    z = x * voxSize.y * voxSize.z + y * voxSize.z + z

    return int(vbit[z])

# C++ rand
def rand ():
    return randint(0, 0x7fff)

'''
def isrectfree (x0, y0, dx, dy):
    global mytexo5

    i = y0 * mytexo5 + (x0 >> 5)

    dx += x0 - 1

    c = (dx >> 5) - (x0 >> 5)

    m = pow2m1[x0 & 31] ^ 0xFFFFFFFF  # inverse value from table
    m1 = pow2m1[(dx & 31) + 1]

    if not c:
        m &= m1

        while dy:
            if zbit[i] & m:
                return 0

            dy -= 1
            i += mytexo5
    else:
        while dy:
            if zbit[i] & m:
                return 0

            x = 0

            for x in range(1, c):
                if zbit[i + x]:
                    return 0

            if (zbit[i+x]&m1)
                return 0;

            dy -= 1
            i += mytexo5

    return 1

static void setrect(int32_t x0, int32_t y0, int32_t dx, int32_t dy)
{
    int32_t i = y0*mytexo5 + (x0>>5);
    dx += x0-1;
    const int32_t c = (dx>>5) - (x0>>5);

    int32_t m = ~pow2m1[x0&31];
    const int32_t m1 = pow2m1[(dx&31)+1];

    if (!c)
    {
        for (m &= m1; dy; dy--, i += mytexo5)
            zbit[i] |= m;
    }
    else
    {
        for (; dy; dy--, i += mytexo5)
        {
            zbit[i] |= m;

            int32_t x;
            for (x=1; x<c; x++)
                zbit[i+x] = -1;

            zbit[i+x] |= m1;
        }
    }
}
'''

def vox2poly ():
    global voxSize, gvox, shcntp, shcntmal, shcnt, gmaxx, gmaxy, garea, pow2m1, gqfacind, shp, mytexo5, zbit

    gvox = voxmodel_t()

    # x is largest dimension, y is 2nd largest dimension
    x = voxSize.x
    y = voxSize.y
    z = voxSize.z

    if x < y and x < z:
        x = z
    elif y < z:
        y = z

    if x < y:
        z = x
        x = y
        y = z

    shcntp = x
    shcntmal = [ 0 ] * (x * y)

    # shcnt = &shcntmal[-shcntp-1];  # negative index (-127)
    shcnt = -shcntp - 1

    gmaxx = 0
    gmaxy = 0
    garea = 0

    if pow2m1[32] != -1:
        for i in range(32):
            pow2m1[i] = (1 << i) - 1

        pow2m1[32] = -1

    for i in range(7):
        gqfacind[i] = -1

    # TODO: is +1 needed?
    i = max(voxSize.y, voxSize.z) + 1

    # int32_t *const bx0 = (int32_t *)Xmalloc(i<<1);
    # int32_t *const by0 = (int32_t *)(((intptr_t)bx0)+i);
    bx0 = [ 0 ] * i
    by0 = [ 0 ] * i

    ov = 0  # int32_t
    oz = 0  # int32_t

    for cnt in [ 0, 1 ]:
        daquad = [ cntquad, addquad ][cnt]

        gvox.qcnt = 0

        for i in range(len(by0)):
            by0[i] = -1

        v = 0

        print('=' * 50)

        for i in [ -1, 1 ]:
            for y in range(voxSize.y):
                for x in range(voxSize.x + 1):
                    for z in range(voxSize.z + 1):
                        print(f'i={i} x={x} y={y} z={z}', isolid(x, y, z), isolid(x, y + i, z), x, y + i, z) # i=1 x=0 y=5 z=27
                        ov = v
                        # v = is current voxel solid && behind voxel is not
                        v = int(isolid(x, y, z) and not isolid(x, y + i, z))
                        print(f'ov={bool(ov)} v={bool(v)} by0[z]={by0[z]} oz={oz}')

                        # by0[z]=28 oz=28 v=0 ov=0
                        # if there is z-start (z0) && (z-start != oz || v >= ov)
                        if by0[z] >= 0 and (by0[z] != oz or v >= ov):
                            print('call', daquad.__name__)
                            daquad(bx0[z], y, by0[z], x, y, by0[z], x, y, z, int(i >= 0))
                            by0[z] = -1

                        # if (current is solid and behind is not) && !(prev is solid and behind is not)
                        if v > ov:
                            _oz = oz
                            # Vec3(117, 0, 28)
                            # remember z-start candidate (+z - down) (28 from Vec3(117, 0, 28))
                            oz = z
                            _which = 'next' if i == -1 else 'prev'
                            print('v > ov:')
                            print(f'    isolid cur={ bool(isolid(x, y, z)) }; not isolid y-{_which}: { not isolid(x, y + i, z) }')
                            print(f'    _oz={_oz} z={z}')
                        # if not (current is solid and behind is not) && (prev is solid and behind is not) && (remembered z-start != z-start candidate)
                        elif v < ov and by0[z] != oz:
                            # Vec3(117, 0, 32)
                            _by0z = by0[z]
                            bx0[z] = x   # remember x-start for current z value (bx0[32] = 117)
                            by0[z] = oz  # remember z-start for current z value (by0[32] = 28)
                            print('v < ov and by0[z] != oz:')
                            print(f'    isolid cur={ bool(isolid(x, y, z)) }; not isolid y-{_which}: { not isolid(x, y + i, z) }')
                            print(f'    oz={oz} z={z} _by0z={_by0z} bx0[z]=x={x} by0[z]=oz={oz}')

                        print('-' * 50)

        print('=' * 50)
        sys.exit()
    
        for i in [ -1, 1 ]:
            for z in range(voxSize.z):
                for x in range(voxSize.x + 1):
                    for y in range(voxSize.y + 1):
                        ov = v                        
                        v = int(isolid(x, y, z) and not isolid(x, y, z - i))

                        if by0[y] >= 0 and (by0[y] != oz or v >= ov):
                            daquad(bx0[y], by0[y], z, x, by0[y], z, x, y, z, int(i >= 0) + 2)
                            by0[y] = -1

                        if v > ov:
                            oz = y
                        elif v < ov and by0[y] != oz:
                            bx0[y] = x
                            by0[y] = oz

        for i in [ -1, 1 ]:
            for x in range(voxSize.x):
                for y in range(voxSize.y + 1):
                    for z in range(voxSize.z + 1):
                        ov = v
                        v = int(isolid(x, y, z) and not isolid(x - i, y, z))

                        if by0[z] >= 0 and (by0[z] != oz or v >= ov):
                            daquad(x, bx0[z], by0[z], x, y, by0[z], x, y, z, int(i >= 0) + 4)
                            by0[z] = -1

                        if v > ov:
                            oz = z
                        elif v < ov and by0[z] != oz:
                            bx0[z] = y
                            by0[z] = oz
        if not cnt:
            shp = [ Vec2() for _ in range(gvox.qcnt) ]

            sc = 0

            for y in range(gmaxy, 0, -1):
                for x in range(gmaxx, y - 1, -1):
                    # shcnt changes from counter to head index
                    # shcnt = &shcntmal[-shcntp-1];  # negative index (-127)
                    assert (shcnt + y * shcntp + x) >= 0

                    i = shcntmal[shcnt + y * shcntp + x]

                    shcntmal[shcnt + y * shcntp + x] = sc

                    for i in range(i, 0, -1):
                        shp[sc].x = x
                        shp[sc].y = y
                        sc += 1

            gvox.mytexx = 32

            while gvox.mytexx < (gmaxx + VOXBORDWIDTH_X2):
                gvox.mytexx <<= 1

            gvox.mytexy = 32

            while gvox.mytexy < (gmaxy + VOXBORDWIDTH_X2):
                gvox.mytexy <<= 1

            # This should be sufficient to fit most skins...
            while gvox.mytexx * gvox.mytexy * 8 < garea * 9:
                if gvox.mytexx <= gvox.mytexy:
                    gvox.mytexx <<= 1
                else:
                    gvox.mytexy <<= 1

            mytexo5 = gvox.mytexx >> 5

            zbit = [ False ] * (gvox.mytexx * gvox.mytexy)

            v = gvox.mytexx * gvox.mytexy

            # constexpr vec2_u16_t vbw = { (VOXBORDWIDTH<<1), (VOXBORDWIDTH<<1) };
            
            for z in range(sc):
                d = Vec2(
                    shp[z].x + VOXBORDWIDTH_X2,
                    shp[z].y + VOXBORDWIDTH_X2,
                )

                i = v

                x0 = 0
                y0 = 0

                while True:
                    x0 = ((rand() & 32767) * (gvox.mytexx + 1 - d.x)) >> 15
                    y0 = ((rand() & 32767) * (gvox.mytexy + 1 - d.y)) >> 15

                    i -= 1

                    assert i >= 0

                    if isrectfree(x0, y0, d.x, d.y):
                        break

                while y0 and isrectfree(x0, y0 - 1, d.x, 1):
                    y0 -= 1

                while x0 and isrectfree(x0 - 1, y0, 1, d.y):
                    x0 -= 1

                setrect(x0, y0, d.x, d.y)

                # Overwrite size with top-left location
                shp[z].x = x0
                shp[z].y = y0

            gquad = gquad or []
            gquad += [ voxrect_t() for _ in range(gvox.qcnt - len(gquad)) ]

            gvox.mytex = [ 0 ] * (gvox.mytexx * gvox.mytexy)

    shp = None
    zbit = None

    phack = [ 0, 1.0 / 256.0 ]

    gvox.vertex = [ 0.0 ] * (gvox.qcnt * 5 * 4)
    gvox.index  = [ 0   ] * (gvox.qcnt * 3 * 2)

    ru = 1.0 / gvox.mytexx
    rv = 1.0 / gvox.mytexy

    for i in range(gvox.qcnt):
        vptr = gquad[i].v
        vsum = Vec3(
            vptr[0].x + vptr[2].x,
            vptr[0].y + vptr[2].y,
            vptr[0].z + vptr[2].z,
        )

        for j in range(4):
            gvox.vertex[((i << 2) + j) * 5 + 0] = vptr[j].x - phack[int(vsum.x > (vptr[j].x << 1))] + phack[int(vsum.x < (vptr[j].x << 1))]
            gvox.vertex[((i << 2) + j) * 5 + 1] = vptr[j].y - phack[int(vsum.y > (vptr[j].y << 1))] + phack[int(vsum.y < (vptr[j].y << 1))]
            gvox.vertex[((i << 2) + j) * 5 + 2] = vptr[j].z - phack[int(vsum.z > (vptr[j].z << 1))] + phack[int(vsum.z < (vptr[j].z << 1))]
            gvox.vertex[((i << 2) + j) * 5 + 3] = vptr[j].u * ru
            gvox.vertex[((i << 2) + j) * 5 + 4] = vptr[j].v * rv

        gvox.index[(i << 1) * 3 + 0] = (i << 2) + 0
        gvox.index[(i << 1) * 3 + 1] = (i << 2) + 1
        gvox.index[(i << 1) * 3 + 2] = (i << 2) + 2
        gvox.index[((i << 1) + 1) * 3 + 0] = (i << 2) + 0
        gvox.index[((i << 1) + 1) * 3 + 1] = (i << 2) + 2
        gvox.index[((i << 1) + 1) * 3 + 2] = (i << 2) + 3

    gquad = None
    
    return gvox


def loadVoxel (kvxPath):
    global voxSize, voxPiv, vbit, vcolhashsizm1

    assert isFile(kvxPath)

    with openFile(kvxPath) as f:
        # i32 mip1leng
        # vec3 voxSize
        # vec3 voxPivot
        # i32 xoffset[voxSize.x + 1]
        # u16 xyoffset[voxSize.x][voxSize.y + 1]

        mip1leng = f.i32()
        voxSize  = Vec3(*f.vec3i32())
        pivot    = f.vec3i32()

        voxPiv.x = pivot[0] / 256.0
        voxPiv.y = pivot[1] / 256.0
        voxPiv.z = pivot[2] / 256.0

        print(voxSize)

        xoffset  = f.u32(voxSize.x + 1)  # unused?
        xyoffset = f.u16(voxSize.x * (voxSize.y + 1))  # uint16_t[]
        # print(voxSize.x, voxSize.y, voxSize.z, xyoffset); #sys.exit()
        tbufOffset = f.tell()
        voxDataSize = mip1leng - tbufOffset + 4  # unused?

        pal = read_pal(f)

        alloc_vbit()

        vcolhashsizm1 = 4096

        while vcolhashsizm1 < (mip1leng >> 1):
            vcolhashsizm1 <<= 1

        vcolhashsizm1 -= 1

        alloc_vcolhashead()

        f.fromStart(tbufOffset)

        tbuf = f.read()
        cptr = 0

        _vcnt = 0

        # [0, 126)
        for x in range(voxSize.x):
            # left-to-right: j = x * (10 * 35); 0, 350, 700, ...
            j = x * voxSize.y * voxSize.z

            # print(f'x = { x }; j = { j }')

            # [0, 10)
            for y in range(voxSize.y):
                # y -- top to bottom
                # idx = 125 * (10 + 1) + 9
                idx = x * (voxSize.y + 1) + y

                # Byte count of: z0 | k | flags | color[0] | color[1] | ... | color[k - 1]
                i   = xyoffset[idx + 1] - xyoffset[idx]  # 0, 0, 0, 5, 12, 21, 30, 37, 42, 42, 42, 0, 0, 7, 17, 27, 35, 43, 53, 63, 70, 70
                z1  = 0

                # print(f'    j = { j }; y = { y }; idx = {idx}; {xyoffset[idx + 1]} - {xyoffset[idx]} = {i}')

                # z0 | k | flags | color[0] | color[1] | ... | color[k - 1]
                while i:
                    z0 = tbuf[cptr]      # offset from top in voxels 
                    k  = tbuf[cptr + 1]  # count of solid voxels
                    fl = tbuf[cptr + 2]  # flags
                    # print(f'        z0 = { z0 }; k = { k }; fl = { fl }; cptr = { cptr }')

                    cptr += 3

                    # voxels inside on the object (not surface)
                    if not (fl & 16):
                        # print('    ^^^ 1:', z1, z0)
                        setzrange1(vbit, j + z1, j + z0)

                    i -= k + 3  # k color indices and 3 bytes for z0, k, flags
                    z1 = z0 + k

                    setzrange1(vbit, j + z0, j + z1)
                    # print('    ^^^ 2:', z0, z1)

                    for z in range(z0, z1):
                        # put surface voxel
                        # print('putvox', x, y, z, pal[tbuf[cptr]])
                        putvox(x, y, z, pal[tbuf[cptr]])
                        _vcnt+=1
                        cptr += 1

                # plus one vertical column (1, 1, 35)
                # j += 35
                j += voxSize.z

            # print('---')

        print(vcolhashsizm1, _vcnt)
        # vox2poly()
        # sys.exit()


def loadVoxels ():
    for voxel in VOXELS:
        kvxPath = voxel['path']
        kvxPath = getAbsPath(joinPath(GAME_DIR, kvxPath))

        print(kvxPath)

        loadVoxel(kvxPath)

        print(' ')



if __name__ == '__main__':
    # loadVoxels()
    loadVoxel(joinPath(GAME_DIR, 'voxels', '209_BATON.kvx')) 
    # loadVoxel(joinPath(GAME_DIR, 'voxels', '7267_TURRET_A.kvx')) 