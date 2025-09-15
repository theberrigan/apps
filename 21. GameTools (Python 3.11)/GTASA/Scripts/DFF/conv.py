import os, struct
# from plugin2 import ImportRenderware
from dff2 import DFF
from dragonff import dff as DragonFF

IDEs = [
    'data/maps/LA/LAn.ide',
    'data/maps/LA/LAn2.ide',
    'data/maps/LA/LAs.ide',
    'data/maps/LA/LAs2.ide',
    'data/maps/LA/LAe.ide',
    'data/maps/LA/LAe2.ide',
    'data/maps/LA/LAw2.ide',
    'data/maps/LA/LAw.ide',
    'data/maps/LA/LAwn.ide',
    'data/maps/LA/LAhills.ide',
    'data/maps/LA/LAxref.ide',
    'data/maps/SF/SFn.ide',
    'data/maps/SF/SFs.ide',
    'data/maps/SF/SFse.ide',
    'data/maps/SF/SFe.ide',
    'data/maps/SF/SFw.ide',
    'data/maps/SF/SFxref.ide',
    'data/maps/vegas/vegasN.ide',
    'data/maps/vegas/vegasS.ide',
    'data/maps/vegas/vegasE.ide',
    'data/maps/vegas/vegasW.ide',
    'data/maps/vegas/vegaxref.ide',
    'data/maps/country/countryN.ide',
    'data/maps/country/countN2.ide',
    'data/maps/country/countryS.ide',
    'data/maps/country/countryE.ide',
    'data/maps/country/countryW.ide',
    'data/maps/country/counxref.ide',
]

IPLs = [
    'data/maps/LA/LAn.ipl',
    'data/maps/LA/LAn2.ipl',
    'data/maps/LA/LAs.ipl',
    'data/maps/LA/LAs2.ipl',
    'data/maps/LA/LAe.ipl',
    'data/maps/LA/LAe2.ipl',
    'data/maps/LA/LAw.ipl',
    'data/maps/LA/LAwn.ipl',
    'data/maps/LA/LAw2.ipl',
    'data/maps/LA/LAhills.ipl',
    'data/maps/SF/SFn.ipl',
    'data/maps/SF/SFs.ipl',
    'data/maps/SF/SFse.ipl',
    'data/maps/SF/SFe.ipl',
    'data/maps/SF/SFw.ipl',
    'data/maps/vegas/vegasN.ipl',
    'data/maps/vegas/vegasS.ipl',
    'data/maps/vegas/vegasE.ipl',
    'data/maps/vegas/vegasW.ipl',
    'data/maps/country/countryN.ipl',
    'data/maps/country/countN2.ipl',
    'data/maps/country/countrys.ipl',
    'data/maps/country/countryE.ipl',
    'data/maps/country/countryW.ipl',
]

# IDE - http://gtamodding.ru/wiki/IDE
# IPL - http://gtamodding.ru/wiki/IPL
# DFF - http://gtamodding.ru/wiki/DFF
# TXD - http://gtamodding.ru/wiki/TXD

# ide:
# objs
# uniqueId (DWORD), dff (string[24]), txd (string[24]), drawDistance (float), flags (DWORD)
# end

IDE_SECTION_NAMES = [ 'objs', 'tobj', 'anim', 'peds', 'tobj', 'weap', 'cars', 'path', 'hier', 'txdp', '2dfx' ]
IPL_SECTION_NAMES = [ 'inst', 'cull', 'path', 'grge', 'enex', 'pick', 'jump', 'tcyc', 'auzo', 'mult', 'cars' ]

def parseSections (lines, sections):
    lines = [ line.strip() for line in lines ]
    result = { section: [] for section in sections }
    section = None

    for line in lines:
        line = line.strip()
        lineLow = line.lower()

        if not line or line[0] in [ '#', ';' ]:
            continue
        elif lineLow in sections:
            section = lineLow
        elif not section:
            raise('Section name is expected')
        elif lineLow == 'end':
            section = None
        else:
            result[section].append([ param.strip() for param in line.split(',') ])

    return result


def parseIDE (lines):
    data = parseSections(lines, IDE_SECTION_NAMES)
    objs = data['objs']

    for i, params in enumerate(objs):
        if len(params) != 5:
            raise('5 params are expected')

        objs[i] = { 
            'id': int(params[0]),
            'dff': 'img/{}.dff'.format(params[1]),
            'txd': 'img/{}.txd'.format(params[2]),
            'drawDistance': float(params[3]),
            'flags': int(params[4])
        }

    return data


