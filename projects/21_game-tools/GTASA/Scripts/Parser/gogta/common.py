import os, struct, json


def checkSamePaths (*paths):
    return len(set([ os.path.normpath(path).lower() for path in paths ])) == 1


def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items


def getPathExtension (path):
    ext = os.path.splitext(path)[1]

    if ext:
        return ext[1:].lower()
    else:
        return ''


def readNullString (descriptor):
    buff = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'\x00':
            break

        buff += byte

    return buff.decode('utf-8')


def bytesToNullString (byteSeq):
    buff = b''

    for byte in byteSeq:
        if byte == 0:
            break

        buff += byte.to_bytes(1, 'little')

    return buff.decode('utf-8')


def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])


def formatSize (size):
    if size >= (1024 ** 3):
        return '{:.1f}gb'.format(size / (1024 ** 3))
    elif size >= (1024 ** 2):
        return '{:.1f}mb'.format(size / (1024 ** 2))
    elif size >= 1024:
        return '{:.1f}kb'.format(size / 1024)
    else:
        return '{}b'.format(size)


class ObjectJSONEncoder (json.JSONEncoder):
    def default (self, obj):
        return obj.__dict__


def formatJson (obj):
    return json.dumps(obj, indent=4, ensure_ascii=False, cls=ObjectJSONEncoder)


def walkDir (directory, testFn, isRecursive=True, rootItems=None):
    assert os.path.isdir(directory), 'Directory doesn\'t exist: {}'.format(directory)

    rootItems = tuple(item.lower() for item in (rootItems or []))
    directory = os.path.normpath(directory)
    paths = []

    def walk (directory, isRoot=False):
        for item in os.listdir(directory):
            if isRoot and rootItems and (item.lower() not in rootItems):
                continue

            itemPath = os.path.join(directory, item)
            isDir = os.path.isdir(itemPath)
            isFile = os.path.isfile(itemPath)

            if testFn(itemPath, isFile, isDir):
                paths.append(itemPath)

            if isDir and isRecursive:
                walk(itemPath)

    walk(directory, True)

    return paths


def getIndex (sequence, subSequence):
    try:
        return sequence.index(subSequence)
    except:
        return -1


if __name__ == '__main__':
    pass
