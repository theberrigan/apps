import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum2
from bfw.types.stack import Stack
from bfw.native.limits import U16_BYTES
from bfw.platform.windows.consts import MS_WINDOWS_LANGS



# Docs:
# - Microsoft PE & COFF (1999).pdf
# - Microsoft PE & COFF (2006).pdf
# - Microsoft PE (MSDN, 2024).pdf
# - https://rsdn.org/article/baseserv/peloader.xml
# - https://0xrick.github.io/win-internals/pe1/
# - https://www.ambray.dev/writing-a-windows-loader/
# - SEH: https://learn.microsoft.com/en-us/cpp/cpp/structured-exception-handling-c-cpp?view=msvc-170
# - Rich Header: https://www.ntcore.com/files/richsign.htm

# PE   - exe/dll - image file
# COFF - obj     - object file, is given as input to the linker, which produces an image file
# Timestamps have the same format as that used by the time functions in C
# file pointer - offset in the file on disk
# RVA - in PE: address of an item after image is loaded to memory, relative to base address of an image
# VA - absolute address of an item after image is loaded to memory
# ----------------
# Physical Address - real address of data in RAM
# Virtual Address  - address of the data in the virtual space of the process
# Base Address     - VA of the beginning of the PE file in memory
# Relative VA      - virtual address of the data relative to the beginning of the PE file in memory

# OptHdr.SizeOfImage - total size of image in memory after loading PE into it
# OptHdr.SizeOfHeaders - total size of all headers in PE, aligned by fileAlignment

# Loading PE:
# 1. Allocate Space - We will need to allocate memory that can match both the size and protection requirements of the sections of our binary
# 2. Copy Data - We need to copy the data from our binary to the allocated space, adjusting file offsets to Virtual Addresses as we go.
# 3. Handle Relocations - We must adjust references after copying our data.
# 4. Resolve Imports - Generally, binaries need to be linked dynamically to other libraries in order to interact with the operating system at runtime.
# 5. TLS Callbacks - We will find and invoke the TLS Callbacks - an array of functions that are invoked prior to the application's entry point.
# 6. Finally, we will locate and invoke the binary's entry point. We will discuss some differences here between DLLs and Executables.

# WORD  == unsigned short == uint16_t
# DWORD == unsigned long  == uint32_t
# BOOL  == int
# LONG  == long == int32_t

# DOS Header and Stub:
# - signature (b'MZ')
# - ...
# - offset to PE signature
# PE Signature (b'PE\x00\x00')
# [COFF] File Header
# - machine            - see PEMachineType
# - sectionCount       - max 96 (see below)
# - timestamp          - when the file was created
# - symbolTableOffset  - [DEPRECATED, should be 0] file offset to COFF symbol table or 0 (absent)
# - symbolCount        - [DEPRECATED, should be 0] count of string table entries, which immediately follows the symbol table
# - optionalHeaderSize
# - characteristics    - flags that indicate the attributes of the file (see PEFileHeaderFlag)
# Optional Header
# Sections[FileHeader.sectionCount]


PE_DOS_HEADER_SIZE           = 64
PE_DOS_HEADER_SIGNATURE      = b'MZ'
PE_DOS_STANDART_PROGRAM      = b'\x0E\x1F\xBA\x0E\x00\xB4\x09\xCD\x21\xB8\x01\x4C\xCD\x21\x54\x68\x69\x73\x20\x70\x72\x6F\x67\x72\x61\x6D\x20\x63\x61\x6E\x6E\x6F\x74\x20\x62\x65\x20\x72\x75\x6E\x20\x69\x6E\x20\x44\x4F\x53\x20\x6D\x6F\x64\x65\x2E\x0D\x0D\x0A\x24\x00\x00\x00\x00\x00\x00\x00'
PE_DOS_STANDART_PROGRAM_SIZE = len(PE_DOS_STANDART_PROGRAM)

PE_SIGNATURE = b'PE\x00\x00'

# sizeof(IMAGE_FILE_HEADER)
PE_COFF_HEADER_SIZE = 20

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

# sizeof(IMAGE_SECTION_HEADER)
PE_SECTION_HEADER_SIZE = 40

# IMAGE_SIZEOF_SHORT_NAME
PE_SECTION_HEADER_NAME_SIZE = 8

# sizeof(IMAGE_DEBUG_DIRECTORY)
PE_DEBUG_DIR_ENTRY_SIZE = 28



# What hardware platform is Windows currently running on
# IMAGE_FILE_MACHINE_*
class PEMachineType (Enum2):
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


# IMAGE_FILE_*
class PEFileHeaderFlag:
    RELOCS_STRIPPED         = 0x0001  # Image only, Windows CE, and Microsoft Windows NT and later. This indicates that the file does not contain base relocations and must therefore be loaded at its preferred base address. If the base address is not available, the loader reports an error. The default behavior of the linker is to strip base relocations from executable (EXE) files.
    EXECUTABLE_IMAGE        = 0x0002  # Image only. This indicates that the image file is valid and can be run. If this flag is not set, it indicates a linker error.
    LINE_NUMS_STRIPPED      = 0x0004  # COFF line numbers have been removed. This flag is deprecated and should be zero.
    LOCAL_SYMS_STRIPPED     = 0x0008  # COFF symbol table entries for local symbols have been removed. This flag is deprecated and should be zero.
    AGGRESIVE_WS_TRIM       = 0x0010  # Obsolete. Aggressively trim working set. This flag is deprecated for Windows 2000 and later and must be zero.
    LARGE_ADDRESS_AWARE     = 0x0020  # Application can handle > 2-GB addresses.
    BYTES_REVERSED_LO       = 0x0080  # Little endian: the least significant bit (LSB) precedes the most significant bit (MSB) in memory. This flag is deprecated and should be zero.
    IS32                    = 0x0100  # Machine is based on a 32-bit-word architecture.
    DEBUG_STRIPPED          = 0x0200  # Debugging information is removed from the image file.
    REMOVABLE_RUN_FROM_SWAP = 0x0400  # If the image is on removable media, fully load it and copy it to the swap file.
    NET_RUN_FROM_SWAP       = 0x0800  # If the image is on network media, fully load it and copy it to the swap file.
    SYSTEM                  = 0x1000  # The image file is a system file, not a user program.
    DLL                     = 0x2000  # The image file is a dynamic-link library (DLL). Such files are considered executable files for almost all purposes, although they cannot be directly run.
    UP_SYSTEM_ONLY          = 0x4000  # The file should be run only on a uniprocessor machine.
    BYTES_REVERSED_HI       = 0x8000  # Big endian: the MSB precedes the LSB in memory. This flag is deprecated and should be zero


# IMAGE_NT_OPTIONAL_HDR*_MAGIC
class PEOptionalHeaderSignature (Enum2):
    # ROM = 0x107
    PE32  = 0x10b
    PE32P = 0x20b


# IMAGE_SUBSYSTEM_*
class PESubSystemType (Enum2):
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


