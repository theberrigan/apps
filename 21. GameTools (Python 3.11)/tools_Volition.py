# Volition Games Tools

import re
import sys
import math

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import Enum
from bfw.native.limits import *



# VOLITION GAMES (D:\.dev\VolitionGames)
# +----+------------------------------------------+-----------+----------+----------+---------+
# |  # | Name                                     | Engine    | Release  | Package  | Version |
# +----+------------------------------------------+-----------+----------+----------+---------+
# |  1 | Descent: FreeSpace                       | CTG       | Jun 1998 | vp       |         |
# |  2 | FreeSpace 2                              | CTG       | Sep 1999 | vp       |         |
# |  3 | Summoner                                 | CTG       | Mar 2001 | vpp      |       1 |
# |  4 | Red Faction                              | Geo-Mod   | Sep 2001 | vpp      |       1 |
# |  5 | Red Faction II                           | Geo-Mod   | Apr 2003 | packfile |         |
# |  6 | The Punisher                             | CTG       | Jan 2005 | vpp      |       3 |
# |  7 | Saints Row 2                             | CTG       | Jan 2009 | vpp_pc   |       4 |
# |  8 | Red Faction Guerrilla Steam Edition      | Geo-Mod 2 | Sep 2009 | vpp_pc   |       3 |
# |  9 | Red Faction: Armageddon                  | Geo-Mod 2 | Jun 2011 | vpp_pc   |       6 |
# | 10 | Saints Row: The Third Initiation Station | CTG       | Nov 2011 | vpp_pc   |       6 |
# | 11 | Saints Row: The Third                    | CTG       | Nov 2011 | vpp_pc   |       6 |
# | 12 | Saints Row IV: Inauguration Station      | CTG       | Aug 2013 | vpp_pc   |      10 |
# | 13 | Saints Row IV (Re-Elected)               | CTG       | Aug 2013 | vpp_pc   |      10 |
# | 14 | Saints Row: Gat out of Hell              | CTG       | Jan 2015 | vpp_pc   |      10 |
# | 15 | Agents of Mayhem                         | CTG       | Aug 2017 | vpp_pc   |      17 |
# | 16 | Red Faction Guerrilla Re-Mars-tered      | Geo-Mod 2 | Jul 2018 | vpp_pc   |       3 |
# | 17 | Saints Row: The Third Remastered         | CTG       | May 2021 | vpp_pc   |       6 |
# | 18 | Saints Row                               | CTG       | Aug 2023 | vpp_pc   |      17 |
# +----+------------------------------------------+-----------+----------+----------+---------+


# PLATFORMS (ctg/src/lib/vlib/vlib_base.h)
# +-----------------+-------+---------------+-------+----------------+-------------+
# | Platform        | Code  | Byte Order    | Bits  | File Extension | Compression |
# +-----------------+-------+---------------+-------+----------------+-------------+
# | Windows PC      | pc    | Little Endian | 32/64 | _pc            | zlib        |
# | PlayStation 3   | ps3   | Big Endian    | 32    | _ps3           | edge        |
# | PlayStation 4   | ps4   | Little Endian | 64    | _ps4           | zlib        |
# | Xbox 360        | xbox2 | Big Endian    | 32    | _xbox2         | lzx         |
# | Xbox One        | xbox3 | Little Endian | 64    | _xbox3         | zlib        |
# | Nintendo Switch | nx64  | Little Endian | 64    | _nx64          | zstd        |
# +-----------------+-------+---------------+-------+----------------+-------------+



GAMES_DIR = r'D:\.dev\VolitionGames'

GAME_01_DIR = joinPath(GAMES_DIR, '01_Freespace')
GAME_02_DIR = joinPath(GAMES_DIR, '02_Freespace 2')
GAME_03_DIR = joinPath(GAMES_DIR, '03_The Summoner')
GAME_04_DIR = joinPath(GAMES_DIR, '04_Red Faction')
GAME_05_DIR = joinPath(GAMES_DIR, '05_Red Faction II')
GAME_06_DIR = joinPath(GAMES_DIR, '06_The Punisher')
GAME_07_DIR = joinPath(GAMES_DIR, '07_Saints Row 2')
GAME_08_DIR = joinPath(GAMES_DIR, '08_Red Faction Guerrilla')
GAME_08_DIR = joinPath(GAMES_DIR, '08_Red Faction Guerrilla Steam Edition')
GAME_09_DIR = joinPath(GAMES_DIR, '09_Red Faction Armageddon')
GAME_10_DIR = joinPath(GAMES_DIR, '10_Saints Row The Third Initiation Station')
GAME_11_DIR = joinPath(GAMES_DIR, '11_Saints Row The Third')
GAME_12_DIR = joinPath(GAMES_DIR, '12_Saints Row IV Inauguration Station')
GAME_13_DIR = joinPath(GAMES_DIR, '13_Saints Row IV')
GAME_14_DIR = joinPath(GAMES_DIR, '14_Saints Row Gat out of Hell')
GAME_15_DIR = joinPath(GAMES_DIR, '15_Agents of Mayhem')
GAME_16_DIR = joinPath(GAMES_DIR, '16_Red Faction Guerrilla Re-Mars-tered')
GAME_17_DIR = joinPath(GAMES_DIR, '17_Saints Row The Third Remastered')
GAME_18_DIR = joinPath(GAMES_DIR, '18_Saints Row (2022)')

