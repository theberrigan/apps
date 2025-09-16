from ctypes import windll

# see <Python>/Lib/ctypes/wintypes.py
from ctypes.wintypes import (
    ATOM,
    BOOL,
    BOOLEAN,
    BYTE,
    CHAR,
    COLORREF,
    DOUBLE,
    DWORD,
    FILETIME,
    FLOAT,
    HACCEL,
    HANDLE,
    HBITMAP,
    HBRUSH,
    HCOLORSPACE,
    HDC,
    HDESK,
    HDWP,
    HENHMETAFILE,
    HFONT,
    HGDIOBJ,
    HGLOBAL,
    HHOOK,
    HICON,
    HINSTANCE,
    HKEY,
    HKL,
    HLOCAL,
    HMENU,
    HMETAFILE,
    HMODULE,
    HMONITOR,
    HPALETTE,
    HPEN,
    HRGN,
    HRSRC,
    HSTR,
    HTASK,
    HWINSTA,
    HWND,
    INT,
    LANGID,
    LARGE_INTEGER,
    LCID,
    LCTYPE,
    LGRPID,
    LONG,
    LPARAM,
    LPBOOL,
    LPBYTE,
    LPCOLESTR,
    LPCOLORREF,
    LPCSTR,
    LPCVOID,
    LPCWSTR,
    LPDWORD,
    LPFILETIME,
    LPHANDLE,
    LPHKL,
    LPINT,
    LPLONG,
    LPMSG,
    LPOLESTR,
    LPPOINT,
    LPRECT,
    LPRECTL,
    LPSC_HANDLE,
    LPSIZE,
    LPSIZEL,
    LPSTR,
    LPUINT,
    LPVOID,
    LPWIN32_FIND_DATAA,
    LPWIN32_FIND_DATAW,
    LPWORD,
    LPWSTR,
    MAX_PATH,
    MSG,
    OLESTR,
    PBOOL,
    PBOOLEAN,
    PBYTE,
    PCHAR,
    PDWORD,
    PFILETIME,
    PFLOAT,
    PHANDLE,
    PHKEY,
    PINT,
    PLARGE_INTEGER,
    PLCID,
    PLONG,
    PMSG,
    POINT,
    POINTL,
    PPOINT,
    PPOINTL,
    PRECT,
    PRECTL,
    PSHORT,
    PSIZE,
    PSIZEL,
    PSMALL_RECT,
    PUINT,
    PULARGE_INTEGER,
    PULONG,
    PUSHORT,
    PWCHAR,
    PWIN32_FIND_DATAA,
    PWIN32_FIND_DATAW,
    PWORD,
    RECT,
    RECTL,
    RGB,
    SC_HANDLE,
    SERVICE_STATUS_HANDLE,
    SHORT,
    SIZE,
    SIZEL,
    SMALL_RECT,
    UINT,
    ULARGE_INTEGER,
    ULONG,
    USHORT,
    VARIANT_BOOL,
    WCHAR,
    WIN32_FIND_DATAA,
    WIN32_FIND_DATAW,
    WORD,
    WPARAM,
    _COORD,
    _FILETIME,
    _LARGE_INTEGER,
    _POINTL,
    _RECTL,
    _SMALL_RECT,
    _ULARGE_INTEGER,
    tagMSG,
    tagPOINT,
    tagRECT,
    tagSIZE,
)

from ..base import *



KERNEL32 = windll.kernel32
INVALID_HANDLE_VALUE = HANDLE(-1).value



