# Wolfenstein: The New Order Extractor

import os, struct, json, ctypes, zlib, gzip
from collections import namedtuple

GAME_DIR = r'G:\Steam\steamapps\common\Wolfenstein.The.New.Order'
SIGNATURE_SER = b'\x03\x53\x45\x52'

FILE_MASTER_INDEX_NAME = 'master.index'
FILE_STREAMED_RESOURCES_NAME = 'streamed.resources'
FILE_STREAMED_RESOURCES_KEY = '<streamed>'

def formatBytes (byteSeq):
    return ' '.join([ '{:02X}'.format(b) for b in byteSeq ])


class FileAttributes:
    def __init__ (self, path, descriptor):
        self.path = path
        self.descriptor = descriptor

    def __str__ (self):
        return '{}(path={}, descriptor={})'.format(
            self.__class__.__name__, 
            self.path, 
            self.descriptor
        )

    def __repr__ (self):
        return self.__str__()


class ResourceFileAttributes:
    def __init__ (self, key, indexFile, resourceFile):
        self.key = key
        self.indexFile = indexFile
        self.resourceFile = resourceFile

    def __str__ (self):
        return '{}(key={}, indexFile={}, resourceFile={})'.format(
            self.__class__.__name__, 
            self.key, 
            self.indexFile, 
            self.resourceFile
        )

    def __repr__ (self):
        return self.__str__()


