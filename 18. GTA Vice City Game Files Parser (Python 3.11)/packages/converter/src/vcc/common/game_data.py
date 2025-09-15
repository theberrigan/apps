from .types import *

from .bfw_ import bfw

from bfw.types.enums import Enum



# for handling.cfg and object.dat
GRAVITY = 0.008

# all models with draw distance greater
# than LOD_DISTANCE are treated as low-LOD
LOD_DISTANCE = 300  # * TheCamera.LODDistMultiplier (default 1.0)


# noinspection SpellCheckingInspection
class ModelId (Enum):
    DODO               = -2             # MI_DODO
    TRAIN              = -1             # MI_TRAIN
    PLAYER             = 0              # MI_PLAYER
    COP                = 1              # MI_COP
    SWAT               = 2              # MI_SWAT
    FBI                = 3              # MI_FBI
    ARMY               = 4              # MI_ARMY
    MEDIC              = 5              # MI_MEDIC
    FIREMAN            = 6              # MI_FIREMAN
    MALE01             = 7              # MI_MALE01
    HFYST              = 9              # MI_HFYST
    HFOST              = 10             # MI_HFOST
    HMYST              = 11             # MI_HMYST
    HMOST              = 12             # MI_HMOST
    HFYRI              = 13             # MI_HFYRI
    HFORI              = 14             # MI_HFORI
    HMYRI              = 15             # MI_HMYRI
    HMORI              = 16             # MI_HMORI
    HFYBE              = 17             # MI_HFYBE
    HFOBE              = 18             # MI_HFOBE
    HMYBE              = 19             # MI_HMYBE
    HMOBE              = 20             # MI_HMOBE
    HFYBU              = 21             # MI_HFYBU
    HFYMD              = 22             # MI_HFYMD
    HFYCG              = 23             # MI_HFYCG
    HFYPR              = 24             # MI_HFYPR
    HFOTR              = 25             # MI_HFOTR
    HMOTR              = 26             # MI_HMOTR
    HMYAP              = 27             # MI_HMYAP
    HMOCA              = 28             # MI_HMOCA
    TAXI_D             = HMOCA          # MI_TAXI_D
    BMODK              = 29             # MI_BMODK
    BMYKR              = 30             # MI_BMYKR
    BFYST              = 31             # MI_BFYST
    BFOST              = 32             # MI_BFOST
    BMYST              = 33             # MI_BMYST
    BMOST              = 34             # MI_BMOST
    BFYRI              = 35             # MI_BFYRI
    BFORI              = 36             # MI_BFORI
    BMYRI              = 37             # MI_BMYRI
    BFYBE              = 38             # MI_BFYBE
    BMYBE              = 39             # MI_BMYBE
    BFOBE              = 40             # MI_BFOBE
    BMOBE              = 41             # MI_BMOBE
    BMYBU              = 42             # MI_BMYBU
    BFYPR              = 43             # MI_BFYPR
    BFOTR              = 44             # MI_BFOTR
    BMOTR              = 45             # MI_BMOTR
    BMYPI              = 46             # MI_BMYPI
    BMYBB              = 47             # MI_BMYBB
    WMYCR              = 48             # MI_WMYCR
    WFYST              = 49             # MI_WFYST
    WFOST              = 50             # MI_WFOST
    WMYST              = 51             # MI_WMYST
    WMOST              = 52             # MI_WMOST
    WFYRI              = 53             # MI_WFYRI
    WFORI              = 54             # MI_WFORI
    WMYRI              = 55             # MI_WMYRI
    WMORI              = 56             # MI_WMORI
    WFYBE              = 57             # MI_WFYBE
    WMYBE              = 58             # MI_WMYBE
    WFOBE              = 59             # MI_WFOBE
    WMOBE              = 60             # MI_WMOBE
    WMYCW              = 61             # MI_WMYCW
    WMYGO              = 62             # MI_WMYGO
    WFOGO              = 63             # MI_WFOGO
    WMOGO              = 64             # MI_WMOGO
    WFYLG              = 65             # MI_WFYLG
    WMYLG              = 66             # MI_WMYLG
    WFYBU              = 67             # MI_WFYBU
    WMYBU              = 68             # MI_WMYBU
    WMOBU              = 69             # MI_WMOBU
    WFYPR              = 70             # MI_WFYPR
    WFOTR              = 71             # MI_WFOTR
    WMOTR              = 72             # MI_WMOTR
    WMYPI              = 73             # MI_WMYPI
    WMOCA              = 74             # MI_WMOCA
    WFYJG              = 75             # MI_WFYJG
    WMYJG              = 76             # MI_WMYJG
    WFYSK              = 77             # MI_WFYSK
    WMYSK              = 78             # MI_WMYSK
    WFYSH              = 79             # MI_WFYSH
    WFOSH              = 80             # MI_WFOSH
    JFOTO              = 81             # MI_JFOTO
    JMOTO              = 82             # MI_JMOTO
    CBA                = 83             # MI_CBA
    CBB                = 84             # MI_CBB
    HNA                = 85             # MI_HNA
    HNB                = 86             # MI_HNB
    SGA                = 87             # MI_SGA
    SGB                = 88             # MI_SGB
    CLA                = 89             # MI_CLA
    CLB                = 90             # MI_CLB
    GDA                = 91             # MI_GDA
    GDB                = 92             # MI_GDB
    BKA                = 93             # MI_BKA
    BKB                = 94             # MI_BKB
    PGA                = 95             # MI_PGA
    PGB                = 96             # MI_PGB
    VICE1              = 97             # MI_VICE1
    VICE2              = 98             # MI_VICE2
    VICE3              = 99             # MI_VICE3
    VICE4              = 100            # MI_VICE4
    VICE5              = 101            # MI_VICE5
    VICE6              = 102            # MI_VICE6
    VICE7              = 103            # MI_VICE7
    VICE8              = 104            # MI_VICE8
    WFYG1              = 105            # MI_WFYG1
    WFYG2              = 106            # MI_WFYG2
    SPECIAL01          = 109            # MI_SPECIAL01
    SPECIAL02          = 110            # MI_SPECIAL02
    SPECIAL03          = 111            # MI_SPECIAL03
    SPECIAL04          = 112            # MI_SPECIAL04
    SPECIAL05          = 113            # MI_SPECIAL05
    SPECIAL06          = 114            # MI_SPECIAL06
    SPECIAL07          = 115            # MI_SPECIAL07
    SPECIAL08          = 116            # MI_SPECIAL08
    SPECIAL09          = 117            # MI_SPECIAL09
    SPECIAL10          = 118            # MI_SPECIAL10
    SPECIAL11          = 119            # MI_SPECIAL11
    SPECIAL12          = 120            # MI_SPECIAL12
    SPECIAL13          = 121            # MI_SPECIAL13
    SPECIAL14          = 122            # MI_SPECIAL14
    SPECIAL15          = 123            # MI_SPECIAL15
    SPECIAL16          = 124            # MI_SPECIAL16
    SPECIAL17          = 125            # MI_SPECIAL17
    SPECIAL18          = 126            # MI_SPECIAL18
    SPECIAL19          = 127            # MI_SPECIAL19
    SPECIAL20          = 128            # MI_SPECIAL20
    SPECIAL21          = 129            # MI_SPECIAL21
    LAST_PED           = SPECIAL21      # MI_LAST_PED
    FIRST_VEHICLE      = 130            # MI_FIRST_VEHICLE
    LANDSTAL           = FIRST_VEHICLE  # MI_LANDSTAL
    IDAHO              = 131            # MI_IDAHO
    STINGER            = 132            # MI_STINGER
    LINERUN            = 133            # MI_LINERUN
    PEREN              = 134            # MI_PEREN
    SENTINEL           = 135            # MI_SENTINEL
    RIO                = 136            # MI_RIO
    FIRETRUCK          = 137            # MI_FIRETRUCK
    TRASH              = 138            # MI_TRASH
    STRETCH            = 139            # MI_STRETCH
    MANANA             = 140            # MI_MANANA
    INFERNUS           = 141            # MI_INFERNUS
    VOODOO             = 142            # MI_VOODOO
    PONY               = 143            # MI_PONY
    MULE               = 144            # MI_MULE
    CHEETAH            = 145            # MI_CHEETAH
    AMBULAN            = 146            # MI_AMBULAN
    FBICAR             = 147            # MI_FBICAR
    MOONBEAM           = 148            # MI_MOONBEAM
    ESPERANT           = 149            # MI_ESPERANT
    TAXI               = 150            # MI_TAXI
    WASHING            = 151            # MI_WASHING
    BOBCAT             = 152            # MI_BOBCAT
    MRWHOOP            = 153            # MI_MRWHOOP
    BFINJECT           = 154            # MI_BFINJECT
    HUNTER             = 155            # MI_HUNTER
    POLICE             = 156            # MI_POLICE
    ENFORCER           = 157            # MI_ENFORCER
    SECURICA           = 158            # MI_SECURICA
    BANSHEE            = 159            # MI_BANSHEE
    PREDATOR           = 160            # MI_PREDATOR
    BUS                = 161            # MI_BUS
    RHINO              = 162            # MI_RHINO
    BARRACKS           = 163            # MI_BARRACKS
    CUBAN              = 164            # MI_CUBAN
    CHOPPER            = 165            # MI_CHOPPER
    ANGEL              = 166            # MI_ANGEL
    COACH              = 167            # MI_COACH
    CABBIE             = 168            # MI_CABBIE
    STALLION           = 169            # MI_STALLION
    RUMPO              = 170            # MI_RUMPO
    RCBANDIT           = 171            # MI_RCBANDIT
    ROMERO             = 172            # MI_ROMERO
    PACKER             = 173            # MI_PACKER
    SENTXS             = 174            # MI_SENTXS
    ADMIRAL            = 175            # MI_ADMIRAL
    SQUALO             = 176            # MI_SQUALO
    SEASPAR            = 177            # MI_SEASPAR
    PIZZABOY           = 178            # MI_PIZZABOY
    GANGBUR            = 179            # MI_GANGBUR
    AIRTRAIN           = 180            # MI_AIRTRAIN
    DEADDODO           = 181            # MI_DEADDODO
    SPEEDER            = 182            # MI_SPEEDER
    REEFER             = 183            # MI_REEFER
    TROPIC             = 184            # MI_TROPIC
    FLATBED            = 185            # MI_FLATBED
    YANKEE             = 186            # MI_YANKEE
    CADDY              = 187            # MI_CADDY
    ZEBRA              = 188            # MI_ZEBRA
    TOPFUN             = 189            # MI_TOPFUN
    SKIMMER            = 190            # MI_SKIMMER
    PCJ600             = 191            # MI_PCJ600
    FAGGIO             = 192            # MI_FAGGIO
    FREEWAY            = 193            # MI_FREEWAY
    RCBARON            = 194            # MI_RCBARON
    RCRAIDER           = 195            # MI_RCRAIDER
    GLENDALE           = 196            # MI_GLENDALE
    OCEANIC            = 197            # MI_OCEANIC
    SANCHEZ            = 198            # MI_SANCHEZ
    SPARROW            = 199            # MI_SPARROW
    PATRIOT            = 200            # MI_PATRIOT
    LOVEFIST           = 201            # MI_LOVEFIST
    COASTG             = 202            # MI_COASTG
    DINGHY             = 203            # MI_DINGHY
    HERMES             = 204            # MI_HERMES
    SABRE              = 205            # MI_SABRE
    SABRETUR           = 206            # MI_SABRETUR
    PHEONIX            = 207            # MI_PHEONIX
    WALTON             = 208            # MI_WALTON
    REGINA             = 209            # MI_REGINA
    COMET              = 210            # MI_COMET
    DELUXO             = 211            # MI_DELUXO
    BURRITO            = 212            # MI_BURRITO
    SPAND              = 213            # MI_SPAND
    MARQUIS            = 214            # MI_MARQUIS
    BAGGAGE            = 215            # MI_BAGGAGE
    KAUFMAN            = 216            # MI_KAUFMAN
    MAVERICK           = 217            # MI_MAVERICK
    VCNMAV             = 218            # MI_VCNMAV
    RANCHER            = 219            # MI_RANCHER
    FBIRANCH           = 220            # MI_FBIRANCH
    VIRGO              = 221            # MI_VIRGO
    GREENWOO           = 222            # MI_GREENWOO
    JETMAX             = 223            # MI_JETMAX
    HOTRING            = 224            # MI_HOTRING
    SANDKING           = 225            # MI_SANDKING
    BLISTAC            = 226            # MI_BLISTAC
    POLMAV             = 227            # MI_POLMAV
    BOXVILLE           = 228            # MI_BOXVILLE
    BENSON             = 229            # MI_BENSON
    MESA               = 230            # MI_MESA
    RCGOBLIN           = 231            # MI_RCGOBLIN
    HOTRINA            = 232            # MI_HOTRINA
    HOTRINB            = 233            # MI_HOTRINB
    BLOODRA            = 234            # MI_BLOODRA
    BLOODRB            = 235            # MI_BLOODRB
    VICECHEE           = 236            # MI_VICECHEE
    LAST_VEHICLE       = VICECHEE       # MI_LAST_VEHICLE
    WHEEL_RIM          = 237            # MI_WHEEL_RIM
    WHEEL_OFFROAD      = 238            # MI_WHEEL_OFFROAD
    WHEEL_TRUCK        = 239            # MI_WHEEL_TRUCK
    CAR_DOOR           = 240            # MI_CAR_DOOR
    CAR_BUMPER         = 241            # MI_CAR_BUMPER
    CAR_PANEL          = 242            # MI_CAR_PANEL
    CAR_BONNET         = 243            # MI_CAR_BONNET
    CAR_BOOT           = 244            # MI_CAR_BOOT
    CAR_WHEEL          = 245            # MI_CAR_WHEEL
    BODYPARTA          = 246            # MI_BODYPARTA
    BODYPARTB          = 247            # MI_BODYPARTB
    WHEEL_SPORT        = 250            # MI_WHEEL_SPORT
    WHEEL_SALOON       = 251            # MI_WHEEL_SALOON
    WHEEL_LIGHTVAN     = 252            # MI_WHEEL_LIGHTVAN
    WHEEL_CLASSIC      = 253            # MI_WHEEL_CLASSIC
    WHEEL_ALLOY        = 254            # MI_WHEEL_ALLOY
    WHEEL_LIGHTTRUCK   = 255            # MI_WHEEL_LIGHTTRUCK
    WHEEL_SMALLCAR     = 256            # MI_WHEEL_SMALLCAR
    AIRTRAIN_VLO       = 257            # MI_AIRTRAIN_VLO
    MOBILE             = 258            # MI_MOBILE
    BRASS_KNUCKLES     = 259            # MI_BRASS_KNUCKLES
    SCREWDRIVER        = 260            # MI_SCREWDRIVER
    GOLFCLUB           = 261            # MI_GOLFCLUB
    NIGHTSTICK         = 262            # MI_NIGHTSTICK
    KNIFE              = 263            # MI_KNIFE
    BASEBALL_BAT       = 264            # MI_BASEBALL_BAT
    HAMMER             = 265            # MI_HAMMER
    MEAT_CLEAVER       = 266            # MI_MEAT_CLEAVER
    MACHETE            = 267            # MI_MACHETE
    KATANA             = 268            # MI_KATANA
    CHAINSAW           = 269            # MI_CHAINSAW
    GRENADE            = 270            # MI_GRENADE
    TEARGAS            = 271            # MI_TEARGAS
    MOLOTOV            = 272            # MI_MOLOTOV
    MISSILE            = 273            # MI_MISSILE
    COLT45             = 274            # MI_COLT45
    PYTHON             = 275            # MI_PYTHON
    RUGER              = 276            # MI_RUGER
    SHOTGUN            = 277            # MI_SHOTGUN
    SPAS12_SHOTGUN     = 278            # MI_SPAS12_SHOTGUN
    STUBBY_SHOTGUN     = 279            # MI_STUBBY_SHOTGUN
    M4                 = 280            # MI_M4
    TEC9               = 281            # MI_TEC9
    UZI                = 282            # MI_UZI
    SILENCEDINGRAM     = 283            # MI_SILENCEDINGRAM
    MP5                = 284            # MI_MP5
    SNIPERRIFLE        = 285            # MI_SNIPERRIFLE
    LASERSCOPE         = 286            # MI_LASERSCOPE
    ROCKETLAUNCHER     = 287            # MI_ROCKETLAUNCHER
    FLAMETHROWER       = 288            # MI_FLAMETHROWER
    M60                = 289            # MI_M60
    MINIGUN            = 290            # MI_MINIGUN
    BOMB               = 291            # MI_BOMB
    CAMERA             = 292            # MI_CAMERA
    FINGERS            = 293            # MI_FINGERS
    MINIGUN2           = 294            # MI_MINIGUN2
    CUTOBJ01           = 295            # MI_CUTOBJ01
    CUTOBJ02           = 296            # MI_CUTOBJ02
    CUTOBJ03           = 297            # MI_CUTOBJ03
    CUTOBJ04           = 298            # MI_CUTOBJ04
    CUTOBJ05           = 299            # MI_CUTOBJ05
    NUM_DEFAULT_MODELS = 300            # NUM_DEFAULT_MODELS

    # The following must be mapped by string name after *.ide loading
    # ---------------------------------------------------------------
    FIRE_HYDRANT              = None  # MI_FIRE_HYDRANT
    PHONESIGN                 = None  # MI_PHONESIGN
    NOPARKINGSIGN1            = None  # MI_NOPARKINGSIGN1
    BUSSIGN1                  = None  # MI_BUSSIGN1
    ROADWORKBARRIER1          = None  # MI_ROADWORKBARRIER1
    DUMP1                     = None  # MI_DUMP1
    TRAFFICCONE               = None  # MI_TRAFFICCONE
    NEWSSTAND                 = None  # MI_NEWSSTAND
    POSTBOX1                  = None  # MI_POSTBOX1
    BIN                       = None  # MI_BIN
    WASTEBIN                  = None  # MI_WASTEBIN
    PHONEBOOTH1               = None  # MI_PHONEBOOTH1
    PARKINGMETER              = None  # MI_PARKINGMETER
    PARKINGMETER2             = None  # MI_PARKINGMETER2
    MALLFAN                   = None  # MI_MALLFAN
    HOTELFAN_NIGHT            = None  # MI_HOTELFAN_NIGHT
    HOTELFAN_DAY              = None  # MI_HOTELFAN_DAY
    HOTROOMFAN                = None  # MI_HOTROOMFAN
    TRAFFICLIGHTS             = None  # MI_TRAFFICLIGHTS
    TRAFFICLIGHTS_VERTICAL    = None  # MI_TRAFFICLIGHTS_VERTICAL
    TRAFFICLIGHTS_MIAMI       = None  # MI_TRAFFICLIGHTS_MIAMI
    TRAFFICLIGHTS_TWOVERTICAL = None  # MI_TRAFFICLIGHTS_TWOVERTICAL
    SINGLESTREETLIGHTS1       = None  # MI_SINGLESTREETLIGHTS1
    SINGLESTREETLIGHTS2       = None  # MI_SINGLESTREETLIGHTS2
    SINGLESTREETLIGHTS3       = None  # MI_SINGLESTREETLIGHTS3
    DOUBLESTREETLIGHTS        = None  # MI_DOUBLESTREETLIGHTS
    STREETLAMP1               = None  # MI_STREETLAMP1
    STREETLAMP2               = None  # MI_STREETLAMP2
    TREE2                     = None  # MI_TREE2
    TREE3                     = None  # MI_TREE3
    TREE6                     = None  # MI_TREE6
    TREE8                     = None  # MI_TREE8
    CRANE_1                   = None  # MODELID_CRANE_1
    CRANE_2                   = None  # MODELID_CRANE_2
    CRANE_3                   = None  # MODELID_CRANE_3
    CRANE_4                   = None  # MODELID_CRANE_4
    CRANE_5                   = None  # MODELID_CRANE_5
    CRANE_6                   = None  # MODELID_CRANE_6
    COLLECTABLE1              = None  # MI_COLLECTABLE1
    MONEY                     = None  # MI_MONEY
    CARMINE                   = None  # MI_CARMINE
    GARAGEDOOR2               = None  # MI_GARAGEDOOR2
    GARAGEDOOR3               = None  # MI_GARAGEDOOR3
    GARAGEDOOR4               = None  # MI_GARAGEDOOR4
    GARAGEDOOR5               = None  # MI_GARAGEDOOR5
    GARAGEDOOR6               = None  # MI_GARAGEDOOR6
    GARAGEDOOR7               = None  # MI_GARAGEDOOR7
    GARAGEDOOR9               = None  # MI_GARAGEDOOR9
    GARAGEDOOR10              = None  # MI_GARAGEDOOR10
    GARAGEDOOR11              = None  # MI_GARAGEDOOR11
    GARAGEDOOR12              = None  # MI_GARAGEDOOR12
    GARAGEDOOR13              = None  # MI_GARAGEDOOR13
    GARAGEDOOR14              = None  # MI_GARAGEDOOR14
    GARAGEDOOR15              = None  # MI_GARAGEDOOR15
    GARAGEDOOR16              = None  # MI_GARAGEDOOR16
    GARAGEDOOR18              = None  # MI_GARAGEDOOR18
    GARAGEDOOR19              = None  # MI_GARAGEDOOR19
    GARAGEDOOR20              = None  # MI_GARAGEDOOR20
    GARAGEDOOR21              = None  # MI_GARAGEDOOR21
    GARAGEDOOR22              = None  # MI_GARAGEDOOR22
    GARAGEDOOR23              = None  # MI_GARAGEDOOR23
    GARAGEDOOR24              = None  # MI_GARAGEDOOR24
    GARAGEDOOR25              = None  # MI_GARAGEDOOR25
    GARAGEDOOR26              = None  # MI_GARAGEDOOR26
    NAUTICALMINE              = None  # MI_NAUTICALMINE
    BRIEFCASE                 = None  # MI_BRIEFCASE
    GLASS1                    = None  # MI_GLASS1
    GLASS8                    = None  # MI_GLASS8
    EXPLODINGBARREL           = None  # MI_EXPLODINGBARREL
    PICKUP_ADRENALINE         = None  # MI_PICKUP_ADRENALINE
    PICKUP_BODYARMOUR         = None  # MI_PICKUP_BODYARMOUR
    PICKUP_INFO               = None  # MI_PICKUP_INFO
    PICKUP_HEALTH             = None  # MI_PICKUP_HEALTH
    PICKUP_BONUS              = None  # MI_PICKUP_BONUS
    PICKUP_BRIBE              = None  # MI_PICKUP_BRIBE
    PICKUP_KILLFRENZY         = None  # MI_PICKUP_KILLFRENZY
    PICKUP_CAMERA             = None  # MI_PICKUP_CAMERA
    PICKUP_REVENUE            = None  # MI_PICKUP_REVENUE
    PICKUP_SAVEGAME           = None  # MI_PICKUP_SAVEGAME
    PICKUP_PROPERTY           = None  # MI_PICKUP_PROPERTY
    PICKUP_PROPERTY_FORSALE   = None  # MI_PICKUP_PROPERTY_FORSALE
    PICKUP_CLOTHES            = None  # MI_PICKUP_CLOTHES
    BOLLARDLIGHT              = None  # MI_BOLLARDLIGHT
    FENCE                     = None  # MI_FENCE
    FENCE2                    = None  # MI_FENCE2
    PETROLPUMP                = None  # MI_PETROLPUMP
    PETROLPUMP2               = None  # MI_PETROLPUMP2
    BUOY                      = None  # MI_BUOY
    PARKTABLE                 = None  # MI_PARKTABLE
    LAMPPOST1                 = None  # MI_LAMPPOST1
    VEG_PALM01                = None  # MI_VEG_PALM01
    VEG_PALM02                = None  # MI_VEG_PALM02
    VEG_PALM03                = None  # MI_VEG_PALM03
    VEG_PALM04                = None  # MI_VEG_PALM04
    VEG_PALM05                = None  # MI_VEG_PALM05
    VEG_PALM06                = None  # MI_VEG_PALM06
    VEG_PALM07                = None  # MI_VEG_PALM07
    VEG_PALM08                = None  # MI_VEG_PALM08
    MLAMPPOST                 = None  # MI_MLAMPPOST
    BARRIER1                  = None  # MI_BARRIER1
    LITTLEHA_POLICE           = None  # MI_LITTLEHA_POLICE
    TELPOLE02                 = None  # MI_TELPOLE02
    TRAFFICLIGHT01            = None  # MI_TRAFFICLIGHT01
    PARKBENCH                 = None  # MI_PARKBENCH
    PLC_STINGER               = None  # MI_PLC_STINGER
    LIGHTBEAM                 = None  # MI_LIGHTBEAM
    AIRPORTRADAR              = None  # MI_AIRPORTRADAR
    RCBOMB                    = None  # MI_RCBOMB
    BEACHBALL                 = None  # MI_BEACHBALL
    SANDCASTLE1               = None  # MI_SANDCASTLE1
    SANDCASTLE2               = None  # MI_SANDCASTLE2
    JELLYFISH                 = None  # MI_JELLYFISH
    JELLYFISH01               = None  # MI_JELLYFISH01
    FISH1SINGLE               = None  # MI_FISH1SINGLE
    FISH1S                    = None  # MI_FISH1S
    FISH2SINGLE               = None  # MI_FISH2SINGLE
    FISH2S                    = None  # MI_FISH2S
    FISH3SINGLE               = None  # MI_FISH3SINGLE
    FISH3S                    = None  # MI_FISH3S
    TURTLE                    = None  # MI_TURTLE
    DOLPHIN                   = None  # MI_DOLPHIN
    SHARK                     = None  # MI_SHARK
    SUBMARINE                 = None  # MI_SUBMARINE
    ESCALATORSTEP             = None  # MI_ESCALATORSTEP
    LOUNGE_WOOD_UP            = None  # MI_LOUNGE_WOOD_UP
    LOUNGE_TOWEL_UP           = None  # MI_LOUNGE_TOWEL_UP
    LOUNGE_WOOD_DN            = None  # MI_LOUNGE_WOOD_DN
    LOTION                    = None  # MI_LOTION
    BEACHTOWEL01              = None  # MI_BEACHTOWEL01
    BEACHTOWEL02              = None  # MI_BEACHTOWEL02
    BEACHTOWEL03              = None  # MI_BEACHTOWEL03
    BEACHTOWEL04              = None  # MI_BEACHTOWEL04
    BLIMP_NIGHT               = None  # MI_BLIMP_NIGHT
    BLIMP_DAY                 = None  # MI_BLIMP_DAY
    YT_MAIN_BODY              = None  # MI_YT_MAIN_BODY
    YT_MAIN_BODY2             = None  # MI_YT_MAIN_BODY2

    @classmethod
    def setModelId (cls, modelName : str, value : int):
        keys = MODEL_NAME_TO_ID.get(modelName.lower())

        if not keys:
            return

        for key in keys:
            cls.setValue(key, value)


