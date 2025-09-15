import os, struct, enum

class SectionType:
    NAOBJECT               = 0x00
    STRUCT                 = 0x01
    STRING                 = 0x02
    EXTENSION              = 0x03
    CAMERA                 = 0x05
    TEXTURE                = 0x06
    MATERIAL               = 0x07
    MATLIST                = 0x08
    ATOMICSECT             = 0x09
    PLANESECT              = 0x0A
    WORLD                  = 0x0B
    SPLINE                 = 0x0C
    MATRIX                 = 0x0D
    FRAMELIST              = 0x0E
    GEOMETRY               = 0x0F
    CLUMP                  = 0x10
    LIGHT                  = 0x12
    UNICODESTRING          = 0x13
    ATOMIC                 = 0x14
    TEXTURENATIVE          = 0x15
    TEXDICTIONARY          = 0x16
    ANIMDATABASE           = 0x17
    IMAGE                  = 0x18
    SKINANIMATION          = 0x19
    GEOMETRYLIST           = 0x1A
    ANIMANIMATION          = 0x1B
    HANIMANIMATION         = 0x1B
    TEAM                   = 0x1C
    CROWD                  = 0x1D
    DMORPHANIMATION        = 0x1E
    RIGHTTORENDER          = 0x1F
    MTEFFECTNATIVE         = 0x20
    MTEFFECTDICT           = 0x21
    TEAMDICTIONARY         = 0x22
    PITEXDICTIONARY        = 0x23
    TOC                    = 0x24
    PRTSTDGLOBALDATA       = 0x25
    ALTPIPE                = 0x26
    PIPEDS                 = 0x27
    PATCHMESH              = 0x28
    CHUNKGROUPSTART        = 0x29
    CHUNKGROUPEND          = 0x2A
    UVANIMDICT             = 0x2B
    COLLTREE               = 0x2C
    ENVIRONMENT            = 0x2D
    COREPLUGINIDMAX        = 0x2E


    map = None

    @staticmethod
    def getName (value):
        if SectionType.map is None:
            SectionType.map = { getattr(SectionType, key): key for key in dir(SectionType) if key.isupper() }

        return SectionType.map[value] if value in SectionType.map else '0x{:X}'.format(value)


class VirtualReader:
    def __init__ (self, filePath):
        self.filePath = filePath
        self.cursor = 0
        self.size = 0
        self.buffer = None
        self.open()

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self):
        with open(self.filePath, 'rb') as f:
            self.buffer = f.read()
            self.cursor = 0
            self.size = len(self.buffer)

    def close (self):
        self.buffer = None
        self.cursor = 0
        self.size = 0

    def read (self, sizeToRead = None):
        sizeLeft = max(0, self.size - self.cursor)

        if sizeToRead is None or sizeToRead < 0 or sizeToRead >= sizeLeft:
            sizeToRead = sizeLeft

        if sizeToRead == 0:
            return b''

        chunk = self.buffer[self.cursor:self.cursor + sizeToRead]
        self.cursor += sizeToRead

        return chunk

    def tell (self):
        return self.cursor

    def seek (self, offset):
        if type(offset) != int or offset < 0:
            raise OSError('Invalid argument')

        self.cursor = offset

        return self.cursor

    def readStruct (self, structFormat):
        return struct.unpack(structFormat, self.read(struct.calcsize(structFormat)))

    def readHex (self, sizeToRead):
        return ' '.join([ '{:02X}'.format(b) for b in list(self.read(sizeToRead)) ])


class SectionHeader:
    def __init__ (self, reader):
        self.reader = reader
        header = self.reader.readStruct('III')
        self.sectionType = header[0]
        self.contentSize = header[1]
        self.rwVersion = self.decodeVersion(header[2])
        self.headerEnd = self.reader.tell()
        self.contentEnd = self.headerEnd + self.contentSize

    @staticmethod
    def decodeVersion (version):
        if (version & 0xFFFF0000) == 0:
            return version << 8
        else:
            p1 = ((version >> 14) & 0x3FF00) + 0x30000
            p2 = (version >> 16) & 0x3F

            return p1 | p2

    def __str__ (self):
        return '{}(sectionType={}, contentSize={}, rwVersion=0x{:X})'.format(
            self.__class__.__name__,
            SectionType.getName(self.sectionType),
            self.contentSize,
            self.rwVersion
        )


class DFF:
    def __init__ (self, filePath):
        self.filePath = filePath
        self.reader = VirtualReader(filePath)
        self.root = None

    def readRoot (self):
        header = SectionHeader(self.reader)

        if header.sectionType == SectionType.CLUMP:
            self.root = ClumpSection(self.reader, header)
        elif header.sectionType == SectionType.UVANIMDICT:
            self.root = UVAnimDictSection(self.reader, header)
        else:
            raise Exception('Unexpected root section {} ({})'.format(
                SectionType.getName(header.sectionType),
                self.filePath
            ))