class Unpacker:
    def __init__ (self, gameDir):
        self.gameDir = gameDir
        self.baseDir = os.path.join(gameDir, 'base')
        self.vtDir = os.path.join(gameDir, 'virtualtextures')
        self.resourceFiles = []
        self.streamedFiles = {}
        self.nextGroupId = 0
        self.nextResourceId = 0

        self._totalCompSize = 0
        self._totalDecompSize = 0

    def __del__ (self):
        for rscFileAttrs in self.resourceFiles:
            self.closeFile(rscFileAttrs.indexFile)
            self.closeFile(rscFileAttrs.resourceFile)

        for fileAttrs in self.streamedFiles.values():
            self.closeFile(fileAttrs)

    def createGroupId (self):
        groupId = self.nextGroupId
        self.nextGroupId += 1
        return groupId

    def createResourceId (self):
        resourceId = self.nextResourceId
        self.nextResourceId += 1
        return resourceId

    @staticmethod
    def create (gameDir):
        unpacker = Unpacker(gameDir)
        unpacker.checkDirectories()
        unpacker.collectFiles()
        return unpacker

    def checkDirectories (self):
        if not os.path.isdir(self.gameDir):
            raise Exception('Game directory doesn\'t exist: {}'.format(self.gameDir))

        if not os.path.isdir(self.baseDir):
            raise Exception('Base directory doesn\'t exist: {}'.format(self.baseDir))

        if not os.path.isdir(self.vtDir):
            raise Exception('Virtualtextures directory doesn\'t exist: {}'.format(self.vtDir))

    def collectFiles (self):
        for itemName in os.listdir(self.baseDir):
            itemPath = os.path.join(self.baseDir, itemName)

            if not os.path.isfile(itemPath):
                continue

            fileAttrs = FileAttributes(
                path = itemPath,
                descriptor = None
            )

            if itemName == FILE_STREAMED_RESOURCES_NAME:
                self.streamedFiles[FILE_STREAMED_RESOURCES_KEY] = fileAttrs
            elif itemName.lower().endswith('.streamed'):
                self.streamedFiles[itemName] = fileAttrs

        # -------------------------------------------------------------------------

        filePath = os.path.join(self.baseDir, FILE_MASTER_INDEX_NAME)

        if not os.path.isfile(filePath):
            raise Exception('Master index file doesn\'t exist: {}'.format(filePath))

        with open(filePath, 'rb') as f:
            signature = f.read(4)

            if signature != SIGNATURE_SER:
                raise Exception('Wrong index file signature')

            entryCount = struct.unpack('>I', f.read(4))[0]

            for _ in range(entryCount):
                idxFileName = self.readSizedString(f)
                rscFileName = self.readSizedString(f)

                idxFilePath = os.path.join(self.baseDir, idxFileName)
                rscFilePath = os.path.join(self.baseDir, rscFileName)

                if not os.path.isfile(idxFilePath):
                    raise Exception('Index file doesn\'t exist: {}'.format(idxFilePath))

                if not os.path.isfile(rscFilePath):
                    raise Exception('Resource file doesn\'t exist: {}'.format(rscFilePath))

                self.resourceFiles.append(ResourceFileAttributes(
                    key = os.path.splitext(idxFileName)[0],
                    indexFile = FileAttributes(
                        path = idxFilePath,
                        descriptor = None
                    ),
                    resourceFile = FileAttributes(
                        path = rscFilePath,
                        descriptor = None
                    )
                ))


    def readSizedString (self, descriptor):
        strLength = struct.unpack('<I', descriptor.read(4))[0]
        return descriptor.read(strLength).decode('utf-8')

    def bytesToNullString (self, byteSeq):
        return ''.join([ chr(b) for b in byteSeq if b > 0 ])

    def openFileToRead (self, fileAttrs):
        if not fileAttrs.descriptor:
            fileAttrs.descriptor = open(fileAttrs.path, 'rb') 

        return fileAttrs.descriptor

    def closeFile (self, fileAttrs):
        if fileAttrs.descriptor:
            fileAttrs.descriptor.close()
            fileAttrs.descriptor = None

    def decompressData (self, data, addHeader = True):
        if addHeader:
            data = b'\x78\xda' + data

        decompress = zlib.decompressobj()
        data = decompress.decompress(data)
        data += decompress.flush()

        return data

    def readResourceFile (self, rscFileAttrs, resources):
        print('Read resource file \'{}\''.format(rscFileAttrs.key))

        chunk = rscFileAttrs.key
        idxFile = self.openFileToRead(rscFileAttrs.indexFile)
        rscFile = self.openFileToRead(rscFileAttrs.resourceFile)

        signature = idxFile.read(4)

        if signature != SIGNATURE_SER:
            raise Exception('Wrong signature')

        # Skip 24 always-zeroed bytes
        contentSize, _unk, entryCount = struct.unpack('>I24xII', idxFile.read(4 + 24 + 4 * 2))

        # + groupKey is not always looks like a path
        # + resourcePath always looks like a path
        # + many-to-many relationship between paths and keys
        # + groupKey-resourcePath combination can occur multiple times
        # + only one index file can have group(s) with the same group key
        # + only one index file can have resource(s) with the same resource path

        # For sounds:
        # - Extension of resourcePath is '.decl' if sub-resources == 0
        # - Extension of resourcePath is '.samplepack' if sub-resources > 1
        # - Sounds never have sub-resources count equal to 1

        # For samples:
        # - Samples always have '.bsnd' extension
        # - Samples always have sub-resources

        # Only sounds and samples can have sub-resources

        for _ in range(entryCount):
            groupBeginCursorPos = idxFile.tell()
            entryIndex = struct.unpack('>I', idxFile.read(4))[0]
            resourceType = self.readSizedString(idxFile)
            groupKey = self.readSizedString(idxFile)
            resourcePath = self.readSizedString(idxFile)
            resourceOffset, resourceDecompSize, resourceCompSize, subResourceCount = struct.unpack('>4I', idxFile.read(4 * 4))
            isSoundOrSample = resourceType in [ 'sound', 'sample' ]

            if subResourceCount > 0 and not isSoundOrSample:
                raise Exception('Expected no sub-resources for resource type \'{}\', but {} given'.format(resourceType, subResourceCount))

            # ------------------------------------------

            self._totalCompSize += resourceCompSize
            self._totalDecompSize += resourceDecompSize

            # if resourceType == 'sound' and resourceCompSize != resourceDecompSize:
            #     rscFile.seek(resourceOffset)
            #     data = self.decompressData(rscFile.read(resourceCompSize))
            #     print(data, '\n')

            # if resourceCompSize == resourceDecompSize and resourceCompSize > 100: # and resourceCompSize >= 8 and resourceCompSize <= 12:
            #     rscFile.seek(resourceOffset)
            #     data = rscFile.read(resourceCompSize)
            #     try: 
            #         print('+', data[:30], self.decompressData(data)[:30])
            #     except:
            #         print('-', data[:30])

                
                # print(chunk, groupBeginCursorPos, resourceOffset, resourceCompSize, resourceDecompSize)
                # print(data)

            # subResourceCount == 0:
            # 3038032 7882 1167
            # 3039200 97   66   # 'sound'
            # 3039280 547  313 

            # ------------------------------------------

            subResources = []

            resources.append({
                'chunk': chunk,
                'entryIndex': entryIndex,
                'resourceType': resourceType,
                'groupKey': groupKey,
                'resourcePath': resourcePath,
                'resourceOffset': resourceOffset,
                'resourceCompSize': resourceCompSize,
                'resourceDecompSize': resourceDecompSize,
                'subResources': subResources
            })

            for _ in range(subResourceCount):
                streamedFileName = self.bytesToNullString(idxFile.read(16))
                subResourceOffset, subResourceSize = struct.unpack('>2I', idxFile.read(4 * 2))
                streamedFileName = FILE_STREAMED_RESOURCES_KEY if not streamedFileName else '{}.streamed'.format(streamedFileName)

                subResources.append({
                    'streamedFileName': streamedFileName,
                    'subResourceOffset': subResourceOffset,
                    'subResourceSize': subResourceSize
                })


                # if rscFileName in self.streamedFiles:
                #     file = self.openFileToRead(self.streamedFiles[rscFileName])


                # if resourceType == 'sample':
                #     print(resourceType, '{}:{}:{}'.format(rscFileName, offset, size), groupKey, resourcePath)

            _unk5bytes = idxFile.read(5)

            # - != + !=
            # + == + !=
            # + == + ==
            # + != + ==
            if resourceType in ['cm', 'file'] and _unk5bytes != b'\x00\x00\x00\x00\x00' and resourceCompSize == resourceDecompSize:
                rscFile.seek(resourceOffset)
                data = rscFile.read(resourceCompSize)
                # if not data.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):
                print(resourceType, resourceOffset, struct.unpack('>BI', _unk5bytes), resourceCompSize, data[:48], '\n')

            # if _unk5bytes != b'\x00\x00\x00\x00\x00':
            #     print(idxFilePath, resourceType, formatBytes(_unk5bytes), subResourceCount, f.tell() - 5, '{}:{}:{}'.format(rscFilePath, resourceOffset, compressedSize))

            # print(entryIndex, resourceType, groupKey, resourcePath, resourceOffset, uncompressedSize, compressedSize, _unk5bytes, f.tell())

        # print(groupCount, _unk, groupCount - _unk)

        # print(totalSubCount)

        # for resourceType, rscCount in db.items():
        #     print('{:5d}'.format(rscCount), resourceType)

        return resources

    def readResourceFiles (self):
        resources = []

        for rscFileAttrs in self.resourceFiles:
            resources = self.readResourceFile(rscFileAttrs, resources)
            # break

        print('Total compressed:   {:.2f}Gb'.format(self._totalCompSize / 1024 / 1024 / 1024))
        print('Total decompressed: {:.2f}Gb'.format(self._totalDecompSize / 1024 / 1024 / 1024))

        # print(json.dumps(resources, ensure_ascii=False, indent=4))

