import os
import re
import sys
import shutil
import time
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
GAME_NAME = 'Alan Wake'
SAVE_FILE_PATH = 'G:\\Steam\\userdata\\108850163\\108710\\remote\\savegame.aws'
BASE_BACKUP_DIR = os.path.join(SCRIPT_DIR, 'Game Saves')
GAME_BACKUP_DIR = os.path.join(BASE_BACKUP_DIR, GAME_NAME)


def getModifiedTime (itemPath):
    if not os.path.exists(itemPath):
        return 0

    return int(os.path.getmtime(itemPath))


def getBachups ():
    if not os.path.isdir(GAME_BACKUP_DIR):
        return []

    backups = []

    for item in os.listdir(GAME_BACKUP_DIR):
        itemPath = os.path.join(GAME_BACKUP_DIR, item)

        if not os.path.isfile(itemPath) or not item.lower().endswith('.aws'):
            continue

        baseFileName = os.path.splitext(item)[0]

        nameParts = baseFileName.split('_', maxsplit=3)

        if len(nameParts) != 4 or \
           not nameParts[0].isnumeric() or \
           not nameParts[1].isnumeric() or \
           not nameParts[2].isnumeric():
            continue

        backups.append((
            int(nameParts[0]),
            int(nameParts[1]),
            int(nameParts[2]),
            nameParts[3],
            itemPath
        ))

    return backups


def createBackup ():
    print('Enter name:')

    while True:
        name = input().strip() or 'Unnamed'

        if re.match(r'^[^\\\/\:\*\?\"\<\>\|]+$', name):
            break

        print('Incorrect name. Try again:')

    os.makedirs(GAME_BACKUP_DIR, exist_ok=True)

    backups = sorted(getBachups(), key=lambda item: item[0], reverse=True)

    if backups:
        nextIndex = backups[0][0] + 1
    else:
        nextIndex = 1

    if not os.path.isfile(SAVE_FILE_PATH):
        print('Game save file doesn\'t exist:', SAVE_FILE_PATH)
        return 

    modTs = getModifiedTime(SAVE_FILE_PATH)
    bkpTs = int(time.time())
    ext   = os.path.splitext(SAVE_FILE_PATH)[1]

    bkpFileName = f'{nextIndex:04d}_{ modTs }_{ bkpTs }_{ name }{ ext }'
    bkpFilePath = os.path.join(GAME_BACKUP_DIR, bkpFileName)

    if os.path.isfile(bkpFilePath):
        print('Backup already exists:', bkpFilePath)
        return

    shutil.copy2(SAVE_FILE_PATH, bkpFilePath)

    print('Backup created:', bkpFileName)


def restoreBackup ():
    backups = sorted(getBachups(), key=lambda item: item[0])

    if not backups:
        print('No backups found')
        return 

    print('Select backup:\n')
    print('#     Save date            Backup date          Backup name')
    print('-' * 80)

    for index, modTs, bkpTs, bkpName, bkpFilePath in backups:
        modDate = datetime.fromtimestamp(modTs).strftime('%d-%m-%Y %H:%M:%S')
        bkpDate = datetime.fromtimestamp(bkpTs).strftime('%d-%m-%Y %H:%M:%S')

        print(f'{index:04d}  { modDate }  { bkpDate }  { bkpName }')

    print(' ')

    fileToRestore  = None

    while True:
        indexToRestore = input().strip()

        if indexToRestore.isnumeric():
            indexToRestore = int(indexToRestore)

            for index, modTs, bkpTs, bkpName, bkpFilePath in backups:
                if index == indexToRestore:
                    fileToRestore = bkpFilePath
                    break

            if fileToRestore:
                break            

        print('Incorrect backup. Try again:')

    shutil.copy(fileToRestore, SAVE_FILE_PATH)

    print('Restored:', os.path.basename(fileToRestore))


def exit ():
    sys.exit(0)


def waitCmd (actions):
    print('\nSelect action:')

    for i, (actionName, _) in enumerate(actions):
        print(f'{(i + 1)}. { actionName }')

    print(' ')

    actionIndex = input().strip()

    if not actionIndex.isnumeric():
        print('Unknown action')
        return

    actionIndex = int(actionIndex) - 1

    if not (0 <= actionIndex < len(actions)):
        print('Unknown action')
        return

    actions[actionIndex][1]()


def main ():
    actions = [
        ('Create backup', createBackup),
        ('Restore from backup', restoreBackup),
        ('Exit', exit),
    ]

    print(f'Active game: { GAME_NAME }')

    try:
        while True:
            waitCmd(actions)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()