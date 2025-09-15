import os
from collections import namedtuple
from common import GAME_DIR, readStruct


SECTION_TYPE_NAOBJECT         = 0x00
SECTION_TYPE_STRUCT           = 0x01
SECTION_TYPE_STRING           = 0x02
SECTION_TYPE_EXTENSION        = 0x03
SECTION_TYPE_CAMERA           = 0x05
SECTION_TYPE_TEXTURE          = 0x06
SECTION_TYPE_MATERIAL         = 0x07
SECTION_TYPE_MATLIST          = 0x08
SECTION_TYPE_ATOMICSECT       = 0x09
SECTION_TYPE_PLANESECT        = 0x0A
SECTION_TYPE_WORLD            = 0x0B
SECTION_TYPE_SPLINE           = 0x0C
SECTION_TYPE_MATRIX           = 0x0D
SECTION_TYPE_FRAMELIST        = 0x0E
SECTION_TYPE_GEOMETRY         = 0x0F
SECTION_TYPE_CLUMP            = 0x10
SECTION_TYPE_LIGHT            = 0x12
SECTION_TYPE_UNICODESTRING    = 0x13
SECTION_TYPE_ATOMIC           = 0x14
SECTION_TYPE_TEXTURENATIVE    = 0x15
SECTION_TYPE_TEXDICTIONARY    = 0x16
SECTION_TYPE_ANIMDATABASE     = 0x17
SECTION_TYPE_IMAGE            = 0x18
SECTION_TYPE_SKINANIMATION    = 0x19
SECTION_TYPE_GEOMETRYLIST     = 0x1A
SECTION_TYPE_ANIMANIMATION    = 0x1B
SECTION_TYPE_HANIMANIMATION   = 0x1B
SECTION_TYPE_TEAM             = 0x1C
SECTION_TYPE_CROWD            = 0x1D
SECTION_TYPE_DMORPHANIMATION  = 0x1E
SECTION_TYPE_RIGHTTORENDER    = 0x1f
SECTION_TYPE_MTEFFECTNATIVE   = 0x20
SECTION_TYPE_MTEFFECTDICT     = 0x21
SECTION_TYPE_TEAMDICTIONARY   = 0x22
SECTION_TYPE_PITEXDICTIONARY  = 0x23
SECTION_TYPE_TOC              = 0x24
SECTION_TYPE_PRTSTDGLOBALDATA = 0x25
SECTION_TYPE_ALTPIPE          = 0x26
SECTION_TYPE_PIPEDS           = 0x27
SECTION_TYPE_PATCHMESH        = 0x28
SECTION_TYPE_CHUNKGROUPSTART  = 0x29
SECTION_TYPE_CHUNKGROUPEND    = 0x2A
SECTION_TYPE_UVANIMDICT       = 0x2B
SECTION_TYPE_COLLTREE         = 0x2C
SECTION_TYPE_ENVIRONMENT      = 0x2D
SECTION_TYPE_COREPLUGINIDMAX  = 0x2E


class RWBSReader:
    def __init__ (self, filePath):
        self.filePath = filePath

    @staticmethod
    def create (filePath):
        reader = RWBSReader(filePath)
        return reader

    def decodeVersion (self, version):
        if (version & 0xFFFF0000) == 0:
            return version << 8
        else:
            p1 = ((version >> 14) & 0x3FF00) + 0x30000
            p2 = (version >> 16) & 0x3F
            
            return p1 | p2

    def parse (self):            
        if not os.path.isfile(self.filePath):
            raise Exception('File doesn\'t exist: {}'.format(self.filePath))

        # fileSize = os.path.getsize(self.filePath)

        with open(self.filePath, 'rb') as f:
            sectionType, contentSize, rwVersion = readStruct('<3I', f)
            rwVersion = self.decodeVersion(rwVersion)

            print(sectionType, contentSize, hex(rwVersion))


'''
    Section:
        - Header
        - Content (struct)
        - Additional/child content
'''

if __name__ == '__main__':
    # reader = RWBSReader.create(os.path.join(GAME_DIR, 'models', 'fronten2.txd'))
    reader = RWBSReader.create(os.path.join(GAME_DIR, '.mods', '+ PS2 Vehicles', 'models', 'gta3.img', 'androm.dff'))
    reader.parse()