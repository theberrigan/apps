from common import formatJson
from common_readers import readSectionedTextFile
from constants import GAME_DIR, GAME_FILES
from scanner import scanDirByExtension

# https://gtamods.com/wiki/Item_Definition#Sections_2
# http://gtamodding.ru/wiki/IDE

IDE_SECTION_CARS = 'cars'
IDE_SECTION_OBJS = 'objs'
IDE_SECTION_TOBJ = 'tobj'
IDE_SECTION_ANIM = 'anim'
IDE_SECTION_PEDS = 'peds'
IDE_SECTION_PATH = 'path'
IDE_SECTION_WEAP = 'weap'
IDE_SECTION_HIER = 'hier'
IDE_SECTION_TXDP = 'txdp'
IDE_SECTION_2DFX = '2dfx'


class IDEVehicle:
    def __init__ (self, modelId, modelName, textureName, vehicleType, handlingId, gameName, animGroup, vehicleClass, frequency, level, compRules, wheelModelId=None, wheelFrontScale=None, wheelRearScale=None, wheelUpgradeClass=None):
        self.sectionType = IDE_SECTION_CARS
        self.modelId = int(modelId)
        self.modelName = modelName
        self.textureName = textureName
        self.type = vehicleType
        self.handlingId = handlingId
        self.gameName = gameName
        self.animGroup = animGroup
        self.vehicleClass = vehicleClass
        self.frequency = int(frequency)
        self.level = int(level)
        self.compRules = int('0x' + compRules, 16)
        self.wheelModelId = int(wheelModelId) if (wheelModelId is not None) else None
        self.wheelFrontScale = float(wheelFrontScale) if (wheelFrontScale is not None) else None
        self.wheelRearScale = float(wheelRearScale) if (wheelRearScale is not None) else None
        self.wheelUpgradeClass = int(wheelUpgradeClass) if (wheelUpgradeClass is not None) else None


class IDEObject:
    def __init__ (self, modelId, modelName, textureName, drawDistance, flags, *args, **kwargs):
        # Skip args & kwargs
        self.sectionType = IDE_SECTION_OBJS
        self.modelId = int(modelId)
        self.modelName = modelName
        self.textureName = textureName
        self.drawDistance = float(drawDistance)
        self.flags = int(flags)


class IDETimeObject:
    def __init__ (self, modelId, modelName, textureName, drawDistance, flags, timeOn, timeOff):
        self.sectionType = IDE_SECTION_TOBJ
        self.modelId = int(modelId)
        self.modelName = modelName
        self.textureName = textureName
        self.drawDistance = float(drawDistance)
        self.flags = int(flags)
        self.timeOn = int(timeOn)
        self.timeOff = int(timeOff)


class IDEAnimation:
    def __init__ (self, modelId, modelName, textureName, animName, drawDistance, flags):
        self.sectionType = IDE_SECTION_ANIM
        self.modelId = int(modelId)
        self.modelName = modelName
        self.textureName = textureName
        self.animName = animName
        self.drawDistance = float(drawDistance)
        self.flags = int(flags)


class IDEPed:
    def __init__ (self, modelId, modelName, textureName, pedType, behavior, animGroup, drivableCars, flags, animFile, radio1, radio2, voiceArchive, voice1, voice2):
        self.sectionType = IDE_SECTION_PEDS
        self.modelId = int(modelId)
        self.modelName = modelName
        self.textureName = textureName
        self.pedType = pedType
        self.behavior = behavior
        self.animGroup = animGroup
        self.drivableCars = int('0x' + drivableCars, 16)
        self.flags = int(flags)
        self.animFile = animFile
        self.radio1 = int(radio1)
        self.radio2 = int(radio2)
        self.voiceArchive = voiceArchive
        self.voice1 = voice1
        self.voice2 = voice2


class IDEPath:
    def __init__ (self, *args, **kwargs):
        self.sectionType = IDE_SECTION_PATH
        pass


class IDEWeapon:
    def __init__ (self, modelId, modelName, textureName, animName, meshCount, drawDistance, *args, **kwargs):
        self.sectionType = IDE_SECTION_WEAP
        self.modelId = int(modelId)
        self.modelName = modelName
        self.textureName = textureName
        self.animName = animName
        self.meshCount = int(meshCount)
        self.drawDistance = float(drawDistance)


