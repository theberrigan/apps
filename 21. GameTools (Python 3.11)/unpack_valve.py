# Valve's Games Extractor

import os, sys, struct, json, zlib, lzma, hashlib
from enum import Enum, IntEnum, unique

GAME_DIR = r'G:\Steam\steamapps\common\Half-Life 2\hl2'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SIGNATURE_MDL = b'IDST'


class VirtualReader:
    def __init__ (self, data, name=None):
        self.buffer = data
        self.size = len(data)
        self.cursor = 0
        self.name = name

    def __del__ (self):
        self.close()

    def __enter__ (self):
        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def open (self):
        pass

    def close (self):
        self.buffer = None
        self.size = 0
        self.cursor = 0

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


def readJson (filePath, defaultValue=None):
    if not os.path.isfile(filePath):
        return defaultValue

    with open(filePath, 'rb') as f:
        try:
            return json.loads(f.read().decode('utf-8').strip())
        except:
            print('Can\'t parse json file:', filePath)
            return defaultValue


def writeJson (filePath, data):
    with open(filePath, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


def md5 (data):
    if data is None:
        return None

    if not isinstance(data, bytes):
        data = str(data).encode('utf-8')

    return hashlib.md5(data).hexdigest().lower()


def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])


def formatSize (size):
    if size >= (1024 ** 3):
        return '{:.1f} Gb'.format(size / (1024 ** 3))
    elif size >= (1024 ** 2):
        return '{:.1f} Mb'.format(size / (1024 ** 2))
    elif size >= 1024:
        return '{:.1f} Kb'.format(size / 1024)
    else:
        return '{} B'.format(size)


def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items


def readNullString (descriptor):
    buff = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'\x00':
            break

        buff += byte

    return buff.decode('utf-8')


def readAlignedString (reader, alignment=4):
    buff = b''

    while True:
        chunk = reader.read(alignment)
        buff += chunk

        if b'\x00' in chunk:
            return buff[:buff.index(b'\x00')].decode('utf-8')

def decodeString (data):    
    if b'\x00' in data:
        data = data[:data.index(b'\x00')]

    return data.decode('utf-8')


def decompressZlib (data):
    decompress = zlib.decompressobj()
    data = decompress.decompress(data)
    data += decompress.flush()

    return data


def decompressLZMA (data):
    return lzma.decompress(data)


# ------------------------------------------------------------------------------------

MAX_NUM_LODS = 8


class FlexCtrlRemapType:
    PASSTHRU = 0
    TWOWAY   = 1  # Control 0 -> ramps from 1-0 from 0->0.5. Control 1 -> ramps from 0-1 from 0.5->1
    NWAY     = 2  # StepSize = 1 / (control count-1) Control n -> ramps from 0-1-0 from (n-1)*StepSize to n*StepSize to (n+1)*StepSize. A second control is needed to specify amount to use 
    EYELID   = 3


class keepCursor:
    def __init__ (self, reader):
        self.reader = reader
        self.cursor = reader.tell()

    def __enter__ (self):
        self.cursor = self.reader.tell()

    def __exit__ (self, *args, **kwargs):
        self.reader.seek(self.cursor)


def readVec3 (reader):
    return readStruct('<3f', reader)


def readQuaternion (reader):
    return readStruct('<4f', reader)


def readMat3x4 (reader):
    return readStruct('<12f', reader)


# mstudiobone_t
def readBone (reader):
    startOffset = reader.tell()

    nameOffset        = readStruct('<i', reader)   # int         sznameindex
    parent            = readStruct('<i', reader)   # int         parent
    boneController    = readStruct('<6i', reader)  # int         bonecontroller[6]
    pos               = readVec3(reader)           # Vector      pos
    quat              = readQuaternion(reader)     # Quaternion  quat
    rot               = readVec3(reader)           # RadianEuler rot
    posScale          = readVec3(reader)           # Vector      posscale
    rotScale          = readVec3(reader)           # Vector      rotscale
    poseToBone        = readMat3x4(reader)         # matrix3x4_t poseToBone
    qAlignment        = readQuaternion(reader)     # Quaternion  qAlignment
    flags             = readStruct('<i', reader)   # int         flags
    procType          = readStruct('<i', reader)   # int         proctype
    procOffset        = readStruct('<i', reader)   # int         procindex
    physicsBone       = readStruct('<i', reader)   # int         physicsbone
    surfacePropOffset = readStruct('<i', reader)   # int         surfacepropidx
    contents          = readStruct('<i', reader)   # int         contents
    _unused           = readStruct('<8i', reader)  # int         unused[8]

    endOffset = reader.tell()

    data = {
        'name':              '',
        'parent':            parent,
        'boneController':    boneController,
        'pos':               pos,
        'quat':              quat,
        'rot':               rot,
        'posScale':          posScale,
        'rotScale':          rotScale,
        'poseToBone':        poseToBone,
        'qAlignment':        qAlignment,
        'flags':             flags,
        'procType':          procType,
        'procOffset':        procOffset,
        'physicsBone':       physicsBone,
        'surfacePropOffset': surfacePropOffset,
        'contents':          contents,
    }

    if nameOffset:
        reader.seek(startOffset + nameOffset)

        data['name'] = readNullString(reader)

        reader.seek(endOffset)

    return data


