from ..common import bfw
from ..common.types import *
from ..common.consts import *
from ..common.game_data import *

from .consts import *
from .types import *

from ..formats.gxt import GXT_EXT, GXTReader
from ..formats.txd import TXD_EXT, TXDReader, TXDStore, Texture, TXD
from ..formats.handling import Handling, HandlingReader
from ..formats.surface import SurfaceReader, SurfaceCombo
from ..formats.ped_stats import PedStatsReader, PedStats
from ..formats.time_cycle import TimeCycleReader, TCWeather
from ..formats.sfx import SFXReader, SFXSample, SFX_RAW_FILE_PATH, SFX_SDT_FILE_PATH
from ..formats.particles import ParticleReader, Particles, Particle, PARTICLE_TYPES_TO_FRAMES
from ..formats.ide import SimpleObject, initModelInfos, IDEReader, GameObjects, GameObjectType
from ..formats.bootstrap import Bootstrap, LoadResourceType
from ..formats.dff import DFFReader, DFF, RWClump
from ..formats.col import CollisionReader, TempCollisions, ColModel
from ..formats.object import ObjectReader, ObjectInfo
from ..formats.ifp import IFPReader, AnimBlock
from ..formats.ipl import IPLReader, Placements
from ..formats.car_colors import CarColorReader, CarColors
from ..formats.water import WaterReader, Water
from ..formats.peds import PedReader, PedData
from ..formats.ped_stats import PedStatsReader
from ..formats.ped_groups import PedGroupsReader, PedGroup
from ..formats.weapons import WeaponReader, WeaponInfo
from ..formats.fly_paths import readFlyPaths, FlyPaths
from ..formats.cutscene import readCutscenes, CutsceneData

from bfw.utils import *



class TXDList:
    def __init__ (self):
        self.particles : Opt[TXD] = None


class TextureList:
    def __init__ (self):
        self.font     : Dict[str, Texture] = {}
        self.hud      : Dict[str, Texture] = {}
        self.splash   : Dict[str, Texture] = {}
        self.frontend : Dict[str, Texture] = {}


class LoadContext:
    def __init__ (self):
        self.txdStore         : Opt[TXDStore]                = None
        self.langs            : Dict[str, dict]              = {}
        self.handling         : Opt[Handling]                = None
        self.tempColModels    : Opt[Type[TempCollisions]]    = None
        self.surface          : Opt[List[SurfaceCombo]]      = None
        self.pedStats         : Opt[PedStats]                = None
        self.timeCycle        : Opt[List[TCWeather]]         = None
        self.sfx              : Opt[List[SFXSample]]         = None
        self.particles        : Opt[Particles]               = None
        self.txd              : TXDList                      = TXDList()
        self.textures         : TextureList                  = TextureList()
        self.modelInfos       : Opt[GameObjects]             = None  # modelId to model (CSimpleModelInfo)
        self.objs             : Opt[List[ObjectInfo]]        = None
        self.animBlocks       : Opt[Dict[str, AnimBlock]]    = None
        self.placements       : Opt[Placements]              = None
        self.carColors        : Opt[CarColors]               = None
        self.playerTexture    : Opt[Texture]                 = None
        self.water            : Opt[Water]                   = None
        self.peds             : Opt[List[PedData]]           = None
        self.pedStats         : Opt[PedStats]                = None
        self.weapons          : Opt[WeaponInfo]              = None
        self.pedGroups        : Opt[List[PedGroup]]          = None
        self.markers          : Opt[Dict[str, RWClump]]      = None
        self.flyPaths         : Opt[FlyPaths]                = None
        self.cutscenes        : Opt[Dict[str, CutsceneData]] = None