if __name__ == '__main__':
    unpacker = Unpacker.create(GAME_DIR)
    unpacker.readResourceFiles()
    print('End')

    # 78 DA
    # 78 9C
    # 78 5E
    # 78 01
    # with open('_test.bin', 'rb') as f:
    #     data = b'\x78\xda' + f.read()

    #     decompress = zlib.decompressobj()
    #     inflated = decompress.decompress(data)
    #     inflated += decompress.flush()
    #     print(inflated)


    # https://stackoverflow.com/questions/252417/how-can-i-use-a-dll-file-from-python
    # hllDll = ctypes.WinDLL('G:\\Steam\\steamapps\\common\\Wolfenstein.The.New.Order\\base\\oo2core_8_win64.dll')

#     typedef int WINAPI OodLZ_CompressFunc(
#   int codec, uint8 *src_buf, size_t src_len, uint8 *dst_buf, int level,
#   void *opts, size_t offs, size_t unused, void *scratch, size_t scratch_size);
#   
# typedef int WINAPI OodLZ_DecompressFunc(
#   uint8 *src_buf, int src_len, uint8 *dst, size_t dst_size, int fuzz,
#   int crc, int verbose, uint8 *dst_base, size_t e, void *cb, void *cb_ctx, 
#   void *scratch, size_t scratch_size, int threadPhase);

    # OodLZ_Compress

'''
aas
achievement
aiBehavior
aiBehaviorVo
aiEvent
aiTurnParms
ammo
anim
animWeb
articulatedFigure
atlas
automap
baseModel
batteryWeapon
breakable
cg
chapter
cloth
cm
credits
cuttableResource
damage
destructiblePiece
difficultysetting
discreteAnimation
dragJoints
ebolt
enigma
entityDef
env
facialAnimSet
faction
file
flare
foliage
foliageModel
font
footstepEvents
fx
gamemodesp
glass
glassModel
globalflag
gore
goreBehavior
handIK
health
image
impactParticles
impactSounds
inventoryItem
job
jointconversion
laserCutterUpgrade
lasercutter
layer
loadingscreen
lootPool
mapInfo
material
md6Def
model
modelLOD
morphVertices
particle
playerArmor
playerProps
playerUpgradeAmmo
projectile
projectileImpactEffect
prtMeshDist
reachIK
renderParm
renderProg
ribbon
rollBones
sample
secrets
secrettype
skeleton
skins
sound
soundmixing
specialEvent
staticImage
staticParticleModel
subWeb
swfresource
table
targetinglaser
throwable
trackingParms
trailbeam
tutorialEvent
twitchPain
vehicle
vehicleWindowKit
video
visemeSet
vmtrPreload
voiceover
voicetrack
walkIK
weapon
weaponUpgrade
'''