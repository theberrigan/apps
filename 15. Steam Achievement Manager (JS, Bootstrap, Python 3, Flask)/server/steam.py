import os
import sys
import json
from registry import Registry
from ctypes import CDLL, c_char_p

STEAM_CLIENT_DLL = 'steamclient64.dll'  # or steamclient.dll for 32-bit Python.exe

# https://www.electronjs.org/blog/forge-v6-release
# https://www.electronjs.org/docs/latest/tutorial/using-native-node-modules/

def exit (*args, **kwargs):
    print(*args, **kwargs)
    sys.exit(0)


def findSteamDir ():
    with Registry() as r:
        steamDir = r.openKey('/SOFTWARE/WOW6432Node/Valve/Steam').getValue('InstallPath')
        steamDir = steamDir or r.openKey('/SOFTWARE/Valve/Steam').getValue('InstallPath')

    if steamDir and os.path.isdir(steamDir):
        return os.path.abspath(steamDir)

    return None


def loadSteamClient ():
    steamDir = findSteamDir()

    if not steamDir:
        return None

    libPath = os.path.abspath(os.path.join(steamDir, STEAM_CLIENT_DLL))

    if not os.path.isfile(libPath):
        return None

    try:
        return CDLL(libPath)
    except:
        return None


def toCStr (string):
    return c_char_p(string.encode('utf-8'))


def main ():
    steam = loadSteamClient()

    if not steam:
        exit(f'Failed to load { STEAM_CLIENT_DLL }')

    with open('../misc/steamclient64_interfaces.json', 'r', encoding='utf-8') as f:
        ifaces = json.loads(f.read())

    # print(ifaces)

    for iface in ifaces:
        if steam.CreateInterface(toCStr(iface), 0):
            print(iface)

    # print()


if __name__ == '__main__':
    main()