# IMAGE_DLLCHARACTERISTICS_*
class PEDLLFlag:
    HIGH_ENTROPY_VA       = 0x0020  # Image can handle a high entropy 64-bit virtual address space.
    DYNAMIC_BASE          = 0x0040  # DLL can be relocated at load time.
    FORCE_INTEGRITY       = 0x0080  # Code Integrity checks are enforced.
    NX_COMPAT             = 0x0100  # Image is NX compatible
    NO_ISOLATION          = 0x0200  # Image understands isolation and doesn't want it
    NO_SEH                = 0x0400  # Image does not use SEH. No SE handler may reside in this image. No SE handler may be called in this image.
    NO_BIND               = 0x0800  # Do not bind this image.
    APPCONTAINER          = 0x1000  # Image should execute in an AppContainer
    WDM_DRIVER            = 0x2000  # Driver uses WDM model
    GUARD_CF              = 0x4000  # Image supports Control Flow Guard.
    TERMINAL_SERVER_AWARE = 0x8000  # Terminal Server aware.


# IMAGE_DIRECTORY_ENTRY_*
class PEDirEntryIndex (Enum2):
    EXPORT         = 0   # Export Directory
    IMPORT         = 1   # Import Directory
    RESOURCE       = 2   # Resource Directory
    EXCEPTION      = 3   # Exception Directory
    SECURITY       = 4   # Security Directory
    BASERELOC      = 5   # Base Relocation Table
    DEBUG          = 6   # Debug Directory
    # COPYRIGHT      = 7   # (X86 usage)
    ARCHITECTURE   = 7   # Architecture Specific Data
    GLOBALPTR      = 8   # RVA of GP
    TLS            = 9   # TLS Directory
    LOAD_CONFIG    = 10  # Load Configuration Directory
    BOUND_IMPORT   = 11  # Bound Import Directory in headers
    IAT            = 12  # Import Address Table
    DELAY_IMPORT   = 13  # Delay Load Import Descriptors
    COM_DESCRIPTOR = 14  # COM Runtime descriptor
    RESERVED       = 15  # Reserved


# IMAGE_SCN_*
class PESectionFlag:
    TYPE_REG               = 0x00000000  # Reserved
    TYPE_DSECT             = 0x00000001  # Reserved
    TYPE_NOLOAD            = 0x00000002  # Reserved
    TYPE_GROUP             = 0x00000004  # Reserved
    TYPE_NO_PAD            = 0x00000008  # Reserved
    TYPE_COPY              = 0x00000010  # Reserved
    CNT_CODE               = 0x00000020  # Section contains code
    CNT_INITIALIZED_DATA   = 0x00000040  # Section contains initialized data
    CNT_UNINITIALIZED_DATA = 0x00000080  # Section contains uninitialized data
    LNK_OTHER              = 0x00000100  # Reserved
    LNK_INFO               = 0x00000200  # Section contains comments or some other type of information
    TYPE_OVER              = 0x00000400  # Reserved
    LNK_REMOVE             = 0x00000800  # Section contents will not become part of image
    LNK_COMDAT             = 0x00001000  # Section contents comdat
    MEM_PROTECTED          = 0x00004000  # Obsolete
    NO_DEFER_SPEC_EXC      = 0x00004000  # Reset speculative exceptions handling bits in the TLB entries for this section
    GPREL                  = 0x00008000  # Section content can be accessed relative to GP
    MEM_FARDATA            = 0x00008000  # 
    MEM_SYSHEAP            = 0x00010000  # Obsolete
    MEM_PURGEABLE          = 0x00020000  # 
    MEM_16BIT              = 0x00020000  # 
    MEM_LOCKED             = 0x00040000  # 
    MEM_PRELOAD            = 0x00080000  # 
    ALIGN_1BYTES           = 0x00100000  #
    ALIGN_2BYTES           = 0x00200000  #
    ALIGN_4BYTES           = 0x00300000  #
    ALIGN_8BYTES           = 0x00400000  #
    ALIGN_16BYTES          = 0x00500000  # Default alignment if no others are specified.
    ALIGN_32BYTES          = 0x00600000  #
    ALIGN_64BYTES          = 0x00700000  #
    ALIGN_128BYTES         = 0x00800000  #
    ALIGN_256BYTES         = 0x00900000  #
    ALIGN_512BYTES         = 0x00A00000  #
    ALIGN_1024BYTES        = 0x00B00000  #
    ALIGN_2048BYTES        = 0x00C00000  #
    ALIGN_4096BYTES        = 0x00D00000  #
    ALIGN_8192BYTES        = 0x00E00000  #
    ALIGN_MASK             = 0x00F00000  #
    LNK_NRELOC_OVFL        = 0x01000000  # Section contains extended relocations
    MEM_DISCARDABLE        = 0x02000000  # Section can be discarded
    MEM_NOT_CACHED         = 0x04000000  # Section is not cachable
    MEM_NOT_PAGED          = 0x08000000  # Section is not pageable
    MEM_SHARED             = 0x10000000  # Section is shareable
    MEM_EXECUTE            = 0x20000000  # Section is executable
    MEM_READ               = 0x40000000  # Section is readable
    MEM_WRITE              = 0x80000000  # Section is writeable


# RT_*
class PEResType (Enum2):
    CURSOR       = 1
    BITMAP       = 2
    ICON         = 3
    MENU         = 4
    DIALOG       = 5
    STRING       = 6
    FONTDIR      = 7
    FONT         = 8
    ACCELERATOR  = 9
    RCDATA       = 10
    MESSAGETABLE = 11
    GROUP_CURSOR = 12
    GROUP_ICON   = 14
    VERSION      = 16
    DLGINCLUDE   = 17
    PLUGPLAY     = 19
    VXD          = 20
    ANICURSOR    = 21
    ANIICON      = 22
    HTML         = 23
    MANIFEST     = 24


