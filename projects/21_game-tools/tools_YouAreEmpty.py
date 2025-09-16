# You Are Empty Tools

import os
import re
import sys
import time
import regex
import zipfile as zf

from datetime import datetime, timezone

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *



GAME_DIR  = r'D:\Documents\Downloads\Torrents\You Are Empty [DVD-версия] [1C]\game'
DATA_DIR  = joinPath(GAME_DIR, 'data')
DATA2_DIR = joinPath(GAME_DIR, 'data2')

RES_DIRS = [
    [ joinPath(DATA_DIR, 'levels'),            joinPath(DATA2_DIR, 'levels', 'levels.pak')             ],
    [ joinPath(DATA_DIR, 'maps'),              joinPath(DATA2_DIR, 'maps', 'maps.pak')                 ],
    [ joinPath(DATA_DIR, 'materials'),         joinPath(DATA2_DIR, 'materials')                        ],
    [ joinPath(DATA_DIR, 'models'),            joinPath(DATA2_DIR, 'models', 'models.pak')             ],
    [ joinPath(DATA_DIR, 'rpl'),               joinPath(DATA2_DIR, 'rpl', 'rpl.pak')                   ],
    [ joinPath(DATA_DIR, 'scripts', 'engine'), joinPath(DATA2_DIR, 'scripts', 'engine', 'engine.pak')  ],
    [ joinPath(DATA_DIR, 'scripts', 'game'),   joinPath(DATA2_DIR, 'scripts', 'game', 'game.pak')      ],
    [ joinPath(DATA_DIR, 'sounds'),            joinPath(DATA2_DIR, 'sounds',  'sounds.pak')            ],
    [ joinPath(DATA_DIR, 'textures'),          joinPath(DATA2_DIR, 'textures', 'textures.pak')         ],
]

PAK_EXTS = [ '.pak', '.zip' ]
# PAK_EXT  = '.pak'



def merge ():    
    for [ resDir, destPath ] in RES_DIRS:
        print(resDir)

        pakPaths = list(iterFiles(resDir, False, PAK_EXTS))

        resMap = {}

        for resPath in iterFiles(resDir, True, excludeExts=PAK_EXTS):
            resRelPath  = getRelPath(resPath, resDir)
            resBaseName = getBaseName(resRelPath).lower()
            resModDate  = datetime.fromtimestamp(getPathModTime(resPath))

            if resBaseName not in resMap:
                resMap[resBaseName] = {
                    'modDate': resModDate,
                    'outPath': resRelPath,
                    'outPathDate': resModDate,
                    'data': readBin(resPath),
                    'isFS': True
                }
            else:
                info = resMap[resBaseName]

                if info['modDate'] < resModDate:
                    info['modDate'] = resModDate
                    info['data']    = readBin(resPath)

                if info['outPathDate'] > resModDate:
                    info['outPathDate'] = resModDate
                    info['outPath']     = resRelPath

                print('Updated')

        for pakPath in iterFiles(resDir, False, PAK_EXTS):
            print(pakPath)

            with zf.ZipFile(pakPath, 'r') as arc:
                for entry in arc.infolist():
                    if entry.is_dir():
                        continue

                    resRelPath  = entry.filename
                    resBaseName = getBaseName(resRelPath).lower()
                    resModDate  = datetime(*entry.date_time)  # .timestamp()

                    if resMap.get(resBaseName, {}).get('isFS', False):
                        print('In FS:', resRelPath)
                        continue

                    data = arc.read(entry.filename)

                    if resBaseName not in resMap:
                        resMap[resBaseName] = {
                            'modDate': resModDate,
                            'outPath': resRelPath,
                            'outPathDate': resModDate,
                            'data': data,
                            'isFS': False
                        }
                    else:
                        info = resMap[resBaseName]

                        if info['modDate'] < resModDate:
                            info['modDate'] = resModDate
                            info['data']    = data

                            print('Patch:', resRelPath, info['outPath'])

                        if info['outPathDate'] > resModDate:
                            info['outPathDate'] = resModDate
                            info['outPath']     = resRelPath

                            print('New path:', resRelPath)

                    # print(resBaseName)


            # print(resMap[resBaseName])

        packToPak = False

        for pakExt in PAK_EXTS:
            if destPath.lower().endswith(pakExt.lower()):
                packToPak = True
                break

        if packToPak:
            createFileDirs(destPath)

            with zf.ZipFile(destPath, 'w', compression=zf.ZIP_DEFLATED, compresslevel=9) as arc:
                for info in resMap.values():
                    resDestPath = re.sub(r'[\\/]+', '/', info['outPath'])

                    modTime = tuple(info['modDate'].timetuple())[:6]

                    entryInfo = zf.ZipInfo(filename=resDestPath, date_time=modTime)
                    # entryInfo.compress_type = zf.ZIP_DEFLATED

                    arc.writestr(entryInfo, info['data'], compress_type=zf.ZIP_DEFLATED, compresslevel=9)
        else:
            for info in resMap.values():
                resDestPath = getAbsPath(joinPath(destPath, info['outPath']))

                createFileDirs(resDestPath)
                writeBin(resDestPath, info['data'])

                modTime = info['modDate'].timestamp()

                os.utime(resDestPath, (modTime, modTime))

        print(' ')



if __name__ == '__main__':
    merge()