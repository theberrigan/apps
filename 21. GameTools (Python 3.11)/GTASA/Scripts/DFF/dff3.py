import struct, os

SECTION_TYPE = {
    -1        : 'ANY',
    0         : 'NONE',
    0x0001    : 'STRUCT',
    0x0002    : 'STRING',
    0x0003    : 'EXTENSION',
    0x0006    : 'TEXTURE',
    0x0007    : 'MATERIAL',
    0x0008    : 'MATERIALLIST',
    0x000E    : 'FRAMELIST',
    0x000F    : 'GEOMETRY',
    0x0010    : 'CLUMP',
    0x0014    : 'ATOMIC',
    0x001A    : 'GEOMETRYLIST',
    # 0x001F    : 'RIGHT_TO_RENDER',
    # 0x105     : 'MORPH_PLG',
    # 0x116     : 'SKIN_PLG',
    # 0x118     : 'PARTICLES_PLG',
    # 0x11E     : 'HANIM_PLG',
    # 0x11F     : 'USER_DATA_PLG',
    # 0x120     : 'MATERIAL_EFFECTS_PLG',
    # 0x127     : 'ANISOTROPY_PLG',
    # 0x135     : 'UV_ANIMATION_PLG',
    # 0x50E     : 'BIN_MESH_PLG',
    # 0x510     : 'NATIVE_DATA_PLG',
    # 0x253F2F3 : 'PIPELINE',
    # 0x253F2F6 : 'SPECULAR_MATERIAL',
    # 0x253F2F8 : 'EFFECT2D',
    # 0x253F2F9 : 'NIGHT_VERTEX_COLOR',
    # 0x253F2FA : 'COLLISION_MODEL',
    # 0x253F2FC : 'REFLECTION_MATERIAL',
    # 0x253F2FD : 'BREAKABLE',
    # 0x253F2FE : 'NODE_NAME',
}

def readFormat (f, fmt):
    return struct.unpack(fmt, f.read(struct.calcsize(fmt)))

def decodeVersion (version):
    if (version & 0xFFFF0000) == 0:
        return version << 8
    else:
        p1 = ((version >> 14) & 0x3FF00) + 0x30000
        p2 = (version >> 16) & 0x3F

        return p1 | p2

def read (f, fileSize, level):
    while f.tell() < fileSize:
        header = readFormat(f, 'III')
        sectionType = header[0]
        contentSize = header[1]
        version = decodeVersion(header[2])
        headerEnd = f.tell()

        if version == 0x36003 and sectionType in SECTION_TYPE:
            print(' ' * (level * 4 - 1), SECTION_TYPE[sectionType])
            read(f, f.tell() + contentSize, level + 1)

        f.seek(headerEnd + contentSize)


# filePath = './img/slamvan.dff'
filePath = './img/bonaventura_LAn.dff'
with open(filePath, 'rb') as f:
    read(f, os.path.getsize(filePath), 0)