# IMAGE_DEBUG_TYPE_*
class PEDebugDataType (Enum2):
    UNKNOWN       = 0           # IMAGE_DEBUG_TYPE_UNKNOWN               - An unknown value that is ignored by all tools
    COFF          = 1           # IMAGE_DEBUG_TYPE_COFF                  - The COFF debug information (line numbers, symbol table, and string table). This type of debug information is also pointed to by fields in the file headers
    CODEVIEW      = 2           # IMAGE_DEBUG_TYPE_CODEVIEW              - The Visual C++ debug information
    FPO           = 3           # IMAGE_DEBUG_TYPE_FPO                   - The frame pointer omission (FPO) information. This information tells the debugger how to interpret nonstandard stack frames, which use the EBP register for a purpose other than as a frame pointer
    MISC          = 4           # IMAGE_DEBUG_TYPE_MISC                  - The location of DBG file
    EXCEPTION     = 5           # IMAGE_DEBUG_TYPE_EXCEPTION             - A copy of .pdata section
    FIXUP         = 6           # IMAGE_DEBUG_TYPE_FIXUP                 - Reserved
    OMAP_TO_SRC   = 7           # IMAGE_DEBUG_TYPE_OMAP_TO_SRC           - The mapping from an RVA in image to an RVA in source image
    OMAP_FROM_SRC = 8           # IMAGE_DEBUG_TYPE_OMAP_FROM_SRC         - The mapping from an RVA in source image to an RVA in image
    BORLAND       = 9           # IMAGE_DEBUG_TYPE_BORLAND               - Reserved for Borland
    RESERVED10    = 10          # IMAGE_DEBUG_TYPE_RESERVED10            - Reserved
    BBT           = RESERVED10  # IMAGE_DEBUG_TYPE_BBT                   - Reserved
    CLSID         = 11          # IMAGE_DEBUG_TYPE_CLSID                 - 
    VC_FEATURE    = 12          # IMAGE_DEBUG_TYPE_VC_FEATURE            - 
    POGO          = 13          # IMAGE_DEBUG_TYPE_POGO                  - 
    ILTCG         = 14          # IMAGE_DEBUG_TYPE_ILTCG                 - 
    MPX           = 15          # IMAGE_DEBUG_TYPE_MPX                   - 
    REPRO         = 16          # IMAGE_DEBUG_TYPE_REPRO                 - PE determinism or reproducibility.
    UNDEFINED1    = 17          #                                        - Debugging information is embedded in the PE file at location specified by PointerToRawData.
    SPGO          = 18          # IMAGE_DEBUG_TYPE_SPGO                  - 
    UNDEFINED2    = 19          #                                        - Stores crypto hash for the content of the symbol file used to build the PE/COFF file.
    EX_DLL_FLAGS  = 20          # IMAGE_DEBUG_TYPE_EX_DLLCHARACTERISTICS - Extended DLL characteristics bits.



# WIN_CERT_REVISION_*
class WindowsCertRevision (Enum2):
    Rev10 = 0x100
    Rev20 = 0x200

# WIN_CERT_TYPE_*
class WindowsCertType (Enum2):
    X509             = 1  # bCertificate contains an X.509 Certificate
    PKCS_SIGNED_DATA = 2  # bCertificate contains a PKCS SignedData structure
    RESERVED_1       = 3  # Reserved
    TS_STACK_SIGNED  = 4  # Terminal Server Protocol Stack Certificate signing


# IMAGE_DOS_HEADER
class PEDOSHeader:
    def __init__ (self):
        self.signature         = None
        self.lastPageSize      = None
        self.pageCount         = None
        self.relocCount        = None
        self.parHeaderSize     = None
        self.minExtraParCount  = None
        self.maxExtraParCount  = None
        self.ssRegInitValue    = None
        self.spRegInitValue    = None
        self.checksum          = None
        self.ipRegInitValue    = None
        self.csRegInitValue    = None
        self.relocTableAddress = None
        self.overlayCount      = None
        self.reserved          = None
        self.oemId             = None
        self.oemInfo           = None
        self.reserved2         = None
        self.peHeaderOffset    = None

    @classmethod
    def read (cls, f):
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

        # TODO: check header.signature

        if header.peHeaderOffset < 0:
            raise Exception(f'Invalid PE header offset: { header.peHeaderOffset }')

        if header.peHeaderOffset < PE_DOS_HEADER_SIZE:
            raise Exception(f'Invalid PE header offset: { header.peHeaderOffset }. It is inside of DOS section [0:{ PE_DOS_HEADER_SIZE }]')

        if header.peHeaderOffset >= f.getSize(): 
            raise Exception(f'Invalid PE header offset: { header.peHeaderOffset }. It is greater than file size: { f.getSize() }')

        return header

    def isSignatureValid (self):
        return self.signature == PE_DOS_HEADER_SIGNATURE


# DOS header + DOS program + [ rich header ]
# https://0xrick.github.io/win-internals/pe3/
# https://securelist.com/the-devils-in-the-rich-header/84348/
class PEDOSSection:
    def __init__ (self):
        self._header            = None
        self._program           = None
        self._programSize       = None
        self._isProgramStandard = None

    @classmethod
    def read (cls, f):
        section = cls()

        section._header = PEDOSHeader.read(f)

        programStart   = f.tell()
        peHeaderOffset = section._header.peHeaderOffset

        if PE_DOS_HEADER_SIZE < peHeaderOffset <= f.getSize():
            section._program           = f.read(peHeaderOffset - programStart)
            section._programSize       = len(section._program)
            section._isProgramStandard = section._programSize == PE_DOS_STANDART_PROGRAM_SIZE and section._program == PE_DOS_STANDART_PROGRAM
        else:
            section._program           = None
            section._programSize       = 0
            section._isProgramStandard = False

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
    def canHaveRichHeader (self):
        return not self._isProgramStandard and self._programSize > 0


# IMAGE_FILE_HEADER
class PEFileHeader:
    def __init__ (self):
        self.machine            = None
        self.sectionCount       = None
        self.timestamp          = None
        self.symbolTableOffset  = None
        self.symbolCount        = None
        self.optionalHeaderSize = None
        self.characteristics    = None

    @classmethod
    def read (cls, f):
        header = cls()

        if f.remaining() < PE_COFF_HEADER_SIZE:
            raise Exception('Remaining file size is too small to contain a COFF header')
        
        _headerStart = f.tell()

        header.machine            = f.u16()  # WORD  Machine              - The number that identifies the type of target machine (see PEMachineType)
        header.sectionCount       = f.u16()  # WORD  NumberOfSections     - Indicates the size of the section table, which immediately follows the headers (windows loader limits it to 96)
        header.timestamp          = f.u32()  # DWORD TimeDateStamp        - The low 32 bits of the number of seconds since 00:00 January 1, 1970 (a C run-time time_t value), which indicates when the file was created.
        header.symbolTableOffset  = f.u32()  # DWORD PointerToSymbolTable - The file offset of the COFF symbol table, or zero if no COFF symbol table is present. This value should be zero for an image because COFF debugging information is deprecated.
        header.symbolCount        = f.u32()  # DWORD NumberOfSymbols      - This data can be used to locate the string table, which immediately follows the symbol table. This value should be zero for an image because COFF debugging information is deprecated.
        header.optionalHeaderSize = f.u16()  # WORD  SizeOfOptionalHeader - The size of the optional header, which is required for executable files but not for object files. This value should be zero for an object file.
        header.characteristics    = f.u16()  # WORD  Characteristics      - The flags that indicate the attributes of the file. (see PEFileHeaderFlag)

        assert (_headerStart + PE_COFF_HEADER_SIZE) == f.tell()

        if not PEMachineType.hasValue(header.machine):
            raise Exception(f'Invalid machine type in COFF header: { header.machine }')
   
        return header


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


