import struct


class Vec:
    keyMap = [
        [ 'x', 'r', 'u' ]
    ]

    def __init__ (self, *components):
        self.componentCount = len(self.keyMap)
        self.keyMap = { key: i for i, keys in enumerate(self.keyMap) for key in keys }
        self.update(*components)

    def __index__ (self, index):
        return self.components[index]

    def __getattr__ (self, attr):
        if attr in self.keyMap:
            return self.components[self.keyMap[attr]]
        
        return super().__getattr__(attr)

    def __setattr__ (self, attr, value):
        if attr in self.keyMap:
            self.components[self.keyMap[attr]] = value

        super().__setattr__(attr, value)

    def __str__ (self):
        return '{}({})'.format(self.__class__.__name__, ', '.join(map(lambda c: str(c), self.components)))

    def __iter__ (self):
        for component in self.components:
            yield component

    def update (self, *components):
        if len(components) > self.componentCount:
            raise Exception('{} has {} components, {} given'.format(self.__class__.__name__, self.componentCount, len(components)))

        self.components = list(components) + [ 0 ] * (self.componentCount - len(components))


class Vec2 (Vec):
    keyMap = [
        [ 'x', 'r', 'u' ],
        [ 'y', 'g', 'v' ],
    ]


class Vec3 (Vec):
    keyMap = [
        [ 'x', 'r', 'u' ],
        [ 'y', 'g', 'v' ],
        [ 'z', 'b' ],
    ]


class Vec4 (Vec):
    keyMap = [
        [ 'x', 'r', 'u' ],
        [ 'y', 'g', 'v' ],
        [ 'z', 'b' ],
        [ 'w', 'a' ]
    ]


# ---------------------------

class SectionType:
    NONE = 0
    STRUCT = 0x0001
    STRING = 0x0002
    EXTENSION = 0x0003
    TEXTURE = 0x0006
    MATERIAL = 0x0007
    MATERIALLIST = 0x0008
    FRAMELIST = 0x000E
    GEOMETRY = 0x000F
    CLUMP = 0x0010
    ATOMIC = 0x0014
    GEOMETRYLIST = 0x001A
    RENDERRIGHTS = 0x001F

class GeometryFlag:
    TRISTRIP = 0x0001
    POSITIONS = 0x0002
    TEXTURED = 0x0004
    PRELIT = 0x0008
    NORMALS = 0x0010
    LIGHT = 0x0020
    MODULATEMATERIALCOLOR = 0x0040
    TEXTURED2 = 0x0080


class Geometry:
    def __init__ (self):
        self.flags = 0
        self.surfAmbient = 0.0
        self.surfSpecular = 0.0
        self.surfDiffuse = 0.0
        self.vertices = []
        self.vertColors = []
        self.hasEnvUV = False
        self.triangles = []
        self.hasNormals = False

    def addVertex (self, vertex):
        self.vertices.append(vertex)

    def addVertexColor (self, color):
        self.vertColors.append(color)

    def addTriangle (self, triangle):
        self.triangles.append(triangle)


class Vertex:
    def __init__(self, coords=None, normal=None):
        self.coords = coords
        self.normal = normal
        self.uv = None
        self.envUV = None
        self.extraUV = []


class Triangle:
    def __init__(self, vertices, matId):
        self.vertices = vertices
        self.matId = matId


class Header:
    def __init__ (self, sectionType, contentSize, encodedVersion):
        self.sectionType = sectionType
        self.contentSize = contentSize
        self.rwVersion = self.decodeVersion(encodedVersion)

    def decodeVersion (self, version):
        if (version & 0xFFFF0000) == 0:
            return version << 8
        else:
            p1 = ((version >> 14) & 0x3FF00) + 0x30000
            p2 = (version >> 16) & 0x3F
            
            return p1 | p2

    def __str__ (self):
        return 'Header(sectionType=0x{:x}, contentSize={}, rwVersion=0x{:x})'.format(self.sectionType, self.contentSize, self.rwVersion)

class Reader:
    def __init__ (self, filepath):
        self.filepath = filepath
        self.descriptor = open(filepath, 'rb')

    def __del__ (self):
        self.close()

    def close (self):
        if self.descriptor:
            self.descriptor.close()
            self.descriptor = None

    def read (self, size=None):
        return self.descriptor.read(size)

    def readFormat (self, format):
        return struct.unpack(format, self.descriptor.read(struct.calcsize(format)))

    def tell (self):
        return self.descriptor.tell()

    def seek (self, pos):
        return self.descriptor.seek(pos)


