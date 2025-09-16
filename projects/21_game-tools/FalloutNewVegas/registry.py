from winreg import HKEY_LOCAL_MACHINE, ConnectRegistry, OpenKeyEx, QueryValueEx
from re import sub as replace


def normKey (key):
    return replace(r'[\\\/]+', '\\\\', key.strip())


# noinspection PyBroadException
class Registry:
    def __init__ (self, rootKey=HKEY_LOCAL_MACHINE):
        self.rootKey = rootKey
        self.root = None
        self.reg = None

    def __enter__ (self):
        try:
            self.root = self.reg = ConnectRegistry(None, self.rootKey)
        except:
            self.root = self.reg = None

        return self

    def __exit__ (self, *args, **kwargs):
        self.close()

    def __del__ (self):
        self.close()

    def close (self):
        if self.reg:
            self.reg.Close()

        self.reg = None        

    def openKey (self, key):
        key = normKey(key)

        if key and key[0] == '\\':
            self.reg = self.root
            key = key[1:]

        try:
            self.reg = OpenKeyEx(self.reg, key)
        except:
            self.reg = None

        return self

    def getValue (self, key, defaultValue=None):
        try:
            return QueryValueEx(self.reg, key)[0]
        except:
            return defaultValue


__all__ = [ 'Registry' ]


if __name__ == '__main__':
    pass