# IMAGE_OPTIONAL_HEADER[32|64]
class PEOptionalHeader:
    def __init__ (self):
        self.is32               = None
        self.signature          = None
        self.linkerMajorVersion = None
        self.linkerMinorVersion = None
        self.codeSize           = None
        self.initDataSize       = None
        self.uninitDataSize     = None
        self.entryPointOffset   = None
        self.codeOffset         = None
        self.dataOffset         = None
        self.imageBaseOffset    = None
        self.sectionAlignment   = None
        self.fileAlignment      = None
        self.osMajorVersion     = None
        self.osMinorVersion     = None
        self.imageMajorVersion  = None
        self.imageMinorVersion  = None
        self.subSysMajorVersion = None
        self.subSysMinorVersion = None
        self.win32Version       = None
        self.imageSize          = None
        self.headersSize        = None
        self.imageChecksum      = None
        self.subSys             = None
        self.dllCharacteristics = None
        self.stackReserveSize   = None
        self.stackCommitSize    = None
        self.heapReserveSize    = None
        self.heapCommitSize     = None
        self.loaderFlags        = None
        self.dirEntryCount      = None
        self.dirEntries         = None

    @classmethod
    def read (cls, f, headerSize):
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

        # PE_DIR_ENTRY_MAX_COUNT
        dirEntrySize = header.dirEntryCount * PE_DIR_ENTRY_SIZE
        headerRem    = headerEnd - f.tell()
        fileRem      = f.remaining()

        if headerRem < dirEntrySize:
            raise Exception(f'Remaining optional header silze ({ headerRem }) is not large enought to contain { header.dirEntryCount } directory entries of total size { dirEntrySize } bytes')

        if fileRem < dirEntrySize:
            raise Exception(f'Remaining file silze ({ headerRem }) is not large enought to contain { header.dirEntryCount } directory entries of total size { dirEntrySize } bytes')

        header.dirEntries = [ None ] * PE_DIR_ENTRY_MAX_COUNT  # IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES] - Each data directory gives the address and size of a table or string that Windows uses.

        for i in range(header.dirEntryCount):
            header.dirEntries[i] = PEDirEntry.read(f)
    
        assert f.tell() == headerEnd

        return header


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

        return header


# IMAGE_IMPORT_DESCRIPTOR
class PEImportDirEntry:
    def __init__ (self):
        self.lookupTableRVA  = None
        self.timestamp       = None
        self.forwardChain    = None
        self.nameRVA         = None
        self.addressTableRVA = None
        self.name            = None
        self.lookups         = None
        self.iat             = None

    @classmethod
    def read (cls, f):
        entry = cls()

        # NOTE: entry is null when ENTIRE struct is 0, not only entry.lookupTableRVA

        entry.lookupTableRVA  = f.u32()  # DWORD OriginalFirstThunk - RVA to original unbound IAT (PIMAGE_THUNK_DATA), 0 for terminating null import descriptor
        entry.timestamp       = f.u32()  # DWORD TimeDateStamp      - 0 if not bound, -1 if bound, and real date/time stamp in IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT (new BIND), O.W. date/time stamp of DLL bound to (Old BIND)
        entry.forwardChain    = f.u32()  # DWORD ForwarderChain     - -1 if no forwarders
        entry.nameRVA         = f.u32()  # DWORD Name
        entry.addressTableRVA = f.u32()  # DWORD FirstThunk         - RVA to IAT (if bound this IAT has actual addresses)

        isLastEntry = (
            entry.lookupTableRVA  == \
            entry.timestamp       == \
            entry.forwardChain    == \
            entry.nameRVA         == \
            entry.addressTableRVA == 0
        )

        if isLastEntry:
            return None

        return entry


class PEImportTableEntry:
    def __init__ (self):
        self.isOrdinal = None
        self.ordinal   = None
        self.nameRVA   = None
        self.hint      = None
        self.name      = None

    @classmethod
    def read (cls, f, is32):
        entry = cls()

        assert f.remaining() >= 4

        if is32:
            num = f.u32()

            entry.isOrdinal = bool(num >> 31)  # Ordinal/Name Flag - If this bit is set, import by ordinal. Otherwise, import by name. Bit is masked as 0x80000000 for PE32, 0x8000000000000000 for PE32+.
        else:
            num = f.u64()

            entry.isOrdinal = bool(num >> 63)  # Ordinal/Name Flag - If this bit is set, import by ordinal. Otherwise, import by name. Bit is masked as 0x80000000 for PE32, 0x8000000000000000 for PE32+.

        if num == 0:
            return None

        if entry.isOrdinal:
            entry.ordinal = num & 0xFFFF      # Ordinal Number      - A 16-bit ordinal number. This field is used only if the Ordinal/Name Flag bit field is 1 (import by ordinal). Bits 30-15 or 62-15 must be 0.
            entry.nameRVA = None              # Hint/Name Table RVA - A 31-bit RVA of a hint/name table entry. This field is used only if the Ordinal/Name Flag bit field is 0 (import by name). For PE32+ bits 62-31 must be zero.
        else:
            entry.ordinal = None              # Ordinal Number      - A 16-bit ordinal number. This field is used only if the Ordinal/Name Flag bit field is 1 (import by ordinal). Bits 30-15 or 62-15 must be 0.
            entry.nameRVA = num & 0x7FFFFFFF  # Hint/Name Table RVA - A 31-bit RVA of a hint/name table entry. This field is used only if the Ordinal/Name Flag bit field is 0 (import by name). For PE32+ bits 62-31 must be zero.

        return entry


# IMAGE_REL_BASED_*
class PEBaseRelocType (Enum2):
    ABSOLUTE            = 0   # The base relocation is skipped. This type can be used to pad a block.
    HIGH                = 1   # The base relocation adds the high 16 bits of the difference to the 16-bit field at offset. The 16-bit field represents the high value of a 32-bit word.
    LOW                 = 2   # The base relocation adds the low 16 bits of the difference to the 16-bit field at offset. The 16-bit field represents the low half of a 32-bit word.
    HIGHLOW             = 3   # The base relocation applies all 32 bits of the difference to the 32-bit field at offset.
    HIGHADJ             = 4   # The base relocation adds the high 16 bits of the difference to the 16-bit field at offset. The 16-bit field represents the high value of a 32-bit word. The low 16 bits of the 32-bit value are stored in the 16-bit word that follows this base relocation. This means that this base relocation occupies two slots.
    MIPS_JMPADDR        = 5   # The relocation interpretation is dependent on the machine type. When the machine type is MIPS, the base relocation applies to a MIPS jump instruction.
    ARM_MOV32           = 5   # This relocation is meaningful only when the machine type is ARM or Thumb. The base relocation applies the 32-bit address of a symbol across a consecutive MOVW/MOVT instruction pair.
    RISCV_HIGH20        = 5   # This relocation is only meaningful when the machine type is RISC-V. The base relocation applies to the high 20 bits of a 32-bit absolute address.
    THUMB_MOV32         = 7   # This relocation is meaningful only when the machine type is Thumb. The base relocation applies the 32-bit address of a symbol to a consecutive MOVW/MOVT instruction pair.
    RISCV_LOW12I        = 7   # This relocation is only meaningful when the machine type is RISC-V. The base relocation applies to the low 12 bits of a 32-bit absolute address formed in RISC-V I-type instruction format.
    RISCV_LOW12S        = 8   # This relocation is only meaningful when the machine type is RISC-V. The base relocation applies to the low 12 bits of a 32-bit absolute address formed in RISC-V S-type instruction format.
    LOONGARCH32_MARK_LA = 8   # This relocation is only meaningful when the machine type is LoongArch 32-bit. The base relocation applies to a 32-bit absolute address formed in two consecutive instructions.
    LOONGARCH64_MARK_LA = 8   # This relocation is only meaningful when the machine type is LoongArch 64-bit. The base relocation applies to a 64-bit absolute address formed in four consecutive instructions.
    MIPS_JMPADDR16      = 9   # The relocation is only meaningful when the machine type is MIPS. The base relocation applies to a MIPS16 jump instruction.
    DIR64               = 10  # The base relocation applies the difference to the 64-bit field at offset.


