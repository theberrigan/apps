# Dishonored Tools

import sys
import struct

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.native.base import loadWinDLL, cCast, cPtr, CWchar, CPtr, CPtrVoid, cSizeOf, cRef, CWStr, CStruct, CU64, CI32, CU8, CF32
from bfw.native.windows import KERNEL32, BYTE, DWORD, LONG, WCHAR, LPDWORD, LPWSTR, LPCVOID, LPVOID, BOOL, MAX_PATH, HANDLE, HMODULE, INVALID_HANDLE_VALUE
from bfw.dll import createBuffer



def decompressSave ():
    data = readBin(r"G:\Steam\userdata\108850163\205100\remote\Dishonored17.sav")

    for i in range(500):
        try:
            data = decompressData(data[i:])
            print(i)
            break
        except:
            pass

    writeBin(r"G:\Steam\userdata\108850163\205100\remote\Dishonored17.sav", data)


def findProcess1 ():
    psLib     = loadWinDLL('psapi.dll')
    kernelLib = loadWinDLL('kernel32.dll')

    psLib.EnumProcesses.restype = BOOL
    psLib.EnumProcesses.argtypes = [
        CPtrVoid,  # arg0: [out] DWORD   *lpidProcess
        DWORD,     # arg1: [in]  DWORD   cb
        LPDWORD,   # arg2: [out] LPDWORD lpcbNeeded
    ]

    psLib.EnumProcessModules.restype = BOOL
    psLib.EnumProcessModules.argtypes = [
        HANDLE,         # arg0: [in]  HANDLE  hProcess
        CPtr(HMODULE),  # arg1: [out] HMODULE *lphModule
        DWORD,          # arg2: [in]  DWORD   cb
        LPDWORD,        # arg3: [out] LPDWORD lpcbNeeded
    ]

    psLib.GetModuleBaseNameW.restype = DWORD
    psLib.GetModuleBaseNameW.argtypes = [
        HANDLE,    # arg0: [in]           HANDLE  hProcess
        HMODULE,   # arg1: [in, optional] HMODULE hModule
        LPWSTR,    # arg2: [out]          LPWSTR  lpBaseName
        DWORD,     # arg3: [in]           DWORD   nSize
    ]

    kernelLib.OpenProcess.restype = HANDLE
    kernelLib.OpenProcess.argtypes = [
        DWORD,  # arg0: [in] DWORD dwDesiredAccess
        BOOL,   # arg1: [in] BOOL  bInheritHandle
        DWORD,  # arg2: [in] DWORD dwProcessId
    ]

    PROCESS_TERMINATE                 = 0x0001
    PROCESS_CREATE_THREAD             = 0x0002
    PROCESS_SET_SESSIONID             = 0x0004
    PROCESS_VM_OPERATION              = 0x0008
    PROCESS_VM_READ                   = 0x0010
    PROCESS_VM_WRITE                  = 0x0020
    PROCESS_DUP_HANDLE                = 0x0040
    PROCESS_CREATE_PROCESS            = 0x0080
    PROCESS_SET_QUOTA                 = 0x0100
    PROCESS_SET_INFORMATION           = 0x0200
    PROCESS_QUERY_INFORMATION         = 0x0400
    PROCESS_SUSPEND_RESUME            = 0x0800
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    PROCESS_SET_LIMITED_INFORMATION   = 0x2000
    PROCESS_ALL_ACCESS                = 0x1FFFFF

    aProcesses = (DWORD * 1024)()
    cbNeeded   = DWORD(0)

    isOk = psLib.EnumProcesses(cRef(aProcesses), cSizeOf(aProcesses), cRef(cbNeeded))

    if not isOk:
        raise Exception('Failed to EnumProcesses')

    cProcesses = cbNeeded.value // cSizeOf(DWORD)

    for i in range(cProcesses):
        processId = aProcesses[i]

        if not processId:
            continue

        szProcessName = CWStr(MAX_PATH)

        hProcess = kernelLib.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, processId)

        if hProcess is None:
            continue

        hMod     = HMODULE()
        cbNeeded = DWORD(0)

        isOk = psLib.EnumProcessModules(hProcess, cRef(hMod), cSizeOf(hMod), cRef(cbNeeded))

        if not isOk:
            print('ERROR: Failed to EnumProcessModules')
            continue

        nameSize = psLib.GetModuleBaseNameW(hProcess, hMod, szProcessName, cSizeOf(szProcessName) // cSizeOf(CWchar))

        if not nameSize:
            print('ERROR: Failed to get process name')
            continue

        processName = szProcessName.value

        if processName.lower() != 'steam.exe':
            continue

        print(szProcessName.value)

        break
        # TODO: CloseHandle(hProcess)


ULONG_PTR = CU64
SIZE_T    = ULONG_PTR

NULL              = 0
MAX_MODULE_NAME32 = 255

TH32CS_SNAPHEAPLIST = 0x00000001
TH32CS_SNAPPROCESS  = 0x00000002
TH32CS_SNAPTHREAD   = 0x00000004
TH32CS_SNAPMODULE   = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
TH32CS_SNAPALL      = TH32CS_SNAPHEAPLIST | TH32CS_SNAPPROCESS | TH32CS_SNAPTHREAD | TH32CS_SNAPMODULE
TH32CS_INHERIT      = 0x80000000

PROCESS_TERMINATE                 = 0x0001
PROCESS_CREATE_THREAD             = 0x0002
PROCESS_SET_SESSIONID             = 0x0004
PROCESS_VM_OPERATION              = 0x0008
PROCESS_VM_READ                   = 0x0010
PROCESS_VM_WRITE                  = 0x0020
PROCESS_DUP_HANDLE                = 0x0040
PROCESS_CREATE_PROCESS            = 0x0080
PROCESS_SET_QUOTA                 = 0x0100
PROCESS_SET_INFORMATION           = 0x0200
PROCESS_QUERY_INFORMATION         = 0x0400
PROCESS_SUSPEND_RESUME            = 0x0800
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_SET_LIMITED_INFORMATION   = 0x2000
PROCESS_ALL_ACCESS                = 0x1FFFFF


class PROCESSENTRY32W (CStruct):
    _fields_ = [
        ('dwSize',              DWORD),
        ('cntUsage',            DWORD),
        ('th32ProcessID',       DWORD),             # this process
        ('th32DefaultHeapID',   ULONG_PTR),
        ('th32ModuleID',        DWORD),             # associated exe
        ('cntThreads',          DWORD),
        ('th32ParentProcessID', DWORD),             # this process's parent process
        ('pcPriClassBase',      LONG),              # Base priority of process's threads
        ('dwFlags',             DWORD),
        ('szExeFile',           WCHAR * MAX_PATH),  # Path
    ]

PROCESSENTRY32    = PROCESSENTRY32W
LPPROCESSENTRY32W = CPtr(PROCESSENTRY32W)
LPPROCESSENTRY32  = CPtr(PROCESSENTRY32)


class MODULEENTRY32W (CStruct):
    _fields_ = [
        ('dwSize',        DWORD),
        ('th32ModuleID',  DWORD),       # This module
        ('th32ProcessID', DWORD),       # owning process
        ('GlblcntUsage',  DWORD),       # Global usage count on the module
        ('ProccntUsage',  DWORD),       # Module usage count in th32ProcessID's context
        ('modBaseAddr',   CPtr(BYTE)),  # Base address of module in th32ProcessID's context
        ('modBaseSize',   DWORD),       # Size in bytes of module starting at modBaseAddr
        ('hModule',       HMODULE),     # The hModule of this module in th32ProcessID's context
        ('szModule',      WCHAR * (MAX_MODULE_NAME32 + 1)),
        ('szExePath',     WCHAR * MAX_PATH),
    ]

MODULEENTRY32    = MODULEENTRY32W
LPMODULEENTRY32W = CPtr(MODULEENTRY32W)
LPMODULEENTRY32  = CPtr(MODULEENTRY32)


def findProcess2 (targetProcessName):
    targetProcessName = targetProcessName.lower()

    k32 = loadWinDLL('kernel32.dll')

    k32.CreateToolhelp32Snapshot.restype = HANDLE
    k32.CreateToolhelp32Snapshot.argtypes = [
        DWORD,  # arg0: [in] DWORD dwFlags
        DWORD,  # arg1: [in] DWORD th32ProcessID
    ]

    k32.Process32NextW.restype = BOOL
    k32.Process32NextW.argtypes = [
        HANDLE,             # arg0: [in]  HANDLE            hSnapshot
        LPPROCESSENTRY32W,  # arg1: [out] LPPROCESSENTRY32W lppe
    ]

    k32.Module32NextW.restype = BOOL
    k32.Module32NextW.argtypes = [
        HANDLE,            # arg0: [in]  HANDLE           hSnapshot
        LPMODULEENTRY32W,  # arg1: [out] LPMODULEENTRY32W lpme
    ]

    k32.OpenProcess.restype = HANDLE
    k32.OpenProcess.argtypes = [
        DWORD,  # arg0: [in] DWORD dwDesiredAccess
        BOOL,   # arg1: [in] BOOL  bInheritHandle
        DWORD,  # arg2: [in] DWORD dwProcessId
    ]

    k32.CloseHandle.restype = BOOL
    k32.CloseHandle.argtypes = [
        HANDLE,  # arg0: [in] HANDLE hObject
    ]

    k32.ReadProcessMemory.restype = BOOL
    k32.ReadProcessMemory.argtypes = [
        HANDLE,   # arg0: [in]  HANDLE  hProcess
        LPCVOID,  # arg1: [in]  LPCVOID lpBaseAddress
        LPVOID,   # arg2: [out] LPVOID  lpBuffer
        SIZE_T,   # arg3: [in]  SIZE_T  nSize
        SIZE_T,   # arg4: [out] SIZE_T  *lpNumberOfBytesRead
    ]

    k32.WriteProcessMemory.restype = BOOL
    k32.WriteProcessMemory.argtypes = [
        HANDLE,   # arg0: [in]  HANDLE  hProcess,
        LPVOID,   # arg1: [in]  LPVOID  lpBaseAddress,
        LPCVOID,  # arg2: [in]  LPCVOID lpBuffer,
        SIZE_T,   # arg3: [in]  SIZE_T  nSize,
        SIZE_T,   # arg4: [out] SIZE_T  *lpNumberOfBytesWritten
    ]

    # ---------------------

    entry = PROCESSENTRY32()

    entry.dwSize = cSizeOf(PROCESSENTRY32)

    snapshot = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)

    if snapshot == INVALID_HANDLE_VALUE:
        raise Exception('Failed to create snapshot')

    processId     = None
    processHandle = None

    while k32.Process32NextW(snapshot, entry):
        if entry.szExeFile.lower() == targetProcessName:            
            processId     = entry.th32ProcessID
            processHandle = k32.OpenProcess(PROCESS_ALL_ACCESS, False, processId)

            if processHandle == NULL:
                raise Exception(f'Failed to open process { processId }')

            break

    if snapshot:
        k32.CloseHandle(snapshot)

    if processId is None:
        raise Exception('Failed to find process')

    # ---------------------

    entry = MODULEENTRY32()

    entry.dwSize = cSizeOf(MODULEENTRY32)

    snapshot = k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, processId)

    if snapshot == INVALID_HANDLE_VALUE:
        raise Exception('Failed to create snapshot')

    moduleAddress = None

    while k32.Module32NextW(snapshot, entry):
        if entry.szModule.lower() == targetProcessName: 
            moduleAddress = entry.modBaseAddr
            break

    if snapshot:
        k32.CloseHandle(snapshot)

    if moduleAddress is None:
        raise Exception('Failed to find process base module address')

    moduleAddress = cCast(moduleAddress, CPtrVoid).value

    # ---------------------

    # https://github.com/Crayfry/Dishonored_Cheat_menu/
    # https://www.playground.ru/dishonored/cheat/dishonored_definitive_edition_tablitsa_dlya_cheat_engine_upd_03_03_2022_paul44-1183752 (Dishonored_v1.4_Released.CT)
    statMap = {    
        0x1C: 'hostiles_killed',
        0x1E: 'civilians_killed',
        0x03: 'alarms_rung',
        0x04: 'bodies_found',
        0x0A: 'ghost',
        0x22: 'runes_found',
        0x27: 'corrupted_charms_found',
        0x24: 'outsider_shrines_found',
        0x25: 'sokolov_paintings_found',
        0x21: 'coins_found',
        0x23: 'bone_charms_found',
    }

    playerOffset = 0x0105F628
    healthOffset = 0x00000344
    # statsOffset  = 0xB70

    pPlayer    = readMemory(processHandle, moduleAddress + playerOffset, CI32(), k32)
    statOffset = readMemory(processHandle, pPlayer.value + 0xB7C, CI32(), k32)
    statCount  = readMemory(processHandle, pPlayer.value + 0xB80, CI32(), k32)
    # health     = readMemory(processHandle, pPlayer.value + healthOffset, CI32(), k32)

    stats = {}

    for i in range(statCount.value):
        offset = 12 * i

        valueOffset = statOffset.value + offset + 4

        statType     = readMemory(processHandle, statOffset.value + offset, CU8(), k32)
        currentValue = readMemory(processHandle, valueOffset, CF32(), k32)
        targetValue  = readMemory(processHandle, statOffset.value + offset + 8, CI32(), k32)

        statKey = statMap[statType.value]

        stats[statKey] = {
            'valueOffset':  valueOffset,
            'currentValue': currentValue.value,
            'targetValue':  targetValue.value,
        }

    valueOffset = stats['ghost']['valueOffset']

    writeMemory(processHandle, valueOffset, CF32(0.0), k32)

    pjp(stats)

    # ---------------------

    if processHandle:
        k32.CloseHandle(processHandle)


def readMemory (processHandle, address, buffer, k32):
    isOk = k32.ReadProcessMemory(processHandle, address, cRef(buffer), cSizeOf(buffer), 0)

    if not isOk:
        raise Exception(f'Failed to read value from address 0x{address:08X}')

    return buffer


def writeMemory (processHandle, address, buffer, k32):
    isOk = k32.WriteProcessMemory(processHandle, address, cRef(buffer), cSizeOf(buffer), 0)

    if not isOk:
        raise Exception(f'Failed to write value to address 0x{address:08X}')

    return buffer



def main ():
    findProcess2('dishonored.exe')


if __name__ == '__main__':
    main()
    