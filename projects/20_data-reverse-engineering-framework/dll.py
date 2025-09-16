from ctypes import Array as CArray, c_uint8 as CU8
from typing import Union, List, Tuple, Type, Callable, Any


def getTypeName (entity):
    return type(entity).__name__

BufferType = CArray[CU8]

def createBuffer (
    size : Union[int, None] = None,
    data : Union[bytes, bytearray, None] = None
) -> BufferType:
    if isinstance(data, bytes):
        data = bytearray(data)

    if data is not None and not isinstance(data, bytearray):
        raise TypeError(f'Specified data must be bytes or bytearray, but { getTypeName(data) } given')

    if size is not None and not isinstance(size, int):
        raise TypeError(f'Specified size must be int, but { getTypeName(size) } given')

    if size is not None and size < 0:
        raise TypeError(f'Specified size must be >= 0, but { size } given')

    if size is None and data is None:
        raise TypeError('Neither data nor buffer size specified')

    dataSize = len(data) if data is not None else 0

    if size is not None and data is not None and size < dataSize:
        raise TypeError(f'Specified buffer size ({ size }) less than data size ({ dataSize })')

    bufferSize = size if size is not None else dataSize
    bufferType = CU8 * bufferSize

    if dataSize > 0:
        return bufferType.from_buffer(data)

    return bufferType()



if __name__ == '__main__':
    # b = createBuffer(size=5)
    # print(b)
    b = createBuffer(size=1)
    # print(b)