PE_BASE_RELOC_BLOCK_HEADER_SIZE = 8
PE_BASE_RELOC_BLOCK_ENTRY_SIZE  = 2
PE_BASE_RELOC_BLOCK_MIN_SIZE    = PE_BASE_RELOC_BLOCK_HEADER_SIZE + PE_BASE_RELOC_BLOCK_ENTRY_SIZE


# part of IMAGE_BASE_RELOCATION
class PEBaseReloc:
    def __init__ (self):
        self.type   = None
        self.offset = None

    @classmethod
    def read (cls, f):
        reloc = cls()

        value = f.u16()  # WORD TypeOffset[i] - Entry

        reloc.type   = (value >> 12) & 15  # 4  bits Type   - Stored in the high 4 bits of the WORD, a value that indicates the type of base relocation to be applied (see PEBaseRelocType)
        reloc.offset = value & 0xFFF       # 12 bits Offset - Stored in the remaining 12 bits of the WORD, an offset from the starting address that was specified in the Page RVA field for the block. This offset specifies where the base relocation is to be applied.

        if not PEBaseRelocType.hasValue(reloc.type):
            raise Exception(f'Unknown relocation type { reloc.type }')            

        return reloc


# https://stackoverflow.com/a/22513813
# IMAGE_BASE_RELOCATION
class PEBaseRelocBlock:
    def __init__ (self):
        self.pageRVA   = None
        self.blockSize = None
        self.relocs    = None

    @classmethod
    def read (cls, f, maxSize):
        block = cls()

        block.pageRVA   = f.u32()  # DWORD VirtualAddress - The image base plus the page RVA is added to each offset to create the VA where the base relocation must be applied.
        block.blockSize = f.u32()  # DWORD SizeOfBlock    - The total number of bytes in the base relocation block, including the Page RVA and Block Size fields and the Type/Offset fields that follow.

        if block.blockSize > maxSize:
            raise Exception('OOB')

        relocsSize = block.blockSize - PE_BASE_RELOC_BLOCK_HEADER_SIZE

        if relocsSize % PE_BASE_RELOC_BLOCK_ENTRY_SIZE != 0:
            raise Exception('Remaining space is not a multiple of PE_BASE_RELOC_BLOCK_ENTRY_SIZE')

        entryCount = relocsSize // PE_BASE_RELOC_BLOCK_ENTRY_SIZE

        block.relocs = [ PEBaseReloc.read(f) for _ in range(entryCount) ]

        return block


class PELoader:
    @classmethod
    def load (cls, f, pe):
        mem = bytearray(pe.optionalHeader.imageSize)

        cls._loadHeaders(f, pe, mem)
        cls._loadSections(f, pe, mem)

        return MemReader(mem)

    @classmethod
    def _loadHeaders (cls, f, pe, mem):
        f.seek(0)

        headersSize = pe.optionalHeader.headersSize

        mem[0:headersSize] = f.read(headersSize)        

    @classmethod
    def _loadSections (cls, f, pe, mem):
        for section in pe.sections:
            f.seek(section.rawDataPtr)

            dataSize = min(section.rawDataSize, section.virtualSize)
            dstStart = section.virtualAddress
            dstEnd   = dstStart + dataSize

            mem[dstStart:dstEnd] = f.read(dataSize)

            if dataSize < section.virtualSize:
                padSize = section.virtualSize - dataSize

                mem[dstEnd:dstEnd + padSize] = b'\x00' * padSize


class ProcessMemory:
    pass  # linked list of ProcessMemoryBlock

# wrapper for one of: in-mem image, unallocated memory
class ProcessMemoryBlock:
    pass

# IMAGE_EXPORT_DIRECTORY
class PEExportDirTable:
    Size = 40

    def __init__ (self):
        self.flags           = None
        self.timestamp       = None
        self.majorVersion    = None
        self.minorVersion    = None
        self.nameRVA         = None
        self.ordinalBase     = None
        self.exportCount     = None
        self.nameCount       = None
        self.exportsRVA      = None
        self.namePointersRVA = None
        self.nameOrdinalsRVA = None

    @classmethod
    def read (cls, f, remSize):
        table = cls()

        if remSize < cls.Size:
            raise Exception('OOB')

        table.flags           = f.u32()  # DWORD Characteristics       - Reserved, must be 0.
        table.timestamp       = f.u32()  # DWORD TimeDateStamp         - The time and date that the export data was created.
        table.majorVersion    = f.u16()  # WORD  MajorVersion          - The major version number. The major and minor version numbers can be set by the user.
        table.minorVersion    = f.u16()  # WORD  MinorVersion          - The minor version number.
        table.nameRVA         = f.u32()  # DWORD Name                  - The address of the ASCII string that contains the name of the DLL. This address is relative to the image base.
        table.ordinalBase     = f.u32()  # DWORD Base                  - The starting ordinal number for exports in this image. This field specifies the starting ordinal number for the export address table. It is usually set to 1.
        table.exportCount     = f.u32()  # DWORD NumberOfFunctions     - The number of entries in the export address table.
        table.nameCount       = f.u32()  # DWORD NumberOfNames         - The number of entries in the name pointer table. This is also the number of entries in the ordinal table.
        table.exportsRVA      = f.u32()  # DWORD AddressOfFunctions    - The address of the export address table, relative to the image base.
        table.namePointersRVA = f.u32()  # DWORD AddressOfNames        - The address of the export name pointer table, relative to the image base. The table size is given by the Number of Name Pointers field.
        table.nameOrdinalsRVA = f.u32()  # DWORD AddressOfNameOrdinals - The address of the ordinal table, relative to the image base.

        return table


class PEExportEntry:
    Size = 4

    def __init__ (self):
        self.isForwarded          = None
        self.symbolRVA            = None
        self.symbolName           = None
        self.symbolOrdinal        = None
        self.forwardDLLName       = None
        self.forwardSymbolName    = None
        self.forwardSymbolOrdinal = None

    @classmethod
    def read (cls, f, symbolOrdinal, symbolRVA, minRVA, maxRVA):
        entry = cls()

        entry.symbolRVA     = symbolRVA
        entry.symbolOrdinal = symbolOrdinal
        entry.isForwarded   = minRVA <= symbolRVA < maxRVA

        # someLib#1
        # someLib.someFn
        # someLib.dll#1
        # someLib.dll.someFn
        if entry.isForwarded:
            f.seek(symbolRVA)

            name = f.string()
            name = name.rsplit('.', maxsplit=1)

            entry.forwardDLLName = name[0]

            symbolName = name[1]

            if symbolName[0] == '#':
                entry.forwardSymbolOrdinal = int(symbolName[1:], 10)
            else:
                entry.forwardSymbolName = symbolName

        return entry


