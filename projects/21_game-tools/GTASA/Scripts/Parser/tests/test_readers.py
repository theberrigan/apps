import os
import pytest
import hashlib
import struct
from gogta.readers import BinaryFileReader


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(TEST_DIR, 'samples')


def prepareDirs ():
    os.makedirs(SAMPLES_DIR, exist_ok=True)


def md5 (data):
    return hashlib.md5(data).hexdigest().lower()


@pytest.fixture
def fileToRead1 ():
    prepareDirs()

    commands = []

    strings = [
        ('Привет', [ 'utf-8', 'utf-16' ]),
        ('Hello', [ 'ascii', 'utf-8', 'utf-16' ])
    ]

    trashBytes = bytes(range(40))

    data = trashBytes[:6]
    chunkOffset = len(data)

    for string, encodings in strings:
        for encoding in encodings:
            for addTrash in [ True, False ]:
                item = string.encode(encoding)

                stringSize = len(item)

                if encoding == 'ascii':
                    item += b'\x00'

                stringSizeWithNull = len(item)

                if addTrash:
                    item += trashBytes[:(len(string) // 2)]

                itemSize = len(item)
                data += struct.pack('<3I', stringSize, stringSizeWithNull, itemSize)
                data += item
                commands.append((string, encoding, stringSize, stringSizeWithNull, itemSize))

    chunkSize = len(data) - chunkOffset
    data += trashBytes[:6]

    filePath = os.path.join(SAMPLES_DIR, f'{ md5(data) }.txt')

    if not os.path.isfile(filePath):
        with open(filePath, 'wb') as f:
            f.write(data)

    return filePath, chunkOffset, chunkSize, commands


def test_BinaryFileReader (fileToRead1):
    filePath, chunkOffset, chunkSize, commands = fileToRead1

    with BinaryFileReader(filePath, chunkOffset, chunkSize) as f:
        startChecked = False
        for string, encoding, stringSize, stringSizeWithNull, itemSize in commands:
            if not startChecked:
                startChecked = True
                assert f.tell() == 0, 'Wrong rel offset'
                assert f.tell(True) == chunkOffset, 'Wrong abs offset'

            stringSizeRead, stringSizeWithNullRead, itemSizeRead = f.readStruct('<3I')

            assert stringSizeRead == stringSize, 'Wrong stringSize'
            assert stringSizeWithNullRead == stringSizeWithNull, 'Wrong stringSizeWithNull'
            assert itemSizeRead == itemSize, 'Wrong itemSize'

            skipTrash = encoding != 'ascii' and stringSize != itemSize

            stringRead = f.readString(size=(stringSize if skipTrash else itemSize), isNullTerm=(encoding == 'ascii'), encoding=encoding)

            if skipTrash:
                f.seek(itemSize - stringSize, 1)

            assert stringRead == string, 'Wrong string'
