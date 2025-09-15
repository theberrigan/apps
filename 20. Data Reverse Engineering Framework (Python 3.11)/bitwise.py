# pip install bytearray
from bitarray import bitarray



class AbstractBitVec:
    pass

# Much slower than BoolBitVec, but compact in memory
class BinBitVec (AbstractBitVec):
    def __init__ (self, size):
        assert size > 0

        self.size = size
        self.mask = (2 ** size) - 1
        self.value = 0

    def _assertIndex (self, index):
        assert 0 <= index < self.size, 'Too big index'

    def _assertBit (self, bit):
        assert bit.bit_length() <= self.size, 'Too far bit'

    def setIndex (self, index):
        # self._assertIndex(index)
        self.value |= 1 << index

    def clearIndex (self, index):
        # self._assertIndex(index)
        self.value &= self.mask ^ (1 << index)

    def checkIndex (self, index):
        # self._assertIndex(index)
        return bool(self.value & (1 << index))

    def setBit (self, bit):
        # self._assertBit(bit)
        self.value |= bit

    def clearBit (self, bit):
        # self._assertBit(bit)
        self.value &= self.mask ^ bit

    def checkBit (self, bit):
        # self._assertBit(bit)
        return bool(self.value & bit)

    def reset (self):
        self.value = 0


# Much faster than BinBitVec, but consumes more memory
class BoolBitVec (AbstractBitVec):
    def __init__ (self, size):
        assert size > 0

        self.size  = size
        self.value = None

        self.reset()

    def _assertIndex (self, index):
        assert 0 <= index < self.size, 'Too big index'

    def setIndex (self, index):
        # self._assertIndex(index)
        self.value[index] = True

    def clearIndex (self, index):
        # self._assertIndex(index)
        self.value[index] = False

    def checkIndex (self, index):
        # self._assertIndex(index)
        return self.value[index]

    def reset (self):
        self.value = [ False ] * self.size


# Much faster than BinBitVec, but consumes more memory
class BitVec (AbstractBitVec):
    def __init__ (self, size):
        assert size > 0

        self.size  = size
        self.count = (size + 7) >> 3
        self.value = None

        self.reset()

    def _assertIndex (self, index):
        assert 0 <= index < self.size, 'Too big index'

    def setIndex (self, index):
        # self._assertIndex(index)
        self.value[index >> 3] |= 1 << (index & 7)

    def clearIndex (self, index):
        # self._assertIndex(index)
        self.value[index >> 3] &= 0xFFFFFFFF ^ (1 << (index & 7))

    def checkIndex (self, index):
        # self._assertIndex(index)
        return bool(self.value[index >> 3] & (1 << (index & 7)))

    def reset (self):
        self.value = [ 0 ] * self.count


class BABitVec (AbstractBitVec):
    def __init__ (self, size):
        assert size > 0

        self.size  = size
        self.value = None

        self.reset()

    def _assertIndex (self, index):
        assert 0 <= index < self.size, 'Too big index'

    def setIndex (self, index):
        # self._assertIndex(index)
        self.value[index] = 1

    def clearIndex (self, index):
        # self._assertIndex(index)
        self.value[index] = 0

    def checkIndex (self, index):
        # self._assertIndex(index)
        return bool(self.value[index])

    def reset (self):
        self.value = bitarray(self.size)
        self.value.setall(0)



def __test__ ():
    size = 128
    idx1 = 111
    idx2 = 16

    b = BinBitVec(size)

    b.setIndex(idx2)
    b.setIndex(idx1)
    assert b.checkIndex(0) == False
    assert b.checkIndex(idx1) == True
    b.clearIndex(5)
    assert b.checkIndex(idx1) == True
    b.clearIndex(idx1)
    assert b.checkIndex(idx1) == False
    assert b.checkIndex(idx2) == True
    b.reset()
    assert b.checkIndex(idx1) == False
    assert b.checkIndex(idx2) == False

    # try:
    #     b.checkIndex(size)
    #     print('Failed')
    #     return
    # except:
    #     pass

    import time
    from pympler.asizeof import asizeof

    size = 256 * 1024

    # 3.245073080062866
    # 35560
    # 0.09201645851135254
    # 2097736

    vecs = [ BinBitVec, BoolBitVec, BitVec, BABitVec ]

    for cls in vecs:
        _start = time.time()

        bf = cls(size)

        for i in range(bf.size):
            bf.setIndex(i)

        for i in range(bf.size):
            assert bf.checkIndex(i)

        for i in range(bf.size):
            bf.clearIndex(i)

        _done = time.time() - _start

        print(cls.__name__, _done, asizeof(bf))



__all__ = [
    'AbstractBitVec',
    'BinBitVec',
    'BoolBitVec'
]



if __name__ == '__main__':
    __test__()