class Section:
    sectionType = SectionType.NONE

    def __init__ (self, reader):
        self.reader = reader
        self.header = None

    def readHeader (self, checkSectionType=True):
        self.header = Header(*self.reader.readFormat('III'))

        if checkSectionType and self.sectionType != None and self.sectionType != self.header.sectionType:
            raise Exception('Expected section 0x{:x}, but 0x{:x} given'.format(self.sectionType, self.header.sectionType))

        self.curPosAfterContent = self.reader.tell() + self.header.contentSize

    def setCursorAfterContent (self):
        self.reader.seek(self.curPosAfterContent)


class ClumpSection (Section):
    sectionType = SectionType.CLUMP

    def __init__ (self, reader):
        super().__init__(reader)

        self.struct = None
        self.frameList = None
        self.geometryList = None

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.struct = ClumpStructSection(self.reader)
        self.frameList = FrameListSection(self.reader)
        self.geometryList = GeometryListSection(self.reader)

        # # TODO: array?
        # for i in range(atomicCount):
        #     self.atomic = AtomicSection(self.reader)

        # self.extension = ExtensionSection(self.reader)

class ClumpStructSection (Section):
    sectionType = SectionType.STRUCT

    def __init__ (self, reader):
        super().__init__(reader)

        self.atomicCount = 0
        self.lightCount = 0
        self.cameraCount = 0

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.atomicCount = self.reader.readFormat('i')[0]

        if self.header.rwVersion > 0x33000:
            self.lightCount, self.cameraCount = self.reader.readFormat('ii')


class FrameListSection (Section):
    sectionType = SectionType.FRAMELIST

    def __init__ (self, reader):
        super().__init__(reader)

        self.extensions = []

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.struct = FrameListStructSection(self.reader)
        
        for i in range(self.struct.frameCount):
            self.extensions.append(ExtensionSection(self.reader))


class FrameListStructSection (Section):
    sectionType = SectionType.STRUCT

    def __init__ (self, reader):
        super().__init__(reader)

        self.frameCount = 0
        self.frames = []

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.frameCount = self.reader.readFormat('i')[0]

        for i in range(self.frameCount):
            rotation = self.reader.readFormat('fffffffff')
            position = self.reader.readFormat('fff')
            (parent, flags) = self.reader.readFormat('ii')
            # TODO: wrap to Frame class
            self.frames.append((rotation, position, parent, flags))


class GeometryListSection (Section):
    sectionType = SectionType.GEOMETRYLIST

    def __init__ (self, reader):
        super().__init__(reader)

        self.struct = None
        self.geometry = []

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.struct = GeometryListStructSection(self.reader)
        
        for i in range(self.struct.geomCount):
            self.geometry.append(GeometrySection(self.reader))


class GeometryListStructSection (Section):
    sectionType = SectionType.STRUCT

    def __init__ (self, reader):
        super().__init__(reader)

        self.geomCount = 0

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.geomCount = self.reader.readFormat('i')[0]


class GeometrySection (Section):
    sectionType = SectionType.GEOMETRY

    def __init__ (self, reader):
        super().__init__(reader)

        self.struct = None

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.struct = GeometryStructSection(self.reader)


class GeometryStructSection (Section):
    sectionType = SectionType.STRUCT

    def __init__ (self, reader):
        super().__init__(reader)

        self.geometries = []
        self.materialList = None

        self.readHeader()
        self.readContent()

    def readContent (self):
        geometry = Geometry()
        self.geometries.append(geometry)

        flags, texCount, triCount, vertCount, morphCount = self.reader.readFormat('HHiii')

        geometry.flags = flags

        if self.header.rwVersion < 0x34001:
            geometry.surfAmbient, geometry.surfSpecular, geometry.surfDiffuse = self.reader.readFormat('fff')

        for i in range(vertCount):
            geometry.addVertex(Vertex())

        if flags & GeometryFlag.PRELIT:            
            for i in range(vertCount):
                # TODO: normalize [0-255] -> [0.0, 1.0]
                geometry.addVertexColor(Vec4(*self.reader.readFormat('BBBB')))

        for i in range(vertCount):
            # TODO: reverse second uv component
            geometry.vertices[i].uv = Vec2(*self.reader.readFormat('ff'))

        if texCount > 1:
            geometry.hasEnvUV = True
            
            for i in range(vertCount):
                # TODO: reverse second uv component
                geometry.vertices[i].envUV = Vec2(*self.reader.readFormat('ff'))

        if texCount > 2:
            for i in range(texCount - 2):
                for j in range(vertCount):
                    geometry.vertices[i].extraUV.append(Vec2(*self.reader.readFormat('ff')))

        for i in range(triCount):
            c, b, matId, a = self.reader.readFormat('HHHH')
            
            if max(a, b, c) >= vertCount:
                raise Exception('Vertex indices out of range for triangle.')
            
            geometry.addTriangle(Triangle(Vec3(a, b, c), matId))

        if morphCount != 1:
            raise Exception("Multiple frames not supported")

        for i in range(morphCount):
            bx, by, bz, br, hasVerts, hasNormals = self.reader.readFormat('ffffii')
            
            if hasVerts > 0:
                for j in range(vertCount):
                    geometry.vertices[j].coords = Vec3(*self.reader.readFormat('fff'))
            
            if hasNormals > 0:
                geometry.hasNormals = True
                
                for j in range(vertCount):
                    geometry.vertices[j].normal = Vec3(*self.reader.readFormat('fff'))

        # self.materialList = MaterialListSection(self.reader)