VPP_SIGNATURE       = b'\xCE\x0A\x89\x51'
VPP_SIGNATURE_NX    = b'\xCE\x0D\x0A\x89'
VPP_MIN_HEADER_SIZE = 4 + 4  # signature + version

CRC_TABLE = [
    0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA, 0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3, 
    0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988, 0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91, 
    0x1DB71064, 0x6AB020F2, 0xF3B97148, 0x84BE41DE, 0x1ADAD47D, 0x6DDDE4EB, 0xF4D4B551, 0x83D385C7, 
    0x136C9856, 0x646BA8C0, 0xFD62F97A, 0x8A65C9EC, 0x14015C4F, 0x63066CD9, 0xFA0F3D63, 0x8D080DF5, 
    0x3B6E20C8, 0x4C69105E, 0xD56041E4, 0xA2677172, 0x3C03E4D1, 0x4B04D447, 0xD20D85FD, 0xA50AB56B, 
    0x35B5A8FA, 0x42B2986C, 0xDBBBC9D6, 0xACBCF940, 0x32D86CE3, 0x45DF5C75, 0xDCD60DCF, 0xABD13D59, 
    0x26D930AC, 0x51DE003A, 0xC8D75180, 0xBFD06116, 0x21B4F4B5, 0x56B3C423, 0xCFBA9599, 0xB8BDA50F, 
    0x2802B89E, 0x5F058808, 0xC60CD9B2, 0xB10BE924, 0x2F6F7C87, 0x58684C11, 0xC1611DAB, 0xB6662D3D, 
    0x76DC4190, 0x01DB7106, 0x98D220BC, 0xEFD5102A, 0x71B18589, 0x06B6B51F, 0x9FBFE4A5, 0xE8B8D433, 
    0x7807C9A2, 0x0F00F934, 0x9609A88E, 0xE10E9818, 0x7F6A0DBB, 0x086D3D2D, 0x91646C97, 0xE6635C01, 
    0x6B6B51F4, 0x1C6C6162, 0x856530D8, 0xF262004E, 0x6C0695ED, 0x1B01A57B, 0x8208F4C1, 0xF50FC457, 
    0x65B0D9C6, 0x12B7E950, 0x8BBEB8EA, 0xFCB9887C, 0x62DD1DDF, 0x15DA2D49, 0x8CD37CF3, 0xFBD44C65, 
    0x4DB26158, 0x3AB551CE, 0xA3BC0074, 0xD4BB30E2, 0x4ADFA541, 0x3DD895D7, 0xA4D1C46D, 0xD3D6F4FB, 
    0x4369E96A, 0x346ED9FC, 0xAD678846, 0xDA60B8D0, 0x44042D73, 0x33031DE5, 0xAA0A4C5F, 0xDD0D7CC9, 
    0x5005713C, 0x270241AA, 0xBE0B1010, 0xC90C2086, 0x5768B525, 0x206F85B3, 0xB966D409, 0xCE61E49F, 
    0x5EDEF90E, 0x29D9C998, 0xB0D09822, 0xC7D7A8B4, 0x59B33D17, 0x2EB40D81, 0xB7BD5C3B, 0xC0BA6CAD, 
    0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A, 0xEAD54739, 0x9DD277AF, 0x04DB2615, 0x73DC1683, 
    0xE3630B12, 0x94643B84, 0x0D6D6A3E, 0x7A6A5AA8, 0xE40ECF0B, 0x9309FF9D, 0x0A00AE27, 0x7D079EB1, 
    0xF00F9344, 0x8708A3D2, 0x1E01F268, 0x6906C2FE, 0xF762575D, 0x806567CB, 0x196C3671, 0x6E6B06E7, 
    0xFED41B76, 0x89D32BE0, 0x10DA7A5A, 0x67DD4ACC, 0xF9B9DF6F, 0x8EBEEFF9, 0x17B7BE43, 0x60B08ED5, 
    0xD6D6A3E8, 0xA1D1937E, 0x38D8C2C4, 0x4FDFF252, 0xD1BB67F1, 0xA6BC5767, 0x3FB506DD, 0x48B2364B, 
    0xD80D2BDA, 0xAF0A1B4C, 0x36034AF6, 0x41047A60, 0xDF60EFC3, 0xA867DF55, 0x316E8EEF, 0x4669BE79, 
    0xCB61B38C, 0xBC66831A, 0x256FD2A0, 0x5268E236, 0xCC0C7795, 0xBB0B4703, 0x220216B9, 0x5505262F, 
    0xC5BA3BBE, 0xB2BD0B28, 0x2BB45A92, 0x5CB36A04, 0xC2D7FFA7, 0xB5D0CF31, 0x2CD99E8B, 0x5BDEAE1D, 
    0x9B64C2B0, 0xEC63F226, 0x756AA39C, 0x026D930A, 0x9C0906A9, 0xEB0E363F, 0x72076785, 0x05005713, 
    0x95BF4A82, 0xE2B87A14, 0x7BB12BAE, 0x0CB61B38, 0x92D28E9B, 0xE5D5BE0D, 0x7CDCEFB7, 0x0BDBDF21, 
    0x86D3D2D4, 0xF1D4E242, 0x68DDB3F8, 0x1FDA836E, 0x81BE16CD, 0xF6B9265B, 0x6FB077E1, 0x18B74777, 
    0x88085AE6, 0xFF0F6A70, 0x66063BCA, 0x11010B5C, 0x8F659EFF, 0xF862AE69, 0x616BFFD3, 0x166CCF45, 
    0xA00AE278, 0xD70DD2EE, 0x4E048354, 0x3903B3C2, 0xA7672661, 0xD06016F7, 0x4969474D, 0x3E6E77DB, 
    0xAED16A4A, 0xD9D65ADC, 0x40DF0B66, 0x37D83BF0, 0xA9BCAE53, 0xDEBB9EC5, 0x47B2CF7F, 0x30B5FFE9, 
    0xBDBDF21C, 0xCABAC28A, 0x53B39330, 0x24B4A3A6, 0xBAD03605, 0xCDD70693, 0x54DE5729, 0x23D967BF, 
    0xB3667A2E, 0xC4614AB8, 0x5D681B02, 0x2A6F2B94, 0xB40BBE37, 0xC30C8EA1, 0x5A05DF1B, 0x2D02EF8D,
]


