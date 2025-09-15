import sys
import zlib
import subprocess

sys.path.insert(0, r'C:\Projects\GameTools')

from deps.utils import *
from deps.reader import *


ARCHIVE_PATH = r'D:\Documents\Source\Game Engines Sources\Source Engine 2007-2020 and Valve games.7z'
SOURCE_PATH  = r'C:\Projects\_Sources\GameEngines\SourceEngine2013_5\Source'
EXTS         = [ '.c', '.cpp', '.cxx', '.cc', '.h', '.hxx', '.hpp', '.sln', '.filters', '.vcxproj', '.vpc' ]
EXCLUDE_PATHS = [
    '.misc\\',
    'everything'
]

for i, path in enumerate(EXCLUDE_PATHS):
    hasSlash = path[-1] in [ '\\', '/' ]
    EXCLUDE_PATHS[i] = (getAbsPath(joinPath(SOURCE_PATH, path)) + (os.path.sep if hasSlash else '')).lower()


def collectArchivedFiles ():
    process = subprocess.run([ '7z', 'l', '-bb0', '-r', '-slt', ARCHIVE_PATH ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    isOk = not process.stderr

    if not isOk:
        print('Error', process.stderr)
        return

    lines = process.stdout.decode('utf-8').split('\n')

    skipLine = True

    items = []
    item  = {}

    for i, line in enumerate(lines):
        line = line.strip()

        if line == '----------':
            skipLine = False
            continue

        if skipLine:
            continue

        if not line:
            if item:
                items.append(item)
                item = {}

            continue

        key, value = line.split('=', maxsplit=1)

        item[key.strip()] = value.strip()

    items = [
        {
            'path': getAbsPath(joinPath(SOURCE_PATH, *item['Path'].split('\\')[1:])),
            'crc':  int(item['CRC'], 16) if item['CRC'] else None
        }
        for item in items
        if item['Attributes'][0] != 'D' and item['Path'].startswith('SE2013 (24) (HL, HL2, CSS, TF, TF2, TFC, Portal, DoD)')
    ]

    archPaths = { item['path'].lower(): item['crc'] for item in items }
    srcExts = [ '.c', '.cpp', '.cxx', '.cc', '.h', '.hxx', '.hpp' ]

    for path in iterFiles(SOURCE_PATH):
        path = path.lower()

        if path not in archPaths:
            continue

        # print(path)

        ext = getExt(path)

        if ext not in srcExts:
            continue

        with openFile(path) as f:
            data = f.read()

        crc = zlib.crc32(data) & 0xffffffff
        archCrc = archPaths[path]

        if archCrc is not None and archCrc != crc:
            print(path)



'''
    newPaths  = [ path for path in iterFiles(SOURCE_PATH) if path.lower() not in archPaths ]
    newPaths2 = []

    totalSize = 0
    exts = {}

    for path in newPaths:
        pathLC = path.lower()
        stop = False

        for ePath in EXCLUDE_PATHS:
            if pathLC.startswith(ePath):
                stop = True
                break

        if stop or (getExt(path).lower() in EXTS):
            continue

        newPaths2.append(path)

        ext = getExt(path)
        size = getFileSize(path)

        exts[ext] = exts.get(ext, 0) + size
        totalSize += size

        print(path)

    exts = sorted(exts.items(), key=lambda item: item[1], reverse=True)

    for k, v in exts:
        print(k, formatSize(v))

    print('\n', formatSize(totalSize))
'''

# {'Path': 'SE2013 (24) (HL, HL2, CSS, TF, TF2, TFC, Portal, DoD)\\external\\crypto++-5.6.3\\cryptopp563.diff', 'Size': '0', 'Packed Size': '0', 'Modified': '2018-04-21 20:43:29', 'Attributes': 'RAI', 'CRC': '', 'Encrypted': '-', 'Method': '', 'Block': ''}
# {'Path': 'SE2013 (24) (HL, HL2, CSS, TF, TF2, TFC, Portal, DoD)\\external\\vpc\\devtools\\bin\\.empty', 'Size': '0', 'Packed Size': '0', 'Modified': '2018-04-21 20:43:29', 'Attributes': 'RAI', 'CRC': '', 'Encrypted': '-', 'Method': '', 'Block': ''}
# {'Path': 'SE2013 (24) (HL, HL2, CSS, TF, TF2, TFC, Portal, DoD)\\materialsystem\\stdshaders\\common_vertexlitgeneric_vs20.fxc', 'Size': '0', 'Packed Size': '0', 'Modified': '2018-04-21 20:43:59', 'Attributes': 'AI', 'CRC': '', 'Encrypted': '-', 'Method': '', 'Block': ''}
# {'Path': 'SE2013 (24) (HL, HL2, CSS, TF, TF2, TFC, Portal, DoD)\\materialsystem\\stdshaders\\modulate_vs11.vsh', 'Size': '0', 'Packed Size': '0', 'Modified': '2018-04-21 20:44:00', 'Attributes': 'AI', 'CRC': '', 'Encrypted': '-', 'Method': '', 'Block': ''}
# {'Path': 'SE2013 (24) (HL, HL2, CSS, TF, TF2, TFC, Portal, DoD)\\utils\\vmpi_private\\mysql\\lib\\opt\\libmySQL.dll', 'Size': '233472', 'Packed Size': '', 'Modified': '2018-04-21 20:44:26', 'Attributes': 'AI', 'CRC': '9422CC9C', 'Encrypted': '-', 'Method': 'BCJ2 LZMA2:26 LZMA:20:lc0:lp2 LZMA:20:lc0:lp2', 'Block': '8'}
    

if __name__ == '__main__':
    pass # print(getAbsPath('.misc') + )
    collectArchivedFiles()