# when name in ide found, corresponding keys of the ModelId enum
# must be updated with id from that ide using ModelId.setValue(key, newValue)
# noinspection SpellCheckingInspection
MODEL_NAME_TO_ID = {
    'fire_hydrant'      : [ 'FIRE_HYDRANT' ],
    'phonesign'         : [ 'PHONESIGN' ],
    'noparkingsign1'    : [ 'NOPARKINGSIGN1' ],
    'bussign1'          : [ 'BUSSIGN1' ],
    'roadworkbarrier1'  : [ 'ROADWORKBARRIER1', 'BARRIER1' ],
    'dump1'             : [ 'DUMP1' ],
    'trafficcone'       : [ 'TRAFFICCONE' ],
    'newsstand1'        : [ 'NEWSSTAND' ],
    'postbox1'          : [ 'POSTBOX1' ],
    'bin1'              : [ 'BIN' ],
    'wastebin'          : [ 'WASTEBIN' ],
    'phonebooth1'       : [ 'PHONEBOOTH1' ],
    'parkingmeter'      : [ 'PARKINGMETER' ],
    'parkingmeterg'     : [ 'PARKINGMETER2' ],
    'mall_fans'         : [ 'MALLFAN' ],
    'htl_fan_rotate_nt' : [ 'HOTELFAN_NIGHT' ],
    'htl_fan_rotate_dy' : [ 'HOTELFAN_DAY' ],
    'hotroomfan'        : [ 'HOTROOMFAN' ],
    'trafficlight1'     : [ 'TRAFFICLIGHTS', 'TRAFFICLIGHT01' ],
    'mtraffic4'         : [ 'TRAFFICLIGHTS_VERTICAL' ],
    'mtraffic1'         : [ 'TRAFFICLIGHTS_MIAMI' ],
    'mtraffic2'         : [ 'TRAFFICLIGHTS_TWOVERTICAL' ],
    'lamppost1'         : [ 'SINGLESTREETLIGHTS1', 'LAMPPOST1' ],
    'lamppost2'         : [ 'SINGLESTREETLIGHTS2' ],
    'lamppost3'         : [ 'SINGLESTREETLIGHTS3' ],
    'doublestreetlght1' : [ 'DOUBLESTREETLIGHTS' ],
    'streetlamp1'       : [ 'STREETLAMP1' ],
    'streetlamp2'       : [ 'STREETLAMP2' ],
    'veg_tree3'         : [ 'TREE2' ],
    'veg_treea1'        : [ 'TREE3' ],
    'veg_treeb1'        : [ 'TREE6' ],
    'veg_treea3'        : [ 'TREE8' ],
    'doc_crane_cab0'    : [ 'CRANE_1' ],
    'doc_crane_cab01'   : [ 'CRANE_2' ],
    'doc_crane_cab02'   : [ 'CRANE_3' ],
    'doc_crane_cab03'   : [ 'CRANE_4' ],
    'boatcranelg0'      : [ 'CRANE_5' ],
    'lodnetopa0'        : [ 'CRANE_6' ],
    'package1'          : [ 'COLLECTABLE1' ],
    'money'             : [ 'MONEY' ],
    'barrel1'           : [ 'CARMINE' ],
    'dk_paynspraydoor'  : [ 'GARAGEDOOR2' ],
    'dk_waretankdoor1'  : [ 'GARAGEDOOR3' ],
    'hav_garagedoor1'   : [ 'GARAGEDOOR4' ],
    'hav_garagedoor02'  : [ 'GARAGEDOOR5' ],
    'hav_garagedoor03'  : [ 'GARAGEDOOR6' ],
    'hav_garagedoor04'  : [ 'GARAGEDOOR7' ],
    'lh_showdoor03'     : [ 'GARAGEDOOR9' ],
    'lh_showdoor1'      : [ 'GARAGEDOOR10' ],
    'lhtankdoor'        : [ 'GARAGEDOOR11' ],
    'nbtgardoor'        : [ 'GARAGEDOOR12' ],
    'dk_camjonesdoor'   : [ 'GARAGEDOOR13' ],
    'nbtgardoor02'      : [ 'GARAGEDOOR14' ],
    'dt_savedra'        : [ 'GARAGEDOOR15' ],
    'dt_savedrb'        : [ 'GARAGEDOOR16' ],
    'dk_bombdoor'       : [ 'GARAGEDOOR18' ],
    'haiwshpnsdoor'     : [ 'GARAGEDOOR19' ],
    'wshpnsdoor'        : [ 'GARAGEDOOR20' ],
    'nbecpnsdoor'       : [ 'GARAGEDOOR21' ],
    'nbtgardoor03'      : [ 'GARAGEDOOR22' ],
    'dt_savedrc'        : [ 'GARAGEDOOR23' ],
    'dt_savedrd'        : [ 'GARAGEDOOR24' ],
    'man_frntstepgd'    : [ 'GARAGEDOOR25' ],
    'svegrgedoor'       : [ 'GARAGEDOOR26' ],
    'barrel2'           : [ 'NAUTICALMINE' ],
    'briefcase'         : [ 'BRIEFCASE' ],
    'wglasssmash'       : [ 'GLASS1' ],
    'glassfx_composh'   : [ 'GLASS8' ],
    'barrel4'           : [ 'EXPLODINGBARREL' ],
    'adrenaline'        : [ 'PICKUP_ADRENALINE' ],
    'bodyarmour'        : [ 'PICKUP_BODYARMOUR' ],
    'info'              : [ 'PICKUP_INFO' ],
    'health'            : [ 'PICKUP_HEALTH' ],
    'bonus'             : [ 'PICKUP_BONUS' ],
    'bribe'             : [ 'PICKUP_BRIBE' ],
    'killfrenzy'        : [ 'PICKUP_KILLFRENZY' ],
    'camerapickup'      : [ 'PICKUP_CAMERA' ],
    'bigdollar'         : [ 'PICKUP_REVENUE' ],
    'pickupsave'        : [ 'PICKUP_SAVEGAME' ],
    'property_locked'   : [ 'PICKUP_PROPERTY' ],
    'property_fsale'    : [ 'PICKUP_PROPERTY_FORSALE' ],
    'clothesp'          : [ 'PICKUP_CLOTHES' ],
    'bollardlight'      : [ 'BOLLARDLIGHT' ],
    'bar_barrier10'     : [ 'FENCE' ],
    'bar_barrier12'     : [ 'FENCE2' ],
    'petrolpump'        : [ 'PETROLPUMP' ],
    'washgaspump'       : [ 'PETROLPUMP2' ],
    'bouy'              : [ 'BUOY' ],
    'parktable1'        : [ 'PARKTABLE' ],
    'veg_palm04'        : [ 'VEG_PALM01' ],
    'veg_palwee02'      : [ 'VEG_PALM02' ],
    'veg_palmkbb11'     : [ 'VEG_PALM03' ],
    'veg_palmkb4'       : [ 'VEG_PALM04' ],
    'veg_palm02'        : [ 'VEG_PALM05' ],
    'veg_palmkb3'       : [ 'VEG_PALM06' ],
    'veg_palmbig14'     : [ 'VEG_PALM07' ],
    'veg_palm01'        : [ 'VEG_PALM08' ],
    'mlamppost'         : [ 'MLAMPPOST' ],
    'littleha_police'   : [ 'LITTLEHA_POLICE' ],
    'telgrphpole02'     : [ 'TELPOLE02' ],
    'parkbench1'        : [ 'PARKBENCH' ],
    'plc_stinger'       : [ 'PLC_STINGER' ],
    'od_lightbeam'      : [ 'LIGHTBEAM' ],
    'ap_radar1_01'      : [ 'AIRPORTRADAR' ],
    'rcbomb'            : [ 'RCBOMB' ],
    'beachball'         : [ 'BEACHBALL' ],
    'sandcastle1'       : [ 'SANDCASTLE1' ],
    'sandcastle2'       : [ 'SANDCASTLE2' ],
    'jellyfish'         : [ 'JELLYFISH' ],
    'jellyfish01'       : [ 'JELLYFISH01' ],
    'fish1single'       : [ 'FISH1SINGLE' ],
    'fish1s'            : [ 'FISH1S' ],
    'fish2single'       : [ 'FISH2SINGLE' ],
    'fish2s'            : [ 'FISH2S' ],
    'fish3single'       : [ 'FISH3SINGLE' ],
    'fish3s'            : [ 'FISH3S' ],
    'turtle'            : [ 'TURTLE' ],
    'dolphin'           : [ 'DOLPHIN' ],
    'shark'             : [ 'SHARK' ],
    'submarine'         : [ 'SUBMARINE' ],
    'esc_step'          : [ 'ESCALATORSTEP' ],
    'lounge_wood_up'    : [ 'LOUNGE_WOOD_UP' ],
    'lounge_towel_up'   : [ 'LOUNGE_TOWEL_UP' ],
    'lounge_wood_dn'    : [ 'LOUNGE_WOOD_DN' ],
    'lotion'            : [ 'LOTION' ],
    'beachtowel01'      : [ 'BEACHTOWEL01' ],
    'beachtowel02'      : [ 'BEACHTOWEL02' ],
    'beachtowel03'      : [ 'BEACHTOWEL03' ],
    'beachtowel04'      : [ 'BEACHTOWEL04' ],
    'blimp_night'       : [ 'BLIMP_NIGHT' ],
    'blimp_day'         : [ 'BLIMP_DAY' ],
    'yt_main_body'      : [ 'YT_MAIN_BODY' ],
    'yt_main_body2'     : [ 'YT_MAIN_BODY2' ],
}