# mstudiobbox_t
def readHitbox (reader):
    startOffset = reader.tell()

    bone       = readStruct('<i', reader)   # int    bone
    group      = readStruct('<i', reader)   # int    group
    bbmin      = readVec3(reader)           # Vector bbmin
    bbmax      = readVec3(reader)           # Vector bbmax
    nameOffset = readStruct('<i', reader)   # int    szhitboxnameindex
    _unused    = readStruct('<8i', reader)  # int    unused[8]

    endOffset = reader.tell()

    data = {
        'name':       '',
        'bone':       bone,
        'group':      group,
        'bbmin':      bbmin,
        'bbmax':      bbmax,
    }

    if nameOffset:
        reader.seek(startOffset + nameOffset)

        data['name'] = readNullString(reader)

        reader.seek(endOffset)

    return data


# mstudiohitboxset_t
def readHitboxSet (reader):
    startOffset = reader.tell()

    nameOffset   = readStruct('<i', reader)  # + int sznameindex
    hitboxCount  = readStruct('<i', reader)  # + int numhitboxes
    hitboxOffset = readStruct('<i', reader)  # + int hitboxindex

    endOffset = reader.tell()

    data = {
        'name':     '',
        'hitboxes': []
    }

    if nameOffset:
        reader.seek(startOffset + nameOffset)

        data['name'] = readNullString(reader)

        reader.seek(endOffset)

    reader.seek(startOffset + hitboxOffset)

    data['hitboxes'] = [ readHitbox(reader) for _ in range(hitboxCount) ]

    reader.seek(endOffset)

    return data


# mstudiomovement_t
def readMovement (reader):
    return {
        'endFrame': readStruct('<i', reader),  # + int    endframe
        'flags':    readStruct('<i', reader),  # + int    motionflags
        'v0':       readStruct('<f', reader),  # + float  v0
        'v1':       readStruct('<f', reader),  # + float  v1
        'angle':    readStruct('<f', reader),  # + float  angle
        'vector':   readVec3(reader),          # + Vector vector
        'position': readVec3(reader),          # + Vector position
    }


'''
struct mstudioanim_valueptr_t
{
    short   offset[3];
    inline mstudioanimvalue_t *pAnimvalue( int i ) const { 
        if (offset[i] > 0) 
            return  (mstudioanimvalue_t *)(((byte *)this) + offset[i]); 
        else 
            return NULL; 
    };
};
'''

# mstudioanim_valueptr_t
def readAnimValue (reader):
    startOffset = reader.tell()

    offsets = readStruct('<3h', reader)

    endOffset = reader.tell()

    items = []

    for offset in offsets:
        if offset > 0:
            reader.seek(startOffset + offset)
            value = readStruct('<h', reader)
            items.append({
                'value': value,
                'valid': (value >> 8) & 0xFF,
                'total': (value >> 0) & 0xFF,
            })
        else:
            items.append(None)

    reader.seek(endOffset)

    return items

# mstudioanim_t
def readAnim (reader):
    startOffset = reader.tell()

    data = {
        'bone':       readStruct('<B', reader),  # byte  bone
        'flags':      readStruct('<B', reader),  # byte  flags
        'nextOffset': readStruct('<h', reader),  # short nextoffset
    }

    endOffset = reader.tell()

    reader.seek(endOffset)
    rotV = readAnimValue(reader)

    reader.seek(endOffset)

    return data

'''

struct mstudioanim_t
{
    byte                bone
    byte                flags
    inline byte             *pData( void ) const { return (((byte *)this) + sizeof( struct mstudioanim_t )); };
    inline mstudioanim_valueptr_t   *pRotV( void ) const { return (mstudioanim_valueptr_t *)(pData()); };
    inline mstudioanim_valueptr_t   *pPosV( void ) const { return (mstudioanim_valueptr_t *)(pData()) + ((flags & STUDIO_ANIM_ANIMROT) != 0); };

    // valid if animation unvaring over timeline
    inline Quaternion48     *pQuat48( void ) const { return (Quaternion48 *)(pData()); };
    inline Quaternion64     *pQuat64( void ) const { return (Quaternion64 *)(pData()); };
    inline Vector48         *pPos( void ) const { return (Vector48 *)(pData() + ((flags & STUDIO_ANIM_RAWROT) != 0) * sizeof( *pQuat48() ) + ((flags & STUDIO_ANIM_RAWROT2) != 0) * sizeof( *pQuat64() ) ); };

    short               nextoffset;
    inline mstudioanim_t    *pNext( void ) const { if (nextoffset != 0) return  (mstudioanim_t *)(((byte *)this) + nextoffset); else return NULL; };
};
'''

