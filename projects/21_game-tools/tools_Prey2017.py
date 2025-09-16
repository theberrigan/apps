# Prey 2017 Tools

import sys
import shutil
import subprocess
import zipfile

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.xml import XMLNode, etree



GAME_DIR      = r'G:\Steam\steamapps\common\Prey'
MOONCRASH_DIR = joinPath(GAME_DIR, 'Whiplash')
BACKUP_DIR    = joinPath(GAME_DIR, '.my', '.backup')
PAK_ROOT_DIR  = joinPath(GAME_DIR, 'GameSDK')
MY_ROOT_DIR   = joinPath(GAME_DIR, '.my')
TOOLS_DIR     = r'D:\Apps\_Categories\Game Tools\Prey'
PC_PATH       = joinPath(TOOLS_DIR, 'PreyConvert.exe')
BXMLD_PATH    = joinPath(TOOLS_DIR, 'BinXMLDecode.exe')
UNLUAC_PATH   = r'D:\Apps\_Categories\Game Tools\unluac\unluac\unluac_1.2.3.530.jar'

BML_SIGNATURE = b'CryXmlB\x00'
ZIP_SIGNATURE = b'PK\x03\x04'



def decrypt (pakPath, bkpPath):
    zipPath = replaceExt(pakPath, '.zip')

    proc = subprocess.run([ PC_PATH, pakPath, zipPath ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = proc.stdout + b' ' + proc.stderr

    if proc.returncode != 0 or b'Successfully created' not in output:
        print('Failed to decrypt:', pakPath)
        print(output.decode('utf-8'))
        print(' ')
        removeFile(zipPath)
        return

    createDirs(getDirPath(bkpPath))

    shutil.move(pakPath, bkpPath)
    shutil.move(zipPath, pakPath)

def decryptAll (rootDir):
    for pakPath in iterFiles(rootDir, True, [ '.pak' ]):
        signature = readBin(pakPath, 4)

        if signature != ZIP_SIGNATURE:
            bkpPath = getRelPath(pakPath, GAME_DIR)
            bkpPath = joinPath(BACKUP_DIR, bkpPath)

            print(pakPath, bkpPath)
            decrypt(pakPath, bkpPath)
            print(' ')

def decrypt2 (pakPath):
    zipPath = replaceExt(pakPath, '.zip')

    proc = subprocess.run([ PC_PATH, pakPath, zipPath ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = proc.stdout + b' ' + proc.stderr

    if proc.returncode != 0 or b'Successfully created' not in output:
        print('Failed to decrypt:', pakPath)
        print(output.decode('utf-8'))
        print(' ')
        removeFile(zipPath)
        return

    removeFile(pakPath)
    shutil.move(zipPath, pakPath)

def decryptAll2 (rootDir):
    for pakPath in iterFiles(rootDir, True, [ '.pak' ]):
        signature = readBin(pakPath, 4)

        if signature != ZIP_SIGNATURE:
            print(pakPath)
            decrypt2(pakPath)
            print(' ')


def decompile (srcPath):
    dstPath = replaceExt(srcPath, '.lua_tmp')

    proc = subprocess.run([ 'java', '-jar', UNLUAC_PATH, '--output', dstPath, srcPath ], stdout=sys.stdout, stderr=sys.stderr)

    if proc.returncode != 0:
        removeFile(dstPath)
        return

    removeFile(srcPath)

    shutil.move(dstPath, srcPath)

def decompileAll (rootDir):
    for srcPath in iterFiles(rootDir, True, [ '.lua' ]):
        signature = readBin(srcPath, 4)

        if b'Lua' in signature:
            print(srcPath)
            decompile(srcPath)
            print(' ')

def decodeXML (srcPath):
    dstPath = replaceExt(srcPath, '.xml_tmp')

    proc = subprocess.run([ BXMLD_PATH, srcPath, dstPath ], stdout=sys.stdout, stderr=sys.stderr)

    if proc.returncode != 0 or not isFile(dstPath) or not getFileSize(dstPath):
        removeFile(dstPath)
        return

    removeFile(srcPath)

    shutil.move(dstPath, srcPath)

def decodeAllXML (rootDir):
    for srcPath in iterFiles(rootDir, True, [ '.xml' ]):
        signature = readBin(srcPath, len(BML_SIGNATURE))

        if signature == BML_SIGNATURE:
            print(srcPath)
            decodeXML(srcPath)
            print(' ')

def extractAll (rootDir):
    for pakPath in iterFiles(rootDir, True, [ '.pak' ]):
        signature = readBin(pakPath, len(ZIP_SIGNATURE))

        if signature == ZIP_SIGNATURE:
            print(pakPath)

            dstDir = replaceExt(pakPath, '.zip')

            try:
                with zipfile.ZipFile(pakPath, 'r') as zf:
                    zf.extractall(dstDir)

                removeFile(pakPath)
            except Exception as e:
                print(e)
                continue

            # return

            print(' ')

def scan (rootDir):
    for filePath in iterFiles(rootDir, True):
        if 'audio' in filePath.lower() or 'music' in filePath.lower():
            print(filePath)


def scan2 (rootDir):
    ids = [ 1059183802 ]
    patterns = []

    for i in ids:
        patterns.append(i.to_bytes(4, 'little'))
        patterns.append(str(i).encode('utf-8'))
        patterns.append(hex(i)[2:].lower().encode('utf-8'))
        patterns.append(hex(i)[2:].upper().encode('utf-8'))

    print(patterns)

    for filePath in iterFiles(rootDir, True, excludeExts=[ '.bk2', '.bik', '.pak' ]):
        data = readBin(filePath)

        for pattern in patterns:
            if pattern in data:
                print(filePath, formatHex(pattern))

def buildAudioPaths ():
    for filePath in iterFiles(r'G:\Steam\steamapps\common\Prey\GameSDK\GameData.zip\Libs\GameAudio', True, [ '.xml' ]):
        node = XMLNode(readBin(filePath))

        if node.getTag() != 'ATLConfig':
            continue

        print(filePath)

        preloads = node.findAll('AudioPreloads/ATLPreloadRequest/ATLConfigGroup/WwiseFile')

        for preload in preloads:
            print(preload.getAttribute('wwise_name'))

        triggers = node.find('AudioTriggers')

        if triggers:
            triggers = triggers.findAll('ATLTrigger')

            print(f'{ len(triggers) } triggers')

            for i, trigger in enumerate(triggers):
                event = trigger.find('WwiseEvent')

                triggerName = trigger.getAttribute('atl_name')
                triggerPath = trigger.getAttribute('path')
                eventName   = event.getAttribute('wwise_name')

                assert '/' not in eventName

                if triggerPath:
                    soundPath = f'{ triggerPath }/{ eventName }'
                else:
                    soundPath = eventName

                # print(f'- { i }.', soundPath, '-' * 50, triggerName)

        print(' ')



def main ():
    # decodeAllXML(GAME_DIR)
    # decompileAll(GAME_DIR)
    # scan(GAME_DIR)
    # scan2(GAME_DIR)
    # decryptAll2(GAME_DIR)
    # decodeXML(r"D:\Apps\_Categories\Game Tools\.Prey\GameSDK\music.xml")
    # extractAll(GAME_DIR)
    buildAudioPaths()



if __name__ == '__main__':
    main()

'''
Apex.bnk              27
Arboretum.bnk         131
Ark_Global.bnk        1281
Ark_Music.bnk         206
Ark_TestBank2.bnk     1
Bridge.bnk            48
CargoBay.bnk          34
CrewFacilities.bnk    95
Cystoid.bnk           59
DeepStorage.bnk       34
End_Game.bnk          41
Exterior.bnk          61
GUTs.bnk              163
g_events_d.bnk        198
Humans.bnk            139
Incubation.bnk        406
LifeSupport.bnk       42
Lobby.bnk             109
Mimic.bnk             295
Nightmare.bnk         102
Operator_Military.bnk 280
Phantom.bnk           255
Physics.bnk           857
Player.bnk            1446
Poltergeist.bnk       51
PowerSource.bnk       61
Prototype.bnk         168
Psychotronics.bnk     166
ShuttleBay.bnk        33
SimLab.bnk            245
Technopath.bnk        72
Telepath.bnk          114
Weaver.bnk            76
'''