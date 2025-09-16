from ..maths import Vec3




# ----------------------------------------------------------------------------------------------------------------------

def saveMipAsPNG (pack, outPath : str):  # : RGBData
    import struct
    from PIL import Image as PILImage

    channels = sum(pack.buffer, [])

    buffer = struct.pack(f'<{ len(channels) }B', *channels)

    img = PILImage.frombytes('RGBA', (pack.width, pack.height), buffer)

    img.save(outPath)

# ----------------------------------------------------------------------------------------------------------------------

# ClearBounds
def clearBounds (mins : Vec3, maxs : Vec3):
    # make bogus range
    mins[0] = mins[1] = mins[2] = 999999
    maxs[0] = maxs[1] = maxs[2] = -999999

# AddPointToBounds
def addPointToBounds (v : Vec3, mins : Vec3, maxs : Vec3):
    for i in range(3):
        val = v[i]

        if val < mins[i]:
            mins[i] = val

        if val > maxs[i]:
            maxs[i] = val

# Mod_StudioBoundVertex
def boundVertex (mins : Vec3, maxs : Vec3, vertexCount : int, vertex : Vec3):
    if vertexCount == 0:
        clearBounds(mins, maxs)

    addPointToBounds(vertex, mins, maxs)

# ----------------------------------------------------------------------------------------------------------------------

def FS_LoadFile ():
    """
    reads any file
    returns raw buffer (not meta/lump) or NULL
    """
    pass

def W_LoadFile ():
    """
    opens and reads WAD file lump; finds index of lump in the WAD and reads the lump
    used when FS_Open return NULL
    returns ptr to raw buffer or NULL
    """
    pass

def FS_Open ():
    """
    opens file for read or write
    returns descriptor or NULL
    """
    pass

def FS_OpenReadFile ():
    """
    opens file to read
    returns NULL if wad
    or returns file descriptor if fs file
    """
    pass

def FS_FindFile ():
    """
    searches in search paths (in GAME_ROOT/valve and in *.wad files)
    returns index of lump in wad
    or returns GAME_ROOT/valve
    """
    pass

def COM_ExtractFilePath ():
    """
    return dirPath
    """
    pass

def W_TypeFromExt ():
    """
    if not ext or ext == '*' returns WADLumpType.Any
    or returns WADLumpType mapped to ext
    or returns WADLumpType.Null
    """
    pass

# ----------------------------------------------------------------------------------------------------------------------



__all__ = [
    'saveMipAsPNG',
    'clearBounds',
    'addPointToBounds',
    'boundVertex',
]