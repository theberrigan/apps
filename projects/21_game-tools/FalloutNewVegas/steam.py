import os

from utils import *
from vdf import parseVDF
from registry import Registry


PROGRAM_FILES_32_DIR = expandPathVars('%ProgramFiles(x86)%')
PROGRAM_FILES_64_DIR = expandPathVars('%ProgramW6432%')


def findSteamDir ():
    with Registry() as r:
        steamDir = r.openKey(f'/SOFTWARE/WOW6432Node/Valve/Steam').getValue('InstallPath')
        steamDir = steamDir or r.openKey(f'/SOFTWARE/Valve/Steam').getValue('InstallPath')

    if steamDir and isDir(steamDir):
        return getAbsPath(steamDir)

    programFilesDirs = [
        PROGRAM_FILES_32_DIR,
        PROGRAM_FILES_64_DIR
    ]

    for programFilesDir in programFilesDirs:
        steamDir = joinPath(programFilesDir, 'Steam')

        if isFile(joinPath(steamDir, 'steam.exe')):
            return steamDir

    return None


def getSteamLibraries (steamDir = None):
    steamDir = steamDir or findSteamDir()

    result = []

    if not steamDir or not isDir(steamDir):
        return result

    libsConfigPath = joinPath(steamDir, 'steamapps', 'libraryfolders.vdf')

    if not isFile(libsConfigPath):
        return result

    libsConfig = parseVDF(libsConfigPath)

    if not libsConfig:
        return result

    libInfos = libsConfig.get('libraryfolders', {})

    for libInfo in libInfos.values():
        libDir  = libInfo.get('path')
        libApps = libInfo.get('apps', {}).keys()

        if not libDir or not isDir(libDir):
            continue

        libDir = getAbsPath(libDir)

        result.append({
            'libDir':   libDir,
            'gamesDir': joinPath(libDir, 'steamapps', 'common'),
            'appIds':   [ int(appId) for appId in libApps ]
        })

    return result


def getGameDirNameByAppId (appId, steamDir = None):
    steamDir = steamDir or findSteamDir()

    if not steamDir or not isDir(steamDir):
        return None

    manifestPath = joinPath(steamDir, 'steamapps', f'appmanifest_{ appId }.acf')

    if not manifestPath or not isFile(manifestPath):
        return None

    manifest = parseVDF(manifestPath)

    if not manifest:
        return None

    gameDirName = manifest.get('AppState', {}).get('installdir')

    return gameDirName


def findGameDir (appId, gameDirNames=None):
    if gameDirNames is None:
        gameDirNames = []

    gameDir = Registry().openKey(f'/SOFTWARE/Microsoft/Windows/CurrentVersion/Uninstall/Steam App { appId }').getValue('InstallLocation')

    if gameDir and isDir(gameDir):
        return getAbsPath(gameDir)

    steamDir = findSteamDir()

    if not steamDir:
        return None

    gameDirName  = getGameDirNameByAppId(appId, steamDir)
    gameLibInfos = getSteamLibraries(steamDir)

    if not gameLibInfos:
        return None

    libGamesDir = None

    for libInfo in gameLibInfos:
        if appId in libInfo['appIds']:
            libGamesDir = libInfo['gamesDir']
            break

    if libGamesDir and gameDirName:
        gameDir = joinPath(libGamesDir, gameDirName)

        if gameDir and isDir(gameDir):
            return gameDir

    if gameDirName:
        gameDirNames = [ gameDirName ] + gameDirNames

    libGamesDirs = [ info['gamesDir'] for info in gameLibInfos if isDir(info['gamesDir']) ]

    for isExactMatch in [ True, False ]:
        for libGamesDir in libGamesDirs:
            for item in os.listdir(libGamesDir):
                itemPath = joinPath(libGamesDir, item)

                if not isDir(itemPath):
                    continue

                for gameDirName in gameDirNames:
                    itemLC = item.lower()
                    nameLC = gameDirName.lower()

                    if isExactMatch and itemLC == nameLC or not isExactMatch and itemLC.startswith(nameLC):
                        return itemPath

    return None


def __test__ ():
    print(findSteamDir())
    print(toJson(getSteamLibraries()))
    print(getGameDirNameByAppId(22490))
    print(findGameDir(22490, [ 'Fallout New Vegas' ]))


__all__ = [
    'findSteamDir',
    'getSteamLibraries',
    'getGameDirNameByAppId',
    'findGameDir',
]


if __name__ == '__main__':
    __test__()