# noinspection SpellCheckingInspection
class AnimAssocGroupId (Enum):
    STD                   = 0   # ASSOCGRP_STD
    VAN                   = 1   # ASSOCGRP_VAN
    COACH                 = 2   # ASSOCGRP_COACH
    BIKE_STANDARD         = 3   # ASSOCGRP_BIKE_STANDARD
    BIKE_VESPA            = 4   # ASSOCGRP_BIKE_VESPA
    BIKE_HARLEY           = 5   # ASSOCGRP_BIKE_HARLEY
    BIKE_DIRT             = 6   # ASSOCGRP_BIKE_DIRT
    UNARMED               = 7   # ASSOCGRP_UNARMED
    SCREWDRIVER           = 8   # ASSOCGRP_SCREWDRIVER
    KNIFE                 = 9   # ASSOCGRP_KNIFE
    BASEBALLBAT           = 10  # ASSOCGRP_BASEBALLBAT
    GOLFCLUB              = 11  # ASSOCGRP_GOLFCLUB
    CHAINSAW              = 12  # ASSOCGRP_CHAINSAW
    PYTHON                = 13  # ASSOCGRP_PYTHON
    COLT                  = 14  # ASSOCGRP_COLT
    SHOTGUN               = 15  # ASSOCGRP_SHOTGUN
    BUDDY                 = 16  # ASSOCGRP_BUDDY
    TEC                   = 17  # ASSOCGRP_TEC
    UZI                   = 18  # ASSOCGRP_UZI
    RIFLE                 = 19  # ASSOCGRP_RIFLE
    M60                   = 20  # ASSOCGRP_M60
    SNIPER                = 21  # ASSOCGRP_SNIPER
    THROW                 = 22  # ASSOCGRP_THROW
    FLAMETHROWER          = 23  # ASSOCGRP_FLAMETHROWER
    MEDIC                 = 24  # ASSOCGRP_MEDIC
    SUNBATHE              = 25  # ASSOCGRP_SUNBATHE
    PLAYER_IDLE           = 26  # ASSOCGRP_PLAYER_IDLE
    RIOT                  = 27  # ASSOCGRP_RIOT
    STRIP                 = 28  # ASSOCGRP_STRIP
    LANCE                 = 29  # ASSOCGRP_LANCE
    PLAYER                = 30  # ASSOCGRP_PLAYER
    PLAYERROCKET          = 31  # ASSOCGRP_PLAYERROCKET
    PLAYER1ARMED          = 32  # ASSOCGRP_PLAYER1ARMED
    PLAYER2ARMED          = 33  # ASSOCGRP_PLAYER2ARMED
    PLAYERBBBAT           = 34  # ASSOCGRP_PLAYERBBBAT
    PLAYERCHAINSAW        = 35  # ASSOCGRP_PLAYERCHAINSAW
    SHUFFLE               = 36  # ASSOCGRP_SHUFFLE
    OLD                   = 37  # ASSOCGRP_OLD
    GANG1                 = 38  # ASSOCGRP_GANG1
    GANG2                 = 39  # ASSOCGRP_GANG2
    FAT                   = 40  # ASSOCGRP_FAT
    OLDFAT                = 41  # ASSOCGRP_OLDFAT
    JOGGER                = 42  # ASSOCGRP_JOGGER
    WOMAN                 = 43  # ASSOCGRP_WOMAN
    WOMANSHOP             = 44  # ASSOCGRP_WOMANSHOP
    BUSYWOMAN             = 45  # ASSOCGRP_BUSYWOMAN
    SEXYWOMAN             = 46  # ASSOCGRP_SEXYWOMAN
    FATWOMAN              = 47  # ASSOCGRP_FATWOMAN
    OLDWOMAN              = 48  # ASSOCGRP_OLDWOMAN
    JOGWOMAN              = 49  # ASSOCGRP_JOGWOMAN
    PANICCHUNKY           = 50  # ASSOCGRP_PANICCHUNKY
    SKATE                 = 51  # ASSOCGRP_SKATE
    PLAYERBACK            = 52  # ASSOCGRP_PLAYERBACK
    PLAYERLEFT            = 53  # ASSOCGRP_PLAYERLEFT
    PLAYERRIGHT           = 54  # ASSOCGRP_PLAYERRIGHT
    ROCKETBACK            = 55  # ASSOCGRP_ROCKETBACK
    ROCKETLEFT            = 56  # ASSOCGRP_ROCKETLEFT
    ROCKETRIGHT           = 57  # ASSOCGRP_ROCKETRIGHT
    CHAINSAWBACK          = 58  # ASSOCGRP_CHAINSAWBACK
    CHAINSAWLEFT          = 59  # ASSOCGRP_CHAINSAWLEFT
    CHAINSAWRIGHT         = 60  # ASSOCGRP_CHAINSAWRIGHT


