from ctypes import (
    CDLL,
    cast,
    byref as byRef,
    sizeof as cSizeOf, 
    c_bool as cBool,
    c_char_p as cCP,
    c_float as cF32,
    c_double as cF64,
    c_byte as cI8,
    c_ubyte as cU8,
    c_short as cI16,
    c_ushort as cU16,
    c_int as cI32,
    c_uint as cU32,
    c_longlong as cI64,
    c_ulonglong as cU64,
    c_void_p as cVP,
)

from utils import *

assert cSizeOf(cI8)  == cSizeOf(cU8)  == 1
assert cSizeOf(cI16) == cSizeOf(cU16) == 2
assert cSizeOf(cI32) == cSizeOf(cU32) == 4
assert cSizeOf(cI64) == cSizeOf(cU64) == 8



C_INT_TYPES = {
    8:  (cI8,  cU8 ),
    16: (cI16, cU16),
    32: (cI32, cU32),
    64: (cI64, cU64),
}



def toSigned (num, size):
    return C_INT_TYPES[size][0](int(num)).value

def toUnsigned (num, size):
    return C_INT_TYPES[size][1](int(num)).value

def toI8 (num):
    return toSigned(num, 8)

def toU8 (num):
    return toUnsigned(num, 8)

def toI16 (num):
    return toSigned(num, 16)

def toU16 (num):
    return toUnsigned(num, 16)

def toI32 (num):
    return toSigned(num, 32)

def toU32 (num):
    return toUnsigned(num, 32)

def toI64 (num):
    return toSigned(num, 64)

def toU64 (num):
    return toUnsigned(num, 64)

# https://docs.python.org/3/library/operator.html
# p1 + p2     p1.__add__(p2)
# p1 - p2     p1.__sub__(p2)
# p1 * p2     p1.__mul__(p2)
# p1 ** p2    p1.__pow__(p2)
# p1 / p2     p1.__truediv__(p2)
# p1 // p2    p1.__floordiv__(p2)
# p1 % p2     p1.__mod__(p2)
# p1 << p2    p1.__lshift__(p2)
# p1 >> p2    p1.__rshift__(p2)
# p1 & p2     p1.__and__(p2)
# p1 | p2     p1.__or__(p2)
# p1 ^ p2     p1.__xor__(p2)
# ~p1         p1.__invert__()

# p1 < p2     p1.__lt__(p2)
# p1 <= p2    p1.__le__(p2)
# p1 == p2    p1.__eq__(p2)
# p1 != p2    p1.__ne__(p2)
# p1 > p2     p1.__gt__(p2)
# p1 >= p2    p1.__ge__(p2)

# repr, is, ==, in, rcs, lcs

# https://stackoverflow.com/questions/30488777/what-does-rank-mean-in-relation-to-type-conversion
# https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2012/n3337.pdf [p82]
# https://en.cppreference.com/w/c/language/conversion
# https://en.cppreference.com/w/cpp/language/types
# https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html

'''
# type = sign|exponent|mantissa/fraction
# float = 1|8|23, bias 127        // 7
# double = 1|11|52, bias 1023     // 15?

   0 123 -- indices of digits in significand
+/-d.ddd * B^e -- floating-point number
+/-d.ddd -- significand (or mantissa)
       B -- base (always even)
       e -- exponent
       p -- precision, number of digits in significand
   e_min -- min possible exponent
   e_max -- max possible exponent

There are β^p possible significands
There are (e_max - e_min + 1) possible exponents


'''

def setTopmost (op1, op2, value):
    if op1._rank >= op2._rank:
        return op1._set(value)

    return op2._set(value)

def getTypeName (entity):
    return type(entity).__name__

def raiseIncompatTypes (operator, op1, op2):
    tn1 = getTypeName(op1)
    tn2 = getTypeName(op2)

    raise TypeError(f'Operation "{ operator }" is not defined for types "{ tn1 }" and "{ tn2 }"')


class CNumber:
    _castFn = None
    _size = None
    _rank = None

    def __init__ (self):
        raise TypeError(f'Do not instantiate abstract class { self.__class__.__name__ }')

    @classmethod
    def cast (cls, num):
        assert cls._castFn
        return cls._castFn(num)

    @classmethod
    def getSize (cls):
        assert cls._size
        return cls._size