# Volition CRC32
def calcVCRC32 (data, value=0):
    for byte in data:
        value = ((value >> 8) & 0x00FFFFFF) ^ CRC_TABLE[(value ^ byte) & 0xFF]

    return value


class VPPFlag (Enum):
    Compressed = 1 << 0  # PFF_COMPRESSED = 1 << 0  // packfile data is compressed
    Condensed  = 1 << 1  # PFF_CONDENSED  = 1 << 1  // packfile data is run together


class VPPEntryFlag (Enum):
    Compressed = 1 << 0  # PFEF_COMPRESSED = 1 << 0  // this file is compressed


class VPPPlatform (Enum):
    PC      = 1
    PS3     = 2 
    PS4     = 3
    X360    = 4
    XONE    = 5
    NX64    = 6
    Default = PC


VPP_PLATFORM_MAP = {
    'pc':    VPPPlatform.PC,
    'ps3':   VPPPlatform.PS3,
    'ps4':   VPPPlatform.PS4,
    'xbox2': VPPPlatform.X360,
    'xbox3': VPPPlatform.XONE,
    'nx64':  VPPPlatform.NX64,
}


VPP_PLATFORM_NAMES = {
    VPPPlatform.PC:   'Windows PC',
    VPPPlatform.PS3:  'PlayStation 3',
    VPPPlatform.PS4:  'PlayStation 4',
    VPPPlatform.X360: 'Xbox 360',
    VPPPlatform.XONE: 'Xbox One',
    VPPPlatform.NX64: 'Nintendo Switch',
}


class VPPCompressionMethod (Enum):
    No       = 0   # VC_NO_COMPRESSION   = 0
    ZlibFast = 1   # VC_ZLIB_FAST        = 1   // all platforms
    ZlibBest = 9   # VC_ZLIB_BEST        = 9   // all platforms
    ZlibEdge = 10  # VC_ZLIB_EDGE        = 10  // ps3 only
    LZX      = 11  # VC_LZX              = 11  // 360 only     
    Null     = 12  # VC_NULL_COMPRESSION = 12  // all platforms (no compression)
    ZStd     = 13  # VC_ZSTD             = 13  // DSFL n.pfaff: added zstd compression