class STORAGE_PROPERTY_ID:
    StorageDeviceProperty                  = CI32(0)
    StorageAdapterProperty                 = CI32(1)
    StorageDeviceIdProperty                = CI32(2)
    StorageDeviceUniqueIdProperty          = CI32(3)
    StorageDeviceWriteCacheProperty        = CI32(4)
    StorageMiniportProperty                = CI32(5)
    StorageAccessAlignmentProperty         = CI32(6)
    StorageDeviceSeekPenaltyProperty       = CI32(7)
    StorageDeviceTrimProperty              = CI32(8)
    StorageDeviceWriteAggregationProperty  = CI32(9)
    StorageDeviceDeviceTelemetryProperty   = CI32(10)
    StorageDeviceLBProvisioningProperty    = CI32(11)
    StorageDevicePowerProperty             = CI32(12)
    StorageDeviceCopyOffloadProperty       = CI32(13)
    StorageDeviceResiliencyProperty        = CI32(14)
    StorageDeviceMediumProductType         = CI32(15)
    StorageAdapterRpmbProperty             = CI32(16)
    StorageAdapterCryptoProperty           = CI32(17)
    StorageDeviceIoCapabilityProperty      = CI32(48)
    StorageAdapterProtocolSpecificProperty = CI32(49)
    StorageDeviceProtocolSpecificProperty  = CI32(50)
    StorageAdapterTemperatureProperty      = CI32(51)
    StorageDeviceTemperatureProperty       = CI32(52)
    StorageAdapterPhysicalTopologyProperty = CI32(53)
    StorageDevicePhysicalTopologyProperty  = CI32(54)
    StorageDeviceAttributesProperty        = CI32(55)
    StorageDeviceManagementStatus          = CI32(56)
    StorageAdapterSerialNumberProperty     = CI32(57)
    StorageDeviceLocationProperty          = CI32(58)
    StorageDeviceNumaProperty              = CI32(59)
    StorageDeviceZonedDeviceProperty       = CI32(60)
    StorageDeviceUnsafeShutdownCount       = CI32(61)
    StorageDeviceEnduranceProperty         = CI32(62)
    StorageDeviceLedStateProperty          = CI32(63)
    StorageDeviceSelfEncryptionProperty    = CI32(64)
    StorageFruIdProperty                   = CI32(65)


class STORAGE_QUERY_TYPE:
    PropertyStandardQuery   = CI32(0)  # Retrieves the descriptor
    PropertyExistsQuery     = CI32(1)  # Used to test whether the descriptor is supported
    PropertyMaskQuery       = CI32(2)  # Used to retrieve a mask of writeable fields in the descriptor
    PropertyQueryMaxDefined = CI32(3)  # use to validate the value


class STORAGE_BUS_TYPE:
    BusTypeUnknown           = CI32(0)
    BusTypeScsi              = CI32(1)
    BusTypeAtapi             = CI32(2)
    BusTypeAta               = CI32(3)
    BusType1394              = CI32(4)
    BusTypeSsa               = CI32(5)
    BusTypeFibre             = CI32(6)
    BusTypeUsb               = CI32(7)
    BusTypeRAID              = CI32(8)
    BusTypeiScsi             = CI32(9)
    BusTypeSas               = CI32(10)
    BusTypeSata              = CI32(11)
    BusTypeSd                = CI32(12)
    BusTypeMmc               = CI32(13)
    BusTypeVirtual           = CI32(14)
    BusTypeFileBackedVirtual = CI32(15)
    BusTypeSpaces            = CI32(16)
    BusTypeNvme              = CI32(17)
    BusTypeSCM               = CI32(18)
    BusTypeUfs               = CI32(19)
    BusTypeMax               = CI32(20)
    BusTypeMaxReserved       = CI32(0x7F)


class STORAGE_PROPERTY_QUERY (CStruct):
    _fields_ = [
        ('PropertyId',           CI32    ),  # STORAGE_PROPERTY_ID
        ('QueryType',            CI32    ),  # STORAGE_QUERY_TYPE
        ('AdditionalParameters', BYTE * 1),
    ]


class STORAGE_DESCRIPTOR_HEADER (CStruct):
    _fields_ = [
        ('Version', DWORD),
        ('Size',    DWORD),
    ]


class STORAGE_DEVICE_DESCRIPTOR (CStruct):
    _fields_ = [
        ('Version',               DWORD   ),
        ('Size',                  DWORD   ),
        ('DeviceType',            BYTE    ),
        ('DeviceTypeModifier',    BYTE    ),
        ('RemovableMedia',        BOOLEAN ),
        ('CommandQueueing',       BOOLEAN ),
        ('VendorIdOffset',        DWORD   ),
        ('ProductIdOffset',       DWORD   ),
        ('ProductRevisionOffset', DWORD   ),
        ('SerialNumberOffset',    DWORD   ),
        ('BusType',               CI32    ),  # STORAGE_BUS_TYPE
        ('RawPropertiesLength',   DWORD   ),
        ('RawDeviceProperties',   BYTE * 1),
    ]