# mstudioanimdesc_t
def readAnimDesc (reader):
    startOffset = reader.tell()

    basePtr               = readStruct('<i', reader)   # - int   baseptr
    nameOffset            = readStruct('<i', reader)   # + int   sznameindex
    fps                   = readStruct('<f', reader)   # + float fps
    flags                 = readStruct('<i', reader)   # + int   flags
    frameCount            = readStruct('<i', reader)   # + int   numframes
    movementCount         = readStruct('<i', reader)   # ~ int   nummovements
    movementsOffset       = readStruct('<i', reader)   # ~ int   movementindex
    _unused               = readStruct('<6i', reader)  # - int   unused1[6]
    animBlock             = readStruct('<i', reader)   # int   animblock
    animOffset            = readStruct('<i', reader)   # int   animindex
    ikRuleCount           = readStruct('<i', reader)   # int   numikrules
    ikRuleOffset          = readStruct('<i', reader)   # int   ikruleindex
    animBlockIkRuleOffset = readStruct('<i', reader)   # int   animblockikruleindex
    localHierarchyCount   = readStruct('<i', reader)   # int   numlocalhierarchy
    localHierarchyOffset  = readStruct('<i', reader)   # int   localhierarchyindex
    sectionOffset         = readStruct('<i', reader)   # int   sectionindex
    sectionFrames         = readStruct('<i', reader)   # int   sectionframes
    zeroFrameSpan         = readStruct('<h', reader)   # short zeroframespan
    zeroFrameCount        = readStruct('<h', reader)   # short zeroframecount
    zeroFramesOffset      = readStruct('<i', reader)   # int   zeroframeindex
    zeroFrameStallTime    = readStruct('<f', reader)   # float zeroframestalltime

    endOffset = reader.tell()

    data = {
        'name':      '',
        'movements': []
    }  

    # ----------------------------------------------------------

    if nameOffset:
        reader.seek(startOffset + nameOffset)

        data['name'] = readNullString(reader)

        reader.seek(endOffset)

    # ----------------------------------------------------------

    reader.seek(startOffset + movementsOffset)

    data['movements'] = [ readMovement(reader) for _ in range(movementCount) ]

    # ----------------------------------------------------------

    if animBlock == -1:
        anim = None
    elif animBlock == 0:
        reader.seek(startOffset + animOffset)
        anim = readAnim(reader)
    else:
        anim = None
        # TODO:
        # byte *pAnimBlock = pStudiohdr()->GetAnimBlock( block );
        # if ( pAnimBlock ) { return (mstudioanim_t *)(pAnimBlock + index); }
        # return (mstudioanim_t *)NULL;


    print(anim) 

    return data


# [COMPLETED]
# mstudiolinearbone_t
def readLinearBones (reader):
    startOffset = reader.tell()

    boneCount         = readStruct('<i', reader)   # + int numbones
    flagsOffset       = readStruct('<i', reader)   # + int flagsindex
    parentsOffset     = readStruct('<i', reader)   # + int parentindex
    positionsOffset   = readStruct('<i', reader)   # + int posindex
    quatsOffset       = readStruct('<i', reader)   # + int quatindex
    rotsOffset        = readStruct('<i', reader)   # + int rotindex
    poseToBonesOffset = readStruct('<i', reader)   # + int posetoboneindex
    posScalesOffset   = readStruct('<i', reader)   # + int posscaleindex
    rotScalesOffset   = readStruct('<i', reader)   # + int rotscaleindex
    qAlignmentsOffset = readStruct('<i', reader)   # + int qalignmentindex
    _unused           = readStruct('<6i', reader)  # + int unused[6]

    flags       = []
    parents     = []
    positions   = []
    quats       = []
    rots        = []
    poseToBones = []
    posScales   = []
    rotScales   = []
    qAlignments = []

    toRead = [
        (flagsOffset,       flags,       lambda: readStruct('<i', reader)),
        (parentsOffset,     parents,     lambda: readStruct('<i', reader)),
        (positionsOffset,   positions,   lambda: readVec3(reader)),
        (quatsOffset,       quats,       lambda: readQuaternion(reader)),
        (rotsOffset,        rots,        lambda: readVec3(reader)),
        (poseToBonesOffset, poseToBones, lambda: readMat3x4(reader)),
        (posScalesOffset,   posScales,   lambda: readVec3(reader)),
        (rotScalesOffset,   rotScales,   lambda: readVec3(reader)),
        (qAlignmentsOffset, qAlignments, lambda: readQuaternion(reader)),
    ]

    for offset, acc, fn in toRead:
        reader.seek(startOffset + offset)

        for _ in range(boneCount):
            acc.append(fn())

    bones = []

    for i in range(boneCount):
        bones.append({
            'parent':     parents[i],
            'pos':        positions[i],
            'quat':       quats[i],
            'rot':        rots[i],
            'posScale':   posScales[i],
            'rotScale':   rotScales[i],
            'poseToBone': poseToBones[i],
            'qAlignment': qAlignments[i],
            'flags':      flags[i],
        })

    return bones


# [COMPLETED, NOT_TESTED]
# mstudiosrcbonetransform_t
def readSrcBoneTransform (reader):
    startOffset = reader.tell()

    nameOffset    = readStruct('<i', reader)  # int         sznameindex
    preTransform  = readMat3x4(reader)        # matrix3x4_t pretransform 
    postTransform = readMat3x4(reader)        # matrix3x4_t posttransform

    data = {
        'name':          '',
        'preTransform':  preTransform,
        'postTransform': postTransform
    }

    with keepCursor(reader):
        if nameOffset:
            reader.seek(startOffset + nameOffset)
            data['name'] = readNullString(reader)

    return data


