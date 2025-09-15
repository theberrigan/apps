from re import sub as replace

from winreg import (
    HKEY_LOCAL_MACHINE,
    HKEY_CURRENT_USER,
    ConnectRegistry,
    EnumKey,
    EnumValue,
    QueryInfoKey,
    OpenKeyEx,
    QueryValueEx,
    REG_BINARY                     as REG_TYPE_BINARY,
    REG_DWORD                      as REG_TYPE_DWORD,
    REG_DWORD_LITTLE_ENDIAN        as REG_TYPE_DWORD_LE,
    REG_DWORD_BIG_ENDIAN           as REG_TYPE_DWORD_BE,
    REG_EXPAND_SZ                  as REG_TYPE_EXPAND_SZ,
    REG_LINK                       as REG_TYPE_LINK,
    REG_MULTI_SZ                   as REG_TYPE_MULTI_SZ,
    REG_NONE                       as REG_TYPE_NONE,
    REG_QWORD                      as REG_TYPE_QWORD,
    REG_QWORD_LITTLE_ENDIAN        as REG_TYPE_QWORD_LE,
    REG_RESOURCE_LIST              as REG_TYPE_RESOURCE_LIST,
    REG_FULL_RESOURCE_DESCRIPTOR   as REG_TYPE_FULL_RESOURCE_DESCRIPTOR,
    REG_RESOURCE_REQUIREMENTS_LIST as REG_TYPE_RESOURCE_REQUIREMENTS_LIST,
    REG_SZ                         as REG_TYPE_SZ,
)



def normKey (key):
    return replace(r'[\\\/]+', '\\\\', key.strip())


class RegistryValue:
    def __init__ (self):
        self.name  : str = None  # str
        self.value       = None
        self.type  : int = None  # winreg.REG_*


class RegistryKey:
    def __init__ (self, node, root=None):
        self.root = root or node
        self.node = node

    def openKey (self, key):
        key = normKey(key)

        if not key:
            return self

        if key[0] == '\\':
            key  = key[1:]
            root = self.root
        else:
            root = self.node

        node = OpenKeyEx(root, key)

        return RegistryKey(node, self.root)

    def getValue (self, key, defaultValue=None):
        try:
            return QueryValueEx(self.node, key)[0]
        except:
            return defaultValue

    def iterKeys (self):
        node = self.node
        subKeyCount = QueryInfoKey(node)[0]

        for i in range(subKeyCount):
            yield EnumKey(node, i)

    def iterValues (self):
        node = self.node
        valueCount = QueryInfoKey(node)[1]

        for i in range(valueCount):
            name, value, type_ = EnumValue(node, i)

            v = RegistryValue()

            v.name  = name
            v.value = value
            v.type  = type_

            yield v


# noinspection PyBroadException
class Registry:
    def __init__ (self, rootKey=HKEY_LOCAL_MACHINE):
        self.rootKey = rootKey
        self.reg     = None

    def __enter__ (self):
        return self.open()

    def __exit__ (self, *args, **kwargs):
        self.close()

    def __del__ (self):
        self.close()

    def open (self):
        if self.reg is not None:
            raise Exception('Registry is already open')

        self.reg = ConnectRegistry(None, self.rootKey)

        return RegistryKey(self.reg)

    def close (self):
        if self.reg is not None:
            self.reg.Close()

        self.reg = None



__all__ = [
    'HKEY_LOCAL_MACHINE',
    'HKEY_CURRENT_USER',
    'Registry',
    'RegistryKey',
    'RegistryValue',
    'REG_TYPE_BINARY',
    'REG_TYPE_DWORD',
    'REG_TYPE_DWORD_LE',
    'REG_TYPE_DWORD_BE',
    'REG_TYPE_EXPAND_SZ',
    'REG_TYPE_LINK',
    'REG_TYPE_MULTI_SZ',
    'REG_TYPE_NONE',
    'REG_TYPE_QWORD',
    'REG_TYPE_QWORD_LE',
    'REG_TYPE_RESOURCE_LIST',
    'REG_TYPE_FULL_RESOURCE_DESCRIPTOR',
    'REG_TYPE_RESOURCE_REQUIREMENTS_LIST',
    'REG_TYPE_SZ',
]



if __name__ == '__main__':
    pass
