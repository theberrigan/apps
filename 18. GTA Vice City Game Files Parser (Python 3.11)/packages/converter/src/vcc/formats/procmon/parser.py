from typing import List

from ...common import bfw
from ...common.types import *
from ...common.consts import *

from .consts import *
from .types import *

from bfw.utils import *
from bfw.xml import XMLNode



class ProcMonLogReader:
    @classmethod
    def fromFile (cls, filePath : str, encoding : str = 'utf-8'):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        return cls().read(readBin(filePath), encoding)

    def read (self, text : str, encoding : str = 'utf-8') -> List[str]:
        result = []

        xml = XMLNode(text, encoding)

        basePath = r'G:\Steam\steamapps\common\Grand Theft Auto Vice City'

        uniques = {}

        for node in xml.findAll('eventlist/event/Path'):
            path = getAbsPath(node.getText())

            if not isFile(path):
                continue

            if getExt(path) in [ '.exe', '.dll', '.ini', '.wav', '.mp3', '.adf' ]:
                continue

            uniques[path.lower()] = getRelPath(path, basePath)

        uniques = list(uniques.values())

        for path in uniques:
            print(path)

        return result




def _test_ ():
    ProcMonLogReader.fromFile(r'C:\Users\Berrigan\Desktop\Logfile.xml')



__all__ = [
    'ProcMonLogReader',

    '_test_',
]



if __name__ == '__main__':
    _test_()