# - Load IDEs
# - Load DFFs (during this complete IDE loader)
# - Link DFFs with Textures
# - Load IFPs for DFFs
# - Load cutscenes
# - Link with audio
def convertGame ():
    isFullParse = False
    isFastParse = not isFullParse

    ctx = LoadContext()

    ctx.txdStore = TXDStore()

    # LOAD LANGS (GXT)
    # --------------------------------------------------------------------------

    print('Loading languages...')

    for filePath in iterFiles(joinPath(GAME_DIR, 'text'), False, [ GXT_EXT ]):
        langName = getFileName(filePath).lower()

        ctx.langs[langName] = GXTReader.fromFile(filePath, parse=isFullParse)

    # LOAD ALL TEXTURES
    # --------------------------------------------------------------------------

    # print('Loading all textures...')

    # preload all TXDs
    # ctx.txdStore.loadAllTxd(GAME_DIR, metaOnly=isFastParse)

    # LOAD FONTS
    # --------------------------------------------------------------------------

    print('Loading fonts...')

    # TODO: parse fonts?
    txd = ctx.txdStore.loadTxd(joinPath(GAME_DIR, 'models/fonts.txd'), metaOnly=isFastParse)

    # CFont::Initialise()
    # game\src\renderer\Font.cpp:331

    ctx.textures.font['font1'] = txd.getTexture('font1')
    ctx.textures.font['font2'] = txd.getTexture('font2')

    # LOAD HUD
    # --------------------------------------------------------------------------

    print('Loading HUD...')

    # CHud::Initialise()
    # game\src\renderer\Hud.cpp:1706
    txd = ctx.txdStore.loadTxd(joinPath(GAME_DIR, 'models/hud.txd'), metaOnly=isFastParse)

    # fill hud.cpp Sprites using WeaponFilenames
    # NUM_HUD_SPRITES = 69
    # list index is id of sprite
    # sitesniper, sitelaser, viewfinder_128 -- unused
    weaponNames = [
        ('fist', 'fistm'),
        ('brassk', 'brasskA'),
        ('screw', 'screwA'),
        ('golf', 'golfA'),
        ('nightstick', 'nightstickA'),
        ('knife', 'knifeA'),
        ('bat', 'batm'),
        ('hammer', 'hammerA'),
        ('cleaver', 'cleaverA'),
        ('machete', 'macheteA'),
        ('sword', 'swordA'),
        ('chainsaw', 'chainsawA'),
        ('grenade', 'grenadeA'),
        ('grenade', 'grenadeA'),
        ('teargas', 'teargasA'),
        ('molotov', 'molotovA'),
        ('rocket', 'rocketA'),
        ('handGun1', 'handGun1A'),
        ('', ''),
        ('python', 'pythonA'),
        ('chromegun', 'chromegunA'),
        ('spasshotGun', 'spasshotGunA'),
        ('stubshotGun', 'stubshotGunA'),
        ('tec9', 'tec9A'),
        ('uzi1', 'uzi1A'),
        ('uzi2', 'uzi2A'),
        ('mp5', 'mp5A'),
        ('', ''),
        ('m4', 'm4A'),
        ('ruger', 'rugerA'),
        ('sniper', 'sniperA'),
        ('laserscope', 'laserscopeA'),
        ('', ''),
        ('rocket', 'rocketA'),
        ('flamer', 'flamerA'),
        ('m60', 'm60A'),
        ('minigun', 'minigunA'),
        ('bomb', 'bombA'),
        ('', ''),
        ('camera', 'cameraA'),
        ('', ''),
        ('siterocket', 'siterocket'),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('radardisc', 'radardisc'),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('', ''),
        ('sitesniper', 'sitesniperm'),
        ('siteM16', 'siteM16m'),
        ('sitelaser', 'sitelaserm'),
        ('laserdot', 'laserdotm'),
        ('viewfinder_128', 'viewfinder_128m'),
        ('bleeder', ''),
    ]

    for name, maskName in weaponNames:
        if name:
            tex = txd.getTexture(name, silent=True)

            if tex:
                ctx.textures.hud[tex.name] = tex

    # LOAD LOADING SCREEN & SPLASH SCREENS
    # --------------------------------------------------------------------------

    print('Loading splash screens...')

    # main loop / case GS_INIT_ONCE / LoadingScreen()
    # 0   : Used as startup image and as world loading screen in PC version
    # 1-13: Randomly selected in CGame::Initialise() during save loading
    for i in range(0, 14):
        texName = f'loadsc{ i }'

        txd = ctx.txdStore.loadTxd(joinPath(GAME_DIR, f'txd/{ texName }.txd'), metaOnly=isFastParse)

        tex = txd.getTexture(texName)

        ctx.textures.splash[tex.name] = tex

    # LOAD HANDLING
    # --------------------------------------------------------------------------

    print('Loading handling...')

    ctx.handling = HandlingReader.fromFile(joinPath(GAME_DIR, 'data/handling.cfg'), convert=True)

    # LOAD SURFACE
    # --------------------------------------------------------------------------

    print('Generating temp collisions...')

    ctx.tempColModels = TempCollisions.generate()

    # LOAD SURFACE
    # --------------------------------------------------------------------------

    print('Loading surface...')

    ctx.surface = SurfaceReader.fromFile(joinPath(GAME_DIR, 'data/surface.dat'))

    # LOAD PED STATS
    # --------------------------------------------------------------------------

    print('Loading ped stats...')

    ctx.pedStats = PedStatsReader.fromFile(joinPath(GAME_DIR, 'data/pedstats.dat'))

    # LOAD TIME CYCLES
    # --------------------------------------------------------------------------

    print('Loading time cycle...')

    ctx.timeCycle = TimeCycleReader.fromFile(joinPath(GAME_DIR, 'data/timecyc.dat'))

    # LOAD SFX
    # --------------------------------------------------------------------------

    print('Loading SFX...')

    ctx.sfx = SFXReader.fromFile(SFX_RAW_FILE_PATH, SFX_SDT_FILE_PATH)

    # LOAD ALL FRONTEND TEXTURES
    # --------------------------------------------------------------------------

    print('Loading frontend textures...')

    NUM_MENU_SPRITES = 26
    FRONTEND_SPRITES = [
        ('background', ''),
        ('vc_logo', 'vc_logom'),
        ('mouse', 'mousea'),
        ('mapTop01', 'mapTop01A'),
        ('mapTop02', 'mapTop02A'),
        ('mapTop03', 'mapTop03A'),
        ('mapMid01', 'mapMid01A'),
        ('mapMid02', 'mapMid02A'),
        ('mapMid03', 'mapMid03A'),
        ('mapBot01', 'mapBot01A'),
        ('mapBot02', 'mapBot02A'),
        ('mapBot03', 'mapBot03A'),
        ('wildstyle', 'wildstyleA'),
        ('flash', 'flashA'),
        ('kchat', 'kchatA'),
        ('fever', 'feverA'),
        ('vrock', 'vrockA'),
        ('vcpr', 'vcprA'),
        ('espantoso', 'espantosoA'),
        ('emotion', 'emotionA'),
        ('wave103', 'wave103A'),
        ('mp3', 'mp3A'),
        ('downOff', 'buttonA'),
        ('downOn', 'buttonA'),
        ('upOff', 'buttonA'),
        ('upOn', 'buttonA'),
    ]

    # TODO: link with eMenuSprites enum
    # game\src\core\Frontend.cpp:3013
    for path, start, end in [
        ('models/fronten1.txd', 0, 3),
        ('models/fronten2.txd', 3, NUM_MENU_SPRITES),
    ]:
        print(f'\t{ path }')

        txd = ctx.txdStore.loadTxd(joinPath(GAME_DIR, path), metaOnly=isFastParse)

        for i in range(start, end):
            name = FRONTEND_SPRITES[i][0]

            # set m_aFrontEndSprites[i].SetAddressing(rwTEXTUREADDRESSBORDER);
            if not name:
                continue

            tex = txd.getTexture(name)

            ctx.textures.frontend[tex.name] = tex


    # --------------------------------------------------------------------------
    # -------------------------- GAME TO LOAD SELECTED -------------------------
    # --------------------------------------------------------------------------

    # LOAD PARTICLES
    # --------------------------------------------------------------------------

    print('Loading particle data...')

    # TODO: also preload generic.txd
    # TODO: reorganize manually loaded data to ctx.txd and txd.dff
    # TODO: load files by all readers
    # TODO: load all cutscenes *.ifp and *.dat
    # TODO: check removeAllCollisions()
    # TODO: impl ctx.txdStore getTexture('txdName', 'texName') with textureCache (generic) fallback
    # TODO: load outro.txd
    # TODO: correct dff pipelines, right callbacks...

    # From dat:
    # - CFileLoader::LoadModelFile('smth.dff') - load clump, extract atomics to ctx.modelInfos, destroy clump
    #   RwStreamOpen(rwSTREAMFILENAME, rwSTREAMREAD, filename)
    #   clump = RpClumpStreamRead(stream)
    #   RpClumpForAllAtomics(clump, CFileLoader::FindRelatedModelInfoCB, clump)  # check CFileLoader::FindRelatedModelInfoCB!!!
    # Hardcoded:
    # - CFileLoader::LoadAtomicFile2Return('smth.dff') - load and return clump
    # Requested:
    # - CStreaming::ConvertBufferToObject()
    #     mi = ctx.modelInfo...
    #     if mi.isSimple:  # obj, tobj, weapon
    #       CFileLoader::LoadAtomicFile(stream, streamId)
    #         # similar to "From dat" (move atomics to ctx.modelInfos, destroy clump)
    #     else:
    #       CFileLoader::LoadClumpFile(RwStream *stream, uint32 id)
    #         clump = RpClumpStreamRead(stream)
    #         mi.setClump(clump)  # HUGE FN!!!

    # load dff:
    # - find mi
    # - in mi find linked anim and load
    # - in mi find linked tex and load
    # - load dff itself

    ctx.txd.particles = ctx.txdStore.loadTxd(joinPath(GAME_DIR, 'models/particle.txd'), metaOnly=isFastParse)

    # LoadParticleData()
    # load particles from config and link them with textures
    ctx.particles = ParticleReader.fromFile(joinPath(GAME_DIR, 'data/particle.cfg'), ctx)

    # LOAD LEVELS
    # --------------------------------------------------------------------------

    print('Loading levels...')

    initModelInfos(ctx)

    for path in [
        joinPath(GAME_DIR, 'data/default.dat'),
        joinPath(GAME_DIR, 'data/gta_vc.dat'),
    ]:
        for cmd in Bootstrap.fromFile(path):
            relPath = getRelPath(cmd.path, GAME_DIR)

            match cmd.action:
                case LoadResourceType.Splash:  # +
                    # skip, all splashes are handled above
                    print(f'\tSPLASH: { cmd.path }')

                case LoadResourceType.ItemDefinitions:  # +
                    print(f'\tIDE: { relPath }')
                    # fulfills ctx.modelInfos with all models from this ide
                    IDEReader.fromFile(cmd.path, ctx)

                case LoadResourceType.TextureDict:  # +
                    print(f'\tTXD: { relPath }')
                    ctx.txdStore.cacheTxdTextures(cmd.path, metaOnly=isFastParse)

                case LoadResourceType.Model:  # ±
                    print(f'\tDFF: { relPath }')

                    dff = DFFReader.fromFile(cmd.path, ctx)

                    assert ctx.modelInfos

                    for atomic in dff.clump.atomics:
                        frame = atomic.getFrame()

                        assert frame

                        modelName = frame.getBaseName()
                        lodIndex  = frame.getLODIndex()

                        info = ctx.modelInfos.getByName(modelName)

                        assert info
                        assert info.isSimple()

                        info.setAtomic(lodIndex, atomic)

                case LoadResourceType.Collision:  # +
                    print(f'\tCOL: { relPath }')

                    addCollisions(ctx, CollisionReader.fromFile(cmd.path))

                case LoadResourceType.ItemPlacements:
                    print(f'\tIPL: { relPath }')

                    if ctx.objs is None:
                        ObjectReader.fromFile(joinPath(GAME_DIR, 'data/object.dat'), ctx)
                        loadGTA3Image(ctx)

                    IPLReader.fromFile(cmd.path, ctx)
                case _:
                    raise Exception(f'Unknown action { cmd.action }')

            '''
            ms_aInfoForModel = [
                0   -6500 (0-MODELINFOSIZE)                      - models
                6500-7885 (STREAM_OFFSET_TXD-STREAM_OFFSET_COL)  - txds
                7885-7916 (STREAM_OFFSET_COL-STREAM_OFFSET_ANIM) - cols
                7916-7951 (STREAM_OFFSET_ANIM-NUMSTREAMINFO)     - anims
            ]
            
            MAXVEHICLESLOADED = 50
            
            DFF - if has model info in ctx.modelInfos
            TXD - always
            IFP - always
            COL - always, and also:
                def->bounds.left = 1000000.0f;
                def->bounds.top = 1000000.0f;
                def->bounds.right = -1000000.0f;
                def->bounds.bottom = -1000000.0f;
                def->minIndex = INT16_MAX;
                def->maxIndex = INT16_MIN;
                strcpy(def->name, name);
                
            islandLODmainland - id of "IslandLODmainland" from ctx.modelInfos
            islandLODbeach - id of "IslandLODbeach" from ctx.modelInfos
            
            !!! when LoadAllCollisions skip "generic" it is already loaded with ide
            
            CStreaming::ConvertBufferToObject - parses all loaded data from *.img
            '''

            # TODO:
            #  for(i = 1; i < COLSTORESIZE; i++)
            #      if(CColStore::GetSlot(i))
            #          CColStore::GetBoundingBox(i).Grow(120.0f);
            #  CWorld::RepositionCertainDynamicObjects();
            #  CColStore::RemoveAllCollision();

            # +ide, +col, +object.dat, ±ifp, ±ipl, cuts/*.dat


    # LOAD VEHICLE COLORS
    # --------------------------------------------------------------------------

    print('Loading vehicle colors...')

    CarColorReader.fromFile(joinPath(GAME_DIR, 'data/carcols.dat'), ctx)

    # TODO: CVehicleModelInfo::LoadEnvironmentMaps() -- load texture "white" from txd "particle"

    # LOAD PLAYER SKIN
    # --------------------------------------------------------------------------

    print('Loading player skin...')

    # TODO: apply correct filters
    ctx.playerTexture = ctx.txdStore.loadImage(joinPath(GAME_DIR, 'models/generic/player.bmp'), '@player_skin')

    # LOAD WATER
    # --------------------------------------------------------------------------

    print('Loading water...')

    WaterReader.fromFile(joinPath(GAME_DIR, 'data/waterpro.dat'), ctx)

    # LOAD WATER
    # --------------------------------------------------------------------------

    print('Loading ped animations...')

    addAnimation(ctx, IFPReader.fromFile(joinPath(GAME_DIR, 'anim/ped.ifp')))

    # TODO: do this, but load DFF clumps into ctx.modelInfos correctly first
    # animAssocGroups = Array(ANIM_ASSOC_GROUP_COUNT, AnimBlendAssocGroup)
    # ms_aAnimAssocGroups = new CAnimBlendAssocGroup[NUM_ANIM_ASSOC_GROUPS];
    # CreateAnimAssocGroups();

    # LOAD PED DATA
    # --------------------------------------------------------------------------

    print('Loading ped data...')

    PedReader.fromFile(joinPath(GAME_DIR, 'data/ped.dat'), ctx)
    PedStatsReader.fromFile(joinPath(GAME_DIR, 'data/pedstats.dat'), ctx)
    PedGroupsReader.fromFile(joinPath(GAME_DIR, 'data/pedgrp.dat'), ctx)
    # TODO: SetAnimOffsetForEnterOrExitVehicle();

    # LOAD WEAPON DATA
    # --------------------------------------------------------------------------

    print('Loading weapon data...')

    WeaponReader.fromFile(joinPath(GAME_DIR, 'data/weapon.dat'), ctx)

    # LOAD 3D MARKERS
    # --------------------------------------------------------------------------

    print('Loading 3D markers...')

    # TODO: load textures from "particle.txd" (see C3dMarkers::Init())
    ctx.markers = {
        'arrow':    DFFReader.fromFile(joinPath(GAME_DIR, 'models/generic/arrow.dff'), ctx).clump,
        'cylinder': DFFReader.fromFile(joinPath(GAME_DIR, 'models/generic/zonecylb.dff'), ctx).clump
    }

    # LOAD FLY PATHS
    # --------------------------------------------------------------------------

    print('Loading fly paths...')

    ctx.flyPaths = readFlyPaths(ctx)

    # LOAD CUTSCENES
    # --------------------------------------------------------------------------

    print('Loading cutscenes...')

    ctx.cutscenes = readCutscenes(joinPath(GAME_DIR, 'anim/cuts'))