class DISK_EXTENT (CStruct):
    _fields_ = [
        ('DiskNumber',     DWORD        ),
        ('StartingOffset', LARGE_INTEGER),
        ('ExtentLength',   LARGE_INTEGER),
    ]


class VOLUME_DISK_EXTENTS (CStruct):
    _fields_ = [
        ('NumberOfDiskExtents', DWORD          ),
        ('Extents',             DISK_EXTENT * 1),
    ]



__all__ = [
    'ATOM',
    'BOOL',
    'BOOLEAN',
    'BYTE',
    'CHAR',
    'COLORREF',
    'DOUBLE',
    'DWORD',
    'FILETIME',
    'FLOAT',
    'HACCEL',
    'HANDLE',
    'HBITMAP',
    'HBRUSH',
    'HCOLORSPACE',
    'HDC',
    'HDESK',
    'HDWP',
    'HENHMETAFILE',
    'HFONT',
    'HGDIOBJ',
    'HGLOBAL',
    'HHOOK',
    'HICON',
    'HINSTANCE',
    'HKEY',
    'HKL',
    'HLOCAL',
    'HMENU',
    'HMETAFILE',
    'HMODULE',
    'HMONITOR',
    'HPALETTE',
    'HPEN',
    'HRGN',
    'HRSRC',
    'HSTR',
    'HTASK',
    'HWINSTA',
    'HWND',
    'INT',
    'LANGID',
    'LARGE_INTEGER',
    'LCID',
    'LCTYPE',
    'LGRPID',
    'LONG',
    'LPARAM',
    'LPBOOL',
    'LPBYTE',
    'LPCOLESTR',
    'LPCOLORREF',
    'LPCSTR',
    'LPCVOID',
    'LPCWSTR',
    'LPDWORD',
    'LPFILETIME',
    'LPHANDLE',
    'LPHKL',
    'LPINT',
    'LPLONG',
    'LPMSG',
    'LPOLESTR',
    'LPPOINT',
    'LPRECT',
    'LPRECTL',
    'LPSC_HANDLE',
    'LPSIZE',
    'LPSIZEL',
    'LPSTR',
    'LPUINT',
    'LPVOID',
    'LPWIN32_FIND_DATAA',
    'LPWIN32_FIND_DATAW',
    'LPWORD',
    'LPWSTR',
    'MAX_PATH',
    'MSG',
    'OLESTR',
    'PBOOL',
    'PBOOLEAN',
    'PBYTE',
    'PCHAR',
    'PDWORD',
    'PFILETIME',
    'PFLOAT',
    'PHANDLE',
    'PHKEY',
    'PINT',
    'PLARGE_INTEGER',
    'PLCID',
    'PLONG',
    'PMSG',
    'POINT',
    'POINTL',
    'PPOINT',
    'PPOINTL',
    'PRECT',
    'PRECTL',
    'PSHORT',
    'PSIZE',
    'PSIZEL',
    'PSMALL_RECT',
    'PUINT',
    'PULARGE_INTEGER',
    'PULONG',
    'PUSHORT',
    'PWCHAR',
    'PWIN32_FIND_DATAA',
    'PWIN32_FIND_DATAW',
    'PWORD',
    'RECT',
    'RECTL',
    'RGB',
    'SC_HANDLE',
    'SERVICE_STATUS_HANDLE',
    'SHORT',
    'SIZE',
    'SIZEL',
    'SMALL_RECT',
    'UINT',
    'ULARGE_INTEGER',
    'ULONG',
    'USHORT',
    'VARIANT_BOOL',
    'WCHAR',
    'WIN32_FIND_DATAA',
    'WIN32_FIND_DATAW',
    'WORD',
    'WPARAM',
    '_COORD',
    '_FILETIME',
    '_LARGE_INTEGER',
    '_POINTL',
    '_RECTL',
    '_SMALL_RECT',
    '_ULARGE_INTEGER',
    'tagMSG',
    'tagPOINT',
    'tagRECT',
    'tagSIZE',
    'KERNEL32',
    'INVALID_HANDLE_VALUE',
    'STORAGE_PROPERTY_ID',
    'STORAGE_QUERY_TYPE',
    'STORAGE_PROPERTY_QUERY',
    'STORAGE_DESCRIPTOR_HEADER',
    'STORAGE_DEVICE_DESCRIPTOR',
    'DISK_EXTENT',
    'VOLUME_DISK_EXTENTS',
]