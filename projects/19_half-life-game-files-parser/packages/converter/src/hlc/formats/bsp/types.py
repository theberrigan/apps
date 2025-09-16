from ...common import bfw

from bfw.types.enums import Enum



class BSPEntityFieldType (Enum):
    Float     = 0     # FIELD_FLOAT           -- Any floating point value
    String    = 1     # FIELD_STRING          -- A string ID (return from ALLOC_STRING)
    Entity    = 2     # FIELD_ENTITY          -- An entity offset (EOFFSET)
    ClassPtr  = 3     # FIELD_CLASSPTR        -- CBaseEntity *
    EHandle   = 4     # FIELD_EHANDLE         -- Entity handle
    EVars     = 5     # FIELD_EVARS           -- EVARS *
    EDict     = 6     # FIELD_EDICT           -- edict_t *, or edict_t *  (same thing)
    Vec       = 7     # FIELD_VECTOR          -- Any vector
    PosVec    = 8     # FIELD_POSITION_VECTOR -- A world coordinate (these are fixed up across level transitions automagically)
    Pointer   = 9     # FIELD_POINTER         -- Arbitrary data pointer... to be removed, use an array of FIELD_CHARACTER
    Integer   = 10    # FIELD_INTEGER         -- Any integer or enum
    Fn        = 11    # FIELD_FUNCTION        -- A class function pointer (Think, Use, etc)
    Bool      = 12    # FIELD_BOOLEAN         -- boolean, implemented as an int, I may use this as a hint for compression
    Short     = 13    # FIELD_SHORT           -- byte integer
    Char      = 14    # FIELD_CHARACTER       -- a byte
    Time      = 15    # FIELD_TIME            -- a floating point time (these are fixed up automatically too!)
    ModelName = 16    # FIELD_MODELNAME       -- Engine string that is a model name (needs precache)
    SoundName = 17    # FIELD_SOUNDNAME       -- Engine string that is a sound name (needs precache)



__all__ = [
    'BSPEntityFieldType'
]