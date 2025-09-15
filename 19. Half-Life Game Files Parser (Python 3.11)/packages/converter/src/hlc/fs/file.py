from ..common import bfw
from ..common.consts import GAME_DIR
from ..formats.wad import getWADs

from bfw.utils import isFile, getAbsPath, joinPath
from bfw.reader import openFile, ReaderType



def openAnyFile (path : str):
    path = getAbsPath(joinPath(GAME_DIR, path))

    if isFile(path):
        return openFile(path, ReaderType.Mem)

    return getWADs().openEntry(path)



__all__ = [
    'openAnyFile'
]