def parsePlainIPL (lines):
    data = parseSections(lines, IPL_SECTION_NAMES)
    insts = data['inst']

    for i, params in enumerate(insts):
        if len(params) != 11:
            raise('11 params are expected')

        insts[i] = { 
            'id': int(params[0]),
            'null': params[1],
            'interior': float(params[2]),
            'position': (float(params[3]), float(params[4]), float(params[5])),
            'rotation': (float(params[6]), float(params[7]), float(params[8]), float(params[9])),
            'LOD': int(params[10])
        }

    return data


# -------------------------------------------

def conv ():
    objs = dict()
    insts = dict()

    for ide in IDEs:
        data = None

        with open(ide, 'r', encoding='utf-8') as f:
            data = parseIDE(f.readlines())

        for item in data['objs']:
            objs[item['id']] = item

        print(ide, '{} objs'.format(len(data['objs'])))

    print('Total objs: {}\n'.format(len(objs)))

    for ipl in IPLs:
        data = None

        with open(ipl, 'r', encoding='utf-8') as f:
            data = parsePlainIPL(f.readlines())

        for item in data['inst']:
            insts[item['id']] = item

        print(ipl, '{} insts'.format(len(data['inst'])))

    print('Total inst: {}\n'.format(len(insts)))

    return objs


# ------------------------------------------------

items = conv().values()
errors = 0

for i, item in enumerate(items):
    filepath = item = item['dff']

    if not os.path.isfile(filepath) and not item.lower().endswith('.dff'):
        continue

    if (i % 1500) == 0:
        print('{}/{} {}'.format(i + 1, len(items), filepath))

    try:
        model = DFF(filepath)
        # model = DragonFF()
        # model.load_file(filepath)
    except Exception as e:
        print(str(e))
        errors += 1

print('Errors:', errors)

# print('-' * 50)
# model = DragonFF()
# model.load_file('./img/bonaventura_LAn.dff')
# print('-' * 50)


# ------------------------------------------------

'''
TYPES = (
    (0x00, 'NAOBJECT'),
    (0x01, 'STRUCT'),
    (0x02, 'STRING'),
    (0x03, 'EXTENSION'),
    (0x05, 'CAMERA'),
    (0x06, 'TEXTURE'),
    (0x07, 'MATERIAL'),
    (0x08, 'MATLIST'),
    (0x09, 'ATOMICSECT'),
    (0x0A, 'PLANESECT'),
    (0x0B, 'WORLD'),
    (0x0C, 'SPLINE'),
    (0x0D, 'MATRIX'),
    (0x0E, 'FRAMELIST'),
    (0x0F, 'GEOMETRY'),
    (0x10, 'CLUMP'),
    (0x12, 'LIGHT'),
    (0x13, 'UNICODESTRING'),
    (0x14, 'ATOMIC'),
    (0x15, 'TEXTURENATIVE'),
    (0x16, 'TEXDICTIONARY'),
    (0x17, 'ANIMDATABASE'),
    (0x18, 'IMAGE'),
    (0x19, 'SKINANIMATION'),
    (0x1A, 'GEOMETRYLIST'),
    (0x1B, 'ANIMANIMATION'),
    (0x1B, 'HANIMANIMATION'),
    (0x1C, 'TEAM'),
    (0x1D, 'CROWD'),
    (0x1E, 'DMORPHANIMATION'),
    (0x1f, 'RIGHTTORENDER'),
    (0x20, 'MTEFFECTNATIVE'),
    (0x21, 'MTEFFECTDICT'),
    (0x22, 'TEAMDICTIONARY'),
    (0x23, 'PITEXDICTIONARY'),
    (0x24, 'TOC'),
    (0x25, 'PRTSTDGLOBALDATA'),
    (0x26, 'ALTPIPE'),
    (0x27, 'PIPEDS'),
    (0x28, 'PATCHMESH'),
    (0x29, 'CHUNKGROUPSTART'),
    (0x2A, 'CHUNKGROUPEND'),
    (0x2B, 'UVANIMDICT'),
    (0x2C, 'COLLTREE'),
    (0x2D, 'ENVIRONMENT'),
    (0x2E, 'COREPLUGINIDMAX'),
)

TYPES_DICT = { id: name for id, name in TYPES }

sectypes = dict()
secnames = dict()

# for item in os.listdir('./img'):
    # filepath = './img/' + item

for item in conv().values():
    filepath = item = item['dff']

    if not os.path.isfile(filepath) and not item.lower().endswith('.dff'):
        continue

    model = DFF(filepath)

    if model._sectype not in sectypes:
        sectypes[model._sectype] = 1
        secnames[model._sectype] = [ item ]
    else:
        sectypes[model._sectype] += 1
        if len(secnames[model._sectype]) <= 5:
            secnames[model._sectype].append(item)

for id, count in sectypes.items():
    print(TYPES_DICT[id] if id in TYPES_DICT else hex(id), count, *[ file for file in secnames[id] ])
'''