class PEExportData:
    def __init__ (self, info, items):
        self.info  = info
        self.items = items


class ResReadContext:
    def __init__ (self):
        self.resources = []
        self.level = 0
        self.infos = Stack()
        self.types = Stack()
        self.attrs = [
            Stack(),  # Type
            Stack(),  # Name
            Stack()   # Language
        ]


class PEResAttr:
    def __init__ (self, isName, value):
        self.isName = isName
        self.value  = value


class PEResource:
    def __init__ (self):
        self.timestamp    = None
        self.majorVersion = None
        self.minorVersion = None
        self.type         = None
        self.name         = None
        self.lang         = None
        self.dataRVA      = None
        self.dataSize     = None
        self.dataEncoding = None


class PEResTable:
    def __init__ (self):
        self.flags          = None
        self.timestamp      = None
        self.majorVersion   = None
        self.minorVersion   = None
        self.nameEntryCount = None
        self.idEntryCount   = None
        self.entries        = None

    # IMAGE_RESOURCE_DIRECTORY
    @classmethod
    def read (cls, f, offsetBase, ctx=None):
        table = cls()

        ctx = ctx or ResReadContext()

        table.flags          = f.u32()  # DWORD Characteristics      - Resource flags. This field is reserved for future use. It is currently set to zero.
        table.timestamp      = f.u32()  # DWORD TimeDateStamp        - The time that the resource data was created by the resource compiler.
        table.majorVersion   = f.u16()  # WORD  MajorVersion         - The major version number, set by the user.
        table.minorVersion   = f.u16()  # WORD  MinorVersion         - The minor version number, set by the user.
        table.nameEntryCount = f.u16()  # WORD  NumberOfNamedEntries - The number of directory entries immediately following the table that use strings to identify Type, Name, or Language entries (depending on the level of the table).
        table.idEntryCount   = f.u16()  # WORD  NumberOfIdEntries    - The number of directory entries immediately following the Name entries that use numeric IDs for Type, Name, or Language entries.

        ctx.infos.push(table)

        for entryCount, isNameEntryExpected in [
            (table.nameEntryCount, True ),
            (table.idEntryCount,   False),
        ]:
            for i in range(entryCount):
                ctx.types.push(isNameEntryExpected)

                cls._readEntry(f, offsetBase, ctx)

                ctx.types.pop()

        ctx.infos.pop()        

        return ctx.resources

    # IMAGE_RESOURCE_DIRECTORY_ENTRY
    @classmethod
    def _readEntry (cls, f, offsetBase, ctx):
        num1 = f.u32()  # Name Offset         - The offset of a string that gives the Type, Name, or Language ID entry, depending on level of table.
                        # Integer ID          - A 32-bit integer that identifies the Type, Name, or Language ID entry.
        num2 = f.u32()  # Data Entry Offset   - High bit 0. Address of a Resource Data entry (a leaf).
                        # Subdirectory Offset - High bit 1. The lower 31 bits are the address of another resource directory table (the next level down).

        entryEnd = f.tell()

        isNameEntry = bool(num1 >> 31)

        if isNameEntry != ctx.types.get():
            raise Exception('Unexpected resource directory entry type')

        # ----------------------

        num1 &= 0x7FFFFFFF

        if isNameEntry:
            nameOffset = offsetBase + num1

            f.seek(nameOffset)

            # IMAGE_RESOURCE_DIRECTORY_STRING
            nameSize  = f.u16()  # char count, not byte count!
            nameSize *= 2        # hack for UCS-2

            # TODO: is it really utf-16?
            value = f.string(nameSize, encoding='utf-16le')
        else:
            value = num1

        ctx.attrs[ctx.level].push(PEResAttr(isNameEntry, value))

        # ----------------------

        hasSubDir = bool(num2 >> 31)  # not isLeaf

        num2 &= 0x7FFFFFFF

        if hasSubDir:
            subDirOffset = offsetBase + num2

            f.seek(subDirOffset)

            ctx.level += 1

            children = cls.read(f, offsetBase, ctx)

            ctx.level -= 1
        else:
            dataOffset = offsetBase + num2

            f.seek(dataOffset)

            cls._readData(f, ctx)

        # ----------------------

        ctx.attrs[ctx.level].pop()

        f.seek(entryEnd)

    # IMAGE_RESOURCE_DATA_ENTRY
    @classmethod
    def _readData (cls, f, ctx):
        res = PEResource()

        info = ctx.infos.get()

        res.timestamp    = info.timestamp
        res.majorVersion = info.majorVersion
        res.minorVersion = info.minorVersion

        res.type = ctx.attrs[0].get()  # see PEResType
        res.name = ctx.attrs[1].get()
        res.lang = ctx.attrs[2].get()  # see WINDOWS_LANGS

        res.dataRVA      = f.u32()  # DWORD OffsetToData - Data RVA             - The address of a unit of resource data in the Resource Data area.
        res.dataSize     = f.u32()  # DWORD Size         - Size                 - The size, in bytes, of the resource data that is pointed to by the Data RVA field.
        res.dataEncoding = f.u32()  # DWORD CodePage     - Codepage             - The code page that is used to decode code point values within the resource data. Typically, the code page would be the Unicode code page.
        _reserved        = f.u32()  # DWORD Reserved     - Reserved, must be 0. - 

        ctx.resources.append(res)


PE_EXCEPTION_ENTRY_AMD64_SIZE = 12


# IMAGE_AMD64_RUNTIME_FUNCTION_ENTRY
class PEExceptionEntryAMD64:
    def __init__ (self):
        self.fnStartRVA = None
        self.fnEndRVA   = None
        self.unwindRVA  = None

    @classmethod
    def read (cls, f):
        entry = cls()

        entry.fnStartRVA = f.u32()  # DWORD BeginAddress - The RVA of the corresponding function
        entry.fnEndRVA   = f.u32()  # DWORD EndAddress   - The RVA of the end of the function
        entry.unwindRVA  = f.u32()  # DWORD UnwindData   - The RVA of the unwind information

        return entry


class PECert:
    def __init__ (self):
        self.type     = None
        self.revision = None
        self.data     = None