# [COMPLETED, NOT_TESTED]
# mstudioboneflexdrivercontrol_t
def readBoneFlexDriverControl (reader):
    startOffset = reader.tell()

    boneComponent  = readStruct('<i', reader)  # ~ int m_nBoneComponent        // Bone component that drives flex, StudioBoneFlexComponent_t
    flexCtrlOffset = readStruct('<i', reader)  # ~ int m_nFlexControllerIndex  // Flex controller to drive
    minValue       = readStruct('<f', reader)  # ~ float m_flMin               // Min value of bone component mapped to 0 on flex controller
    maxValue       = readStruct('<f', reader)  # ~ float m_flMax               // Max value of bone component mapped to 1 on flex controller

    return {
        'boneComponent':  boneComponent,
        'flexCtrlOffset': flexCtrlOffset,
        'minValue':       minValue,
        'maxValue':       maxValue,
    }


# mstudioboneflexdriver_t
def readBoneFlexDriver (reader):
    startOffset = reader.tell()

    boneOffset     = readStruct('<i', reader)   # - int m_nBoneIndex     // Bone to drive flex controller (const mstudiobone_t *pStudioBone = pStudioHdr->pBone( pBoneFlexDriver->m_nBoneIndex ))
    controlCount   = readStruct('<i', reader)   # ~ int m_nControlCount  // Number of flex controllers being driven
    controlsOffset = readStruct('<i', reader)   # ~ int m_nControlIndex  // Index into data where controllers are (relative to this)
    _unused        = readStruct('<3i', reader)  # + int unused[3]

    data = {
        'boneOffset': boneOffset,
        'controls':   []
    }

    with keepCursor(reader):
        reader.seek(startOffset + controlsOffset)
        data['controls'] = [ readBoneFlexDriverControl(reader) for _ in range(controlCount) ]

    print(data['controls'])

    return data


# studiohdr2_t
def readHeader2 (reader):
    startOffset = reader.tell()

    srcBoneTransformCount    = readStruct('<i', reader)    # ~ int   numsrcbonetransform
    srcBoneTransformsOffset  = readStruct('<i', reader)    # ~ int   srcbonetransformindex
    illumPosAttachmentOffset = readStruct('<i', reader)    # - int   illumpositionattachmentindex
    maxEyeDeflection         = readStruct('<f', reader)    # + float flMaxEyeDeflection
    linearBonesOffset        = readStruct('<i', reader)    # + int   linearboneindex
    nameOffset               = readStruct('<i', reader)    # + int   sznameindex
    boneFlexDriverCount      = readStruct('<i', reader)    # ~ int   m_nBoneFlexDriverCount
    boneFlexDriversOffset    = readStruct('<i', reader)    # ~ int   m_nBoneFlexDriverIndex
    _unused                  = readStruct('<56i', reader)  # + int   reserved[56]

    data = {
        'name':              '',
        'maxEyeDeflection':  (maxEyeDeflection or 0.866),
        'linearBones':       [],
        'srcBoneTransforms': [],
        'boneFlexDrivers':   [],
    }

    with keepCursor(reader):
        if nameOffset:
            reader.seek(startOffset + nameOffset)
            data['name'] = readNullString(reader)

        reader.seek(startOffset + linearBonesOffset)
        data['linearBones'] = readLinearBones(reader)

        reader.seek(startOffset + srcBoneTransformsOffset)
        data['srcBoneTransforms'] = [ readSrcBoneTransform(reader) for _ in range(srcBoneTransformCount) ]

        reader.seek(startOffset + boneFlexDriversOffset)
        data['boneFlexDrivers'] = [ readBoneFlexDriver(reader) for _ in range(boneFlexDriverCount) ]

    return data


# mstudiotexture_t
def readTexture (reader):
    startOffset = reader.tell()

    nameOffset     = readStruct('<i', reader)    # int        sznameindex
    flags          = readStruct('<i', reader)    # int        flags
    used           = readStruct('<i', reader)    # int        used
    _unused        = readStruct('<i', reader)    # int        unused1
    material       = readStruct('<i', reader)    # IMaterial* material
    clientMaterial = readStruct('<i', reader)    # void*      clientmaterial
    _unused        = readStruct('<10i', reader)  # int        unused[10]

    data = {
        'name': '',
        'flags': flags,
        'used': used,
        'material': material,
        'clientMaterial': clientMaterial,
    }

    with keepCursor(reader):
        if nameOffset:
            reader.seek(startOffset + nameOffset)
            data['name'] = readNullString(reader)

    return data


# mstudiobodyparts_t
def readBodyPart (reader):
    startOffset = reader.tell()

    nameOffset   = readStruct('<i', reader)  # int sznameindex
    modelCount   = readStruct('<i', reader)  # int nummodels
    base         = readStruct('<i', reader)  # int base
    modelsOffset = readStruct('<i', reader)  # int modelindex  // index into models array

    data = {
        'name': '',
        'base': base,
        'models': []
    }

    with keepCursor(reader):
        if nameOffset:
            reader.seek(startOffset + nameOffset)
            data['name'] = readNullString(reader)

        reader.seek(startOffset + modelsOffset)
        data['models'] = [ readModel(reader)  for _ in range(modelCount) ]

    return data