class AnimBlendAssocGroup:
    def __init__ (self):
        pass
        # CAnimBlock *animBlock
        # CAnimBlendAssociation *assocList
        # int32 numAssociations
        # int32 firstAnimId
        # int32 groupId -- id of self in ms_aAnimAssocGroups


# game/src/core/Streaming.cpp:509 (CStreaming::ConvertBufferToObject)
# TODO: see end of CStreaming::Init2(void)
def loadGTA3Image (ctx : LoadContext):
    for filePath in iterFiles(joinPath(GAME_DIR, 'models', 'gta3'), False):
        match getExt(filePath):
            case '.dff':
                addModel(ctx, DFFReader.fromFile(filePath, ctx))
            case '.txd':
                pass  # TODO
            case '.col':
                addCollisions(ctx, CollisionReader.fromFile(filePath))
            case '.ifp':
                addAnimation(ctx, IFPReader.fromFile(filePath))
                # TODO: CAnimManager::CreateAnimAssocGroups();

    # TODO: links models with anims and textures


def addModel (ctx : LoadContext, dff : DFF):
    assert ctx.modelInfos

    modelName = getFileName(dff.filePath).lower()
    modelInfo = ctx.modelInfos.getByName(modelName)
    clump     = dff.clump

    if not modelInfo:
        printW(f'Model info is not found for model: { getBaseName(dff.filePath) }')
        return

    # obj, time obj, weapon
    # set each atomic into corresponding LOD slot in model info
    if modelInfo.isSimple():
        for atomic in dff.clump.atomics:
            modelInfo.setAtomic(atomic.getFrame().getLODIndex(), atomic)

    # clump, ped, vehicle ()
    # set clump to model info, set HAnimHierarchy to each atomic, update bone weights
    else:
        modelInfo.setClump(clump)


# TODO: add level and smth
def addCollisions (ctx : LoadContext, colModels : Dict[str, ColModel]):
    assert ctx.modelInfos

    for modelName, colModel in colModels.items():
        info = ctx.modelInfos.getByName(modelName)

        if not info:
            printW(f'Model info not found for model "{ modelName }"')
            continue

        info.colModel = colModel


def addAnimation (ctx : LoadContext, animBlock : AnimBlock):
    if not ctx.animBlocks:
        ctx.animBlocks = {}

    assert animBlock.name not in ctx.animBlocks

    ctx.animBlocks[animBlock.name] = animBlock



def _test_ ():
    convertGame()



__all__ = [
    '_test_',
]



if __name__ == '__main__':
    _test_()