VPP_COMPRESSION_NAMES = {
    VPPCompressionMethod.No:       'No compression',
    VPPCompressionMethod.ZlibFast: 'Zlib Fast',
    VPPCompressionMethod.ZlibBest: 'Zlib Best',
    VPPCompressionMethod.ZlibEdge: 'Zlib Edge',
    VPPCompressionMethod.LZX:      'LZX',
    VPPCompressionMethod.Null:     'Null (no compression)',
    VPPCompressionMethod.ZStd:     'ZStd',
}


class VPPHeader:
    def __init__ (self):
        self.version = None  # et_uint32 version;  // version number of packfile


class VPPHeaderV10 (VPPHeader):
    def __init__ (self):
        """
        // Header v10
        struct v_packfile_file_data {
            et_uint32 descriptor;            // packfile descriptor used to validate data
            et_uint32 version;               // version number of packfile
            et_uint32 header_checksum;       // CRC of the header (after this field)
            et_uint32 file_size;             // physical size (in bytes) of the source vpp file
            et_uint32 flags;                 // packfile flags
            et_uint32 num_files;             // number of files in *data section
            et_uint32 dir_size;              // number of bytes in directory section
            et_uint32 filename_size;         // number of bytes in filename section
            et_uint32 data_size;             // number of uncompressed bytes in data files
            et_uint32 compressed_data_size;  // number of compressed bytes in *data section
        }
        """
        super().__init__()

        self.headerHash   = None  # et_uint32 header_checksum;       // CRC of the header (after this field)
        self.fileSize     = None  # et_uint32 file_size;             // physical size (in bytes) of the source vpp file
        self.flags        = None  # et_uint32 flags;                 // packfile flags (see VPPFlag)
        self.entryCount   = None  # et_uint32 num_files;             // number of files in *data section
        self.entriesSize  = None  # et_uint32 dir_size;              // number of bytes in directory section
        self.namesSize    = None  # et_uint32 filename_size;         // number of bytes in filename section
        self.decompSize   = None  # et_uint32 data_size;             // number of uncompressed bytes in data files
        self.compSize     = None  # et_uint32 compressed_data_size;  // number of compressed bytes in *data section
        self.entriesStart = None
        self.namesStart   = None
        self.dataStart    = None
        self.isCompressed = None
        self.isCondensed  = None
        self.compMethod   = None  # VPPCompressionMethod


class VPPVersionConfig:
    def __init__ (self):
        self.headerClass  = None
        self.variableSize = None  # size of version-dependend header part
        self.hashableSize = None


class VPPMeta:
    def __init__ (self):
        self.vppPath  = None  # normalized abs vppPath
        self.platform = None  # VPPPlatform
        self.header   = None  # VPPHeader
        self.entries  = None  # VPPEntry[]


class VPPEntry:
    def __init__ (self):
        self.nameOffset   = None  # filename_entry m_filename_entry;  // filename entry   (used storing filename when reading packfile)
        self.dataOffset   = None  # et_uint32      start;             // offset from start of v_packfile::data (if data is valid) 
        self.decompSize   = None  # et_uint32      size;              // file size (uncompressed source data size)
        self.compSize     = None  # et_uint32      compressed_size;   // compressed file size (or MAX_U32 if data is not compressed)
        self.flags        = None  # et_uint16      flags;             // flags for this file (see VPPEntryFlag)
        self.alignment    = None  # et_uint16      alignment;         // alignment requirement of this file
        self.isCompressed = None
        self.name         = None