'''
class MaterialListSection (Section):
    sectionType = SectionType.MATERIALLIST

    def __init__ (self, reader):
        super().__init__(reader)

        self.struct = None
        self.materials = []

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.struct = MaterialListStructSection(self.reader)
        
        for i in range(self.struct.matCount):
            self.materials.append(MaterialSection(self.reader))


class MaterialListStructSection (Section):
    sectionType = SectionType.STRUCT

    def __init__ (self, reader):
        super().__init__(reader)

        self.matCount = 0

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.matCount = self.reader.readFormat('i')[0]

        # TODO: what is it?
        for i in range(self.matCount):
            junk = self.reader.readFormat('i')[0]


class MaterialSection (Section):
    sectionType = SectionType.MATERIAL

    def __init__ (self, reader):
        super().__init__(reader)

        self.struct = None

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.struct = MaterialStructSection(self.reader)


class MaterialStructSection (Section):
    sectionType = SectionType.STRUCT

    def __init__ (self, reader):
        super().__init__(reader)

        self.material = None
        self.texture = None
        self.extension = None

        self.readHeader()
        self.readContent()

    def readContent (self):
        flags = self.reader.readFormat('I')[0]
        col = self.reader.readFormat('BBBB')
        _, textured, ambient, specular, diffuse = self.reader.readFormat('iifff')
        
        # TODO: wrap to Material
        # TODO: add to geometry
        self.material = (geometry, flags, col, textured, ambient, specular, diffuse)
        
        if textured > 0:
            self.texture = TextureSection(self.reader, material)
            
        self.extension = ExtensionSection(self.reader)


class TextureSection (Section):
    sectionType = SectionType.TEXTURE

    def __init__ (self, reader, material):
        super().__init__(reader)

        self.struct = None

        self.readHeader()
        self.readContent(material)

    def readContent (self, material):
        self.struct = TextureStructSection(self.reader, material)


class TextureStructSection (Section):
    sectionType = SectionType.STRUCT

    def __init__ (self, reader, material):
        super().__init__(reader)

        self.readHeader()
        self.readContent(material)

    def readContent (self, material):
        flags, _ = self.reader.readFormat('HH')
        
        _, texName = self.readSection(RwTypes.STRING)
        _, alphaName = self.readSection(RwTypes.STRING)
        
        if material.readenvmap:
            texture = self.RwTexture(self, material, texName, 1, material.envIntensity)
            material.setEnvTexture(texture)
        else:
            texture = self.RwTexture(self, material, texName, 0, 1)
            material.setTexture(texture)
        
        self.extension = ExtensionSection(self.reader)
'''



class AtomicSection (Section):
    sectionType = SectionType.ATOMIC

    def __init__ (self, reader):
        super().__init__(reader)

        self.readHeader()
        self.readContent()

    def readContent (self):
        pass


# TODO: !!! entension read is incorrect
class ExtensionSection (Section):
    sectionType = SectionType.EXTENSION

    def __init__ (self, reader):
        super().__init__(reader)

        # TODO: what format has extension?
        self.data = ''

        self.readHeader()
        self.readContent()

    def readContent (self):
        self.data = self.reader.read(self.header.contentSize)
        print(struct.unpack('III', self.data[:12]), self.data[12:])



class DFF:
    def __init__ (self, filepath):
        print('{}'.format(filepath))
        self.reader = Reader(filepath)
        self.clump = ClumpSection(self.reader)

# zero = DFF('./img/zero.dff')
zero = DFF('./img/slamvan.dff')