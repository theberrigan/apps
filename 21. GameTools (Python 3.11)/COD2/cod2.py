import os
import sys
import csv
import zipfile
import regex
import json

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.media.image.raw import RawImage
from bfw.xml import XMLNode


GAME_DIR   = r'G:\Games\Call Of Duty 2'
MAIN_DIR   = os.path.join(GAME_DIR, 'main')
RAW_DIR    = os.path.join(GAME_DIR, 'raw')
SOURCE_DIR = os.path.join(RAW_DIR, 'source')
MOD_DIR    = os.path.join(RAW_DIR, 'mod')
DB_PATH    = os.path.join(RAW_DIR, 'db.json')

# os.makedirs(RAW_DIR, exist_ok=True)

# iwdIndex = 0 

# while True:
#     path = os.path.join(MAIN_DIR, 'iw_{:0>2}.iwd'.format(iwdIndex))
#     iwdIndex += 1

#     if not os.path.isfile(path):
#         break

#     print(path)

#     with zipfile.ZipFile(path, 'r') as iwd:
#         iwd.extractall(RAW_DIR)


def readDB ():
    if not os.path.isfile(DB_PATH):
        return {}

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.loads(f.read())


def writeDB (data):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


def extractAll ():
    db = readDB()
    db.setdefault('archives', {})

    archives = db['archives']

    for item in os.listdir(MAIN_DIR):
        itemPath = os.path.join(MAIN_DIR, item)

        if not item.lower().endswith('.iwd') or not os.path.isfile(itemPath):
            continue

        baseName = os.path.splitext(item)[0]

        match = regex.match(r'^(.*[^\d])(\d+)$', baseName)

        assert match

        archKey, archIndex = match.groups()

        archIndex = int(archIndex)

        archives.setdefault(archKey, {
            'chunks': []
        })

        extractDir = os.path.join(SOURCE_DIR, archKey)

        # os.makedirs(extractDir, exist_ok=True)

        with zipfile.ZipFile(itemPath, 'r') as iwd:
            for i in iwd.infolist():
                if not i.is_dir():
                    print(i.date_time)


def readCSV (csvPath):
    items = []

    with open(csvPath, 'r', newline='') as f:
        reader = csv.reader(f)

        keys = None

        for row in reader:
            if not row or not row[0] or row[0][0] == '#':
                continue

            if not keys:
                keys = row
                continue

            assert len(keys) >= len(row)

            item = {}

            for i, value in enumerate(row):
                item[keys[i]] = value

            name = (item.get('name', '') + ' ' + item.get('file', '') + ' ' + item.get('secondaryaliasname', '')).lower()
            loadspec = item.get('loadspec')

            if regex.search(r'weapons/impact/[a-z\d_\.]*flesh', name) and loadspec in [ None, '', 'all_sp' ]:
                items.append(item)

    return items


def convertPNGs ():
    for pngPath in iterFiles(r"G:\Games\Call Of Duty Collector's Edition\Main\.raw\_berrigan\crosshairs", False, [ '.png' ]):
        tgaPath = replaceExt(pngPath, '.tga')

        image = RawImage.fromFile(pngPath)

        print(f'{ image.width }x{ image.height }:{ image.channels * 8 }, { image.colorCount } colors')

        image.save(tgaPath)

        removeFile(pngPath)