class PE:
    def __init__ (self):
        self.dosSection     = None
        self.fileHeader     = None
        self.optionalHeader = None
        self.sections       = None
        self.mem            = None
        # TODO: add data entries

        self.exports    = None
        self.imports    = None
        self.resources  = None
        self.exceptions = None
        self.certs      = None
        self.relocs     = None

    @classmethod
    def fromFile (cls, filePath):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        with openFile(filePath, readerType=ReaderType.FS) as f:
            return cls._read(f)

    @classmethod
    def fromBuffer (cls, data, filePath=None):
        with MemReader(data, filePath=filePath) as f:
            return cls._read(f)

    @classmethod
    def _read (cls, f):
        pe = cls()
        
        pe.dosSection = PEDOSSection.read(f)  # IMAGE_DOS_HEADER

        f.seek(pe.dosSection.header.peHeaderOffset)

        signature = f.read(4)  # DWORD Signature

        # Some malware will cause the Signature value to not exist at all
        # TODO: check sub-signature pefile.py:3102
        if signature != PE_SIGNATURE:
            raise Exception(f'Invalid PE signature ({ signature }), expected { PE_SIGNATURE }')

        pe.fileHeader     = PEFileHeader.read(f)                                                    # IMAGE_FILE_HEADER FileHeader
        pe.optionalHeader = PEOptionalHeader.read(f, pe.fileHeader.optionalHeaderSize)              # IMAGE_OPTIONAL_HEADER[32|64]
        pe.sections       = [ PESectionHeader.read(f) for _ in range(pe.fileHeader.sectionCount) ]  # this offset calculated by IMAGE_FIRST_SECTION
        pe.mem            = PELoader.load(f, pe)

        cls._readDataEntries(f, pe.mem, pe)

        # TODO: do relocations if actualImageBaseAddress != pe.optionalHeader.imageBaseOffset

        # if f.tell() != pe.optionalHeader.headersSize:
        #     print(f.tell(), pe.optionalHeader.headersSize)

        # assert align(f.tell(), pe.optionalHeader.fileAlignment) == pe.optionalHeader.headersSize

        # for entry in pe.optionalHeader.dirEntries:
        #     if entry.virtualAddress >= f.getSize():
        #         print(entry.virtualAddress)

        # 1. Allocate buffer imageBuffer of size pe.optionalHeader.imageSize for entire image file
        # 2. Copy headers to start of the buffer. Size of headers is pe.optionalHeader.headersSize which is a sum of [dos + HT headers + section headers] aligned by pe.optionalHeader.fileAlignment
        # 3. For each section header:
        #    - f.seek(header.rawDataPtr)
        #    - data = f.read(header.rawDataSize)
        #    - if header.rawDataSize < header.virtualSize:
        #    -     data = data.zeroPad(header.virtualSize - header.rawDataSize)
        #    - elif header.rawDataSize > header.virtualSize:
        #    -     data = data[:header.virtualSize]
        #    - imageBuffer.seek(header.virtualAddress)
        #    - imageBuffer.put(data)

        '''
        Arch bits:
        - nt.coff.Machine
        - nt.coff.Characteristics & IMAGE_FILE_LARGE_ADDRESS_AWARE
        - nt.opt.signature in [ 0x10b (PE32), 0x20b (PE32+) ]   // PE32+ images allow for a 64-bit address space while limiting the image size to 2 gigabytes.
        '''

        return pe

    @classmethod
    def _readDataEntries (cls, imageReader, memReader, pe):
        entriesToRead = {
            PEDirEntryIndex.EXPORT:         (cls._readExports,       memReader  ),
            PEDirEntryIndex.IMPORT:         (cls._readImports,       memReader  ),
            PEDirEntryIndex.RESOURCE:       (cls._readResources,     memReader  ),
            PEDirEntryIndex.EXCEPTION:      (cls._readException,     memReader  ),
            PEDirEntryIndex.SECURITY:       (cls._readSecurity,      imageReader),
            PEDirEntryIndex.BASERELOC:      (cls._readRelocations,   memReader  ),
            PEDirEntryIndex.DEBUG:          (cls._readDebug,         memReader  ),
            PEDirEntryIndex.ARCHITECTURE:   (cls._readArch,          memReader  ),
            PEDirEntryIndex.GLOBALPTR:      (cls._readGlobalPtr,     memReader  ),
            PEDirEntryIndex.TLS:            (cls._readTLS,           memReader  ),
            PEDirEntryIndex.LOAD_CONFIG:    (cls._readLoadConfig,    memReader  ),
            PEDirEntryIndex.BOUND_IMPORT:   (cls._readBoundImport,   memReader  ),
            PEDirEntryIndex.IAT:            (cls._readIAT,           memReader  ),
            PEDirEntryIndex.DELAY_IMPORT:   (cls._readDelayImport,   memReader  ),
            PEDirEntryIndex.COM_DESCRIPTOR: (cls._readComDescriptor, memReader  ),
        }

        for i, (dirIndex, (fn, f)) in enumerate(entriesToRead.items()):
            meta = pe.optionalHeader.dirEntries[dirIndex]

            if meta and meta.virtualAddress > 0 and meta.size > 0:
                f.seek(meta.virtualAddress)

                fn(imageReader, memReader, pe, meta)

    # .edata
    @classmethod
    def _readExports (cls, f, mem, pe, meta):
        dataStart = meta.virtualAddress
        dataEnd   = dataStart + meta.size

        info = PEExportDirTable.read(mem, dataEnd - mem.tell())

        if not (dataStart <= info.nameRVA < dataEnd):
            raise Exception('OOB')

        mem.seek(info.nameRVA)

        # TODO: check string OOB
        dllName = mem.string()

        mem.seek(info.exportsRVA)

        # DWORD Export RVA - The address of the exported symbol when loaded into memory, relative to the image base. For example, the address of an exported function.
        # DWORD Forwarder RVA - The pointer to a null-terminated ASCII string in the export section. This string must be within the range that is given by the export table data directory entry. See Optional Header Data Directories (Image Only). This string gives the DLL name and the name of the export (for example, "MYDLL.expfunc") or the DLL name and the ordinal number of the export (for example, "MYDLL.#27").
        exportRVAs = mem.u32(info.exportCount, asArray=True)

        # Ordinals are indices in this array
        exports = [ None ] * info.exportCount

        for i, exportRVA in enumerate(exportRVAs):
            # https://stackoverflow.com/a/40001778
            exports[i] = PEExportEntry.read(mem, info.ordinalBase + i, exportRVA, dataStart, dataEnd)

        if info.nameCount:
            namePointers = []
            nameOrdinals = []

            if info.namePointersRVA:
                mem.seek(info.namePointersRVA)

                namePointers = mem.u32(info.nameCount, asArray=True)

            if info.nameOrdinalsRVA:
                mem.seek(info.nameOrdinalsRVA)

                nameOrdinals = mem.u16(info.nameCount, asArray=True)

            if len(namePointers) != len(nameOrdinals):
                raise Exception('Number of export name pointers is not equal to number of export name ordinals')

            for i in range(info.nameCount):
                namePointer = namePointers[i]
                nameOrdinal = nameOrdinals[i]  # unbiased ordinal [0-...]

                if namePointer:
                    mem.seek(namePointer)

                    exports[nameOrdinal].symbolName = mem.string()

                    assert (nameOrdinal + info.ordinalBase) == exports[nameOrdinal].symbolOrdinal

        pe.exports = PEExportData(info, exports)

        # print(toJson(pe.exports))

    # .idata
    @classmethod
    def _readImports (cls, f, mem, pe, meta):
        # dataEnd = meta.virtualAddress + meta.size

        # TODO:
        imports = pe.imports = dlls = []

        while True:
            dll = PEImportDirEntry.read(mem)

            if dll is None:
                break

            dlls.append(dll)

        for dll in dlls:
            mem.seek(dll.nameRVA)

            dll.name = mem.string()

        for dll in dlls:
            dll.lookups = []
            dll.iat     = []

            tables = [
                (dll.lookupTableRVA,  dll.lookups),
                (dll.addressTableRVA, dll.iat    ),
            ]

            for tableRVA, tableEntries in tables:
                if not tableRVA:
                    continue

                mem.seek(tableRVA)

                while True:
                    entry = PEImportTableEntry.read(mem, pe.optionalHeader.is32)

                    if entry is None:
                        break

                    tableEntries.append(entry)

                for entry in tableEntries:
                    if entry.isOrdinal:
                        continue

                    mem.seek(entry.nameRVA)

                    # IMAGE_IMPORT_BY_NAME
                    entry.hint = mem.u16()
                    entry.name = mem.string()

            dll.lookups = dll.lookups or None
            dll.iat     = dll.iat     or None

        # TODO:
        # - entry.forwardChain (IMAGE_BOUND_FORWARDER_REF)
        # - entry.addressTableRVA (IAT) (https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#import-address-table) (http://sandsprite.com/CodeStuff/Understanding_imports.html)

    # https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#the-rsrc-section
    # https://learn.microsoft.com/en-us/previous-versions/ms809762(v=msdn.10)#pe-file-resources
    # https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/available-language-packs-for-windows?view=windows-11#language-packs
    # .rsrc
    @classmethod
    def _readResources (cls, f, mem, pe, meta):
        dataStart = meta.virtualAddress
        dataEnd   = dataStart + meta.size

        mem.seek(dataStart)

        pe.resources = PEResTable.read(mem, dataStart)

    # https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#the-pdata-section
    # https://learn.microsoft.com/en-us/previous-versions/windows/embedded/aa448751(v=msdn.10)
    # .pdata
    @classmethod
    def _readException (cls, f, mem, pe, meta):
        dataStart = meta.virtualAddress
        dataEnd   = dataStart + meta.size

        # TODO: implement others
        if pe.fileHeader.machine != PEMachineType.AMD64:
            pe.exceptions = None
            print(f'Exception data in .pdata section is not supported for platform { PEMachineType.getKey(pe.fileHeader.machine) }')
            return

        pe.exceptions = exceptions = []

        while (dataEnd - mem.tell()) >= PE_EXCEPTION_ENTRY_AMD64_SIZE:
            exceptions.append(PEExceptionEntryAMD64.read(mem))

    @classmethod
    def _readSecurity (cls, f, mem, pe, meta):
        dataStart = meta.virtualAddress
        dataEnd   = dataStart + meta.size

        pe.certs = certs = []

        # TODO: If the sum of the rounded dwLength values does not equal the Size value, then either the attribute certificate table or the Size field is corrupted.
        # TODO: https://learn.microsoft.com/en-us/windows/win32/debug/pe-format#certificate-data
        while True:
            entryStart = f.tell()

            if entryStart >= dataEnd:
                break

            cert = PECert()

            entrySize     = f.u32()                # DWORD dwLength         - Specifies the length of the attribute certificate entry.
            cert.revision = f.u16()                # WORD  wRevision        - Contains the certificate version number. For details, see the following text. (see WindowsCertRevision)
            cert.type     = f.u16()                # WORD  wCertificateType - Specifies the type of content in bCertificate. For details, see the following text. (see WindowsCertType)
            cert.data     = f.read(entrySize - 8)  # Bytes bCertificate     - Contains a certificate, such as an Authenticode signature. For details, see the following text.

            certs.append(cert)

            f.seek(align(entryStart + entrySize, 8))

    # .reloc
    @classmethod
    def _readRelocations (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

        relocs = pe.relocs = []

        # TODO: In docs "Each block must start on a 32-bit boundary".
        #       Blocks are not aligned actually. WTF?!
        while True:
            blockOffset = mem.tell()
            tailSize    = dataEnd - blockOffset

            if tailSize < PE_BASE_RELOC_BLOCK_MIN_SIZE:
                break

            relocs.append(PEBaseRelocBlock.read(mem, tailSize))

    # .debug
    @classmethod
    def _readDebug (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

        if meta.size % PE_DEBUG_DIR_ENTRY_SIZE != 0:
            raise Exception('Size of debug data directory is not a multiple of PE_DEBUG_DIR_ENTRY_SIZE')

        entryCount = meta.size // PE_DEBUG_DIR_ENTRY_SIZE

        for i in range(entryCount):
            # IMAGE_DEBUG_DIRECTORY
            flags          = mem.u32()  # DWORD Characteristics  - Reserved, must be zero
            ts             = mem.u32()  # DWORD TimeDateStamp    - The time and date that the debug data was created
            majorVersion   = mem.u16()  # WORD  MajorVersion     - The major version number of the debug data format
            minorVersion   = mem.u16()  # WORD  MinorVersion     - The minor version number of the debug data format
            dataType       = mem.u32()  # DWORD Type             - The format of debugging information. This field enables support of multiple debuggers (see PEDebugDataType)
            dataSize       = mem.u32()  # DWORD SizeOfData       - The size of the debug data (not including the debug directory itself)
            rawDataRVA     = mem.u32()  # DWORD AddressOfRawData - The address of the debug data when loaded, relative to the image base
            dataFileOffset = mem.u32()  # DWORD PointerToRawData - The file pointer to the debug data

            print(PEDebugDataType.getKey(dataType))

            # if dataType == PEDebugDataType.CODEVIEW:
            #     f.seek(dataFileOffset)
            #     print(f.read(dataSize))
            #     break

        # print('DEBUG')
        # exit()

    @classmethod
    def _readArch (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

    @classmethod
    def _readGlobalPtr (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

    @classmethod
    def _readTLS (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

    @classmethod
    def _readLoadConfig (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

    @classmethod
    def _readBoundImport (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

    @classmethod
    def _readIAT (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

    @classmethod
    def _readDelayImport (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size

    @classmethod
    def _readComDescriptor (cls, f, mem, pe, meta):
        dataEnd = meta.virtualAddress + meta.size


def _test_ ():
    # PE.fromFile(r"C:\Program Files\Adobe\Adobe Premiere Pro 2023\CEP\extensions\com.adobe.frameio\bin\FrameioHelper.exe")
    # exit()

    # PE.fromFile(r"C:\Projects\_Data_Samples\pe\dll\tk86__many_resources.dll")
    # exit()

    # PE.fromFile(r"G:\Games\Call Of Duty 2\COD2.exe")
    # exit()

    # for rootDir in [
    #     r'C:\Projects\_Data_Samples\pe',
    #     r'C:\Python\3.11_x64',
    #     r'G:\Steam\steamapps\common\ZombieArmy4',
    #     r'G:\Games',
    # ]:
    for rootDir in getDrives(True): 
        for filePath in iterFiles(rootDir, True, [ '.exe', '.dll', '.asi', '.pyd' ]):
            print(filePath)

            try:
                PE.fromFile(filePath)
            except Exception as e:
                print('ERROR:', e)

            print(' ')
            # exit()



__all__ = [
    'PE',
]



if __name__ == '__main__':
    _test_()

