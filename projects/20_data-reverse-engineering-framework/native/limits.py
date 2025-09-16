POW2_8  = 2 ** 8
POW2_16 = 2 ** 16
POW2_32 = 2 ** 32
POW2_64 = 2 ** 64

MAX_U8 = 2 ** 8 - 1
MIN_U8 = 0

MAX_I8 = 2 ** 7 - 1
MIN_I8 = MAX_I8 - MAX_U8

MAX_U16 = 2 ** 16 - 1
MIN_U16 = 0

MAX_I16 = 2 ** 15 - 1
MIN_I16 = MAX_I16 - MAX_U16

MAX_U32 = 2 ** 32 - 1
MIN_U32 = 0

MAX_I32 = 2 ** 31 - 1
MIN_I32 = MAX_I32 - MAX_U32

MAX_U64 = 2 ** 64 - 1
MIN_U64 = 0

MAX_I64 = 2 ** 63 - 1
MIN_I64 = MAX_I64 - MAX_U64

U8_BYTES  = I8_BYTES  = 1
U16_BYTES = I16_BYTES = 2
U32_BYTES = I32_BYTES = 4
U64_BYTES = I64_BYTES = 8

U8_BITS  = I8_BITS  = 8
U16_BITS = I16_BITS = 16
U32_BITS = I32_BITS = 32
U64_BITS = I64_BITS = 64

PTR32_BYTES = 4
PTR64_BYTES = 8

PTR32_BITS = 32
PTR64_BITS = 64



__all__ = [
    'POW2_8',
    'POW2_16',
    'POW2_32',
    'POW2_64',
    'MAX_U8',
    'MIN_U8',
    'MAX_I8',
    'MIN_I8',
    'MAX_U16',
    'MIN_U16',
    'MAX_I16',
    'MIN_I16',
    'MAX_U32',
    'MIN_U32',
    'MAX_I32',
    'MIN_I32',
    'MAX_U64',
    'MIN_U64',
    'MAX_I64',
    'MIN_I64',
    'U8_BYTES',
    'I8_BYTES',
    'U16_BYTES',
    'I16_BYTES',
    'U32_BYTES',
    'I32_BYTES',
    'U64_BYTES',
    'I64_BYTES',
    'U8_BITS',
    'I8_BITS',
    'U16_BITS',
    'I16_BITS',
    'U32_BITS',
    'I32_BITS',
    'U64_BITS',
    'I64_BITS',
    'PTR32_BYTES',
    'PTR64_BYTES',
    'PTR32_BITS',
    'PTR64_BITS',
]



if __name__ == '__main__':
    print(f'U8  = [{ MIN_U8 }, { MAX_U8 }]')
    print(f'I8  = [{ MIN_I8 }, { MAX_I8 }]')
    print(f'U16 = [{ MIN_U16 }, { MAX_U16 }]')
    print(f'I16 = [{ MIN_I16 }, { MAX_I16 }]')
    print(f'U32 = [{ MIN_U32 }, { MAX_U32 }]')
    print(f'I32 = [{ MIN_I32 }, { MAX_I32 }]')
    print(f'U64 = [{ MIN_U64 }, { MAX_U64 }]')
    print(f'I64 = [{ MIN_I64 }, { MAX_I64 }]')