from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSpaces

from .consts import *
from .types import *

from bfw.utils import *



class BootstrapCommand:
    def __init__ (self):
        self.action : TInt = None
        self.path   : TStr = None


class Bootstrap:
    @classmethod
    def loadAll (cls, encoding : str = 'utf-8') -> list[BootstrapCommand]:
        return concatLists([ cls.fromFile(path, encoding) for path in BOOT_ALL_FILE_PATHS ])

    @classmethod
    def fromFile (cls, filePath : str, encoding : str = 'utf-8') -> list[BootstrapCommand]:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding=encoding)

        return cls().read(text)

    def read (self, text : str) -> list[BootstrapCommand]:
        result = []

        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            values = splitSpaces(line)

            action = None
            path   = None

            actionName = values.pop(0).upper()

            match actionName:
                case 'EXIT':
                    break

                case 'TEXDICTION':  # ~
                    action = LoadResourceType.TextureDict
                    path   = self.normPath(values[0])

                case 'COLFILE':  # ~
                    action = LoadResourceType.Collision
                    # num  = int(values[0])  # unused const 0
                    path   = self.normPath(values[1])

                case 'MODELFILE':
                    action = LoadResourceType.Model
                    path   = self.normPath(values[0])

                case 'IDE':  # +
                    action = LoadResourceType.ItemDefinitions
                    path   = self.normPath(values[0])

                case 'IPL':
                    action = LoadResourceType.ItemPlacements
                    path   = self.normPath(values[0])

                case 'SPLASH':  # ~
                    action = LoadResourceType.Splash
                    path   = self.normPath(f'txd/{ values[0] }.txd')

                case _:
                    # Unused:
                    # - IMAGEPATH
                    # - HIERFILE
                    # - CDIMAGE
                    raise Exception(f'Unknown action: { actionName }')

            if action is not None and path is not None:
                command = BootstrapCommand()

                command.action = action
                command.path   = path

                result.append(command)

        return result

    def normPath (self, path):
        return getAbsPath(joinPath(GAME_DIR, path.lower()))



def _test_ ():
    print(toJson(Bootstrap.loadAll()))



__all__ = [
    'Bootstrap',

    '_test_',
]



if __name__ == '__main__':
    _test_()
