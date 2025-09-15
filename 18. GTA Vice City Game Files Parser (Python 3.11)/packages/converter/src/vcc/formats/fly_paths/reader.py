from math import sqrt

from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSeps, toFloats

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum



# CPlaneNode
class FlyPathNode:
    def __init__ (self):
        self.position    : TVec3  = None  # CVector p -- position
        self.totalLength : TFloat = None  # float t -- xy-distance from start on path
        self.isOnGround  : TBool  = None  # bool bOnGround -- i.e. not flying


class FlyPath:
    def __init__ (self):
        self.nodes       : Opt[List[FlyPathNode]] = None
        self.nodeCount   : TInt                   = None
        self.totalLength : TFloat                 = None  # float t -- xy-distance from start on path


class FlyPaths:
    def __init__ (self):
        self.jumbo : Opt[FlyPath] = None
        self.dodo  : Opt[FlyPath] = None
        self.heli  : Opt[FlyPath] = None



class FlyPathsReader:
    @classmethod
    def fromFile (cls, filePath : str, isLooped : TBool) -> FlyPath:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text, isLooped)

    def read (self, text : str, isLooped : TBool) -> FlyPath:
        path = FlyPath()

        path.nodes     = None
        path.nodeCount = None

        nodeId = 0

        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                continue

            values = splitSeps(line)

            if path.nodes is None:
                assert len(values) == 1

                path.nodeCount = int(values[0])

                path.nodes = Array(path.nodeCount, FlyPathNode)

                continue

            assert len(values) == 3

            path.nodes[nodeId].position = toFloats(values)

            nodeId += 1

        path.totalLength = 0

        for i in range(path.nodeCount):
            curNode  = path.nodes[i]
            nextNode = path.nodes[(i + 1) % path.nodeCount]

            curNode.totalLength = path.totalLength

            x1, y1, _ = curNode.position
            x2, y2, _ = nextNode.position

            # magnitude 2D
            if isLooped or i != (path.nodeCount - 1):
                path.totalLength += sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        return path


def readJumboPath () -> FlyPath:
    path = FlyPathsReader.fromFile(joinPath(GAME_DIR, 'data/paths/flight.dat'), True)

    # Figure out which nodes are on ground
    for node in path.nodes:
        if node.position[2] < 14:
            node.position[2] = 14
            node.isOnGround  = True
        else:
            node.isOnGround = False

    # TODO: a lot of init: game\src\vehicles\Plane.cpp:707

    return path


def readDodoPath () -> FlyPath:
    path = FlyPathsReader.fromFile(joinPath(GAME_DIR, 'data/paths/flight2.dat'), True)

    # TODO: some init: game\src\vehicles\Plane.cpp:776

    return path


def readHeliPath () -> FlyPath:
    path = FlyPathsReader.fromFile(joinPath(GAME_DIR, 'data/paths/flight3.dat'), False)

    # TODO: some init: game\src\vehicles\Plane.cpp:782

    return path


def readFlyPaths (ctx : Opt[Any] = None) -> FlyPaths:
    paths = FlyPaths()

    paths.jumbo = readJumboPath()
    paths.dodo  = readDodoPath()
    paths.heli  = readHeliPath()

    # TODO: some init and model loading: game\src\vehicles\Plane.cpp:785

    return paths



def _test_ ():
    pjpd(readFlyPaths())



__all__ = [
    'readFlyPaths',
    'FlyPaths',

    '_test_',
]



if __name__ == '__main__':
    _test_()