class IDEHierarchy:
    def __init__ (self, modelId, modelName, textureName, unused1, drawDistance):
        self.sectionType = IDE_SECTION_HIER
        self.modelId = int(modelId)
        self.modelName = modelName
        self.textureName = textureName
        self.unused1 = unused1
        self.drawDistance = float(drawDistance)


class IDEParentTXD:
    def __init__ (self, textureName, parentTextureName):
        self.sectionType = IDE_SECTION_TXDP
        self.textureName = textureName
        self.parentTextureName = parentTextureName


class IDE2DEffect:
    def __init__ (self, *args):
        self.sectionType = IDE_SECTION_2DFX
        self.unk = None


IDE_SECTION_CLASSES = {
    IDE_SECTION_CARS: IDEVehicle,
    IDE_SECTION_OBJS: IDEObject,
    IDE_SECTION_TOBJ: IDETimeObject,
    IDE_SECTION_ANIM: IDEAnimation,
    IDE_SECTION_PEDS: IDEPed,
    IDE_SECTION_PATH: IDEPath,
    IDE_SECTION_WEAP: IDEWeapon,
    IDE_SECTION_HIER: IDEHierarchy,
    IDE_SECTION_TXDP: IDEParentTXD,
    IDE_SECTION_2DFX: IDE2DEffect,
}


def readIDE (filePaths):
    if type(filePaths) == str:
        filePaths = [ filePaths ]

    items = []

    for filePath in filePaths:
        items += readSectionedTextFile(filePath, IDE_SECTION_CLASSES)

    return items


def scanAndReadIDE (directory, isRecursive=True, rootItems=None):
    paths = scanDirByExtension(directory, 'ide', isRecursive, rootItems)
    items = readIDE(paths)
    return items


if __name__ == '__main__':
    print(formatJson(scanAndReadIDE(GAME_DIR, True, GAME_FILES)))

'''

Stat:
- objs: 14052
- weap: 50
- hier: 35
- tobj: 160
- path: 0
- 2dfx: 97
- anim: 54
- txdp: 38
- peds: 276
- cars: 212

IDEs:
- data/default.ide
- data/peds.ide
- data/txdcut.ide
- data/vehicles.ide
- data/maps/country/countn2.ide
- data/maps/country/countrye.ide
- data/maps/country/countryN.ide
- data/maps/country/countryS.ide
- data/maps/country/countryW.ide
- data/maps/country/counxref.ide
- data/maps/generic/barriers.ide
- data/maps/generic/dynamic.ide
- data/maps/generic/dynamic2.ide
- data/maps/generic/multiobj.ide
- data/maps/generic/procobj.ide
- data/maps/generic/vegepart.ide
- data/maps/interior/gen_int1.ide
- data/maps/interior/gen_int2.ide
- data/maps/interior/gen_int3.ide
- data/maps/interior/gen_int4.ide
- data/maps/interior/gen_int5.ide
- data/maps/interior/gen_intb.ide
- data/maps/interior/int_cont.ide
- data/maps/interior/int_LA.ide
- data/maps/interior/int_SF.ide
- data/maps/interior/int_veg.ide
- data/maps/interior/propext.ide
- data/maps/interior/props.ide
- data/maps/interior/props2.ide
- data/maps/interior/savehous.ide
- data/maps/interior/stadint.ide
- data/maps/LA/LAe.ide
- data/maps/LA/LAe2.ide
- data/maps/LA/LAhills.ide
- data/maps/LA/LAn.ide
- data/maps/LA/LAn2.ide
- data/maps/LA/LAs.ide
- data/maps/LA/LAs2.ide
- data/maps/LA/LAw.ide
- data/maps/LA/LAw2.ide
- data/maps/LA/LaWn.ide
- data/maps/LA/LAxref.ide
- data/maps/leveldes/leveldes.ide
- data/maps/leveldes/levelmap.ide
- data/maps/leveldes/levelxre.ide
- data/maps/leveldes/seabed.ide
- data/maps/SF/SFe.ide
- data/maps/SF/SFn.ide
- data/maps/SF/SFs.ide
- data/maps/SF/SFSe.ide
- data/maps/SF/SFw.ide
- data/maps/SF/SFxref.ide
- data/maps/txd.ide
- data/maps/vegas/vegasE.ide
- data/maps/vegas/VegasN.ide
- data/maps/vegas/VegasS.ide
- data/maps/vegas/VegasW.ide
- data/maps/vegas/vegaxref.ide
- data/maps/veh_mods/veh_mods.ide

'''