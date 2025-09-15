import os
import sys
import struct

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum
from bfw.types.stack import Stack
from bfw.native.limits import U16_BYTES, MAX_U16
from bfw.platform.windows.consts import MS_WINDOWS_LANGS, MS_BUILD_TOOLS_VERSIONS


# TODO:
# - Replace all fields with getters

class PELogLevel (Enum):
    Quiet   = 0
    Error   = 1
    Warning = 2
    Info    = 3


class PELogger:
    def __init__ (self, ctx, level):
        self.ctx   : 'PEParseContext' = ctx
        self.level : PELogLevel       = level

    def _log (self, level, *args, **kwargs):
        message = ' '.join([ str(a) for a in args ])

        if self.ctx.diag is not None:
            self.ctx.diag.append((level, message))

        if self.level >= level:
            print(message, **kwargs)

    def error (self, *args, **kwargs):
        self._log(PELogLevel.Error, '[ERROR]', *args, **kwargs)

    def warn (self, *args, **kwargs):
        self._log(PELogLevel.Warning, '[WARNING]', *args, **kwargs)

    def info (self, *args, **kwargs):
        self._log(PELogLevel.Info, '[INFO]', *args, **kwargs)

# ---------------------------------------------------

class PE:
    def __init__ (self):
        self.filePath       : str | None                   = None
        self.dos            : PEDOSSection | None          = None
        self.fileHeader     : PEFileHeader | None          = None
        self.optionalHeader : PEOptionalHeader | None      = None
        self.sections       : list[PESectionHeader] | None = None

# ---------------------------------------------------


# sizeof(IMAGE_DOS_HEADER)
PE_DOS_HEADER_SIZE      = 64
PE_DOS_HEADER_SIGNATURE = b'MZ'


# IMAGE_DOS_HEADER
class PEDOSHeader:
    def __init__ (self):
        self.signature         : bytes | None     = None
        self.lastPageSize      : int | None       = None
        self.pageCount         : int | None       = None
        self.relocCount        : int | None       = None
        self.parHeaderSize     : int | None       = None
        self.minExtraParCount  : int | None       = None
        self.maxExtraParCount  : int | None       = None
        self.ssRegInitValue    : int | None       = None
        self.spRegInitValue    : int | None       = None
        self.checksum          : int | None       = None
        self.ipRegInitValue    : int | None       = None
        self.csRegInitValue    : int | None       = None
        self.relocTableAddress : int | None       = None
        self.overlayCount      : int | None       = None
        self.reserved          : list[int] | None = None
        self.oemId             : int | None       = None
        self.oemInfo           : int | None       = None
        self.reserved2         : list[int] | None = None
        self.peHeaderOffset    : int | None       = None

    @classmethod
    def _read (cls, f):
        if f.remaining() < PE_DOS_HEADER_SIZE:
            raise Exception('File is too small to contain DOS header')

        header = cls()

        header.signature         = f.read(2)  # WORD e_magic    - Magic number
        header.lastPageSize      = f.u16()    # WORD e_cblp     - Bytes on last page of file
        header.pageCount         = f.u16()    # WORD e_cp       - Pages in file
        header.relocCount        = f.u16()    # WORD e_crlc     - Relocations
        header.parHeaderSize     = f.u16()    # WORD e_cparhdr  - Size of header in paragraphs
        header.minExtraParCount  = f.u16()    # WORD e_minalloc - Minimum extra paragraphs needed
        header.maxExtraParCount  = f.u16()    # WORD e_maxalloc - Maximum extra paragraphs needed
        header.ssRegInitValue    = f.u16()    # WORD e_ss       - Initial (relative) SS value
        header.spRegInitValue    = f.u16()    # WORD e_sp       - Initial SP value
        header.checksum          = f.u16()    # WORD e_csum     - Checksum
        header.ipRegInitValue    = f.u16()    # WORD e_ip       - Initial IP value
        header.csRegInitValue    = f.u16()    # WORD e_cs       - Initial (relative) CS value
        header.relocTableAddress = f.u16()    # WORD e_lfarlc   - File address of relocation table
        header.overlayCount      = f.u16()    # WORD e_ovno     - Overlay number
        header.reserved          = f.u16(4)   # WORD e_res[4]   - Reserved words
        header.oemId             = f.u16()    # WORD e_oemid    - OEM identifier (for e_oeminfo)
        header.oemInfo           = f.u16()    # WORD e_oeminfo  - OEM information; e_oemid specific
        header.reserved2         = f.u16(10)  # WORD e_res2[10] - Reserved words
        header.peHeaderOffset    = f.i32()    # LONG e_lfanew   - File address of new exe header

        if header.signature != PE_DOS_HEADER_SIGNATURE:
            raise Exception(f'Invalid DOS header signature: { header.signature }')

        if header.peHeaderOffset < 0:
            raise Exception(f'Invalid PE header offset: { header.peHeaderOffset }')

        if header.peHeaderOffset < PE_DOS_HEADER_SIZE:
            raise Exception(f'Invalid PE header offset: { header.peHeaderOffset }. It is inside of DOS section [0:{ PE_DOS_HEADER_SIZE }]')

        if header.peHeaderOffset >= f.getSize():
            raise Exception(f'Invalid PE header offset: { header.peHeaderOffset }. It is greater than file size: { f.getSize() }')

        return header


