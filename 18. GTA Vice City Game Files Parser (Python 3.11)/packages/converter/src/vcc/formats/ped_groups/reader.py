import re

from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.fns import splitSeps

from .consts import *
from .types import *

from bfw.utils import *
from bfw.types.enums import Enum



PED_GROUP_COUNT = 67        # NUMPEDGROUPS = 67
PED_GROUP_MODEL_COUNT = 16  # NUMMODELSPERPEDGROUP = 16


class PedGroup:
    def __init__ (self):
        self.models : List[int] = []  # self.models[x] is ctx.modelInfos.<objectType>[i].id

# CPopulation::ms_pPedGroups == List[PedGroup]



class PedGroupsReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any] = None) -> List[PedGroup]:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text, ctx)

    def read (self, text : str, ctx : Opt[Any] = None) -> List[PedGroup]:
        groups = []

        if ctx is not None:
            ctx.pedGroups = groups

        lines = text.split('\n')

        for line in lines:
            line = re.split(r'#|//', line)[0].strip()

            if not line:
                continue

            values = splitSeps(line)

            group = PedGroup()

            groups.append(group)

            for modelName in values:
                modelName = modelName.lower()

                if ctx:
                    modelInfo = ctx.modelInfos.getByName(modelName)

                    assert modelInfo

                    group.models.append(modelInfo.id)
                else:
                    # noinspection PyTypeChecker
                    group.models.append(modelName)

        return groups



def _test_ ():
    print(toJson(PedGroupsReader.fromFile(joinPath(GAME_DIR, 'data/pedgrp.dat'))))



__all__ = [
    'PedGroupsReader',
    'PedGroup',

    '_test_',
]



if __name__ == '__main__':
    _test_()
