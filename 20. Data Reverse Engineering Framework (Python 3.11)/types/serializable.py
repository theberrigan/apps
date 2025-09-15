import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from bfw.utils import *



class Serializable:
    def __str__ (self):
        return str(self)
        # print(self.__dict__)
        # return toJson(vars(self))



def _test_ ():
    pass



__all__ = [
    'Serializable'
]



if __name__ == '__main__':
    _test_()