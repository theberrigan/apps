from ...common import bfw
from ...common.types import *
from ...common.consts import *
from ...common.game_data import *
from ...common.fns import splitSeps, toInts, toFloats

from .consts import *
from .types import *

from bfw.utils import *



# CObjectInfo
class ObjectInfo:
    def __init__ (self):
        self.id                           : TInt   = None
        self.name                         : TStr   = None
        self.mass                         : TFloat = None  # float m_fMass
        self.turnMass                     : TFloat = None  # float m_fTurnMass
        self.airResistance                : TFloat = None  # float m_fAirResistance
        self.elasticity                   : TFloat = None  # float m_fElasticity
        self.percentSubmerged             : TFloat = None  # float ?
        self.buoyancy                     : TFloat = None  # float m_fBuoyancy
        self.uprootLimit                  : TFloat = None  # float m_fUprootLimit
        self.collisionDamageMultiplier    : TFloat = None  # float m_fCollisionDamageMultiplier
        self.collisionDamageEffect        : TInt   = None  # uint8 m_nCollisionDamageEffect
        self.specialCollisionResponseCase : TInt   = None  # uint8 m_nSpecialCollisionResponseCases
        self.cameraToAvoidThisObject      : TBool  = None  # bool  m_bCameraToAvoidThisObject


class ObjectReader:
    @classmethod
    def fromFile (cls, filePath : str, ctx : Opt[Any]):
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        text = readText(filePath, encoding='utf-8')

        return cls().read(text, ctx)

    def createDefaultInfos (self) -> List[ObjectInfo]:
        infos : List[ObjectInfo] = []

        obj = ObjectInfo()

        obj.id                           = 0
        obj.name                         = None
        obj.mass                         = 99999
        obj.turnMass                     = 99999
        obj.airResistance                = 0.99
        obj.elasticity                   = 0.1
        obj.buoyancy                     = GRAVITY * obj.mass * 2
        obj.uprootLimit                  = 0
        obj.collisionDamageMultiplier    = 1
        obj.collisionDamageEffect        = 0
        obj.specialCollisionResponseCase = 0
        obj.cameraToAvoidThisObject      = False

        infos.append(obj)

        obj = ObjectInfo()

        obj.id                           = 1
        obj.name                         = None
        obj.mass                         = 99999
        obj.turnMass                     = 99999
        obj.airResistance                = 0.99
        obj.elasticity                   = 0.1
        obj.buoyancy                     = infos[0].buoyancy
        obj.uprootLimit                  = 0
        obj.collisionDamageMultiplier    = 1
        obj.collisionDamageEffect        = 0
        obj.specialCollisionResponseCase = 0
        obj.cameraToAvoidThisObject      = True

        infos.append(obj)

        obj = ObjectInfo()

        obj.id                           = 2
        obj.name                         = None
        obj.mass                         = 99999
        obj.turnMass                     = 99999
        obj.airResistance                = 0.99
        obj.elasticity                   = 0.1
        obj.buoyancy                     = infos[0].buoyancy
        obj.uprootLimit                  = 0
        obj.collisionDamageMultiplier    = 1
        obj.collisionDamageEffect        = 0
        obj.specialCollisionResponseCase = 4
        obj.cameraToAvoidThisObject      = False

        infos.append(obj)

        obj = ObjectInfo()

        obj.id                           = 3
        obj.name                         = None
        obj.mass                         = 99999
        obj.turnMass                     = 99999
        obj.airResistance                = 0.99
        obj.elasticity                   = 0.1
        obj.buoyancy                     = infos[0].buoyancy
        obj.uprootLimit                  = 0
        obj.collisionDamageMultiplier    = 1
        obj.collisionDamageEffect        = 0
        obj.specialCollisionResponseCase = 4
        obj.cameraToAvoidThisObject      = True

        infos.append(obj)

        return infos

    def read (self, text : str, ctx : Opt[Any]) -> List[ObjectInfo]:
        assert ctx.modelInfos

        infos = ctx.objs = self.createDefaultInfos()

        lines = text.split('\n')

        infoId = 4

        for line in lines:
            line = line.split(';')[0].strip()

            if not line:
                continue

            if line[0] == '*':
                break

            values = splitSeps(line)

            # --------------------------------------------------

            obj = ObjectInfo()

            obj.id                           = infoId
            obj.name                         = values[0].lower()
            obj.mass                         = float(values[1])
            obj.turnMass                     = float(values[2])
            obj.airResistance                = float(values[3])
            obj.elasticity                   = float(values[4])
            obj.percentSubmerged             = float(values[5])
            obj.buoyancy                     = 100 / obj.percentSubmerged * GRAVITY * obj.mass
            obj.uprootLimit                  = float(values[6])
            obj.collisionDamageMultiplier    = float(values[7])
            obj.collisionDamageEffect        = int(values[8])
            obj.specialCollisionResponseCase = int(values[9])
            obj.cameraToAvoidThisObject      = bool(int(values[10]))

            modelInfo = ctx.modelInfos.getByName(obj.name)

            if not modelInfo:
                printW(f'Model info not found for model "{ obj.name }"')
                continue

            if infos[0].mass != obj.mass or \
               infos[0].collisionDamageMultiplier != obj.collisionDamageMultiplier or \
               infos[0].collisionDamageEffect != obj.collisionDamageEffect or \
               infos[0].specialCollisionResponseCase != obj.specialCollisionResponseCase and \
               infos[2].specialCollisionResponseCase != obj.specialCollisionResponseCase:
                modelInfo.setObjectId(obj.id)
                infos.append(obj)
                infoId += 1

                assert infos[obj.id] == obj

            elif infos[0].specialCollisionResponseCase == obj.specialCollisionResponseCase:
                if infos[0].cameraToAvoidThisObject == obj.cameraToAvoidThisObject:
                    modelInfo.setObjectId(0)
                else:
                    modelInfo.setObjectId(1)

            elif infos[2].cameraToAvoidThisObject == obj.cameraToAvoidThisObject:
                modelInfo.setObjectId(2)

            else:
                modelInfo.setObjectId(3)

            # --------------------------------------------------

        return infos



def _test_ ():
    pass



__all__ = [
    'ObjectReader',
    'ObjectInfo',

    '_test_',
]



if __name__ == '__main__':
    _test_()