'''
В большинстве случаев, первой должна идти CLUMP

CLUMP
    HEADER
        uint: sectionType
        uint: contentSize
        uint: version
    END
    STRUCT
        HEADER ... END
        int: atomic_count            
        if HEADER.version > 0x33000:
            int: lightCount
            int: cameraCount
    END
    FRAMELIST
        HEADER ... END
        STRUCT
            int: frameCount
            for i -> frameCount:
                mat3<float>: rotation
                vec3<float>: position
                int: parent
                int: flags/alignment (?, not used)
        END
        for i -> frameCount:
            EXTENSION
                HEADER ... END
                EXTENSION_ENTRY
                    HEADER ... END
                    string: frameName
                END
            END
    END
    GEOMETRYLIST
        HEADER ... END
        STRUCT
            int: geomCount
        END        
        for i -> geomCount:
            GEOMETRY
                HEADER ... END
                STRUCT
                    ushort: flags, 
                    ushort: texCount
                    int: triCount
                    int: vertCount
                    int: morphCount
                    if HEADER.version < 0x34001:
                        float surfAmbient
                        float surfSpecular
                        float surfDiffuse
                    if flags & PRELIT:
                        for i -> vertCount:
                            vec4<uchar> color
                    for i -> vertCount:
                        vec2<float> uv
                    if texCount > 1:                            
                        for i -> vertCount:
                            vec2<float> uv_env
                    if texCount > 2:
                        for i -> (texCount - 2):
                            for j in range(vertCount):
                                vec2<float> uv_extra
                    for i -> triCount:
                        ushort vert2index
                        ushort vert1index
                        ushort matId
                        ushort vert0index
                    for i -> morphCount:
                        float bx
                        float by
                        float bz
                        float br
                        int hasVerts
                        int hasNormals    

                        if hasVerts:
                            for j -> vertCount:
                                vec3<float> coords
                        if hasNormals:
                            for j -> vertCount:
                                vec3<float> normal
                END
                MATERIALLIST
                    HEADER ... END
                    STRUCT
                        int matCount
                        for i -> matCount:
                            int junk
                    END                    
                    for i -> matCount:
                        MATERIAL
                            HEADER ... END
                            STRUCT
                                uint flags
                                vec4<uchar> col
                                int unk
                                int textured
                                float ambient
                                float specular
                                float diffuse
                            END
                            if textured:
                                TEXTURE
                                    HEADER ... END
                                    STRUCT
                                        ushort flags
                                        ushort unk
                                    END
                                    STRING
                                        HEADER ... END
                                        string texName
                                    END
                                    STRING
                                        HEADER ... END
                                        string alphaName
                                    END
                                    EXTENSION
                                        HEADER ... END
                                        EXTENSION_ENTRY
                                            HEADER ... END
                                            ???
                                        END
                                    END
                                END-TEXTURE
                            EXTENSION
                                HEADER ... END
                                EXTENSION_ENTRY
                                    HEADER ... END
                                    ???
                                END
                            END
                        END-MATERIAL
                END-MATERIALLIST
                EXTENSION
                    HEADER ... END
                    EXTENSION_ENTRY
                        HEADER ... END
                        ???
                    END
                END
            END-GEOMETRY
    END-GEOMETRYLIST    
    for i -> atomicCount:
        ATOMIC
            HEADER ... END
            STRUCT
                int frameIndex
                int geomIndex
                uchar flags
                uchar unk
                uchar unk
                uchar unk
                int unk
            END
            EXTENSION
                HEADER ... END
                EXTENSION_ENTRY
                    HEADER ... END
                    ???
                END
            END
        END    
    EXTENSION
        HEADER ... END
        EXTENSION_ENTRY
            HEADER ... END
            ???
        END
    END
END-CLUMP


UVANIMDICT
    HEADER ... END
    STRUCT
        uint animationCount
    END
    for i -> animationCount:
        ANIMANIMATION
            HEADER ... END
            
        
        END-ANIMANIMATION
END-UVANIMDICT

'''


# model = DFF('./img/a51_outbldgs.dff')