class CInteger (CNumber):
    def __init__ (self, num=0):
        if isinstance(num, CNumber):
            num = num.value

        self._num = self.__class__.cast(num)

    @property
    def value (self):
        return self._num

    @property
    def size (self):
        return self.__class__.getSize()

    def get (self):
        return self.value

    def _set (self, value):
        self._num = self.__class__.cast(value)
        return self

    def _exec (self, isRanked, other, fn, operator):
        if isinstance(other, CNumber):
            value = fn(self.value, other.value)

            if not isRanked or self._rank >= other._rank:
                return self._set(value)

            return other._set(value)

        raiseIncompatTypes(operator, self, other)
        
    def __int__ (self):
        return self.value

    def __float__ (self):
        return float(self.value)

    def __len__ (self):
        return self.getSize()

    def __str__ (self):
        return str(self.value)

    def __repr__ (self):
        return f'{ self.__class__.__name__ }({ self.value })'

    def __add__ (self, other):
        return self._exec(other, True, lambda a, b: a + b, '+')

    def __sub__ (self, other):
        return self._exec(other, True, lambda a, b: a - b, '-')

    def __mul__ (self, other):
        return self._exec(other, True, lambda a, b: a * b, '*')

    def __pow__ (self, other):
        return self._exec(other, False, lambda a, b: a ** b, '**')

    def __truediv__ (self, other):
        return self._exec(other, True, lambda a, b: a / b, '/')

    def __floordiv__ (self, other):
        return self._exec(other, True, lambda a, b: a // b, '//')

    def __mod__ (self, other):
        if not isinstance(other, CInteger):
            raiseIncompatTypes('%', self, other)

        return self._exec(other, True, lambda a, b: a % b, '%')

    def __mod__ (self, other):
        if not isinstance(other, CInteger):
            raiseIncompatTypes('<<', self, other)

        return self._exec(other, True, lambda a, b: a << b, '<<')


# p1 + p2     p1.__add__(p2)
# p1 - p2     p1.__sub__(p2)
# p1 * p2     p1.__mul__(p2)
# p1 ** p2    p1.__pow__(p2)
# p1 / p2     p1.__truediv__(p2)
# p1 // p2    p1.__floordiv__(p2)
# p1 % p2     p1.__mod__(p2)
# p1 << p2    p1.__lshift__(p2)
# p1 >> p2    p1.__rshift__(p2)
# p1 & p2     p1.__and__(p2)
# p1 | p2     p1.__or__(p2)
# p1 ^ p2     p1.__xor__(p2)
# ~p1         p1.__invert__()


class CFloat (CNumber):
    pass


class I8 (CInteger):
    _castFn = toI8
    _size = 8
    _rank = 1

class U8 (CInteger):
    _castFn = toU8
    _size = 8
    _rank = 1

class I16 (CInteger):
    _castFn = toI16
    _size = 16
    _rank = 2

class U16 (CInteger):
    _castFn = toU16
    _size = 16
    _rank = 2

class I32 (CInteger):
    _castFn = toI32
    _size = 32
    _rank = 3

class U32 (CInteger):
    _castFn = toU32
    _size = 32
    _rank = 3

class I64 (CInteger):
    _castFn = toI64
    _size = 64
    _rank = 4

class U64 (CInteger):
    _castFn = toU64
    _size = 64
    _rank = 4

class F32 (CFloat):
    _castFn = float
    _size = 32
    _rank = 5

class F64 (CFloat):
    _castFn = float
    _size = 64
    _rank = 6


def sizeOf (num):
    if isinstance(num, CNumber) or type(num) == type and issubclass(num, CNumber):
        return num.getSize()

    return 0

def loadLib (libPath):
    try:
        return CDLL(libPath)
    except:
        return None

# If you need mutable memory blocks, ctypes has a create_string_buffer function which creates these in various ways.
def ll ():
    libPath = getAbsPath('../cpp/projects/PyCExactMath/build/x64/release/cem_x64.dll')
    lib = loadLib(libPath)

    if not lib:
        return

    lib.f32_plus_f32.restype = cF32
    lib.f32_plus_f32.argtypes = [
        cF32,
        cF32,
    ]

    lib.f32_plus_f32_2.argtypes = [
        cF32,
        cF32,
        cVP,
    ]

    buf = cF32()

    lib.f32_plus_f32_2(1.5, 3.25, byRef(buf))

    from struct import unpack

    print(unpack('<f', bytes(buf))[0])

    pStr = cCP('12.35'.encode('ascii'))
    buf  = (cU8 * 4)()

    lib.parseFloat.restype = cBool
    lib.parseFloat.argtypes = [
        cCP,
        cVP,
    ]

    isOk = lib.parseFloat(pStr, byRef(buf))

    if isOk:
        print(buf)
    else:
        print('Failed')

# ------------------------------------------------------------------------------

from random import randint, random, uniform

def gen1 ():
    types = [ 'I8', 'U8', 'I16', 'U16', 'I32', 'U32', 'I64', 'U64', 'F32', 'F64' ]
    result = []

    for i, name in enumerate(types):
        prefix = name[0].lower()
        size = int(name[1:])
        isFloat = prefix == 'f'
        isUnsigned = prefix == 'u'

        if isFloat:
            value = uniform(-999, 999)

            if size == 32:
                value = f'{value:.05f}f'
            else:
                value = f'{value:.012f}'
        else:
            minVal = 0
            maxVal = 2 ** size - 1

            if not isUnsigned:
                minVal = maxVal // 2 - maxVal
                maxVal = maxVal // 2

            value = randint(minVal, maxVal)

            suffix = ''

            if isUnsigned and size >= 32:
                suffix += 'u'

            if size == 64:
                suffix += 'l'

            value = f'{value}{suffix}'

        digits = len(str(len(types)))
        varName = f'v{(i + 1):0{digits}d}'
        varDecl = f'{name} {varName} = {value};'

        result.append({
            'name': name,
            'size': size,
            'value': value,
            'isInt': not isFloat,
            'isUnsigned': isUnsigned,
            'varName': varName,
            'varDecl': varDecl
        })

    return result

def gen2 ():
    types = gen1()
    opRemaps = {
        '**': 'pow({a}, {b})'
    }
    ops = [
        # 0    1  2               3
        ('+',  2, '__add__',      [ 'other' ], ), 
        ('-',  2, '__sub__',      [ 'other' ], ), 
        ('*',  2, '__mul__',      [ 'other' ], ), 
        ('**', 2, '__pow__',      [ 'other' ], ), 
        ('/',  2, '__truediv__',  [ 'other' ], ), 
        # ('//', 2, '__floordiv__', [ 'other' ], ), 
        ('%',  2, '__mod__',      [ 'other' ], ), 
        ('<<', 2, '__lshift__',   [ 'other' ], ), 
        ('>>', 2, '__rshift__',   [ 'other' ], ), 
        ('&',  2, '__and__',      [ 'other' ], ), 
        ('|',  2, '__or__',       [ 'other' ], ), 
        ('^',  2, '__xor__',      [ 'other' ], ),
        ('~',  1, '__invert__',   [],          ),
    ]

    digits = len(str(len(ops) * len(types) ** 2))

    for v in types:
        print(v['varDecl'])

    print(' ')

    i = 0

    for op in ops:
        op2 = opRemaps.get(op[0], op[0])
        isRemapped = op2 != op[0]

        for v1 in types:
            v1Name = v1['varName']
            v1Type = v1['name']

            if op[1] == 1:
                if isRemapped:
                    expr = op2.format(op=op[0], a=v1Name)
                else:
                    expr = f'{op[0]}{v1Name}'

                expr = f'auto r{(i + 1):0{digits}d} = {expr};'
                print(expr)
                i += 1
            else:
                for v2 in types:
                    v2Name = v2['varName']
                    v2Type = v2['name']

                    if isRemapped:
                        expr = op2.format(op=op[0], a=v1Name, b=v2Name)
                    else:
                        expr = f'{v1Name} {op[0]} {v2Name}'

                    expr = f'auto r{(i + 1):0{digits}d} = {expr};  // {v1Type}, {v2Type}'
                    print(expr)
                    i += 1

# bitwise are not allowed with floats

# p1 + p2     p1.__add__(p2)
# p1 - p2     p1.__sub__(p2)
# p1 * p2     p1.__mul__(p2)
# p1 ** p2    p1.__pow__(p2)
# p1 / p2     p1.__truediv__(p2)
# p1 // p2    p1.__floordiv__(p2)
# p1 % p2     p1.__mod__(p2)
# p1 << p2    p1.__lshift__(p2)
# p1 >> p2    p1.__rshift__(p2)
# p1 & p2     p1.__and__(p2)
# p1 | p2     p1.__or__(p2)
# p1 ^ p2     p1.__xor__(p2)
# ~p1         p1.__invert__()


TYPES = gen1()


if __name__ == '__main__':
    gen2()
    # print(toJson(TYPES))
    # ll()
    # print(U16(16) ** U8(4) + U8(1))
    # x = U8(128)
    # x = x + 127
    # print((U32(0xFFFFFF12) * U32(0xFFFF9912)).size)
    # print(repr(U32(0xFFFFFF12)))
    # print(U32(0xFFFFFF12) * 1)
    # print(type(I8) == type, type(I8(8)))
    # print(sizeOf(I8))
    # a = I8(8)
    # b = I16(a)
    # print(sizeOf(a))
    # print(sizeOf(b))
    # print(sizeOf(a))
    # print(sizeOf(None))
    # print(sizeOf(1))
    # print(sizeOf({}))
    # print(float(I8(255)))