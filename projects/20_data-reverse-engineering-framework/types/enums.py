import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bfw.utils import *



'''
# https://peps.python.org/pep-3115
# https://realpython.com/python-metaclasses/
class EnumMeta (type):
    pass
    # def __call__ (*args, **kwargs):
    #     print(args, kwargs)

    def __new__ (cls, name, bases, dct):
        print(f'EnumMeta.__new__ | { cls } | { name } | { bases } | { dct }')
        dct['__qualname__'] = 'ABC'
        return super().__new__(cls, name, bases, dct)

    @classmethod
    def __prepare__ (metacls, cls, bases, **kwds):
        # print(f'EnumMeta.__prepare__ | { metacls } | cls: { cls } | { bases } | { kwds }')
        return {}

class Enum (metaclass=EnumMeta):
    Z = 1

    # def __call__ (*args, **kwargs):
    #     print('Enum.__call__', *args, **kwargs)
    #     # return value

class SomeEnum (Enum):
    White = 2
    Black = 1

print(SomeEnum is SomeEnum)
'''

class Enum2:
    _enum_kvm_ = None
    _enum_vkm_ = None

    @classmethod
    def _createCache (cls, force : bool = False):
        if cls._enum_vkm_ is None or force:
            cls._enum_kvm_ = {
                k: v
                for k, v in cls.__dict__.items()
                if k[0] != '_'
            }

            cls._enum_vkm_ = { v: k for k, v in cls._enum_kvm_.items() }

    @classmethod
    def hasKey (cls, key):
        cls._createCache()
        return key in cls._enum_kvm_

    @classmethod
    def getKey (cls, value):
        cls._createCache()
        return cls._enum_vkm_.get(value)

    @classmethod
    def getFullKey (cls, value):
        cls._createCache()

        key = cls._enum_vkm_.get(value)

        if key is not None:
            key = f'{ cls.__name__ }.{ key }'

        return key

    @classmethod
    def hasValue (cls, value):
        cls._createCache()
        return value in cls._enum_vkm_

    @classmethod
    def getValue (cls, key):
        cls._createCache()
        return cls._enum_kvm_.get(key)

    @classmethod
    def items (cls):
        cls._createCache()
        return cls._enum_kvm_.items()

    @classmethod
    def values (cls):
        cls._createCache()
        return cls._enum_kvm_.values()

    @classmethod
    def keys (cls):
        cls._createCache()
        return cls._enum_kvm_.keys()

    @classmethod
    def getSize (cls):
        cls._createCache()
        return len(cls._enum_kvm_)

    @classmethod
    def setValue (cls, key : str, value):
        setattr(cls, key, value)
        cls._createCache(force=True)

Enum = Enum2



def _test_ ():
    class A (Enum):
        Val = 1

    assert A.Val == 1
    assert A.getValue('Val') == 1
    assert A.getKey(1) == 'Val'
    assert A.getKey(2) is None

    A.setValue('Val', 2)

    assert A.Val == 2, A.Val
    assert A.getValue('Val') == 2
    assert A.getKey(2) == 'Val'
    assert A.getKey(1) is None

    assert Enum.getValue('Val') is None



__all__ = [
    'Enum',
    'Enum2'
]



if __name__ == '__main__':
    _test_()