class VPPReader:
    @classmethod
    def getPackageInfo (cls, vppPath):
        cls(vppPath)._getInfo()

    @classmethod
    def showPackageInfo (cls, vppPath, showSummary=True, showEntries=True):
        cls(vppPath)._showInfo(showSummary, showEntries)

    @classmethod
    def unpackPackage (cls, vppPath):
        cls(vppPath)._unpack()

    @property
    def vppPath (self):
        return self._vppPath

    def __init__ (self, vppPath):
        self._vppPath = self._maintainPath(vppPath)

    def _maintainPath (self, vppPath):
        if not isinstance(vppPath, str):
            raise Exception(f'Expected file path, but { vppPath } given')

        vppPath = getAbsPath(vppPath)

        if not isFile(vppPath):
            raise Exception(f'File does not exist: { vppPath }')

        return vppPath

    def _unpack (self):
        with openFile(self.vppPath) as f:
            meta = self._readMeta(f)

            '''
            print(f'isCondensed = { meta.header.isCondensed }; isCompressed = { meta.header.isCompressed }')

            if meta.header.isCondensed:
                f.seek(meta.header.dataStart)

                if meta.header.isCompressed:
                    assert meta.header.compSize > 0 and meta.header.decompSize > 0 and meta.header.compSize < 0xFFFFFFFF and meta.header.decompSize < 0xFFFFFFFF
                    data = f.read(meta.header.compSize)
                    assert len(data) == meta.header.compSize, (len(data), meta.header.compSize)
                    assert f.remaining() == 0, f.remaining()
                    data = decompressData(data)
                    assert len(data) == meta.header.decompSize, (len(data), meta.header.decompSize)
                else:
                    assert meta.header.compSize == 0xFFFFFFFF and meta.header.decompSize > 0 and meta.header.decompSize < 0xFFFFFFFF
                    data = f.read(meta.header.decompSize)
                    assert len(data) == meta.header.decompSize, (len(data), meta.header.decompSize)
                    assert f.remaining() == 0, f.remaining()

                with MemReader(data) as f2:
                    for entry in meta.entries:
                        f2.seek(entry.dataOffset)

                        data2 = f2.read(entry.decompSize)

                        assert len(data2) == entry.decompSize
            else:
                _compSize   = 0
                _decompSize = 0

                for entry in meta.entries:
                    f.seek(meta.header.dataStart + entry.dataOffset)

                    if entry.isCompressed:
                        data = f.read(entry.compSize)
                        data = decompressData(data)
                        assert len(data) == entry.decompSize, (len(data), entry.decompSize)
                        _compSize += entry.compSize
                    else:
                        data = f.read(entry.decompSize)
                        _decompSize += math.ceil(entry.decompSize / entry.alignment) * entry.alignment

                # TODO: doesn't work
                assert _compSize == 0 and meta.header.compSize == 0xFFFFFFFF and meta.header.decompSize == (f.getSize() - meta.header.dataStart) or \
                       _compSize == meta.header.compSize and meta.header.decompSize == (f.getSize() - meta.header.dataStart - _compSize), (_compSize, meta.header.compSize, meta.header.decompSize, f.getSize() - meta.header.dataStart, _decompSize, meta.header.isCompressed)
            '''

    def _getInfo (self):
        with openFile(self.vppPath) as f:
            return self._readMeta(f)

    def _showInfo (self, showSummary, showEntries):
        meta = self._getInfo()

        if showSummary:
            if meta.header.flags:
                flags = f'0x{meta.header.flags:08X}'
            else:
                flags = '0'

            if meta.header.decompSize == MAX_U32:
                decompSize = f'0x{meta.header.decompSize:08X} (no uncompressed data)'
            else:
                decompSize = f'{ meta.header.decompSize } ({ formatSize(meta.header.decompSize) })'

            if meta.header.compSize == MAX_U32:
                compSize = f'0x{meta.header.compSize:08X} (no compressed data)'
            else:
                compSize = f'{ meta.header.compSize } ({ formatSize(meta.header.compSize) })'

            print('')
            print(f'Path ................. { meta.vppPath }')
            print(f'Platform ............. { meta.platform } ({ VPP_PLATFORM_NAMES[meta.platform] })')
            print(f'Version .............. { meta.header.version }')
            print(f'Header hash .......... 0x{meta.header.headerHash:08X}')
            print(f'File size ............ { meta.header.fileSize } ({ formatSize(meta.header.fileSize) })')
            print(f'Flags ................ { flags }')
            print(f'Entry count .......... { meta.header.entryCount }')
            print(f'Entries offset ....... { meta.header.entriesStart }')
            print(f'Entries size ......... { meta.header.entriesSize } ({ formatSize(meta.header.entriesSize) })')
            print(f'Names offset ......... { meta.header.namesStart }')
            print(f'Names size ........... { meta.header.namesSize } ({ formatSize(meta.header.namesSize) })')
            print(f'Data offset .......... { meta.header.dataStart }')
            print(f'Uncompressed size .... { decompSize }')
            print(f'Compressed size ...... { compSize }')
            print(f'Is compressed ........ { meta.header.isCompressed }')
            print(f'Is condensed ......... { meta.header.isCondensed }')
            print(f'Compression method ... { meta.header.compMethod } ({ VPP_COMPRESSION_NAMES[meta.header.compMethod] })')

        print('')

        if not showEntries or not meta.entries:
            return

        print('Entries:')

        entries = [ ('Name Offset', 'Data Offset', 'Uncompressed Size', 'Compressed Size', 'Flags', 'Alignment', 'Is Compressed', 'Name') ]

        for entry in meta.entries:
            if meta.header.flags:
                flags = f'0x{entry.flags:08X}'
            else:
                flags = '0'

            if entry.decompSize == MAX_U32:
                decompSize = f'0x{entry.decompSize:08X}'
            else:
                decompSize = f'{ entry.decompSize } ({ formatSize(entry.decompSize) })'

            if entry.compSize == MAX_U32:
                compSize = f'0x{entry.compSize:08X}'
            else:
                compSize = f'{ entry.compSize } ({ formatSize(entry.compSize) })'

            entries.append((
                f'{ entry.nameOffset }',
                f'{ entry.dataOffset }',
                f'{ decompSize }',
                f'{ compSize }',
                f'{ entry.flags }',
                f'{ entry.alignment }',
                f'{ entry.isCompressed }',
                f'{ entry.name }',
            ))

        sizes = [ 0 ] * len(entries[0])

        for entry in entries:
            for i, value in enumerate(entry):
                sizes[i] = max(sizes[i], len(value))

        lastEntryIndex = len(entries) - 1
        sep = '+' + '+'.join([ ('-' * (n + 2)) for n in sizes ]) + '+'

        for i, entry in enumerate(entries):
            if i == 0:
                print(sep)

            print('|' + '|'.join([ f' {s:<{sizes[j]}} ' for j, s in enumerate(entry) ]) + '|')

            if i == 0 or i == lastEntryIndex:
                print(sep)

        print('')

    def _readMeta (self, f):
        meta = VPPMeta()

        meta.vppPath  = self.vppPath
        meta.platform = self._getPlatformFromFileName(self.vppPath)
        meta.header   = self._readHeader(f, True)
        meta.entries  = self._readEntries(f, meta.header)

        return meta

    def _getPlatformFromFileName (self, vppPath):
        ext = getExt(vppPath).split('_')

        if len(ext) > 1:            
            return VPP_PLATFORM_MAP.get(ext[-1], VPPPlatform.Default)

        return VPPPlatform.Default

    def _getVersionConfig (self, version):
        config = VPPVersionConfig()

        match version:
            case 1:
                return None

            case 3:
                return None

            case 4:
                return None

            case 6:
                return None

            case (9 | 10):
                config.headerClass  = VPPHeaderV10
                config.variableSize = 32
                config.hashableSize = 28

            case 17:
                return None

            case _:
                return None

        return config

    def _readHeader (self, f, checkIntegrity=False):
        if f.remaining() < VPP_MIN_HEADER_SIZE:
            raise Exception('File is too small to be a package')

        signature = f.read(4)

        # Corrupted file: "Saints Row IV/packfiles/pc/cache/world_textures.vpp_pc".
        # According to the SR4 source code, this file is specific to Nintendo Switch, but for some reason
        # it is included in the PC release of the game, has the .vpp_pc extension and a corrupted signature.
        # (see ng2/sr35/src/game/gamewide/gamewide_packfile.cpp:72-74)
        if signature == VPP_SIGNATURE_NX:
            raise Exception(f'Package "{ getBaseName(self._vppPath) }" is specific to Nintendo Switch and cannot be read')             

        if signature != VPP_SIGNATURE:
            raise Exception('Incorrect package signature')  

        version = f.u32()

        config = self._getVersionConfig(version)

        if config is None:
            raise Exception(f'Unsupported package version: { version }')

        if f.remaining() < config.variableSize:
            raise Exception('Package is truncated')

        header = config.headerClass()

        header.version    = version
        header.headerHash = f.u32()  # et_uint32 header_checksum;  // CRC of the header (after this field)

        hashableData = f.read(config.hashableSize)

        if checkIntegrity:
            headerHash = calcVCRC32(hashableData)

            if headerHash != header.headerHash:
                raise Exception(f'Package header failed an integrity check. Actual hash is 0x{headerHash:08X}. Expected hash is 0x{header.headerHash:08X}')

        with MemReader(hashableData) as f2:
            header.fileSize    = f2.u32()  # et_uint32 file_size;             // physical size (in bytes) of the source vpp file
            header.flags       = f2.u32()  # et_uint32 flags;                 // packfile flags
            header.entryCount  = f2.u32()  # et_uint32 num_files;             // number of files in *data section
            header.entriesSize = f2.u32()  # et_uint32 dir_size;              // number of bytes in directory section
            header.namesSize   = f2.u32()  # et_uint32 filename_size;         // number of bytes in filename section
            header.decompSize  = f2.u32()  # et_uint32 data_size;             // number of uncompressed bytes in data files
            header.compSize    = f2.u32()  # et_uint32 compressed_data_size;  // number of compressed bytes in *data section

            assert not f2.remaining()

        header.entriesStart = f.tell()
        header.namesStart   = header.entriesStart + header.entriesSize
        header.dataStart    = header.namesStart + header.namesSize
        header.isCompressed = bool(header.flags & VPPFlag.Compressed)
        header.isCondensed  = bool(header.flags & VPPFlag.Condensed)
        header.compMethod   = (header.flags >> 11) & 15

        assert header.flags in [ 0, 2, 18433, 18435 ], header.flags
        assert header.compMethod in [ 0, 9 ], header.compMethod

        return header

    def _readEntries (self, f, header):
        f.seek(header.entriesStart)

        entries = [ VPPEntry() for _ in range(header.entryCount) ]

        for entry in entries:
            entry.nameOffset   = f.u64()  # filename_entry m_filename_entry;  // filename entry (used storing filename when reading packfile)
            entry.dataOffset   = f.u32()  # et_uint32      start;             // offset from start of v_packfile::data (if data is valid) 
            entry.decompSize   = f.u32()  # et_uint32      size;              // file size (uncompressed source data size)
            entry.compSize     = f.u32()  # et_uint32      compressed_size;   // compressed file size (or MAX_U32 if data is not compressed)
            entry.flags        = f.u16()  # et_uint16      flags;             // flags for this file (see VPPEntryFlag)
            entry.alignment    = f.u16()  # et_uint16      alignment;         // alignment requirement of this file
            entry.isCompressed = bool(entry.flags & VPPEntryFlag.Compressed)

            assert entry.flags in [ 0, 1 ], entry.flags
            assert entry.alignment in [ 1, 16 ], entry.alignment

        for entry in entries:
            f.seek(header.namesStart + entry.nameOffset)

            entry.name = f.string()

        return entries