'''
inline char * const pszName( void ) const { return ((char *)this) + sznameindex; }
inline mstudiomodel_t *pModel( int i ) const { return (mstudiomodel_t *)(((byte *)this) + modelindex) + i; };
'''

# mstudiomodel_t
def readModel (reader):
    startOffset = reader.tell()

    name              = decodeString(readStruct('<64s', reader))  # char  name[64]
    modelType         = readStruct('<i', reader)                  # int   type
    boundingRadius    = readStruct('<f', reader)                  # float boundingradius
    meshCount         = readStruct('<i', reader)                  # int   nummeshes
    meshesOffset      = readStruct('<i', reader)                  # int   meshindex
    vertexCount       = readStruct('<i', reader)                  # int   numvertices
    verticesOffset    = readStruct('<i', reader)                  # int   vertexindex
    tangentsOffset    = readStruct('<i', reader)                  # int   tangentsindex
    attachmentCount   = readStruct('<i', reader)                  # int   numattachments
    attachmentsOffset = readStruct('<i', reader)                  # int   attachmentindex
    eyeBallCount      = readStruct('<i', reader)                  # int   numeyeballs
    eyeBallsOffset    = readStruct('<i', reader)                  # int   eyeballindex
    vertices          = readModelVertices(reader)                 # mstudio_modelvertexdata_t vertexdata
    _unused           = readStruct('<8i', reader)                 # int   unused[8]

    data = {
        'name': name,
        'type': modelType,
        'boundingRadius': boundingRadius,
        'meshes': [],
    }

    with keepCursor(reader):
        reader.seek(startOffset + meshesOffset)
        data['meshes'] = [ readMesh(reader)  for _ in range(meshCount) ]

    return data

'''
// These functions are defined in application-specific code:
const vertexFileHeader_t            *CacheVertexData(           void *pModelData );

// Access thin/fat mesh vertex data (only one will return a non-NULL result)
const mstudio_modelvertexdata_t     *GetVertexData(     void *pModelData = NULL );
const thinModelVertices_t           *GetThinVertexData( void *pModelData = NULL );

inline  mstudioeyeball_t *pEyeball( int i ) { return (mstudioeyeball_t *)(((byte *)this) + eyeballindex) + i; };
'''

# mstudio_modelvertexdata_t
def readModelVertices (reader):
    startOffset = reader.tell()

    pVertexData  = readStruct('<i', reader)  # const void* pVertexData
    pTangentData = readStruct('<i', reader)  # const void* pTangentData

    data = {}

    return data

    # Vector              *Position( int i ) const;
    # Vector              *Normal( int i ) const;
    # Vector4D            *TangentS( int i ) const;
    # Vector2D            *Texcoord( int i ) const;
    # mstudioboneweight_t *BoneWeights( int i ) const;
    # mstudiovertex_t     *Vertex( int i ) const;
    # bool                HasTangentData( void ) const;
    # int                 GetGlobalVertexIndex( int i ) const;
    # int                 GetGlobalTangentIndex( int i ) const;


# mstudiomesh_t
def readMesh (reader):
    startOffset = reader.tell()

    material       = readStruct('<i', reader)   # + int    material
    modelOffset    = readStruct('<i', reader)   # + int    modelindex     // back reference to this mesh's parent model, don't read to avoid recursion
    vertexCount    = readStruct('<i', reader)   # - int    numvertices    // number of unique vertices/normals/texcoords
    verticesOffset = readStruct('<i', reader)   # - int    vertexoffset   // offset not in bytes, but in items (mstudiovertex_t)
    flexCount      = readStruct('<i', reader)   # + int    numflexes      // vertex animation
    flexesOffset   = readStruct('<i', reader)   # + int    flexindex
    materialType   = readStruct('<i', reader)   # + int    materialtype
    materialParam  = readStruct('<i', reader)   # + int    materialparam
    meshId         = readStruct('<i', reader)   # + int    meshid         // a unique ordinal for this mesh
    center         = readVec3(reader)           # + Vector center
    vertices       = readMashVertices(reader)   # + mstudio_meshvertexdata_t vertexdata
    _unused        = readStruct('<8i', reader)  # + int    unused[8]

    data = {
        'material': material,
        'vertices': vertices,
        'flexes':   [],
    }

    with keepCursor(reader):
        reader.seek(startOffset + flexesOffset)
        data['flexes'] = [ readFlex(reader)  for _ in range(flexCount) ]

    return data

    # // Access thin/fat mesh vertex data (only one will return a non-NULL result)
    # const mstudio_meshvertexdata_t  *GetVertexData(     void *pModelData = NULL );
    # const thinModelVertices_t       *GetThinVertexData( void *pModelData = NULL );


# mstudio_meshvertexdata_t
def readMashVertices (reader):
    startOffset = reader.tell()

    # indirection to this mesh's model's vertex data
    pModelVertexData = readStruct('<i', reader)                   # const mstudio_modelvertexdata_t *modelvertexdata  
    # used for fixup calcs when culling top level lods expected number of mesh verts at desired lod
    lodVertexCount   = readStruct(f'<{ MAX_NUM_LODS }i', reader)  # int numLODVertexes[MAX_NUM_LODS]

    data = {}

    return data

    # Vector              *Position( int i ) const;
    # Vector              *Normal( int i ) const;
    # Vector4D            *TangentS( int i ) const;
    # Vector2D            *Texcoord( int i ) const;
    # mstudioboneweight_t *BoneWeights( int i ) const;
    # mstudiovertex_t     *Vertex( int i ) const;
    # bool                HasTangentData( void ) const;
    # int                 GetModelVertexIndex( int i ) const;
    # int                 GetGlobalVertexIndex( int i ) const;