def patchWeapons ():
    WEAPONS_DIR = r"G:\Games\Call Of Duty 2\raw\weapons\sp"
    OUT_DIR     = r"G:\Games\Call Of Duty 2\main\_mod\weapons\sp"

    createDirs(OUT_DIR)

    def readWeapon (filePath):
        lines = readText(filePath, encoding='cp1252')
        lines = lines.split('\\')

        if not lines:
            return None

        fileType = lines[0]

        if fileType != 'WEAPONFILE':
            raise Exception('Not a weapon file')        

        lineCount = len(lines)

        assert lineCount % 2 == 1

        params = {}

        for i in range(1, lineCount, 2):
            key   = lines[i].strip()
            value = lines[i + 1].strip()

            params[key] = value

        return params

    def encodeWeapon (params):
        lines = [ 'WEAPONFILE' ] + [ f'{ k }\\{ v }' for k, v in params.items() ]

        return '\\'.join(lines)

    for filePath in iterFiles(WEAPONS_DIR, False):
        weapon = readWeapon(filePath)

        reticleCenter = weapon.get('reticleCenter', '').lower()
        reticleSide   = weapon.get('reticleSide', '').lower()

        if reticleCenter in [ 'gfx/reticle/center_cross.tga', '_berrigan/crosshairs/crosshair.tga' ] or \
           reticleSide in [ 'gfx/reticle/side_skinny.tga', 'gfx/reticle/hud@side_small_arc.tga' ]:
            print(getRelPath(filePath, WEAPONS_DIR))

            print('reticleCenter:    ', reticleCenter)
            print('reticleSide:      ', reticleSide)
            print('reticleCenterSize:', weapon.get('reticleCenterSize'))
            print('reticleSideSize:  ', weapon.get('reticleSideSize'))
            print('-' * 20)
            
            weapon['reticleCenter']     = '_crosshair'
            weapon['reticleSide']       = ''
            weapon['reticleCenterSize'] = 32
            weapon['reticleSideSize']   = 0

            print('reticleCenter:    ', weapon.get('reticleCenter'))
            print('reticleSide:      ', weapon.get('reticleSide'))
            print('reticleCenterSize:', weapon.get('reticleCenterSize'))
            print('reticleSideSize:  ', weapon.get('reticleSideSize'))
            print(' ')

            patchedPath = joinPath(OUT_DIR, getBaseName(filePath))

            weapon = encodeWeapon(weapon)

            writeText(patchedPath, weapon, encoding='cp1252')


def collectFiles ():
    data = readBin(r"G:\Games\Call Of Duty Collector's Edition\_trash\.logs\cod.xml")

    root = XMLNode(data)

    events = root.findAll('eventlist/event')

    _paths = {}

    with open(r"G:\Games\Call Of Duty Collector's Edition\_trash\.logs\cod.txt", 'w', encoding='utf-8') as f:
        for event in events:
            op    = event.find('Operation').getText().strip()
            path  = event.find('Path').getText().strip()
            path2 = getRelPath(getAbsPath(path), r"G:\Games\Call Of Duty Collector's Edition")

            key = getAbsPath(path).lower()

            if key not in _paths and path2 and not isDir(path):
                _paths[key] = True

                f.write(f'{ path2 }\n')   


def compare ():
    rootDir = r"G:\Games\Call Of Duty Collector's Edition"
    logPath = joinPath(rootDir, '_trash', '.logs', 'cod.txt')

    gameFiles = (
        list(iterFiles(joinPath(rootDir, 'main'), True)) +
        list(iterFiles(joinPath(rootDir, 'main_english'), True)) +
        list(iterFiles(joinPath(rootDir, 'main_russian'), True))
    )

    usedFiles = readText(logPath).split('\n')
    usedFiles = [ p for p in usedFiles if p.strip().lower().startswith('main') ]
    usedFiles = [ getAbsPath(joinPath(rootDir, p.strip())) for p in usedFiles if p.strip() ]

    pathMap = {}

    for path in (gameFiles + usedFiles):
        pathMap[getAbsPath(path).lower()] = path

    gameFiles = set([ getAbsPath(p).lower() for p in gameFiles ])
    usedFiles = set([ getAbsPath(p).lower() for p in usedFiles ])

    unusedFiles   = sorted(list(gameFiles - usedFiles))
    notFoundFiles = sorted(list(usedFiles - gameFiles))

    print('Unused files:')

    for p in unusedFiles:
        print(f'- { pathMap[p] }')

    print('\n\n')
    print('Not found files:')

    for p in notFoundFiles:
        print(f'- { pathMap[p] }')



if __name__ == '__main__':
    # extractAll()

    COD1_SOUNDS_CSV = r"G:\Games\Call Of Duty Collector's Edition\Main\.raw\soundaliases\iw_sound.csv"
    COD2_SOUNDS_CSV = r'G:\Games\Call Of Duty 2\raw\soundaliases\iw_sound2.csv'

    # print(toJson(readCSV(COD1_SOUNDS_CSV)))
    # print(toJson(readCSV(COD2_SOUNDS_CSV)))

    # convertPNGs()
    patchWeapons()
    # collectFiles()
    # compare()