'''
struct filename_entry {
    uint64 m_entry;
}

struct v_packfile_entry_file_data {
    union {
        char           *filename;         // filename string (used writing data to disk)
        filename_entry m_filename_entry;  // filename entry   (used storing filename when reading packfile)
    } m_filename;
    et_uint32          start;             // offset from start of v_packfile::data (if data is valid) 
    et_uint32          size;              // file size (uncompressed source data size)
    et_uint32          compressed_size;   // compressed file size (or MAX_U32 if data is not compressed)
    et_uint16          flags;             // flags for this file (see VPPEntryFlag)
    et_uint16          alignment;         // alignment requirement of this file
}

struct packfile_write_entry {
    char                       full_path[CF_FULL_PATHNAME_LEN];  // full path to the entry
    v_packfile_entry_file_data entry_data;                       // packfile entry data for this entry(what is actually written to disk)
    uint8                      *data;                            // pointer to the file if it is in memory
}

if( required_alignment == 0 ) {
    // no alignment specified in the file, so default to 16 I guess
    required_alignment = 16;
}
'''



def main ():
    rootDir = r'D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code'
    dupsPath = joinPath(rootDir, 'dups.json')
    dupsTmpPath = joinPath(rootDir, 'dups.tmp.json')
    dupStubExt = '.dup-stub'

    # empty dirs
    # .db .dylib .so .gitDIR .vsDIR .githubDIR

    # totalSize = 0

    # with open(r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\deleted_files.txt", 'a', encoding='utf-8') as f:
    #     f.write('// .db, .dylib, .so, .prx, Wwise/NX64, .git, .github, .vs, vendor files\n')

    #     for filePath in iterFiles(rootDir, True):
    #         if getBaseName(filePath) == '185test.db':
    #             continue

    #         ext = getExt(filePath)

    #         if ext in [ '.db', '.dylib', '.so', '.prx' ]:
    #             totalSize += getFileSize(filePath)
    #             f.write(filePath + '\n')
    #             removeFile(filePath)
    #         elif re.search(r'[\\\/](Wwise\\NX64|\.git|\.github|\.vs)[\\\/]', filePath, flags=re.I):# or dropExt(filePath).lower().endswith('_nx64'):
    #             totalSize += getFileSize(filePath)
    #             f.write(filePath + '\n')
    #             removeFile(filePath)

    #     for dirPath in [
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\Annosoft\SDK3.5.2.0\SDKExamples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\cellSDK",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\codejock\Help",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\codejock\Samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\directx",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\FBX SDK\samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\FCollada\FColladaPlugins\Output",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\FCollada\FCollada\Output",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2010\howto",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2010\samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2010\help",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2011\howto",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2011\samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2011\help",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2012\samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2012\help",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\maxsdk2012\howto",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\Silverlink\Documents",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\SLikeNet\.github",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\SLikeNet\Help",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\SLikeNet\licenses",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\SLikeNet\Samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\SLikeNet\.git",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\xMon_legacy\lib_PS3",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\xMon_legacy\lib_360",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\yebis\samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\yebis\doc",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\yebis\doc",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\ctg\src\vendor\yebis\samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\sr35\src\vendor\dsonline\Samples",
    #         r"D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code\ng2\sr35\src\vendor\dsonline\Docs",
    #     ]:
    #         if not isDir(dirPath):
    #             continue

    #         for filePath in iterFiles(dirPath, True):
    #             totalSize += getFileSize(filePath)
    #             f.write(filePath + '\n')
    #             removeFile(filePath)

    # print(formatSize(totalSize))


    # dups = readJson(dupsPath)
    # refs = dups['refs'] = {}

    # for dsPath in iterFiles(rootDir, True, includeExts=[ dupStubExt ]):
    #     srcPath = readText(dsPath).strip()
    #     refPath = dropExt(getRelPath(dsPath, rootDir))

    #     # print(dsPath)
    #     # print('\t', srcPath, refPath)

    #     assert isFile(joinPath(rootDir, srcPath))

    #     if srcPath in refs:
    #         refs[srcPath].append(refPath)
    #     else:
    #         refs[srcPath] = [ refPath ]

    #     removeFile(dsPath)

    # writeJson(dupsTmpPath, dups, pretty=False)


    # for filePath in iterFiles(pcPath, True):
    #     srcPath = joinPath(rootDir, readText(filePath).strip())
    #     assert isFile(srcPath)
    #     dstPath = dropExt(filePath)
    #     print(srcPath, '-->', dstPath)
    #     copyFile(srcPath, dstPath, True)
    #     removeFile(filePath)


    '''
    import time

    totalSize    = 0
    dupSize      = 0
    lastProgress = 0
    dupStubExt   = '.dup-stub'

    knownFiles = {}
    
    # rootDir = r'D:\.dev\VolitionGames\_SR4SC\_test'
    rootDir = r'D:\.dev\VolitionGames\_SR4SC\sr4_full_source_code'

    dupsPath = joinPath(rootDir, 'dups.json')

    isFromCache = False

    if isFile(dupsPath):
        knownFiles  = readJson(dupsPath)
        isFromCache = True

    if knownFiles:
        print('Using cache file', dupsPath)
    else:
        print('Collecting dups...')

        startTime = time.time()

        for filePath in iterFiles(rootDir, True, excludeExts=[ dupStubExt ]):
            checksum = calcMD5(readBin(filePath))
            relPath  = getRelPath(filePath, rootDir)

            if checksum in knownFiles:
                knownFiles[checksum].append(relPath)
            else:
                knownFiles[checksum] = [ relPath ]

            fileSize   = getFileSize(filePath)
            totalSize += fileSize

            progress = totalSize // (1024 ** 3)

            if progress != lastProgress:
                lastProgress = progress
                timeWasted   = int(time.time() - startTime) * 1000
                timeLeft     = int((173787828534 / totalSize * timeWasted) - timeWasted)

                print(f'-> { formatSize(totalSize) } | { formatTimestamp(timeWasted) } | { formatTimestamp(timeLeft) }')

    dups = {}

    for checksum, files in knownFiles.items():
        if len(files) <= 1:
            continue

        dups[checksum] = files

        print(f'{ checksum }:')

        dupSize += getFileSize(joinPath(rootDir, files[0])) * (len(files) - 1)

        mainPath = files[0]

        for i, filePath in enumerate(files):
            print(f'- { filePath }')

            filePath = joinPath(rootDir, filePath)

            if i > 0:
                writeText(filePath + dupStubExt, f'{ mainPath }\n')
                removeFile(filePath)
                pass

        print('')

    if not isFromCache:
        writeJson(dupsPath, dups, pretty=False)

    print(formatSize(dupSize))
    '''




    exit()

    # ---

    for gameDir in [
        GAME_12_DIR,
        GAME_13_DIR,
        GAME_14_DIR,
    ]:
        for filePath in iterFiles(gameDir, True, [ '.vpp_pc' ]):
            if getFileName(filePath).lower() == 'world_textures':
                continue

            print(filePath)

            if 0:
                try:
                    VPPReader.showPackageInfo(filePath)
                except Exception as e:
                    print('ERROR:', e)
            else:
                VPPReader.showPackageInfo(filePath, True, True)

            # exit()

            print(' ')



if __name__ == '__main__':
    main()