# mstudioflex_t
def readFlex (reader):
    startOffset = reader.tell()

    flexDesc       = readStruct('<i', reader)   # int   flexdesc       // input value
    target0        = readStruct('<f', reader)   # float target0        // zero
    target1        = readStruct('<f', reader)   # float target1        // one
    target2        = readStruct('<f', reader)   # float target2        // one
    target3        = readStruct('<f', reader)   # float target3        // zero
    vertexCount    = readStruct('<i', reader)   # int   numverts
    verticesOffset = readStruct('<i', reader)   # int   vertindex
    flexPair       = readStruct('<i', reader)   # int   flexpair       // second flex desc
    flexAnimType   = readStruct('<B', reader)   # byte  vertanimtype   // See StudioVertAnimType_t
    _unused        = readStruct('<3B', reader)  # byte  unusedchar[3]
    _unused        = readStruct('<6i', reader)  # int   unused[6]

    data = {}

    return data

    # mstudiovertanim_t *pVertanim( int i ) const { Assert( vertanimtype == STUDIO_VERT_ANIM_NORMAL ); return (mstudiovertanim_t *)(((byte *)this) + vertindex) + i; };
    # mstudiovertanim_wrinkle_t *pVertanimWrinkle( int i ) const { Assert( vertanimtype == STUDIO_VERT_ANIM_WRINKLE ); return  (mstudiovertanim_wrinkle_t *)(((byte *)this) + vertindex) + i; };
    # byte *pBaseVertanim( ) const { return ((byte *)this) + vertindex; };
    # int VertAnimSizeBytes() const { return ( vertanimtype == STUDIO_VERT_ANIM_NORMAL ) ? sizeof(mstudiovertanim_t) : sizeof(mstudiovertanim_wrinkle_t); }


# mstudiomouth_t
def readMouth (reader):
    startOffset = reader.tell()

    bone     = readStruct('<i', reader)  # int    bone
    forward  = readVec3(reader)          # Vector forward
    flexDesc = readStruct('<i', reader)  # int    flexdesc

    return {
        'bone': bone,
        'forward': forward,
        'flexDesc': flexDesc,
    }


# mstudioposeparamdesc_t
def readPosParamDesc (reader):
    startOffset = reader.tell()

    nameOffset = readStruct('<i', reader)  # int   sznameindex
    flags      = readStruct('<i', reader)  # int   flags  // ????
    start      = readStruct('<f', reader)  # float start  // starting value
    end        = readStruct('<f', reader)  # float end    // ending value
    loop       = readStruct('<f', reader)  # float loop   // looping range, 0 for no looping, 360 for rotations, etc.

    data = {
        'name': '',
        'flags': flags,
        'start': start,
        'end': end,
        'loop': loop,
    }

    with keepCursor(reader):
        if nameOffset:
            reader.seek(startOffset + nameOffset)
            data['name'] = readNullString(reader)

    return data


# mstudiomodelgroup_t
def readModelGroup (reader):
    startOffset = reader.tell()

    labelOffset = readStruct('<i', reader)  # int szlabelindex
    nameOffset  = readStruct('<i', reader)  # int sznameindex

    data = {
        'label': '',
        'name': '',
    }

    with keepCursor(reader):
        if labelOffset:
            reader.seek(startOffset + labelOffset)
            data['label'] = readNullString(reader)

        if nameOffset:
            reader.seek(startOffset + nameOffset)
            data['name'] = readNullString(reader)

    return data


# [COMPLETED]
# mstudioflexcontrollerui_t
def readFlexCtrlUI (reader):
    startOffset = reader.tell()

    nameOffset = readStruct('<i', reader)        # int  sznameindex
    offset0    = readStruct('<i', reader)        # int  szindex0
    offset1    = readStruct('<i', reader)        # int  szindex1
    offset2    = readStruct('<i', reader)        # int  szindex2
    remapType  = readStruct('<B', reader)        # byte remaptype  // See the FlexControllerRemapType_t enum
    isStereo   = bool(readStruct('<B', reader))  # bool stereo     // Is this a stereo control?
    _unused    = readStruct('<2B', reader)       # byte unused[2]

    isNWay = remapType == FlexCtrlRemapType.NWAY

    data = {
        'name': '',
        'remapType': remapType,
        'isStereo': isStereo,
        'ctrl': None,
        'leftCtrl': None,
        'rightCtrl': None,
        'nWayCtrl': None,
        'ctrlCount': (2 if isStereo else 1) + (1 if isNWay else 0)
    }

    with keepCursor(reader):
        if nameOffset:
            reader.seek(startOffset + nameOffset)
            data['name'] = readNullString(reader)

        if not isStereo:
            reader.seek(startOffset + offset0)
            data['ctrl'] = readFlexCtrl(reader)

        if isStereo:
            reader.seek(startOffset + offset0)
            data['leftCtrl'] = readFlexCtrl(reader)

        if isStereo:
            reader.seek(startOffset + offset1)
            data['rightCtrl'] = readFlexCtrl(reader)

        if isNWay:
            reader.seek(startOffset + offset2)
            data['nWayCtrl'] = readFlexCtrl(reader)

    return data