ANIM_ASSOC_GROUP_COUNT = 61  # NUM_ANIM_ASSOC_GROUPS


# noinspection SpellCheckingInspection
class AnimationId (Enum):
    STD_WALK                          = 0                  # ANIM_STD_WALK
    STD_RUN                           = 1                  # ANIM_STD_RUN
    STD_RUNFAST                       = 2                  # ANIM_STD_RUNFAST
    STD_IDLE                          = 3                  # ANIM_STD_IDLE
    STD_STARTWALK                     = 4                  # ANIM_STD_STARTWALK
    STD_RUNSTOP1                      = 5                  # ANIM_STD_RUNSTOP1
    STD_RUNSTOP2                      = 6                  # ANIM_STD_RUNSTOP2
    STD_IDLE_CAM                      = 7                  # ANIM_STD_IDLE_CAM
    STD_IDLE_HBHB                     = 8                  # ANIM_STD_IDLE_HBHB
    STD_IDLE_TIRED                    = 9                  # ANIM_STD_IDLE_TIRED
    STD_IDLE_BIGGUN                   = 10                 # ANIM_STD_IDLE_BIGGUN
    STD_CHAT                          = 11                 # ANIM_STD_CHAT
    STD_HAILTAXI                      = 12                 # ANIM_STD_HAILTAXI
    STD_KO_FRONT                      = 13                 # ANIM_STD_KO_FRONT
    STD_KO_LEFT                       = 14                 # ANIM_STD_KO_LEFT
    STD_KO_BACK                       = 15                 # ANIM_STD_KO_BACK
    STD_KO_RIGHT                      = 16                 # ANIM_STD_KO_RIGHT
    STD_KO_SHOT_FACE                  = 17                 # ANIM_STD_KO_SHOT_FACE
    STD_KO_SHOT_STOMACH               = 18                 # ANIM_STD_KO_SHOT_STOMACH
    STD_KO_SHOT_ARM_L                 = 19                 # ANIM_STD_KO_SHOT_ARM_L
    STD_KO_SHOT_ARM_R                 = 20                 # ANIM_STD_KO_SHOT_ARM_R
    STD_KO_SHOT_LEG_L                 = 21                 # ANIM_STD_KO_SHOT_LEG_L
    STD_KO_SHOT_LEG_R                 = 22                 # ANIM_STD_KO_SHOT_LEG_R
    STD_SPINFORWARD_LEFT              = 23                 # ANIM_STD_SPINFORWARD_LEFT
    STD_SPINFORWARD_RIGHT             = 24                 # ANIM_STD_SPINFORWARD_RIGHT
    STD_HIGHIMPACT_FRONT              = 25                 # ANIM_STD_HIGHIMPACT_FRONT
    STD_HIGHIMPACT_LEFT               = 26                 # ANIM_STD_HIGHIMPACT_LEFT
    STD_HIGHIMPACT_BACK               = 27                 # ANIM_STD_HIGHIMPACT_BACK
    STD_HIGHIMPACT_RIGHT              = 28                 # ANIM_STD_HIGHIMPACT_RIGHT
    STD_HITBYGUN_FRONT                = 29                 # ANIM_STD_HITBYGUN_FRONT
    STD_HITBYGUN_LEFT                 = 30                 # ANIM_STD_HITBYGUN_LEFT
    STD_HITBYGUN_BACK                 = 31                 # ANIM_STD_HITBYGUN_BACK
    STD_HITBYGUN_RIGHT                = 32                 # ANIM_STD_HITBYGUN_RIGHT
    STD_HIT_FRONT                     = 33                 # ANIM_STD_HIT_FRONT
    STD_HIT_LEFT                      = 34                 # ANIM_STD_HIT_LEFT
    STD_HIT_BACK                      = 35                 # ANIM_STD_HIT_BACK
    STD_HIT_RIGHT                     = 36                 # ANIM_STD_HIT_RIGHT
    STD_HIT_FLOOR                     = 37                 # ANIM_STD_HIT_FLOOR
    STD_HIT_BODYBLOW                  = 38                 # ANIM_STD_HIT_BODYBLOW
    STD_HIT_CHEST                     = 39                 # ANIM_STD_HIT_CHEST
    STD_HIT_HEAD                      = 40                 # ANIM_STD_HIT_HEAD
    STD_HIT_WALK                      = 41                 # ANIM_STD_HIT_WALK
    STD_HIT_WALL                      = 42                 # ANIM_STD_HIT_WALL
    STD_HIT_FLOOR_FRONT               = 43                 # ANIM_STD_HIT_FLOOR_FRONT
    STD_HIT_BEHIND                    = 44                 # ANIM_STD_HIT_BEHIND
    STD_FIGHT_IDLE                    = 45                 # ANIM_STD_FIGHT_IDLE
    STD_FIGHT_2IDLE                   = 46                 # ANIM_STD_FIGHT_2IDLE
    STD_FIGHT_SHUFFLE_F               = 47                 # ANIM_STD_FIGHT_SHUFFLE_F
    STD_FIGHT_BODYBLOW                = 48                 # ANIM_STD_FIGHT_BODYBLOW
    STD_FIGHT_HEAD                    = 49                 # ANIM_STD_FIGHT_HEAD
    STD_FIGHT_KICK                    = 50                 # ANIM_STD_FIGHT_KICK
    STD_FIGHT_KNEE                    = 51                 # ANIM_STD_FIGHT_KNEE
    STD_FIGHT_LHOOK                   = 52                 # ANIM_STD_FIGHT_LHOOK
    STD_FIGHT_PUNCH                   = 53                 # ANIM_STD_FIGHT_PUNCH
    STD_FIGHT_ROUNDHOUSE              = 54                 # ANIM_STD_FIGHT_ROUNDHOUSE
    STD_FIGHT_LONGKICK                = 55                 # ANIM_STD_FIGHT_LONGKICK
    STD_PARTIAL_PUNCH                 = 56                 # ANIM_STD_PARTIAL_PUNCH
    STD_FIGHT_JAB                     = 57                 # ANIM_STD_FIGHT_JAB
    STD_FIGHT_ELBOW_L                 = 58                 # ANIM_STD_FIGHT_ELBOW_L
    STD_FIGHT_ELBOW_R                 = 59                 # ANIM_STD_FIGHT_ELBOW_R
    STD_FIGHT_BKICK_L                 = 60                 # ANIM_STD_FIGHT_BKICK_L
    STD_FIGHT_BKICK_R                 = 61                 # ANIM_STD_FIGHT_BKICK_R
    STD_DETONATE                      = 62                 # ANIM_STD_DETONATE
    STD_PUNCH                         = 63                 # ANIM_STD_PUNCH
    STD_PARTIALPUNCH                  = 64                 # ANIM_STD_PARTIALPUNCH
    STD_KICKGROUND                    = 65                 # ANIM_STD_KICKGROUND
    STD_THROW_UNDER                   = 66                 # ANIM_STD_THROW_UNDER
    STD_FIGHT_SHUFFLE_B               = 67                 # ANIM_STD_FIGHT_SHUFFLE_B
    STD_JACKEDCAR_RHS                 = 68                 # ANIM_STD_JACKEDCAR_RHS
    STD_JACKEDCAR_LO_RHS              = 69                 # ANIM_STD_JACKEDCAR_LO_RHS
    STD_JACKEDCAR_LHS                 = 70                 # ANIM_STD_JACKEDCAR_LHS
    STD_JACKEDCAR_LO_LHS              = 71                 # ANIM_STD_JACKEDCAR_LO_LHS
    STD_QUICKJACK                     = 72                 # ANIM_STD_QUICKJACK
    STD_QUICKJACKED                   = 73                 # ANIM_STD_QUICKJACKED
    STD_CAR_ALIGN_DOOR_LHS            = 74                 # ANIM_STD_CAR_ALIGN_DOOR_LHS
    STD_CAR_ALIGNHI_DOOR_LHS          = 75                 # ANIM_STD_CAR_ALIGNHI_DOOR_LHS
    STD_CAR_OPEN_DOOR_LHS             = 76                 # ANIM_STD_CAR_OPEN_DOOR_LHS
    STD_CARDOOR_LOCKED_LHS            = 77                 # ANIM_STD_CARDOOR_LOCKED_LHS
    STD_CAR_PULL_OUT_PED_LHS          = 78                 # ANIM_STD_CAR_PULL_OUT_PED_LHS
    STD_CAR_PULL_OUT_PED_LO_LHS       = 79                 # ANIM_STD_CAR_PULL_OUT_PED_LO_LHS
    STD_CAR_GET_IN_LHS                = 80                 # ANIM_STD_CAR_GET_IN_LHS
    STD_CAR_GET_IN_LO_LHS             = 81                 # ANIM_STD_CAR_GET_IN_LO_LHS
    STD_CAR_CLOSE_DOOR_LHS            = 82                 # ANIM_STD_CAR_CLOSE_DOOR_LHS
    STD_CAR_CLOSE_DOOR_LO_LHS         = 83                 # ANIM_STD_CAR_CLOSE_DOOR_LO_LHS
    STD_CAR_CLOSE_DOOR_ROLLING_LHS    = 84                 # ANIM_STD_CAR_CLOSE_DOOR_ROLLING_LHS
    STD_CAR_CLOSE_DOOR_ROLLING_LO_LHS = 85                 # ANIM_STD_CAR_CLOSE_DOOR_ROLLING_LO_LHS
    STD_CAR_JUMP_IN_LO_LHS            = 86                 # ANIM_STD_CAR_JUMP_IN_LO_LHS
    STD_GETOUT_LHS                    = 87                 # ANIM_STD_GETOUT_LHS
    STD_GETOUT_LO_LHS                 = 88                 # ANIM_STD_GETOUT_LO_LHS
    STD_CAR_CLOSE_LHS                 = 89                 # ANIM_STD_CAR_CLOSE_LHS
    STD_CAR_ALIGN_DOOR_RHS            = 90                 # ANIM_STD_CAR_ALIGN_DOOR_RHS
    STD_CAR_ALIGNHI_DOOR_RHS          = 91                 # ANIM_STD_CAR_ALIGNHI_DOOR_RHS
    STD_CAR_OPEN_DOOR_RHS             = 92                 # ANIM_STD_CAR_OPEN_DOOR_RHS
    STD_CARDOOR_LOCKED_RHS            = 93                 # ANIM_STD_CARDOOR_LOCKED_RHS
    STD_CAR_PULL_OUT_PED_RHS          = 94                 # ANIM_STD_CAR_PULL_OUT_PED_RHS
    STD_CAR_PULL_OUT_PED_LO_RHS       = 95                 # ANIM_STD_CAR_PULL_OUT_PED_LO_RHS
    STD_CAR_GET_IN_RHS                = 96                 # ANIM_STD_CAR_GET_IN_RHS
    STD_CAR_GET_IN_LO_RHS             = 97                 # ANIM_STD_CAR_GET_IN_LO_RHS
    STD_CAR_CLOSE_DOOR_RHS            = 98                 # ANIM_STD_CAR_CLOSE_DOOR_RHS
    STD_CAR_CLOSE_DOOR_LO_RHS         = 99                 # ANIM_STD_CAR_CLOSE_DOOR_LO_RHS
    STD_CAR_SHUFFLE_RHS               = 100                # ANIM_STD_CAR_SHUFFLE_RHS
    STD_CAR_SHUFFLE_LO_RHS            = 101                # ANIM_STD_CAR_SHUFFLE_LO_RHS
    STD_CAR_SIT                       = 102                # ANIM_STD_CAR_SIT
    STD_CAR_SIT_LO                    = 103                # ANIM_STD_CAR_SIT_LO
    STD_CAR_SIT_P                     = 104                # ANIM_STD_CAR_SIT_P
    STD_CAR_SIT_P_LO                  = 105                # ANIM_STD_CAR_SIT_P_LO
    STD_CAR_DRIVE_LEFT                = 106                # ANIM_STD_CAR_DRIVE_LEFT
    STD_CAR_DRIVE_RIGHT               = 107                # ANIM_STD_CAR_DRIVE_RIGHT
    STD_CAR_DRIVE_LEFT_LO             = 108                # ANIM_STD_CAR_DRIVE_LEFT_LO
    STD_CAR_DRIVE_RIGHT_LO            = 109                # ANIM_STD_CAR_DRIVE_RIGHT_LO
    STD_CAR_DRIVEBY_LEFT              = 110                # ANIM_STD_CAR_DRIVEBY_LEFT
    STD_CAR_DRIVEBY_RIGHT             = 111                # ANIM_STD_CAR_DRIVEBY_RIGHT
    STD_CAR_DRIVEBY_LEFT_LO           = 112                # ANIM_STD_CAR_DRIVEBY_LEFT_LO
    STD_CAR_DRIVEBY_RIGHT_LO          = 113                # ANIM_STD_CAR_DRIVEBY_RIGHT_LO
    STD_CAR_LOOKBEHIND                = 114                # ANIM_STD_CAR_LOOKBEHIND
    STD_BOAT_DRIVE                    = 115                # ANIM_STD_BOAT_DRIVE
    STD_BOAT_DRIVE_LEFT               = 116                # ANIM_STD_BOAT_DRIVE_LEFT
    STD_BOAT_DRIVE_RIGHT              = 117                # ANIM_STD_BOAT_DRIVE_RIGHT
    STD_BOAT_LOOKBEHIND               = 118                # ANIM_STD_BOAT_LOOKBEHIND
    STD_BIKE_PICKUP_LHS               = 119                # ANIM_STD_BIKE_PICKUP_LHS
    STD_BIKE_PICKUP_RHS               = 120                # ANIM_STD_BIKE_PICKUP_RHS
    STD_BIKE_PULLUP_LHS               = 121                # ANIM_STD_BIKE_PULLUP_LHS
    STD_BIKE_PULLUP_RHS               = 122                # ANIM_STD_BIKE_PULLUP_RHS
    STD_BIKE_ELBOW_LHS                = 123                # ANIM_STD_BIKE_ELBOW_LHS
    STD_BIKE_ELBOW_RHS                = 124                # ANIM_STD_BIKE_ELBOW_RHS
    STD_BIKE_FALLOFF                  = 125                # ANIM_STD_BIKE_FALLOFF
    STD_BIKE_FALLBACK                 = 126                # ANIM_STD_BIKE_FALLBACK
    STD_GETOUT_RHS                    = 127                # ANIM_STD_GETOUT_RHS
    STD_GETOUT_LO_RHS                 = 128                # ANIM_STD_GETOUT_LO_RHS
    STD_CAR_CLOSE_RHS                 = 129                # ANIM_STD_CAR_CLOSE_RHS
    STD_CAR_HOOKERTALK                = 130                # ANIM_STD_CAR_HOOKERTALK
    STD_TRAIN_GETIN                   = 131                # ANIM_STD_TRAIN_GETIN
    STD_TRAIN_GETOUT                  = 132                # ANIM_STD_TRAIN_GETOUT
    STD_CRAWLOUT_LHS                  = 133                # ANIM_STD_CRAWLOUT_LHS
    STD_CRAWLOUT_RHS                  = 134                # ANIM_STD_CRAWLOUT_RHS
    STD_ROLLOUT_LHS                   = 135                # ANIM_STD_ROLLOUT_LHS
    STD_ROLLOUT_RHS                   = 136                # ANIM_STD_ROLLOUT_RHS
    STD_GET_UP                        = 137                # ANIM_STD_GET_UP
    STD_GET_UP_LEFT                   = 138                # ANIM_STD_GET_UP_LEFT
    STD_GET_UP_RIGHT                  = 139                # ANIM_STD_GET_UP_RIGHT
    STD_GET_UP_FRONT                  = 140                # ANIM_STD_GET_UP_FRONT
    STD_JUMP_LAUNCH                   = 141                # ANIM_STD_JUMP_LAUNCH
    STD_JUMP_GLIDE                    = 142                # ANIM_STD_JUMP_GLIDE
    STD_JUMP_LAND                     = 143                # ANIM_STD_JUMP_LAND
    STD_FALL                          = 144                # ANIM_STD_FALL
    STD_FALL_GLIDE                    = 145                # ANIM_STD_FALL_GLIDE
    STD_FALL_LAND                     = 146                # ANIM_STD_FALL_LAND
    STD_FALL_COLLAPSE                 = 147                # ANIM_STD_FALL_COLLAPSE
    STD_FALL_ONBACK                   = 148                # ANIM_STD_FALL_ONBACK
    STD_FALL_ONFRONT                  = 149                # ANIM_STD_FALL_ONFRONT
    STD_EVADE_STEP                    = 150                # ANIM_STD_EVADE_STEP
    STD_EVADE_DIVE                    = 151                # ANIM_STD_EVADE_DIVE
    STD_XPRESS_SCRATCH                = 152                # ANIM_STD_XPRESS_SCRATCH
    STD_ROADCROSS                     = 153                # ANIM_STD_ROADCROSS
    STD_TURN180                       = 154                # ANIM_STD_TURN180
    STD_ARREST                        = 155                # ANIM_STD_ARREST
    STD_DROWN                         = 156                # ANIM_STD_DROWN
    STD_DUCK_DOWN                     = 157                # ANIM_STD_DUCK_DOWN
    STD_DUCK_LOW                      = 158                # ANIM_STD_DUCK_LOW
    STD_DUCK_WEAPON                   = 159                # ANIM_STD_DUCK_WEAPON
    STD_RBLOCK_SHOOT                  = 160                # ANIM_STD_RBLOCK_SHOOT
    STD_HANDSUP                       = 161                # ANIM_STD_HANDSUP
    STD_HANDSCOWER                    = 162                # ANIM_STD_HANDSCOWER
    STD_PARTIAL_FUCKU                 = 163                # ANIM_STD_PARTIAL_FUCKU
    STD_PHONE_IN                      = 164                # ANIM_STD_PHONE_IN
    STD_PHONE_OUT                     = 165                # ANIM_STD_PHONE_OUT
    STD_PHONE_TALK                    = 166                # ANIM_STD_PHONE_TALK
    STD_SEAT_DOWN                     = 167                # ANIM_STD_SEAT_DOWN
    STD_SEAT_UP                       = 168                # ANIM_STD_SEAT_UP
    STD_SEAT_IDLE                     = 169                # ANIM_STD_SEAT_IDLE
    STD_SEAT_RVRS                     = 170                # ANIM_STD_SEAT_RVRS
    STD_ATM                           = 171                # ANIM_STD_ATM
    STD_ABSEIL                        = 172                # ANIM_STD_ABSEIL
    STD_NUM                           = 173                # ANIM_STD_NUM
    STD_VAN_OPEN_DOOR_REAR_LHS        = 174                # ANIM_STD_VAN_OPEN_DOOR_REAR_LHS
    STD_VAN_GET_IN_REAR_LHS           = 175                # ANIM_STD_VAN_GET_IN_REAR_LHS
    STD_VAN_CLOSE_DOOR_REAR_LHS       = 176                # ANIM_STD_VAN_CLOSE_DOOR_REAR_LHS
    STD_VAN_GET_OUT_REAR_LHS          = 177                # ANIM_STD_VAN_GET_OUT_REAR_LHS
    STD_VAN_OPEN_DOOR_REAR_RHS        = 178                # ANIM_STD_VAN_OPEN_DOOR_REAR_RHS
    STD_VAN_GET_IN_REAR_RHS           = 179                # ANIM_STD_VAN_GET_IN_REAR_RHS
    STD_VAN_CLOSE_DOOR_REAR_RHS       = 180                # ANIM_STD_VAN_CLOSE_DOOR_REAR_RHS
    STD_VAN_GET_OUT_REAR_RHS          = 181                # ANIM_STD_VAN_GET_OUT_REAR_RHS
    STD_COACH_OPEN_LHS                = 182                # ANIM_STD_COACH_OPEN_LHS
    STD_COACH_OPEN_RHS                = 183                # ANIM_STD_COACH_OPEN_RHS
    STD_COACH_GET_IN_LHS              = 184                # ANIM_STD_COACH_GET_IN_LHS
    STD_COACH_GET_IN_RHS              = 185                # ANIM_STD_COACH_GET_IN_RHS
    STD_COACH_GET_OUT_LHS             = 186                # ANIM_STD_COACH_GET_OUT_LHS
    BIKE_RIDE                         = 187                # ANIM_BIKE_RIDE
    BIKE_READY                        = 188                # ANIM_BIKE_READY
    BIKE_LEFT                         = 189                # ANIM_BIKE_LEFT
    BIKE_RIGHT                        = 190                # ANIM_BIKE_RIGHT
    BIKE_LEANB                        = 191                # ANIM_BIKE_LEANB
    BIKE_LEANF                        = 192                # ANIM_BIKE_LEANF
    BIKE_WALKBACK                     = 193                # ANIM_BIKE_WALKBACK
    BIKE_JUMPON_LHS                   = 194                # ANIM_BIKE_JUMPON_LHS
    BIKE_JUMPON_RHS                   = 195                # ANIM_BIKE_JUMPON_RHS
    BIKE_KICK                         = 196                # ANIM_BIKE_KICK
    BIKE_HIT                          = 197                # ANIM_BIKE_HIT
    BIKE_GETOFF_LHS                   = 198                # ANIM_BIKE_GETOFF_LHS
    BIKE_GETOFF_RHS                   = 199                # ANIM_BIKE_GETOFF_RHS
    BIKE_GETOFF_BACK                  = 200                # ANIM_BIKE_GETOFF_BACK
    BIKE_DRIVEBY_LHS                  = 201                # ANIM_BIKE_DRIVEBY_LHS
    BIKE_DRIVEBY_RHS                  = 202                # ANIM_BIKE_DRIVEBY_RHS
    BIKE_DRIVEBY_FORWARD              = 203                # ANIM_BIKE_DRIVEBY_FORWARD
    BIKE_RIDE_P                       = 204                # ANIM_BIKE_RIDE_P
    ATTACK_1                          = 205                # ANIM_ATTACK_1
    ATTACK_2                          = 206                # ANIM_ATTACK_2
    ATTACK_EXTRA1                     = 207                # ANIM_ATTACK_EXTRA1
    ATTACK_EXTRA2                     = 208                # ANIM_ATTACK_EXTRA2
    ATTACK_3                          = 209                # ANIM_ATTACK_3
    WEAPON_FIRE                       = ATTACK_1           # ANIM_WEAPON_FIRE
    WEAPON_CROUCHFIRE                 = 206                # ANIM_WEAPON_CROUCHFIRE
    WEAPON_FIRE_2ND                   = WEAPON_CROUCHFIRE  # ANIM_WEAPON_FIRE_2ND
    WEAPON_RELOAD                     = 207                # ANIM_WEAPON_RELOAD
    WEAPON_CROUCHRELOAD               = 208                # ANIM_WEAPON_CROUCHRELOAD
    WEAPON_FIRE_3RD                   = 209                # ANIM_WEAPON_FIRE_3RD
    THROWABLE_THROW                   = ATTACK_1           # ANIM_THROWABLE_THROW
    THROWABLE_THROWU                  = 206                # ANIM_THROWABLE_THROWU
    THROWABLE_START_THROW             = 207                # ANIM_THROWABLE_START_THROW
    MELEE_ATTACK                      = ATTACK_1           # ANIM_MELEE_ATTACK
    MELEE_ATTACK_2ND                  = 206                # ANIM_MELEE_ATTACK_2ND
    MELEE_ATTACK_START                = 207                # ANIM_MELEE_ATTACK_START
    MELEE_IDLE_FIGHTMODE              = 208                # ANIM_MELEE_IDLE_FIGHTMODE
    MELEE_ATTACK_FINISH               = 209                # ANIM_MELEE_ATTACK_FINISH
    SUNBATHE_IDLE                     = 210                # ANIM_SUNBATHE_IDLE
    SUNBATHE_DOWN                     = 211                # ANIM_SUNBATHE_DOWN
    SUNBATHE_UP                       = 212                # ANIM_SUNBATHE_UP
    SUNBATHE_ESCAPE                   = 213                # ANIM_SUNBATHE_ESCAPE
    MEDIC_CPR                         = 214                # ANIM_MEDIC_CPR
    PLAYER_IDLE1                      = 215                # ANIM_PLAYER_IDLE1
    PLAYER_IDLE2                      = 216                # ANIM_PLAYER_IDLE2
    PLAYER_IDLE3                      = 217                # ANIM_PLAYER_IDLE3
    PLAYER_IDLE4                      = 218                # ANIM_PLAYER_IDLE4
    RIOT_ANGRY                        = 219                # ANIM_RIOT_ANGRY
    RIOT_ANGRY_B                      = 220                # ANIM_RIOT_ANGRY_B
    RIOT_CHANT                        = 221                # ANIM_RIOT_CHANT
    RIOT_PUNCHES                      = 222                # ANIM_RIOT_PUNCHES
    RIOT_SHOUT                        = 223                # ANIM_RIOT_SHOUT
    RIOT_CHALLENGE                    = 224                # ANIM_RIOT_CHALLENGE
    RIOT_FUCKYOU                      = 225                # ANIM_RIOT_FUCKYOU
    STRIP_A                           = 226                # ANIM_STRIP_A
    STRIP_B                           = 227                # ANIM_STRIP_B
    STRIP_C                           = 228                # ANIM_STRIP_C
    STRIP_D                           = 229                # ANIM_STRIP_D
    STRIP_E                           = 230                # ANIM_STRIP_E
    STRIP_F                           = 231                # ANIM_STRIP_F
    STRIP_G                           = 232                # ANIM_STRIP_G