class PEToolInfo:
    def __init__ (self):
        self.version    : int | None = None
        self.minVersion : int | None = None
        self.id         : int | None = None
        self.count      : int | None = None
        self.name       : str | None = None


PE_DOS_STANDARD_PROGRAM      = b'\x0E\x1F\xBA\x0E\x00\xB4\x09\xCD\x21\xB8\x01\x4C\xCD\x21\x54\x68\x69\x73\x20\x70\x72\x6F\x67\x72\x61\x6D\x20\x63\x61\x6E\x6E\x6F\x74\x20\x62\x65\x20\x72\x75\x6E\x20\x69\x6E\x20\x44\x4F\x53\x20\x6D\x6F\x64\x65\x2E\x0D\x0D\x0A\x24\x00\x00\x00\x00\x00\x00\x00'
PE_DOS_STANDARD_PROGRAM_SIZE = len(PE_DOS_STANDARD_PROGRAM)


# DOS header + DOS program + [ rich header ]
# https://0xrick.github.io/win-internals/pe3/
# https://securelist.com/the-devils-in-the-rich-header/84348/
# https://www.ntcore.com/files/richsign.htm
# http://mirror.sweon.net/madchat/vxdevl/vxmags/29a-8/Articles/29A-8.009
class PEDOSSection:
    def __init__ (self):
        self._header            : PEDOSHeader | None      = None
        self._program           : bytes | None            = None
        self._programSize       : int | None              = None
        self._isProgramStandard : bool | None             = None
        self._tailData          : bytes | None            = None
        self._toolsInfo         : list[PEToolInfo] | None = None

    @classmethod
    def _read (cls, ctx : 'PEParseContext') -> 'PEDOSSection':
        f   = ctx.file
        log = ctx.log

        section : PEDOSSection = cls()

        section._header = PEDOSHeader._read(f)

        peHeaderOffset = section._header.peHeaderOffset

        tailStart = f.tell()
        tailSize  = peHeaderOffset - tailStart

        section._program           = None
        section._programSize       = None
        section._isProgramStandard = None
        section._tailData          = None
        section._toolsInfo         = None

        if tailSize:
            section._tailData = tail = f.read(tailSize)

            if tailSize == PE_DOS_STANDARD_PROGRAM_SIZE and tail == PE_DOS_STANDARD_PROGRAM:
                section._program           = tail
                section._programSize       = tailSize
                section._isProgramStandard = True
            elif tailSize:
                richOffset = tail.rfind(b'Rich')

                if richOffset > -1 and (tailSize - richOffset) >= 8:
                    richEnd  = richOffset + 8
                    richData = bytearray(richOffset)
                    key      = tail[richOffset + 4:richEnd]
                    keyByte  = (4 - (richOffset % 4)) % 4

                    for i in range(richOffset):
                        richData[i] = tail[i] ^ key[keyByte]
                        keyByte = (keyByte + 1) % 4

                    dansStart = richData.rfind(b'DanS')

                    if dansStart > -1:
                        section._program           = tail[:dansStart]
                        section._programSize       = dansStart
                        section._isProgramStandard = section._program == PE_DOS_STANDARD_PROGRAM

                        richData = tail[dansStart:richEnd]
                        richSize = len(richData)

                        if richSize % 2 == 0:
                            with MemReader(richData) as f2:
                                signature = f2.u32()
                                checksum  = f2.u32()
                                checksum2 = f2.u32()
                                checksum3 = f2.u32()

                                dans = 0x536E6144
                                rich = 0x68636952

                                if signature ^ checksum == dans and checksum == checksum2 == checksum3:
                                    section._toolsInfo = toolsInfo = []

                                    for i in range(richSize // 2):
                                        toolVersion = f2.u32()
                                        toolCount   = f2.u32()

                                        if toolVersion == rich:
                                            if toolCount != checksum:
                                                log.warn('Rich header is corrupted')
                                                section._toolsInfo = None

                                            break

                                        toolVersion ^= checksum
                                        toolCount   ^= checksum

                                        toolMinVersion = toolVersion & 0xFFFF
                                        toolId         = (toolVersion >> 16) & 0xFFFF

                                        toolInfo : PEToolInfo = PEToolInfo()

                                        toolInfo.version    = toolVersion
                                        toolInfo.minVersion = toolMinVersion
                                        toolInfo.id         = toolId
                                        toolInfo.count      = toolCount
                                        toolInfo.name       = MS_BUILD_TOOLS_VERSIONS.get(toolVersion, None)

                                        toolsInfo.append(toolInfo)
                                else:
                                    log.warn('Rich header is corrupted')
                        else:
                            log.warn('Rich header size is not a multiple of 2')
                    else:
                        log.warn('DanS signature is not found in the decrypted rich header')

        return section

    @property
    def header (self):
        return self._header

    @property
    def hasProgram (self):
        return self._program is not None

    @property
    def program (self):
        return self._program

    @property
    def programSize (self):
        return self._programSize

    @property
    def isProgramStandard (self):
        return self._isProgramStandard

    @property
    def tailData (self):
        return self._tailData

    @property
    def toolsInfo (self):
        return self._toolsInfo


# What hardware platform is Windows currently running on
# IMAGE_FILE_MACHINE_*
class PEMachineType (Enum):
    UNKNOWN     = 0
    TARGET_HOST = 0x0001  # Useful for indicating we want to interact with the host and not a WoW guest.
    I386        = 0x014c  # Intel 386 (x86)
    R3000       = 0x0162  # MIPS little-endian, 0x160 big-endian
    R4000       = 0x0166  # MIPS little-endian
    R10000      = 0x0168  # MIPS little-endian
    WCEMIPSV2   = 0x0169  # MIPS little-endian WCE v2
    ALPHA       = 0x0184  # Alpha_AXP
    SH3         = 0x01a2  # SH3 little-endian
    SH3DSP      = 0x01a3
    SH3E        = 0x01a4  # SH3E little-endian
    SH4         = 0x01a6  # SH4 little-endian
    SH5         = 0x01a8  # SH5
    ARM         = 0x01c0  # ARM Little-Endian
    THUMB       = 0x01c2  # ARM Thumb/Thumb-2 Little-Endian
    ARMNT       = 0x01c4  # ARM Thumb-2 Little-Endian
    AM33        = 0x01d3
    POWERPC     = 0x01F0  # IBM PowerPC Little-Endian
    POWERPCFP   = 0x01f1
    IA64        = 0x0200  # Intel 64
    MIPS16      = 0x0266  # MIPS
    ALPHA64     = 0x0284  # ALPHA64
    MIPSFPU     = 0x0366  # MIPS
    MIPSFPU16   = 0x0466  # MIPS
    AXP64       = ALPHA64
    TRICORE     = 0x0520  # Infineon
    CEF         = 0x0CEF
    EBC         = 0x0EBC  # EFI Byte Code
    AMD64       = 0x8664  # AMD64 (K8) (x64)
    M32R        = 0x9041  # M32R little-endian
    ARM64       = 0xAA64  # ARM64 Little-Endian
    CEE         = 0xC0EE


# sizeof(IMAGE_FILE_HEADER)
PE_FILE_HEADER_SIZE = 20


# IMAGE_FILE_HEADER
class PEFileHeader:
    def __init__ (self):
        self.machine            : int | None = None
        self.sectionCount       : int | None = None
        self.timestamp          : int | None = None
        self.symbolTableOffset  : int | None = None
        self.symbolCount        : int | None = None
        self.optionalHeaderSize : int | None = None
        self.characteristics    : int | None = None

    @classmethod
    def read (cls, f):
        header = cls()

        if f.remaining() < PE_FILE_HEADER_SIZE:
            raise Exception('Remaining file size is too small to contain a file header')

        _headerStart = f.tell()

        header.machine            = f.u16()  # WORD  Machine              - The number that identifies the type of target machine (see PEMachineType)
        header.sectionCount       = f.u16()  # WORD  NumberOfSections     - Indicates the size of the section table, which immediately follows the headers (windows loader limits it to 96)
        header.timestamp          = f.u32()  # DWORD TimeDateStamp        - The low 32 bits of the number of seconds since 00:00 January 1, 1970 (a C run-time time_t value), which indicates when the file was created.
        header.symbolTableOffset  = f.u32()  # DWORD PointerToSymbolTable - The file offset of the COFF symbol table, or zero if no COFF symbol table is present. This value should be zero for an image because COFF debugging information is deprecated.
        header.symbolCount        = f.u32()  # DWORD NumberOfSymbols      - This data can be used to locate the string table, which immediately follows the symbol table. This value should be zero for an image because COFF debugging information is deprecated.
        header.optionalHeaderSize = f.u16()  # WORD  SizeOfOptionalHeader - The size of the optional header, which is required for executable files but not for object files. This value should be zero for an object file.
        header.characteristics    = f.u16()  # WORD  Characteristics      - The flags that indicate the attributes of the file. (see PEFileHeaderFlag)

        assert (_headerStart + PE_FILE_HEADER_SIZE) == f.tell()

        if not PEMachineType.hasValue(header.machine):
            raise Exception(f'Invalid machine type in file header: { header.machine }')

        return header


# IMAGE_NT_OPTIONAL_HDR*_MAGIC
class PEOptionalHeaderSignature (Enum):
    # ROM = 0x107
    PE32  = 0x10b
    PE32P = 0x20b


# IMAGE_SUBSYSTEM_*
class PESubSystemType (Enum):
    UNKNOWN                  = 0   # An unknown subsystem
    NATIVE                   = 1   # Image doesn't require a subsystem. Device drivers and native Windows processes
    WINDOWS_GUI              = 2   # Image runs in the Windows GUI subsystem.
    WINDOWS_CUI              = 3   # Image runs in the Windows character subsystem.
    OS2_CUI                  = 5   # image runs in the OS/2 character subsystem.
    POSIX_CUI                = 7   # image runs in the Posix character subsystem.
    NATIVE_WINDOWS           = 8   # image is a native Win9x driver.
    WINDOWS_CE_GUI           = 9   # Image runs in the Windows CE subsystem.
    EFI_APPLICATION          = 10  # An Extensible Firmware Interface (EFI) application
    EFI_BOOT_SERVICE_DRIVER  = 11  # An EFI driver with boot services
    EFI_RUNTIME_DRIVER       = 12  # An EFI driver with run-time services
    EFI_ROM                  = 13  # An EFI ROM image
    XBOX                     = 14  # XBOX
    WINDOWS_BOOT_APPLICATION = 16  # Windows boot application.
    XBOX_CODE_CATALOG        = 17


# IMAGE_NUMBEROF_DIRECTORY_ENTRIES
PE_DIR_ENTRY_MAX_COUNT  = 16
PE_DIR_ENTRY_SIZE       = 8
PE_DIR_ENTRIES_MAX_SIZE = PE_DIR_ENTRY_SIZE * PE_DIR_ENTRY_MAX_COUNT

# sizeof(IMAGE_OPTIONAL_HEADER32)
PE_OPT_HEADER32_MAX_SIZE = 224
PE_OPT_HEADER32_MIN_SIZE = PE_OPT_HEADER32_MAX_SIZE - PE_DIR_ENTRIES_MAX_SIZE

# sizeof(IMAGE_OPTIONAL_HEADER64)
PE_OPT_HEADER64_MAX_SIZE = 240
PE_OPT_HEADER64_MIN_SIZE = PE_OPT_HEADER64_MAX_SIZE - PE_DIR_ENTRIES_MAX_SIZE


# IMAGE_DATA_DIRECTORY
class PEDirEntry:
    def __init__ (self):
        self.virtualAddress = None
        self.size           = None

    @classmethod
    def read (cls, f):
        entry = cls()

        entry.virtualAddress = f.u32()  # DWORD VirtualAddress
        entry.size           = f.u32()  # DWORD Size

        return entry


# TODO: support partial reading (pefile.py:3149)
# IMAGE_OPTIONAL_HEADER[32|64]
class PEOptionalHeader:
    def __init__ (self):
        self.is32               : bool | None             = None
        self.signature          : int | None              = None
        self.linkerMajorVersion : int | None              = None
        self.linkerMinorVersion : int | None              = None
        self.codeSize           : int | None              = None
        self.initDataSize       : int | None              = None
        self.uninitDataSize     : int | None              = None
        self.entryPointOffset   : int | None              = None
        self.codeOffset         : int | None              = None
        self.dataOffset         : int | None              = None
        self.imageBaseOffset    : int | None              = None
        self.sectionAlignment   : int | None              = None
        self.fileAlignment      : int | None              = None
        self.osMajorVersion     : int | None              = None
        self.osMinorVersion     : int | None              = None
        self.imageMajorVersion  : int | None              = None
        self.imageMinorVersion  : int | None              = None
        self.subSysMajorVersion : int | None              = None
        self.subSysMinorVersion : int | None              = None
        self.win32Version       : int | None              = None
        self.imageSize          : int | None              = None
        self.headersSize        : int | None              = None
        self.imageChecksum      : int | None              = None
        self.subSys             : int | None              = None
        self.dllCharacteristics : int | None              = None
        self.stackReserveSize   : int | None              = None
        self.stackCommitSize    : int | None              = None
        self.heapReserveSize    : int | None              = None
        self.heapCommitSize     : int | None              = None
        self.loaderFlags        : int | None              = None
        self.dirEntryCount      : int | None              = None
        self.dirEntries         : list[PEDirEntry] | None = None

    @classmethod
    def read (cls, ctx):
        f          = ctx.file
        log        = ctx.log
        headerSize = ctx.pe.fileHeader.optionalHeaderSize

        header = cls()

        if f.remaining() < U16_BYTES:
            raise Exception('Remaining file size is not large enough to contain an optional header')

        headerStartRem = f.remaining()
        headerStart    = f.tell()
        headerEnd      = headerStart + headerSize

        header.signature = f.u16()  # WORD Magic (see PEOptionalHeaderSignature)

        if header.signature == PEOptionalHeaderSignature.PE32:
            header.is32   = True
            minHeaderSize = PE_OPT_HEADER32_MIN_SIZE
        elif header.signature == PEOptionalHeaderSignature.PE32P:
            header.is32   = False
            minHeaderSize = PE_OPT_HEADER64_MIN_SIZE
        else:
            raise Exception(f'Invalid optional header signature ({ header.signature }), expected one of { PEOptionalHeaderSignature.__name__ }')

        if headerSize < minHeaderSize:
            raise Exception(f'Requested header size ({ headerSize }) is less than the minimum optional header size ({ minHeaderSize })')

        if headerStartRem < minHeaderSize:
            raise Exception(f'Remaining file size ({ headerStartRem }) is less than the minimum optional header size ({ minHeaderSize })')

        header.linkerMajorVersion = f.u8()   # BYTE  MajorLinkerVersion       - The linker major version number
        header.linkerMinorVersion = f.u8()   # BYTE  MinorLinkerVersion       - The linker minor version number.
        header.codeSize           = f.u32()  # DWORD SizeOfCode               - The size of the code (text) section, or the sum of all code sections if there are multiple sections.
        header.initDataSize       = f.u32()  # DWORD SizeOfInitializedData    - The size of the initialized data section, or the sum of all such sections if there are multiple data sections.
        header.uninitDataSize     = f.u32()  # DWORD SizeOfUninitializedData  - The size of the uninitialized data section (BSS), or the sum of all such sections if there are multiple BSS sections.
        header.entryPointOffset   = f.u32()  # DWORD AddressOfEntryPoint      - The address of the entry point relative to the image base when the executable file is loaded into memory. For program images, this is the starting address. For device drivers, this is the address of the initialization function. An entry point is optional for DLLs. When no entry point is present, this field must be zero.
        header.codeOffset         = f.u32()  # DWORD BaseOfCode               - The address that is relative to the image base of the beginning-of-code section when it is loaded into memory.

        if header.is32:
            header.dataOffset      = f.u32()  # DWORD BaseOfData - The address that is relative to the image base of the beginning-of-data section when it is loaded into memory.
            header.imageBaseOffset = f.u32()  # DWORD ImageBase  - The preferred address of the first byte of image when loaded into memory; must be a multiple of 64 K. The default for DLLs is 0x10000000. The default for Windows CE EXEs is 0x00010000. The default for Windows NT, Windows 2000, Windows XP, Windows 95, Windows 98, and Windows Me is 0x00400000.
        else:
            header.dataOffset      = None
            header.imageBaseOffset = f.u64()  # ULONGLONG ImageBase - The preferred address of the first byte of image when loaded into memory; must be a multiple of 64 K. The default for DLLs is 0x10000000. The default for Windows CE EXEs is 0x00010000. The default for Windows NT, Windows 2000, Windows XP, Windows 95, Windows 98, and Windows Me is 0x00400000.

        header.sectionAlignment   = f.u32()  # DWORD SectionAlignment            - The alignment (in bytes) of sections when they are loaded into memory. It must be greater than or equal to FileAlignment. The default is the page size for the architecture.
        header.fileAlignment      = f.u32()  # DWORD FileAlignment               - The alignment factor (in bytes) that is used to align the raw data of sections in the image file. The value should be a power of 2 between 512 and 64K, inclusive. The default is 512. If the SectionAlignment is less than the architecture's page size, then FileAlignment must match SectionAlignment.
        header.osMajorVersion     = f.u16()  # WORD  MajorOperatingSystemVersion - The major version number of the required operating system.
        header.osMinorVersion     = f.u16()  # WORD  MinorOperatingSystemVersion - The minor version number of the required operating system.
        header.imageMajorVersion  = f.u16()  # WORD  MajorImageVersion           - The major version number of the image.
        header.imageMinorVersion  = f.u16()  # WORD  MinorImageVersion           - The minor version number of the image.
        header.subSysMajorVersion = f.u16()  # WORD  MajorSubsystemVersion       - The major version number of the subsystem.
        header.subSysMinorVersion = f.u16()  # WORD  MinorSubsystemVersion       - The minor version number of the subsystem.
        header.win32Version       = f.u32()  # DWORD Win32VersionValue           - Reserved, must be zero.
        header.imageSize          = f.u32()  # DWORD SizeOfImage                 - The size (in bytes) of the image, including all headers, as the image is loaded in memory. It must be a multiple of SectionAlignment.
        header.headersSize        = f.u32()  # DWORD SizeOfHeaders               - The combined size of an MS-DOS stub, PE header, and section headers rounded up to a multiple of FileAlignment.
        header.imageChecksum      = f.u32()  # DWORD CheckSum                    - The image file checksum. The algorithm for computing the checksum is incorporated into IMAGHELP.DLL. The following are checked for validation at load time: all drivers, any DLL loaded at boot time, and any DLL that is loaded into a critical Windows process.
        header.subSys             = f.u16()  # WORD  Subsystem                   - The subsystem that is required to run this image (see PESubSystemType)
        header.dllCharacteristics = f.u16()  # WORD  DllCharacteristics          - see PEDLLFlag

        if not PESubSystemType.hasValue(header.subSys):
            raise Exception(f'Invalid optional header subsystem { header.subSys }, expected one of { PESubSystemType.__name__ }')

        if header.is32:
            header.stackReserveSize = f.u32()  # DWORD SizeOfStackReserve - The size of the stack to reserve. Only SizeOfStackCommit is committed; the rest is made available one page at a time until the reserve size is reached.
            header.stackCommitSize  = f.u32()  # DWORD SizeOfStackCommit  - The size of the stack to commit.
            header.heapReserveSize  = f.u32()  # DWORD SizeOfHeapReserve  - The size of the local heap space to reserve. Only SizeOfHeapCommit is committed; the rest is made available one page at a time until the reserve size is reached.
            header.heapCommitSize   = f.u32()  # DWORD SizeOfHeapCommit   - The size of the local heap space to commit.
        else:
            header.stackReserveSize = f.u64()  # ULONGLONG SizeOfStackReserve - The size of the stack to reserve. Only SizeOfStackCommit is committed; the rest is made available one page at a time until the reserve size is reached.
            header.stackCommitSize  = f.u64()  # ULONGLONG SizeOfStackCommit  - The size of the stack to commit.
            header.heapReserveSize  = f.u64()  # ULONGLONG SizeOfHeapReserve  - The size of the local heap space to reserve. Only SizeOfHeapCommit is committed; the rest is made available one page at a time until the reserve size is reached.
            header.heapCommitSize   = f.u64()  # ULONGLONG SizeOfHeapCommit   - The size of the local heap space to commit.

        header.loaderFlags   = f.u32()  # DWORD LoaderFlags         - Reserved, must be zero
        header.dirEntryCount = f.u32()  # DWORD NumberOfRvaAndSizes - The number of data-directory entries in the remainder of the optional header. Each describes a location and size.

        if header.dirEntryCount > PE_DIR_ENTRY_MAX_COUNT:
            log.warn(f'Data directory entry count ({ header.dirEntryCount }) is greater than PE_DIR_ENTRY_MAX_COUNT ({ PE_DIR_ENTRY_MAX_COUNT })')

        # PE_DIR_ENTRY_MAX_COUNT
        dirEntrySize = header.dirEntryCount * PE_DIR_ENTRY_SIZE
        headerRem    = headerEnd - f.tell()
        fileRem      = f.remaining()

        if headerRem < dirEntrySize:
            raise Exception(f'Remaining optional header size ({ headerRem }) is not large enough to contain { header.dirEntryCount } directory entries of total size { dirEntrySize } bytes')

        if fileRem < dirEntrySize:
            raise Exception(f'Remaining file size ({ headerRem }) is not large enough to contain { header.dirEntryCount } directory entries of total size { dirEntrySize } bytes')

        # TODO: correctly read directory data beyond PE_DIR_ENTRY_MAX_COUNT pefile.py:3259
        maxDirEntryCount = max(header.dirEntryCount, PE_DIR_ENTRY_MAX_COUNT)

        header.dirEntries = [ None ] * maxDirEntryCount  # IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES] - Each data directory gives the address and size of a table or string that Windows uses.

        for i in range(header.dirEntryCount):
            # noinspection PyTypeChecker
            header.dirEntries[i] = PEDirEntry.read(f)

        assert f.tell() == headerEnd

        # TODO:
        # if header.entryPointOffset < header.headersSize:
        #     log.warn('SizeOfHeaders is smaller than AddressOfEntryPoint: this file cannot run under Windows 8')

        return header


# sizeof(IMAGE_SECTION_HEADER)
PE_SECTION_HEADER_SIZE = 40

# IMAGE_SIZEOF_SHORT_NAME
PE_SECTION_HEADER_NAME_SIZE = 8

# https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#special-sections
# https://0xrick.github.io/win-internals/pe5/#sections
# IMAGE_SECTION_HEADER
class PESectionHeader:
    def __init__ (self):
        self.name           = None
        self.virtualSize    = None
        self.virtualAddress = None
        self.rawDataSize    = None
        self.rawDataPtr     = None
        self.relocsPtr      = None
        self.lineNumsPtr    = None
        self.relocCount     = None
        self.lineNumsCount  = None
        self.flags          = None

    @classmethod
    def read (cls, f):
        header = cls()

        if f.remaining() < PE_SECTION_HEADER_SIZE:
            raise Exception('Remaining file size is not large enough to contain one more section header')

        header.name           = f.string(PE_SECTION_HEADER_NAME_SIZE)  # BYTE  Name[IMAGE_SIZEOF_SHORT_NAME] - An 8-byte, null-padded UTF-8 encoded string. If the string is exactly 8 characters long, there is no terminating null. For longer names, this field contains a slash (/) that is followed by an ASCII representation of a decimal number that is an offset into the string table. Executable images do not use a string table and do not support section names longer than 8 characters. Long names in object files are truncated if they are emitted to an executable file.
        header.virtualSize    = f.u32()                                # DWORD VirtualSize                   - The total size of the section when loaded into memory. If this value is greater than SizeOfRawData, the section is zero-padded. This field is valid only for executable images and should be set to zero for object files.
        header.virtualAddress = f.u32()                                # DWORD VirtualAddress                - For executable images, the address of the first byte of the section relative to the image base when the section is loaded into memory. For object files, this field is the address of the first byte before relocation is applied; for simplicity, compilers should set this to zero. Otherwise, it is an arbitrary value that is subtracted from offsets during relocation
        header.rawDataSize    = f.u32()                                # DWORD SizeOfRawData                 - The size of the section (for object files) or the size of the initialized data on disk (for image files). For executable images, this must be a multiple of FileAlignment from the optional header. If this is less than VirtualSize, the remainder of the section is zero-filled. Because the SizeOfRawData field is rounded but the VirtualSize field is not, it is possible for SizeOfRawData to be greater than VirtualSize as well. When a section contains only uninitialized data, this field should be zero.
        header.rawDataPtr     = f.u32()                                # DWORD PointerToRawData              - The file pointer to the first page of the section within the COFF file. For executable images, this must be a multiple of FileAlignment from the optional header. For object files, the value should be aligned on a 4-byte boundary for best performance. When a section contains only uninitialized data, this field should be zero.
        header.relocsPtr      = f.u32()                                # DWORD PointerToRelocations          - The file pointer to the beginning of relocation entries for the section. This is set to zero for executable images or if there are no relocations.
        header.lineNumsPtr    = f.u32()                                # DWORD PointerToLinenumbers          - The file pointer to the beginning of line-number entries for the section. This is set to zero if there are no COFF line numbers. This value should be zero for an image because COFF debugging information is deprecated.
        header.relocCount     = f.u16()                                # WORD  NumberOfRelocations           - The number of relocation entries for the section. This is set to zero for executable images.
        header.lineNumsCount  = f.u16()                                # WORD  NumberOfLinenumbers           - The number of line-number entries for the section. This value should be zero for an image because COFF debugging information is deprecated.
        header.flags          = f.u32()                                # DWORD Characteristics               - The flags that describe the characteristics of the section (see PESectionFlag)

        # TODO:
        # - virtualSize is not larger than 256MiB
        # - aligned virtual size is not beyond 0x10000000 (:3609)
        # - pointer to raw data is aligned with fileAlignment
        # - check flags IMAGE_SCN_MEM_WRITE and IMAGE_SCN_MEM_EXECUTE are not set together
        # - raw and virtually are not overlapping
        # -----
        # - check section meta is not nulled
        # - raw data inside of the file and not truncated

        return header

class PEMemory:
    def __init__ (self, data : bytearray):
        self.f : Reader = MemReader(data)

    @classmethod
    def _load (cls, ctx : 'PEParseContext') -> 'PEMemory':
        f  = ctx.file
        pe = ctx.pe

        data = bytearray(pe.optionalHeader.imageSize)

        f.seek(0)

        headersSize = pe.optionalHeader.headersSize

        data[0:headersSize] = f.read(headersSize)

        for section in pe.sections:
            f.seek(section.rawDataPtr)

            dataSize = min(section.rawDataSize, section.virtualSize)
            dstStart = section.virtualAddress
            dstEnd   = dstStart + dataSize

            data[dstStart:dstEnd] = f.read(dataSize)

            if dataSize < section.virtualSize:
                padSize = section.virtualSize - dataSize

                data[dstEnd:dstEnd + padSize] = b'\x00' * padSize

        return cls(data)

# ------------------------------------------------------------------------------------------------

class PEParseContext:
    def __init__ (self):
        self.file : Reader | None   = None
        self.pe   : PE | None       = None
        self.log  : PELogger | None = None
        self.diag : list | None     = None


class PEParseResult:
    def __init__ (self):
        # TODO: define types
        self.isOk        : bool | None = None
        self.pe          : PE | None   = None
        self.diagnostics : list | None = None


PE_SIGNATURE = b'PE\x00\x00'


class PEParser:
    @classmethod
    def fromFile (cls, filePath, logLevel=PELogLevel.Warning, collectDiagnostics=False):
        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        with openFile(filePath, readerType=ReaderType.FS) as f:
            return cls._parse(f, filePath, logLevel, collectDiagnostics)

    @classmethod
    def fromBuffer (cls, data, logLevel=PELogLevel.Warning, collectDiagnostics=False, filePath=None):
        with MemReader(data, filePath=filePath) as f:
            return cls._parse(f, filePath, logLevel, collectDiagnostics)

    @classmethod
    def _parse (cls, f, filePath, logLevel, collectDiagnostics):
        ctx = PEParseContext()

        ctx.file = f
        ctx.pe   = pe  = PE()
        ctx.log  = log = PELogger(ctx, logLevel)

        if collectDiagnostics:
            ctx.diag = []
        else:
            ctx.diag = None

        if isStr(filePath):
            pe.filePath = getAbsPath(filePath)
        else:
            pe.filePath = None

        result = PEParseResult()

        try:
            cls._read(ctx)

            result.isOk = True
            result.pe   = pe
        except Exception as e:
            log.error(str(e))

            result.isOk = False
            result.pe   = None

        if collectDiagnostics:
            result.diagnostics = ctx.diag

        return result

    @classmethod
    def _read (cls, ctx : PEParseContext):
        f  = ctx.file
        pe = ctx.pe

        pe.dos = PEDOSSection._read(ctx)

        f.seek(pe.dos.header.peHeaderOffset)

        signature = f.read(4)  # DWORD Signature

        # Some malware will cause the Signature value to not exist at all
        # TODO: check sub-signature pefile.py:3102
        if signature != PE_SIGNATURE:
            raise Exception(f'Invalid PE signature ({ signature }), expected { PE_SIGNATURE }')

        pe.fileHeader     = PEFileHeader.read(f)        # IMAGE_FILE_HEADER FileHeader
        pe.optionalHeader = PEOptionalHeader.read(ctx)  # IMAGE_OPTIONAL_HEADER[32|64]
        pe.sections       = [ PESectionHeader.read(f) for _ in range(pe.fileHeader.sectionCount) ]  # this offset calculated by IMAGE_FIRST_SECTION
        pe.mem            = PEMemory._load(ctx)



def _test_ ():
    # PEParser.fromFile(r"C:\Program Files\Adobe\Adobe Premiere Pro 2023\CEP\extensions\com.adobe.frameio\bin\FrameioHelper.exe")
    # exit()

    # PEParser.fromFile(r"C:\Projects\_Data_Samples\pe\dll\tk86__many_resources.dll")
    # exit()

    # PEParser.fromFile(r"G:\Games\Call Of Duty 2\COD2.exe")
    # exit()

    for rootDir in [
        r'C:\Projects\_Data_Samples\pe',
        r'C:\Python\3.11_x64',
        r'G:\Steam\steamapps\common\ZombieArmy4',
        r'G:\Games',
    ]:
    # for rootDir in getDrives(True):
        for filePath in iterFiles(rootDir, True, ['.exe', '.dll', '.asi', '.pyd']):
            print(filePath)

            PEParser.fromFile(filePath, logLevel=PELogLevel.Info)

            print(' ')
            # exit()


__all__ = [
    'PEParser',
    'PE',
]

if __name__ == '__main__':
    _test_()

