from .types import WADLumpType



WAD_SIGNATURE            = b'WAD3'
WAD_MAX_ITEM_NAME_LENGTH = 16

WAD_TYPE_TO_EXT = {
    WADLumpType.Palette: 'pal',  # palette
    WADLumpType.DDS:     'dds',  # DDS image
    WADLumpType.GFX:     'lmp',  # quake1, hl pic
    WADLumpType.QFont:   'fnt',  # hl qfonts
    WADLumpType.Mip:     'mip',  # hl/q1 mip
    WADLumpType.Script:  'txt',  # scripts
}

WAD_EXT_TO_TYPE = { v: k for k, v in WAD_TYPE_TO_EXT.items() }



__all__ = [
    'WAD_SIGNATURE',
    'WAD_MAX_ITEM_NAME_LENGTH',
    'WAD_TYPE_TO_EXT',
    'WAD_EXT_TO_TYPE',
]