class AnimAssocFlag (Enum):
    RUNNING           = 1       # ASSOC_RUNNING
    REPEAT            = 2       # ASSOC_REPEAT
    DELETEFADEDOUT    = 4       # ASSOC_DELETEFADEDOUT
    FADEOUTWHENDONE   = 8       # ASSOC_FADEOUTWHENDONE
    PARTIAL           = 0x10    # ASSOC_PARTIAL
    MOVEMENT          = 0x20    # ASSOC_MOVEMENT
    HAS_TRANSLATION   = 0x40    # ASSOC_HAS_TRANSLATION
    HAS_X_TRANSLATION = 0x80    # ASSOC_HAS_X_TRANSLATION -- for 2d velocity extraction
    WALK              = 0x100   # ASSOC_WALK              -- for CPed::PlayFootSteps(void)
    IDLE              = 0x200   # ASSOC_IDLE              -- only xpress scratch has it by default, but game adds it to player's idle animations later
    NOWALK            = 0x400   # ASSOC_NOWALK            -- see CPed::PlayFootSteps(void)
    BLOCK             = 0x800   # ASSOC_BLOCK             -- unused in assoc description, blocks other anims from being played
    FRONTAL           = 0x1000  # ASSOC_FRONTAL           -- anims that we fall to front
    DRIVING           = 0x2000  # ASSOC_DRIVING