# [COMPLETED]
# mstudioflexcontroller_t
def readFlexCtrl (reader):
    startOffset = reader.tell()

    typeOffset    = readStruct('<i', reader)  # int   sztypeindex
    nameOffset    = readStruct('<i', reader)  # int   sznameindex
    localToGlobal = readStruct('<i', reader)  # int   localToGlobal  // remapped at load time to master list
    minValue      = readStruct('<f', reader)  # float min
    maxValue      = readStruct('<f', reader)  # float max

    data = {
        'type': '',
        'name': '',
        'localToGlobal': localToGlobal,
        'minValue': minValue,
        'maxValue': maxValue,
    }

    with keepCursor(reader):
        if typeOffset:
            reader.seek(startOffset + typeOffset)
            data['type'] = readNullString(reader)

        if nameOffset:
            reader.seek(startOffset + nameOffset)
            data['name'] = readNullString(reader)

    return data


# studiohdr_t
def readMDL (filePath):
    if not filePath:
        return

    if not os.path.isfile(filePath):
        raise OSError(f'File doesn\'t exist: { filePath }')

    with open(filePath, 'rb') as f:
        reader = VirtualReader(f.read())

    signature = reader.read(4)  # int id

    assert signature == SIGNATURE_MDL, f'File is not an MDL: { filePath }'

    version                 = readStruct('<i', reader)  # + int    version
    checksum                = readStruct('<i', reader)  # + int    checksum
    name                    = decodeString(readStruct('<64s', reader))  # + char name[64]
    dataSize                = readStruct('<i', reader)  # + int    length
    eyePos                  = readVec3(reader)          # + Vector eyeposition
    illumPos                = readVec3(reader)          # + Vector illumposition
    hullMin                 = readVec3(reader)          # + Vector hull_min
    hullMax                 = readVec3(reader)          # + Vector hull_max
    viewBBoxMin             = readVec3(reader)          # + Vector view_bbmin
    viewBBoxMax             = readVec3(reader)          # + Vector view_bbmax
    flags                   = readStruct('<I', reader)  # + int    flags
    boneCount               = readStruct('<i', reader)  # + int    numbones
    bonesOffset             = readStruct('<i', reader)  # + int    boneindex
    boneCtrlCount           = readStruct('<i', reader)  # - int    numbonecontrollers
    boneCtrlsOffset         = readStruct('<i', reader)  # - int    bonecontrollerindex
    hitboxSetCount          = readStruct('<i', reader)  # + int    numhitboxsets
    hitboxSetsOffset        = readStruct('<i', reader)  # + int    hitboxsetindex
    localAnimCount          = readStruct('<i', reader)  # - int    numlocalanim
    localAnimsOffset        = readStruct('<i', reader)  # - int    localanimindex
    localSeqCount           = readStruct('<i', reader)  # - int    numlocalseq
    localSeqsOffset         = readStruct('<i', reader)  # - int    localseqindex
    activityListVersion     = readStruct('<i', reader)  # + int    activitylistversion
    eventsIndexed           = readStruct('<i', reader)  # + int    eventsindexed
    textureCount            = readStruct('<i', reader)  # + int    numtextures
    texturesOffset          = readStruct('<i', reader)  # + int    textureindex
    textureDirCount         = readStruct('<i', reader)  # + int    numcdtextures
    textureDirsOffset       = readStruct('<i', reader)  # + int    cdtextureindex
    skinRefCount            = readStruct('<i', reader)  # + int    numskinref
    skinRefFamilyCount      = readStruct('<i', reader)  # - int    numskinfamilies
    skinRefsOffset          = readStruct('<i', reader)  # + int    skinindex
    bodyPartCount           = readStruct('<i', reader)  # int    numbodyparts
    bodyPartsOffset         = readStruct('<i', reader)  # int    bodypartindex
    attachmentCount         = readStruct('<i', reader)  # int    numlocalattachments
    attachmentsOffset       = readStruct('<i', reader)  # int    localattachmentindex
    localNodeCount          = readStruct('<i', reader)  # int    numlocalnodes
    localNodesOffset        = readStruct('<i', reader)  # int    localnodeindex
    localNodeNamesOffset    = readStruct('<i', reader)  # int    localnodenameindex
    flexDescCount           = readStruct('<i', reader)  # int    numflexdesc
    flexDescsOffset         = readStruct('<i', reader)  # int    flexdescindex
    flexCtrlCount           = readStruct('<i', reader)  # int    numflexcontrollers
    flexCtrlsOffset         = readStruct('<i', reader)  # int    flexcontrollerindex
    flexRuleCount           = readStruct('<i', reader)  # int    numflexrules
    flexRulesOffset         = readStruct('<i', reader)  # int    flexruleindex
    ikChainCount            = readStruct('<i', reader)  # int    numikchains
    ikChainsOffset          = readStruct('<i', reader)  # int    ikchainindex
    mouthCount              = readStruct('<i', reader)  # + int    nummouths
    mouthsOffset            = readStruct('<i', reader)  # + int    mouthindex
    localPosParamCount      = readStruct('<i', reader)  # + int    numlocalposeparameters
    localPosParamsOffset    = readStruct('<i', reader)  # + int    localposeparamindex
    surfacePropOffset       = readStruct('<i', reader)  # + int    surfacepropindex
    kvsOffset               = readStruct('<i', reader)  # int    keyvalueindex
    kvCount                 = readStruct('<i', reader)  # int    keyvaluesize
    ikLockCount             = readStruct('<i', reader)  # int    numlocalikautoplaylocks
    ikLocksOffset           = readStruct('<i', reader)  # int    localikautoplaylockindex
    mass                    = readStruct('<f', reader)  # + float  mass
    contents                = readStruct('<i', reader)  # + int    contents
    incModelCount           = readStruct('<i', reader)  # + int    numincludemodels
    incModelsOffset         = readStruct('<i', reader)  # + int    includemodelindex
    virtualModel            = readStruct('<i', reader)  # + void*  virtualModel
    animBlockNamesOffset    = readStruct('<i', reader)  # ? int    szanimblocknameindex
    animBlockCount          = readStruct('<i', reader)  # ? int    numanimblocks
    animBlocksOffset        = readStruct('<i', reader)  # ? int    animblockindex
    animBlockModel          = readStruct('<i', reader)  # + void*  animblockModel
    boneTableNamesOffset    = readStruct('<i', reader)  # - int    bonetablebynameindex
    vertexBase              = readStruct('<i', reader)  # + void*  pVertexBase
    offsetBase              = readStruct('<i', reader)  # + void*  pIndexBase
    constDirLightDot        = readStruct('<B', reader)  # + byte   constdirectionallightdot
    rootLod                 = readStruct('<B', reader)  # + byte   rootLOD
    allowedRootLodCount     = readStruct('<B', reader)  # + byte   numAllowedRootLODs
    _unused                 = readStruct('<B', reader)  # + byte   unused[1]
    _unused                 = readStruct('<i', reader)  # + int    unused4
    flexCtrlUICount         = readStruct('<i', reader)  # + int    numflexcontrollerui
    flexCtrlUIsOffset       = readStruct('<i', reader)  # + int    flexcontrolleruiindex
    vertAnimFixedPointScale = readStruct('<f', reader)  # + float  flVertAnimFixedPointScale
    _unused                 = readStruct('<i', reader)  # + int    unused3[1]
    header2Offset           = readStruct('<i', reader)  # + int    studiohdr2index
    _unused                 = readStruct('<i', reader)  # + int    unused2[1]

    header2 = None

    if header2Offset:
        reader.seek(header2Offset)
        header2 = readHeader2(reader)

    reader.seek(bonesOffset)
    bones = [ readBone(reader) for _ in range(boneCount) ]

    # TODO:
    # boneCtrlCount, boneCtrlOffset

    reader.seek(hitboxSetsOffset)
    hitboxSets = [ readHitboxSet(reader) for _ in range(hitboxSetCount) ]

    # TODO:
    # reader.seek(localAnimsOffset)
    # localAnims = [ readAnimDesc(reader) for _ in range(localAnimCount) ]

    reader.seek(texturesOffset)
    textures = [ readTexture(reader) for _ in range(textureCount) ]

    reader.seek(textureDirsOffset)
    textureDirs = []

    for _ in range(textureDirCount):
        pathOffset = readStruct('<i', reader)

        with keepCursor(reader):
            reader.seek(pathOffset)
            textureDirs.append(readNullString(reader))

    reader.seek(skinRefsOffset)
    skinRefs = [ readStruct('<h', reader) for _ in range(skinRefCount) ]

    reader.seek(bodyPartsOffset)
    bodyParts = [ readBodyPart(reader) for _ in range(bodyPartCount) ]

    reader.seek(mouthsOffset)
    mouths = [ readMouth(reader) for _ in range(mouthCount) ]

    reader.seek(localPosParamsOffset)
    localPosParamDescs = [ readPosParamDesc(reader) for _ in range(localPosParamCount) ]

    reader.seek(surfacePropOffset)
    surfaceProp = readStruct('<B', reader)

    reader.seek(incModelsOffset)
    incModels = [ readModelGroup(reader) for _ in range(incModelCount) ]

    reader.seek(flexCtrlUIsOffset)
    flexCtrlUIs = [ readFlexCtrlUI(reader) for _ in range(flexCtrlUICount) ]
     

    # print(bodyPartCount)
    # print(json.dumps(boneCtrlCount, indent=4, ensure_ascii=False))




if __name__ == '__main__':

    readMDL(r'C:\Projects\GameTools\hl2\alyx.mdl')
    # unpackAll(GAME_DIR)
    # print(json.dumps(_stats, indent=4, ensure_ascii=False))
    
    # unpack(os.path.join(GAME_DIR, 'Sounds', 'GmSndMeta.asr_decompressed'))
    # unpack(os.path.join(GAME_DIR, 'Sounds', 'GmSnd.asr'))
    # unpack(os.path.join(GAME_DIR, 'Fonts', 'buttons.asr'))