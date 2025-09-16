from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import isEmptyString, splitSeps

from ..ifp import IFPReader, AnimBlock

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



class CutsceneData:
    def __init__ (self):
        self.name      : Opt[str]               = None
        self.splines   : Opt[List[List[float]]] = None
        self.animBlock : Opt[AnimBlock]         = None


class CutsceneReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> CutsceneData:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text, filePath, ctx)

    # TODO: complete CCutsceneMgr::LoadCutsceneData()
    def read (self, text : str, filePath : str, ctx : Opt[Any]) -> CutsceneData:
        ifpPath = replaceExt(filePath, '.ifp')

        assert isFile(ifpPath)

        cutscene = CutsceneData()

        cutscene.name      = getFileName(filePath).lower()
        cutscene.splines   = []
        cutscene.animBlock = IFPReader.fromFile(ifpPath)

        assert cutscene.name == cutscene.animBlock.name

        lines = text.split('\n')

        path = None

        for line in lines:
            line = line.strip()

            if isEmptyString(line):
                continue

            if line == ';':
                path = None
                continue

            values = [ float(n.rstrip('f')) for n in splitSeps(line) if n ]

            if path is None:
                path = []
                cutscene.splines.append(path)

            path += values

        return cutscene


def readCutscenes (rootPath : str) -> Dict[str, CutsceneData]:
    cutscenes : Dict[str, CutsceneData] = {}

    for filePath in iterFiles(rootPath, False, [ '.dat' ]):
        cutscene = CutsceneReader.fromFile(filePath)

        cutscenes[cutscene.name] = cutscene

    return cutscenes



def _test_ ():
    for name, cutscene in readCutscenes(joinPath(GAME_DIR, 'anim/cuts')).items():
        print(name)



__all__ = [
    'CutsceneReader',
    'CutsceneData',
    'readCutscenes',

    '_test_',
]



if __name__ == '__main__':
    _test_()