class AnimAssocDesc:
    def __init__ (self, animId : int, flags : int):
        self.animId : int = animId
        self.flags  : int = flags


class AnimAssocDefinition:
    def __init__ (
        self,
        name      : str,
        blockName : str,
        modelId   : int,
        animCount : int,
        animNames : List[str],
        animDescs : List[AnimAssocDesc]
    ):
        self.name      : str                 = name       # char const *name
        self.blockName : str                 = blockName  # char const *blockName
        self.modelId   : int                 = modelId    # int32 modelIndex
        self.animCount : int                 = animCount  # int32 numAnims
        self.animNames : List[str]           = animNames  # char const **animNames
        self.animDescs : List[AnimAssocDesc] = animDescs  # AnimAssocDesc *animDescs


ANIM_DESCS : Dict[str, List[AnimAssocDesc]] = {
    'stdAnimDescs': [
        AnimAssocDesc(AnimationId.STD_WALK, AnimAssocFlag.REPEAT | AnimAssocFlag.MOVEMENT | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.WALK),
        AnimAssocDesc(AnimationId.STD_RUN, AnimAssocFlag.REPEAT | AnimAssocFlag.MOVEMENT | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.WALK),
        AnimAssocDesc(AnimationId.STD_RUNFAST, AnimAssocFlag.REPEAT | AnimAssocFlag.MOVEMENT | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.WALK),
        AnimAssocDesc(AnimationId.STD_IDLE, AnimAssocFlag.REPEAT),
        AnimAssocDesc(AnimationId.STD_STARTWALK, AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_RUNSTOP1, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_RUNSTOP2, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_IDLE_CAM, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_IDLE_HBHB, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_IDLE_TIRED, AnimAssocFlag.REPEAT),
        AnimAssocDesc(AnimationId.STD_IDLE_BIGGUN, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CHAT, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_HAILTAXI, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_KO_FRONT, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_KO_LEFT, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_KO_BACK, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_KO_RIGHT, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_KO_SHOT_FACE, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_KO_SHOT_STOMACH, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_KO_SHOT_ARM_L, AnimAssocFlag.PARTIAL | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_KO_SHOT_ARM_R, AnimAssocFlag.PARTIAL | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_KO_SHOT_LEG_L, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_KO_SHOT_LEG_R, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_SPINFORWARD_LEFT, AnimAssocFlag.PARTIAL | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_SPINFORWARD_RIGHT, AnimAssocFlag.PARTIAL | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_HIGHIMPACT_FRONT, AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_HIGHIMPACT_LEFT, AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_HIGHIMPACT_BACK, AnimAssocFlag.PARTIAL | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_HIGHIMPACT_RIGHT, AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_HITBYGUN_FRONT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.NOWALK),
        AnimAssocDesc(AnimationId.STD_HITBYGUN_LEFT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.NOWALK),
        AnimAssocDesc(AnimationId.STD_HITBYGUN_BACK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.NOWALK),
        AnimAssocDesc(AnimationId.STD_HITBYGUN_RIGHT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.NOWALK),
        AnimAssocDesc(AnimationId.STD_HIT_FRONT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_HIT_LEFT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_HIT_BACK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_HIT_RIGHT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_HIT_FLOOR, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_HIT_BODYBLOW, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_HIT_CHEST, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_HIT_HEAD, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_HIT_WALK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_HIT_WALL, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_HIT_FLOOR_FRONT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_HIT_BEHIND, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_IDLE, AnimAssocFlag.REPEAT),
        AnimAssocDesc(AnimationId.STD_FIGHT_2IDLE, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_SHUFFLE_F, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_FIGHT_BODYBLOW, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_HEAD, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_KICK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_KNEE, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_LHOOK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_PUNCH, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_ROUNDHOUSE, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_FIGHT_LONGKICK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_PARTIAL_PUNCH, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.NOWALK),
        AnimAssocDesc(AnimationId.STD_FIGHT_JAB, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_ELBOW_L, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_ELBOW_R, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_BKICK_L, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_BKICK_R, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_DETONATE, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_PUNCH, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_PARTIALPUNCH, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_KICKGROUND, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_THROW_UNDER, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FIGHT_SHUFFLE_B, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_JACKEDCAR_RHS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_JACKEDCAR_LO_RHS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_JACKEDCAR_LHS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_JACKEDCAR_LO_LHS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_QUICKJACK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_QUICKJACKED, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_ALIGN_DOOR_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_ALIGNHI_DOOR_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_OPEN_DOOR_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CARDOOR_LOCKED_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_PULL_OUT_PED_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_PULL_OUT_PED_LO_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_GET_IN_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_GET_IN_LO_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_CLOSE_DOOR_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_CLOSE_DOOR_LO_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_CLOSE_DOOR_ROLLING_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_CLOSE_DOOR_ROLLING_LO_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_JUMP_IN_LO_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_GETOUT_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_GETOUT_LO_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_CLOSE_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_ALIGN_DOOR_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_ALIGNHI_DOOR_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_OPEN_DOOR_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CARDOOR_LOCKED_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_PULL_OUT_PED_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_PULL_OUT_PED_LO_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_GET_IN_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_GET_IN_LO_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_CLOSE_DOOR_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_CLOSE_DOOR_LO_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_SHUFFLE_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_SHUFFLE_LO_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_SIT, AnimAssocFlag.DELETEFADEDOUT),
        AnimAssocDesc(AnimationId.STD_CAR_SIT_LO, AnimAssocFlag.DELETEFADEDOUT),
        AnimAssocDesc(AnimationId.STD_CAR_SIT_P, AnimAssocFlag.DELETEFADEDOUT),
        AnimAssocDesc(AnimationId.STD_CAR_SIT_P_LO, AnimAssocFlag.DELETEFADEDOUT),
        AnimAssocDesc(AnimationId.STD_CAR_DRIVE_LEFT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_CAR_DRIVE_RIGHT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_CAR_DRIVE_LEFT_LO, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_CAR_DRIVE_RIGHT_LO, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_CAR_DRIVEBY_LEFT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_CAR_DRIVEBY_RIGHT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_CAR_DRIVEBY_LEFT_LO, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_CAR_DRIVEBY_RIGHT_LO, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_CAR_LOOKBEHIND, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_BOAT_DRIVE, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_BOAT_DRIVE_LEFT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_BOAT_DRIVE_RIGHT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_BOAT_LOOKBEHIND, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.STD_BIKE_PICKUP_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_BIKE_PICKUP_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_BIKE_PULLUP_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_BIKE_PULLUP_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_BIKE_ELBOW_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_BIKE_ELBOW_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_BIKE_FALLOFF, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_BIKE_FALLBACK, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_GETOUT_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_GETOUT_LO_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_CLOSE_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CAR_HOOKERTALK, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_TRAIN_GETIN, AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_TRAIN_GETOUT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CRAWLOUT_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_CRAWLOUT_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_ROLLOUT_LHS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_ROLLOUT_RHS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_GET_UP, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_GET_UP_LEFT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_GET_UP_RIGHT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_GET_UP_FRONT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_JUMP_LAUNCH, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_JUMP_GLIDE, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_JUMP_LAND, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_FALL, AnimAssocFlag.REPEAT | AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FALL_GLIDE, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FALL_LAND, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_FALL_COLLAPSE, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_FALL_ONBACK, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_FALL_ONFRONT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_EVADE_STEP, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_EVADE_DIVE, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.FRONTAL),
        AnimAssocDesc(AnimationId.STD_XPRESS_SCRATCH, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.IDLE),
        AnimAssocDesc(AnimationId.STD_ROADCROSS, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_TURN180, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_ARREST, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_DROWN, AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_DUCK_DOWN, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_DUCK_LOW, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_DUCK_WEAPON, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_RBLOCK_SHOOT, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_HANDSUP, AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_HANDSCOWER, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.STD_PARTIAL_FUCKU, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.NOWALK),
        AnimAssocDesc(AnimationId.STD_PHONE_IN, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_PHONE_OUT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_PHONE_TALK, AnimAssocFlag.REPEAT | AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_SEAT_DOWN, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_SEAT_UP, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_SEAT_IDLE, AnimAssocFlag.REPEAT | AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_SEAT_RVRS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_ATM, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_ABSEIL, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL),
    ],
    'vanAnimDescs': [
        AnimAssocDesc(AnimationId.STD_VAN_OPEN_DOOR_REAR_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_VAN_GET_IN_REAR_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_VAN_CLOSE_DOOR_REAR_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_VAN_GET_OUT_REAR_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_VAN_OPEN_DOOR_REAR_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_VAN_GET_IN_REAR_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_VAN_CLOSE_DOOR_REAR_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_VAN_GET_OUT_REAR_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
    ],
    'coachAnimDescs': [
        AnimAssocDesc(AnimationId.STD_COACH_OPEN_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_COACH_OPEN_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_COACH_GET_IN_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_COACH_GET_IN_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STD_COACH_GET_OUT_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
    ],
    'bikeAnimDescs': [
        AnimAssocDesc(AnimationId.BIKE_RIDE, AnimAssocFlag.DELETEFADEDOUT),
        AnimAssocDesc(AnimationId.BIKE_READY, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_LEFT, AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_RIGHT, AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_LEANB, AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_LEANF, AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_WALKBACK, AnimAssocFlag.REPEAT | AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_JUMPON_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.BIKE_JUMPON_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.BIKE_KICK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.BIKE_HIT, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.BIKE_GETOFF_LHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.BIKE_GETOFF_RHS, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.BIKE_GETOFF_BACK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
        AnimAssocDesc(AnimationId.BIKE_DRIVEBY_LHS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_DRIVEBY_RHS, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_DRIVEBY_FORWARD, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.PARTIAL | AnimAssocFlag.DRIVING),
        AnimAssocDesc(AnimationId.BIKE_RIDE_P, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.DRIVING),
    ],
    'meleeAnimDescs': [
        AnimAssocDesc(AnimationId.MELEE_ATTACK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.MELEE_ATTACK_2ND, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.MELEE_ATTACK_START, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.NOWALK),
        AnimAssocDesc(AnimationId.MELEE_IDLE_FIGHTMODE, AnimAssocFlag.REPEAT),
        AnimAssocDesc(AnimationId.MELEE_ATTACK_FINISH, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION),
    ],
    'swingAnimDescs': [
        AnimAssocDesc(AnimationId.MELEE_ATTACK, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.MELEE_ATTACK_2ND, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.MELEE_ATTACK_START, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.MELEE_IDLE_FIGHTMODE, AnimAssocFlag.REPEAT),
        AnimAssocDesc(AnimationId.MELEE_ATTACK_FINISH, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
    ],
    'weaponAnimDescs': [
        AnimAssocDesc(AnimationId.WEAPON_FIRE, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.WEAPON_CROUCHFIRE, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.WEAPON_RELOAD, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.WEAPON_CROUCHRELOAD, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.WEAPON_FIRE_3RD, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
    ],
    'medicAnimDescs': [
        AnimAssocDesc(AnimationId.MEDIC_CPR, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
    ],
    'sunbatheAnimDescs': [
        AnimAssocDesc(AnimationId.SUNBATHE_IDLE, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.SUNBATHE_DOWN, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION),
        AnimAssocDesc(AnimationId.SUNBATHE_UP, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION),
        AnimAssocDesc(AnimationId.SUNBATHE_ESCAPE, AnimAssocFlag.REPEAT | AnimAssocFlag.PARTIAL | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION),
    ],
    'playerIdleAnimDescs': [
        AnimAssocDesc(AnimationId.PLAYER_IDLE1, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.PLAYER_IDLE2, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.PLAYER_IDLE3, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.PLAYER_IDLE4, AnimAssocFlag.DELETEFADEDOUT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
    ],
    'riotAnimDescs': [
        AnimAssocDesc(AnimationId.RIOT_ANGRY, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.RIOT_ANGRY_B, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.RIOT_CHANT, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.RIOT_PUNCHES, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.RIOT_SHOUT, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.RIOT_CHALLENGE, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.RIOT_FUCKYOU, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
    ],
    'stripAnimDescs': [
        AnimAssocDesc(AnimationId.STRIP_A, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STRIP_B, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STRIP_C, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STRIP_D, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STRIP_E, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STRIP_F, AnimAssocFlag.REPEAT | AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
        AnimAssocDesc(AnimationId.STRIP_G, AnimAssocFlag.FADEOUTWHENDONE | AnimAssocFlag.PARTIAL),
    ],
    'stdAnimDescsSide': [
        AnimAssocDesc(AnimationId.STD_WALK, AnimAssocFlag.REPEAT | AnimAssocFlag.MOVEMENT | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION | AnimAssocFlag.WALK),
        AnimAssocDesc(AnimationId.STD_RUN, AnimAssocFlag.REPEAT | AnimAssocFlag.MOVEMENT | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION | AnimAssocFlag.WALK),
        AnimAssocDesc(AnimationId.STD_RUNFAST, AnimAssocFlag.REPEAT | AnimAssocFlag.MOVEMENT | AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION | AnimAssocFlag.WALK),
        AnimAssocDesc(AnimationId.STD_IDLE, AnimAssocFlag.REPEAT),
        AnimAssocDesc(AnimationId.STD_STARTWALK, AnimAssocFlag.HAS_TRANSLATION | AnimAssocFlag.HAS_X_TRANSLATION),
    ],
}


ANIM_LISTS : Dict[str, List[str]] = {
    'stdAnimations': [
        'walk_civi',
        'run_civi',
        'sprint_panic',
        'idle_stance',
        'walk_start',
        'run_stop',
        'run_stopr',
        'idle_hbhb',
        'idle_hbhb',
        'idle_tired',
        'idle_armed',
        'idle_chat',
        'idle_taxi',
        'ko_shot_front',
        'ko_shot_front',
        'ko_shot_front',
        'ko_shot_front',
        'ko_shot_face',
        'ko_shot_stom',
        'ko_shot_arml',
        'ko_shot_armr',
        'ko_shot_legl',
        'ko_shot_legr',
        'kd_left',
        'kd_right',
        'ko_skid_front',
        'ko_spin_r',
        'ko_skid_back',
        'ko_spin_l',
        'shot_partial',
        'shot_leftp',
        'shot_partial',
        'shot_rightp',
        'hit_front',
        'hit_l',
        'hit_back',
        'hit_r',
        'floor_hit',
        'hit_bodyblow',
        'hit_chest',
        'hit_head',
        'hit_walk',
        'hit_wall',
        'floor_hit_f',
        'hit_behind',
        'fightidle',
        'fight2idle',
        'fightsh_f',
        'fightbodyblow',
        'fighthead',
        'fightkick',
        'fightknee',
        'fightlhook',
        'fightpunch',
        'fightrndhse',
        'fightlngkck',
        'fightppunch',
        'fightjab',
        'fightelbowl',
        'fightelbowr',
        'fightbkickl',
        'fightbkickr',
        'bomber',
        'punchr',
        'fightppunch',
        'kick_floor',
        'weapon_throwu',
        'fightsh_back',
        'car_jackedrhs',
        'car_ljackedrhs',
        'car_jackedlhs',
        'car_ljackedlhs',
        'car_qjack',
        'car_qjacked',
        'car_align_lhs',
        'car_alignhi_lhs',
        'car_open_lhs',
        'car_doorlocked_lhs',
        'car_pullout_lhs',
        'car_pulloutl_lhs',
        'car_getin_lhs',
        'car_getinl_lhs',
        'car_closedoor_lhs',
        'car_closedoorl_lhs',
        'car_rolldoor',
        'car_rolldoorlo',
        'car_jumpin_lhs',
        'car_getout_lhs',
        'car_getoutl_lhs',
        'car_close_lhs',
        'car_align_rhs',
        'car_alignhi_rhs',
        'car_open_rhs',
        'car_doorlocked_rhs',
        'car_pullout_rhs',
        'car_pulloutl_rhs',
        'car_getin_rhs',
        'car_getinl_rhs',
        'car_closedoor_rhs',
        'car_closedoorl_rhs',
        'car_shuffle_rhs',
        'car_lshuffle_rhs',
        'car_sit',
        'car_lsit',
        'car_sitp',
        'car_sitplo',
        'drive_l',
        'drive_r',
        'drive_lo_l',
        'drive_lo_r',
        'driveby_l',
        'driveby_r',
        'drivebyl_l',
        'drivebyl_r',
        'car_lb',
        'drive_boat',
        'drive_boat_l',
        'drive_boat_r',
        'drive_boat_back',
        'bike_pickupr',
        'bike_pickupl',
        'bike_pullupr',
        'bike_pullupl',
        'bike_elbowr',
        'bike_elbowl',
        'bike_fall_off',
        'bike_fallr',
        'car_getout_rhs',
        'car_getoutl_rhs',
        'car_close_rhs',
        'car_hookertalk',
        'idle_stance',
        'idle_stance',
        'car_crawloutrhs',
        'car_crawloutrhs',
        'car_rollout_lhs',
        'car_rollout_lhs',
        'getup',
        'getup',
        'getup',
        'getup_front',
        'jump_launch',
        'jump_glide',
        'jump_land',
        'fall_fall',
        'fall_glide',
        'fall_land',
        'fall_collapse',
        'fall_back',
        'fall_front',
        'ev_step',
        'ev_dive',
        'xpressscratch',
        'roadcross',
        'turn_180',
        'arrestgun',
        'drown',
        'duck_down',
        'duck_low',
        'weapon_crouch',
        'rblock_cshoot',
        'handsup',
        'handscower',
        'fucku',
        'phone_in',
        'phone_out',
        'phone_talk',
        'seat_down',
        'seat_up',
        'seat_idle',
        'seat_down',
        'atm',
        'abseil',
    ],
    'vanAnimations': [
        'van_openl',
        'van_getinl',
        'van_closel',
        'van_getoutl',
        'van_open',
        'van_getin',
        'van_close',
        'van_getout',
    ],
    'coachAnimations': [
        'coach_opnl',
        'coach_opnl',
        'coach_inl',
        'coach_inl',
        'coach_outl',
    ],
    'bikesAnimations': [
        'bikes_ride',
        'bikes_still',
        'bikes_left',
        'bikes_right',
        'bikes_back',
        'bikes_fwd',
        'bikes_pushes',
        'bikes_jumponr',
        'bikes_jumponl',
        'bikes_kick',
        'bikes_hit',
        'bikes_getoffrhs',
        'bikes_getofflhs',
        'bikes_getoffback',
        'bikes_drivebylhs',
        'bikes_drivebyrhs',
        'bikes_drivebyft',
        'bikes_passenger',
    ],
    'bikevAnimations': [
        'bikev_ride',
        'bikev_still',
        'bikev_left',
        'bikev_right',
        'bikev_back',
        'bikev_fwd',
        'bikev_pushes',
        'bikev_jumponr',
        'bikev_jumponl',
        'bikev_kick',
        'bikev_hit',
        'bikev_getoffrhs',
        'bikev_getofflhs',
        'bikev_getoffback',
        'bikev_drivebylhs',
        'bikev_drivebyrhs',
        'bikev_drivebyft',
        'bikev_passenger',
    ],
    'bikehAnimations': [
        'bikeh_ride',
        'bikeh_still',
        'bikeh_left',
        'bikeh_right',
        'bikeh_back',
        'bikeh_fwd',
        'bikeh_pushes',
        'bikeh_jumponr',
        'bikeh_jumponl',
        'bikeh_kick',
        'bikeh_hit',
        'bikeh_getoffrhs',
        'bikeh_getofflhs',
        'bikeh_getoffback',
        'bikeh_drivebylhs',
        'bikeh_drivebyrhs',
        'bikeh_drivebyft',
        'bikeh_passenger',
    ],
    'bikedAnimations': [
        'biked_ride',
        'biked_still',
        'biked_left',
        'biked_right',
        'biked_back',
        'biked_fwd',
        'biked_pushes',
        'biked_jumponr',
        'biked_jumponl',
        'biked_kick',
        'biked_hit',
        'biked_getoffrhs',
        'biked_getofflhs',
        'biked_getoffback',
        'biked_drivebylhs',
        'biked_drivebyrhs',
        'biked_drivebyft',
        'biked_passenger',
    ],
    'unarmedAnimations': [
        'punchr',
        'kick_floor',
        'fightppunch',
    ],
    'screwdriverAnimations': [
        'fightbodyblow',
        'fightbodyblow',
        'fightppunch',
        'fightidle',
        'fightbodyblow',
    ],
    'knifeAnimations': [
        'weapon_knife_1',
        'weapon_knife_2',
        'knife_part',
        'weapon_knifeidle',
        'weapon_knife_3',
    ],
    'baseballbatAnimations': [
        'weapon_bat_h',
        'weapon_bat_v',
        'bat_part',
        'weapon_bat_h',
        'weapon_golfclub',
    ],
    'golfclubAnimations': [
        'weapon_bat_h',
        'weapon_golfclub',
        'bat_part',
        'weapon_bat_h',
        'weapon_bat_v',
    ],
    'chainsawAnimations': [
        'weapon_csaw',
        'weapon_csawlo',
        'csaw_part',
    ],
    'pythonAnimations': [
        'python_fire',
        'python_crouchfire',
        'python_reload',
        'python_crouchreload',
    ],
    'coltAnimations': [
        'colt45_fire',
        'colt45_crouchfire',
        'colt45_reload',
        'colt45_crouchreload',
        'colt45_cop',
    ],
    'shotgunAnimations': [
        'shotgun_fire',
        'shotgun_crouchfire',
    ],
    'buddyAnimations': [
        'buddy_fire',
        'buddy_crouchfire',
    ],
    'tecAnimations': [
        'tec_fire',
        'tec_crouchfire',
        'tec_reload',
        'tec_crouchreload',
    ],
    'uziAnimations': [
        'uzi_fire',
        'uzi_crouchfire',
        'uzi_reload',
        'uzi_crouchreload',
    ],
    'rifleAnimations': [
        'rifle_fire',
        'rifle_crouchfire',
        'rifle_load',
        'rifle_crouchload',
    ],
    'm60Animations': [
        'm60_fire',
        'm60_fire',
        'm60_reload',
    ],
    'sniperAnimations': [
        'weapon_sniper',
    ],
    'throwAnimations': [
        'weapon_throw',
        'weapon_throwu',
        'weapon_start_throw',
    ],
    'flamethrowerAnimations': [
        'flame_fire',
    ],
    'medicAnimations': [
        'cpr',
    ],
    'sunbatheAnimations': [
        'bather',
        'batherdown',
        'batherup',
        'batherscape',
    ],
    'playerIdleAnimations': [
        'stretch',
        'time',
        'shldr',
        'strleg',
    ],
    'riotAnimations': [
        'riot_angry',
        'riot_angry_b',
        'riot_chant',
        'riot_punches',
        'riot_shout',
        'riot_challenge',
        'riot_fuku',
    ],
    'stripAnimations': [
        'strip_a',
        'strip_b',
        'strip_c',
        'strip_d',
        'strip_e',
        'strip_f',
        'strip_g',
    ],
    'lanceAnimations': [
        'lance',
    ],
    'playerAnimations': [
        'walk_player',
        'run_player',
        'sprint_civi',
        'idle_stance',
        'walk_start',
    ],
    'playerWithRocketAnimations': [
        'walk_rocket',
        'run_rocket',
        'run_rocket',
        'idle_rocket',
        'walk_start_rocket',
    ],
    'player1ArmedAnimations': [
        'walk_player',
        'run_1armed',
        'sprint_civi',
        'idle_stance',
        'walk_start',
    ],
    'player2ArmedAnimations': [
        'walk_armed',
        'run_armed',
        'run_armed',
        'idle_armed',
        'walk_start_armed',
    ],
    'playerBBBatAnimations': [
        'walk_player',
        'run_player',
        'run_player',
        'idle_stance',
        'walk_start',
    ],
    'playerChainsawAnimations': [
        'walk_csaw',
        'run_csaw',
        'run_csaw',
        'idle_csaw',
        'walk_start_csaw',
    ],
    'shuffleAnimations': [
        'walk_shuffle',
        'run_civi',
        'sprint_civi',
        'idle_stance',
    ],
    'oldAnimations': [
        'walk_old',
        'run_civi',
        'sprint_civi',
        'idle_stance',
    ],
    'gang1Animations': [
        'walk_gang1',
        'run_gang1',
        'sprint_civi',
        'idle_stance',
    ],
    'gang2Animations': [
        'walk_gang2',
        'run_gang1',
        'sprint_civi',
        'idle_stance',
    ],
    'fatAnimations': [
        'walk_fat',
        'run_civi',
        'woman_runpanic',
        'idle_stance',
    ],
    'oldFatAnimations': [
        'walk_fatold',
        'run_fatold',
        'woman_runpanic',
        'idle_stance',
    ],
    'joggerAnimations': [
        'jog_malea',
        'run_civi',
        'sprint_civi',
        'idle_stance',
    ],
    'stdWomanAnimations': [
        'woman_walknorm',
        'woman_run',
        'woman_runpanic',
        'woman_idlestance',
    ],
    'womanShopAnimations': [
        'woman_walkshop',
        'woman_run',
        'woman_run',
        'woman_idlestance',
    ],
    'busyWomanAnimations': [
        'woman_walkbusy',
        'woman_run',
        'woman_runpanic',
        'woman_idlestance',
    ],
    'sexyWomanAnimations': [
        'woman_walksexy',
        'woman_run',
        'woman_runpanic',
        'woman_idlestance',
    ],
    'fatWomanAnimations': [
        'walk_fat',
        'woman_run',
        'woman_runpanic',
        'woman_idlestance',
    ],
    'oldWomanAnimations': [
        'woman_walkold',
        'woman_run',
        'woman_runpanic',
        'woman_idlestance',
    ],
    'joggerWomanAnimations': [
        'jog_maleb',
        'woman_run',
        'woman_runpanic',
        'woman_idlestance',
    ],
    'panicChunkyAnimations': [
        'run_fatold',
        'woman_runpanic',
        'woman_runpanic',
        'idle_stance',
    ],
    'skateAnimations': [
        'skate_run',
        'skate_sprint',
        'skate_sprint',
        'skate_idle',
    ],
    'playerStrafeBackAnimations': [
        'walk_back',
        'run_back',
        'run_back',
        'idle_stance',
        'walk_start_back',
    ],
    'playerStrafeLeftAnimations': [
        'walk_left',
        'run_left',
        'run_left',
        'idle_stance',
        'walk_start_left',
    ],
    'playerStrafeRightAnimations': [
        'walk_right',
        'run_right',
        'run_right',
        'idle_stance',
        'walk_start_right',
    ],
    'rocketStrafeBackAnimations': [
        'walk_rocket_back',
        'run_rocket_back',
        'run_rocket_back',
        'idle_rocket',
        'walkst_rocket_back',
    ],
    'rocketStrafeLeftAnimations': [
        'walk_rocket_left',
        'run_rocket_left',
        'run_rocket_left',
        'idle_rocket',
        'walkst_rocket_left',
    ],
    'rocketStrafeRightAnimations': [
        'walk_rocket_right',
        'run_rocket_right',
        'run_rocket_right',
        'idle_rocket',
        'walkst_rocket_right',
    ],
    'chainsawStrafeBackAnimations': [
        'walk_csaw_back',
        'run_csaw_back',
        'run_csaw_back',
        'idle_csaw',
        'walkst_csaw_back',
    ],
    'chainsawStrafeLeftAnimations': [
        'walk_csaw_left',
        'run_csaw_left',
        'run_csaw_left',
        'idle_csaw',
        'walkst_csaw_left',
    ],
    'chainsawStrafeRightAnimations': [
        'walk_csaw_right',
        'run_csaw_right',
        'run_csaw_right',
        'idle_csaw',
        'walkst_csaw_right',
    ]
}


# CAnimManager::ms_aAnimAssocDefinitions
# index is a animGroupId
ANIM_ASSOC_DEFINITIONS : List[AnimAssocDefinition] = [
    AnimAssocDefinition(
        name      = 'man',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['stdAnimations']),
        animNames = ANIM_LISTS['stdAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'van',
        blockName = 'van',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['vanAnimations']),
        animNames = ANIM_LISTS['vanAnimations'],
        animDescs = ANIM_DESCS['vanAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'coach',
        blockName = 'coach',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['coachAnimations']),
        animNames = ANIM_LISTS['coachAnimations'],
        animDescs = ANIM_DESCS['coachAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'bikes',
        blockName = 'bikes',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['bikesAnimations']),
        animNames = ANIM_LISTS['bikesAnimations'],
        animDescs = ANIM_DESCS['bikeAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'bikev',
        blockName = 'bikev',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['bikevAnimations']),
        animNames = ANIM_LISTS['bikevAnimations'],
        animDescs = ANIM_DESCS['bikeAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'bikeh',
        blockName = 'bikeh',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['bikehAnimations']),
        animNames = ANIM_LISTS['bikehAnimations'],
        animDescs = ANIM_DESCS['bikeAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'biked',
        blockName = 'biked',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['bikedAnimations']),
        animNames = ANIM_LISTS['bikedAnimations'],
        animDescs = ANIM_DESCS['bikeAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'unarmed',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['unarmedAnimations']),
        animNames = ANIM_LISTS['unarmedAnimations'],
        animDescs = ANIM_DESCS['meleeAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'screwdrv',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['screwdriverAnimations']),
        animNames = ANIM_LISTS['screwdriverAnimations'],
        animDescs = ANIM_DESCS['meleeAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'knife',
        blockName = 'knife',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['knifeAnimations']),
        animNames = ANIM_LISTS['knifeAnimations'],
        animDescs = ANIM_DESCS['meleeAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'baseball',
        blockName = 'baseball',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['baseballbatAnimations']),
        animNames = ANIM_LISTS['baseballbatAnimations'],
        animDescs = ANIM_DESCS['swingAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'golfclub',
        blockName = 'baseball',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['golfclubAnimations']),
        animNames = ANIM_LISTS['golfclubAnimations'],
        animDescs = ANIM_DESCS['swingAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'chainsaw',
        blockName = 'chainsaw',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['chainsawAnimations']),
        animNames = ANIM_LISTS['chainsawAnimations'],
        animDescs = ANIM_DESCS['meleeAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'python',
        blockName = 'python',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['pythonAnimations']),
        animNames = ANIM_LISTS['pythonAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'colt45',
        blockName = 'colt45',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['coltAnimations']),
        animNames = ANIM_LISTS['coltAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'shotgun',
        blockName = 'shotgun',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['shotgunAnimations']),
        animNames = ANIM_LISTS['shotgunAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'buddy',
        blockName = 'buddy',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['buddyAnimations']),
        animNames = ANIM_LISTS['buddyAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'tec',
        blockName = 'tec',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['tecAnimations']),
        animNames = ANIM_LISTS['tecAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'uzi',
        blockName = 'uzi',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['uziAnimations']),
        animNames = ANIM_LISTS['uziAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'rifle',
        blockName = 'rifle',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['rifleAnimations']),
        animNames = ANIM_LISTS['rifleAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'm60',
        blockName = 'm60',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['m60Animations']),
        animNames = ANIM_LISTS['m60Animations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'sniper',
        blockName = 'sniper',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['sniperAnimations']),
        animNames = ANIM_LISTS['sniperAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'grenade',
        blockName = 'grenade',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['throwAnimations']),
        animNames = ANIM_LISTS['throwAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'flame',
        blockName = 'flame',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['flamethrowerAnimations']),
        animNames = ANIM_LISTS['flamethrowerAnimations'],
        animDescs = ANIM_DESCS['weaponAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'medic',
        blockName = 'medic',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['medicAnimations']),
        animNames = ANIM_LISTS['medicAnimations'],
        animDescs = ANIM_DESCS['medicAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'sunbathe',
        blockName = 'sunbathe',
        modelId   = ModelId.COP,
        animCount = 1,
        animNames = ANIM_LISTS['sunbatheAnimations'],
        animDescs = ANIM_DESCS['sunbatheAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'playidles',
        blockName = 'playidles',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['playerIdleAnimations']),
        animNames = ANIM_LISTS['playerIdleAnimations'],
        animDescs = ANIM_DESCS['playerIdleAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'riot',
        blockName = 'riot',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['riotAnimations']),
        animNames = ANIM_LISTS['riotAnimations'],
        animDescs = ANIM_DESCS['riotAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'strip',
        blockName = 'strip',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['stripAnimations']),
        animNames = ANIM_LISTS['stripAnimations'],
        animDescs = ANIM_DESCS['stripAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'lance',
        blockName = 'lance',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['lanceAnimations']),
        animNames = ANIM_LISTS['lanceAnimations'],
        animDescs = ANIM_DESCS['sunbatheAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'player',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['playerAnimations']),
        animNames = ANIM_LISTS['playerAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'playerrocket',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['playerWithRocketAnimations']),
        animNames = ANIM_LISTS['playerWithRocketAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'player1armed',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['player1ArmedAnimations']),
        animNames = ANIM_LISTS['player1ArmedAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'player2armed',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['player2ArmedAnimations']),
        animNames = ANIM_LISTS['player2ArmedAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'playerbbbat',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['playerBBBatAnimations']),
        animNames = ANIM_LISTS['playerBBBatAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'playercsaw',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['playerChainsawAnimations']),
        animNames = ANIM_LISTS['playerChainsawAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'shuffle',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['shuffleAnimations']),
        animNames = ANIM_LISTS['shuffleAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'oldman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['oldAnimations']),
        animNames = ANIM_LISTS['oldAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'gang1',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['gang1Animations']),
        animNames = ANIM_LISTS['gang1Animations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'gang2',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['gang2Animations']),
        animNames = ANIM_LISTS['gang2Animations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'fatman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['fatAnimations']),
        animNames = ANIM_LISTS['fatAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'oldfatman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['oldFatAnimations']),
        animNames = ANIM_LISTS['oldFatAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'jogger',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['joggerAnimations']),
        animNames = ANIM_LISTS['joggerAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'woman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['stdWomanAnimations']),
        animNames = ANIM_LISTS['stdWomanAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'shopping',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['womanShopAnimations']),
        animNames = ANIM_LISTS['womanShopAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'busywoman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['busyWomanAnimations']),
        animNames = ANIM_LISTS['busyWomanAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'sexywoman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['sexyWomanAnimations']),
        animNames = ANIM_LISTS['sexyWomanAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'fatwoman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['fatWomanAnimations']),
        animNames = ANIM_LISTS['fatWomanAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'oldwoman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['oldWomanAnimations']),
        animNames = ANIM_LISTS['oldWomanAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'jogwoman',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['joggerWomanAnimations']),
        animNames = ANIM_LISTS['joggerWomanAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'panicchunky',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['panicChunkyAnimations']),
        animNames = ANIM_LISTS['panicChunkyAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'skate',
        blockName = 'skate',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['skateAnimations']),
        animNames = ANIM_LISTS['skateAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'playerback',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['playerStrafeBackAnimations']),
        animNames = ANIM_LISTS['playerStrafeBackAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'playerleft',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['playerStrafeLeftAnimations']),
        animNames = ANIM_LISTS['playerStrafeLeftAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescsSide']
    ),
    AnimAssocDefinition(
        name      = 'playerright',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['playerStrafeRightAnimations']),
        animNames = ANIM_LISTS['playerStrafeRightAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescsSide']
    ),
    AnimAssocDefinition(
        name      = 'rocketback',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['rocketStrafeBackAnimations']),
        animNames = ANIM_LISTS['rocketStrafeBackAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'rocketleft',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['rocketStrafeLeftAnimations']),
        animNames = ANIM_LISTS['rocketStrafeLeftAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescsSide']
    ),
    AnimAssocDefinition(
        name      = 'rocketright',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['rocketStrafeRightAnimations']),
        animNames = ANIM_LISTS['rocketStrafeRightAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescsSide']
    ),
    AnimAssocDefinition(
        name      = 'csawback',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['chainsawStrafeBackAnimations']),
        animNames = ANIM_LISTS['chainsawStrafeBackAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescs']
    ),
    AnimAssocDefinition(
        name      = 'csawleft',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['chainsawStrafeLeftAnimations']),
        animNames = ANIM_LISTS['chainsawStrafeLeftAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescsSide']
    ),
    AnimAssocDefinition(
        name      = 'csawright',
        blockName = 'ped',
        modelId   = ModelId.COP,
        animCount = len(ANIM_LISTS['chainsawStrafeRightAnimations']),
        animNames = ANIM_LISTS['chainsawStrafeRightAnimations'],
        animDescs = ANIM_DESCS['stdAnimDescsSide']
    ),
]


ANIM_NAME_TO_ASSOC : Dict[str, int] = {
    'man':          0,
    'van':          1,
    'coach':        2,
    'bikes':        3,
    'bikev':        4,
    'bikeh':        5,
    'biked':        6,
    'unarmed':      7,
    'screwdrv':     8,
    'knife':        9,
    'baseball':     10,
    'golfclub':     11,
    'chainsaw':     12,
    'python':       13,
    'colt45':       14,
    'shotgun':      15,
    'buddy':        16,
    'tec':          17,
    'uzi':          18,
    'rifle':        19,
    'm60':          20,
    'sniper':       21,
    'grenade':      22,
    'flame':        23,
    'medic':        24,
    'sunbathe':     25,
    'playidles':    26,
    'riot':         27,
    'strip':        28,
    'lance':        29,
    'player':       30,
    'playerrocket': 31,
    'player1armed': 32,
    'player2armed': 33,
    'playerbbbat':  34,
    'playercsaw':   35,
    'shuffle':      36,
    'oldman':       37,
    'gang1':        38,
    'gang2':        39,
    'fatman':       40,
    'oldfatman':    41,
    'jogger':       42,
    'woman':        43,
    'shopping':     44,
    'busywoman':    45,
    'sexywoman':    46,
    'fatwoman':     47,
    'oldwoman':     48,
    'jogwoman':     49,
    'panicchunky':  50,
    'skate':        51,
    'playerback':   52,
    'playerleft':   53,
    'playerright':  54,
    'rocketback':   55,
    'rocketleft':   56,
    'rocketright':  57,
    'csawback':     58,
    'csawleft':     59,
    'csawright':    60,
}



__all__ = [
    'GRAVITY',
    'LOD_DISTANCE',
    'ModelId',
    'MODEL_NAME_TO_ID',
    'AnimAssocGroupId',
    'ANIM_ASSOC_GROUP_COUNT',
    'AnimationId',
    'AnimAssocFlag',
    'AnimAssocDesc',
    'AnimAssocDefinition',
    'ANIM_DESCS',
    'ANIM_LISTS',
    'ANIM_ASSOC_DEFINITIONS',
    'ANIM_NAME_TO_ASSOC',
]
