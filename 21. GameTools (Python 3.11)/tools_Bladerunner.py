# Bladerunner Tools

import sys

from hashlib import md5

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2



GAME_DIR     = r'G:\Games\Bladerunner'
SNAPSHOT_DIR = joinPath(GAME_DIR, '_snapshots')



def compareSnapshots (snapshotName1, snapshotName2):
    snapshotPath1 = joinPath(SNAPSHOT_DIR, f'{ snapshotName1 }.json')
    snapshotPath2 = joinPath(SNAPSHOT_DIR, f'{ snapshotName2 }.json')

    snapshot1 = readJson(snapshotPath1)
    snapshot2 = readJson(snapshotPath2)

    names1 = set([ item['fileName'].strip().lower() for item in snapshot1 ])
    names2 = set([ item['fileName'].strip().lower() for item in snapshot2 ])

    removed = sorted(list(names1 - names2))
    created = sorted(list(names2 - names1))
    changed = []

    snapshotMap2 = { item['fileName']: item['checksum'] for item in snapshot2 }

    for item1 in snapshot1:
        name = item1['fileName']

        if name in snapshotMap2 and item1['checksum'] != snapshotMap2[name]:
            changed.append(name)

    changed = sorted(changed)

    for name in removed:
        print(f'- { name }')

    for name in created:
        print(f'+ { name }')

    for name in changed:
        print(f'~ { name }')


def calcFileMD5 (filePath):
    data = readBin(filePath)

    return md5(data).hexdigest().upper()


def createSnapshot (snapshotName):
    files = []

    for filePath in iterFiles(GAME_DIR, False):
        fileName = getBaseName(filePath).lower()
        checksum = calcFileMD5(filePath)

        files.append({
            'fileName': fileName,
            'checksum': checksum,
        })

    createDirs(SNAPSHOT_DIR)

    snapshotPath = joinPath(SNAPSHOT_DIR, f'{ snapshotName }.json')

    writeJson(snapshotPath, files)


def main ():
    # createSnapshot('text')
    compareSnapshots('movies', 'text')




if __name__ == '__main__':
    main()
