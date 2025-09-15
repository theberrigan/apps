import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bfw.utils import *



# p, kw * kw
# p / kw 
# MultiMap(values)
# MultiMap(keys, values)
class MultiMap:
    def __init__ (self, keys=None, values=None, /):
        if values is None:
            values = keys
            keys   = None

        if keys is None:
            keys = list(values[0].keys())

        storages = {}

        for key in keys:
            storages[key] = storage = {}

            setattr(self, key, storage)

        for value in values:
            for key in keys:
                storages[key][value[key]] = value



def _test_ ():    
    mm = MultiMap([ 'id', 'data' ], [
        {
            'id': 1,
            'name': 'Elephant',
            'data': b'5'
        },
        {
            'id': 2,
            'name': 'Zebra',
            'data': b'6'
        },
        {
            'id': 3,
            'name': 'Rhino',
            'data': b'7'
        }
    ])

    print(mm.data[b'7'])



__all__ = [
    'MultiMap'
]



if __name__ == '__main__':
    _test_()