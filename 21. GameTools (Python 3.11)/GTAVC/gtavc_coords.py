import re
import sys
import math

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.reader import *
from bfw.types.enums import *

# https://gtamods.com/wiki/0AD9#Example

# https://gtamods.com/wiki/0167 - create marker
# https://gtamods.com/wiki/0164 - remove marker
# https://gtamods.com/wiki/0165 - color
# https://gtamods.com/wiki/0166 - brightness
# https://gtamods.com/wiki/0168 - size
# https://gtamods.com/wiki/018B - display

# https://gtamods.com/wiki/Saves_(GTA_VC) - save file structure
# https://gtamods.com/wiki/List_of_statistics_(VC)

# 0x821EEC - base address of stunt jumps
# 0x945D30-0x94A170 - base address of pickups https://gtamods.com/wiki/Saves_(GTA_VC)#Block_8:_Pickups (offset in GTAVCsf7_100.b: 75504) (total size = 52 * 336 = 17472)

# 0x9461DC



'''
showMarkers (pink animated arrow)
showOnMission
colors
radius
size : static | dynamic

# type: weapon | health | armor | adrenaline | bribe | rampage | package
# isPaid or price
# model
# name
# comment
# requirement
# areaName

# Health     - #FF87A7
# Armor      - #5EB1BF
# Adrenaline - #257F67
# Rampage    - #FF5900
# Weapon     - #8E8CAB 
# Bribe      - #2A6AD0
# Package    - #DABE09
# Stunt      -        
# Mission    -         - RC Top Fun | Pizza Boy | Off-road | Chopper Checkpoint

'''


PICKUP_TYPES = {
    1:  'PICKUP_IN_SHOP',
    2:  'PICKUP_ON_STREET',
    3:  'PICKUP_ONCE',
    4:  'PICKUP_ONCE_TIMEOUT',
    5:  'PICKUP_ONCE_TIMEOUT_SLOW',
    6:  'PICKUP_COLLECTABLE1',
    7:  'PICKUP_IN_SHOP_OUT_OF_STOCK',
    8:  'PICKUP_MONEY',
    9:  'PICKUP_MINE_INACTIVE',
    10: 'PICKUP_MINE_ARMED',
    11: 'PICKUP_NAUTICAL_MINE_INACTIVE',
    12: 'PICKUP_NAUTICAL_MINE_ARMED',
    13: 'PICKUP_FLOATINGPACKAGE',
    14: 'PICKUP_FLOATINGPACKAGE_FLOATING',
    15: 'PICKUP_ON_STREET_SLOW',
    16: 'PICKUP_ASSET_REVENUE',
    17: 'PICKUP_PROPERTY_LOCKED',
    18: 'PICKUP_PROPERTY_FORSALE',
}

PARSED_PICKUPS = [
    {
        "var": "$2035",
        "model": "#CHNSAW",
        "coords": "30.0 -1330.9 13.0",
        "type": "2 (PICKUP_ON_STREET)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1999",
        "model": "#BAT",
        "coords": "206.7 -1254.4 12.0",
        "type": "2 (PICKUP_ON_STREET)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2000",
        "model": "#COLT45",
        "coords": "-228.4 -1318.2 9.1",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2001",
        "model": "#COLT45",
        "coords": "340.5 -249.5 12.5",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2002",
        "model": "#CHROMEGUN",
        "coords": "42.3 -959.2 21.8",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2003",
        "model": "#CHROMEGUN",
        "coords": "568.9 -449.3 11.1",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2004",
        "model": "#TEC9",
        "coords": "287.9 50.7 10.8",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2005",
        "model": "#GRENADE",
        "coords": "362.2 -500.5 12.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2006",
        "model": "#CLEAVER",
        "coords": "402.6 102.5 11.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2007",
        "model": "#RUGER",
        "coords": "418.9 589.9 18.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2008",
        "model": "#KATANA",
        "coords": "476.9 1014.9 19.2",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2009",
        "model": "#NITESTICK",
        "coords": "402.4 -488.3 12.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2011",
        "model": "#BRASSKNUCKLE",
        "coords": "224.0 -1207.5 11.0",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2012",
        "model": "#KNIFECUR",
        "coords": "118.7 -1546.1 10.8",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2013",
        "model": "#MACHETE",
        "coords": "56.6 -459.3 11.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2014",
        "model": "#UZI",
        "coords": "5.4 -1277.0 10.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2036",
        "model": "#UZI",
        "coords": "157.0 -895.3 12.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2010",
        "model": "#BOMB",
        "coords": "556.6 207.4 14.5",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2015",
        "model": "#M4",
        "coords": "-32.8 1019.2 13.0",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2016",
        "model": "#UZI",
        "coords": "17.3 1145.7 23.5",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2017",
        "model": "#GOLFCLUB",
        "coords": "95.0 279.2 21.8",
        "type": "2 (PICKUP_ON_STREET)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2018",
        "model": "#FLAME",
        "coords": "-546.0 -418.9 9.8",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2019",
        "model": "#SNIPER",
        "coords": "-476.4 -571.2 12.9",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2020",
        "model": "#KATANA",
        "coords": "-554.11 -547.7 10.7",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2021",
        "model": "#MOLOTOV",
        "coords": "-755.7 1347.5 11.8",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2022",
        "model": "#UZI",
        "coords": "-545.8 694.6 11.0",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2023",
        "model": "#M4",
        "coords": "-980.4 118.7 9.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2024",
        "model": "#M4",
        "coords": "-1221.0 -641.6 11.7",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2025",
        "model": "#SNIPER",
        "coords": "-742.1 -949.9 9.9",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2026",
        "model": "#ROCKETLA",
        "coords": "-995.1 -1178.1 13.6",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2027",
        "model": "#INGRAMSL",
        "coords": "-713.3 -1466.0 11.2",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2028",
        "model": "#FLAME",
        "coords": "-1015.1 -1392.9 11.5",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2029",
        "model": "#SHOTGSPA",
        "coords": "-1359.0 -742.2 14.9",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2030",
        "model": "#M60",
        "coords": "-1744.9 -288.9 29.7",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2031",
        "model": "#GRENADE",
        "coords": "-939.8 -464.9 10.9",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2032",
        "model": "#PYTHON",
        "coords": "-1182.7 -61.1 11.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2033",
        "model": "#BUDDYSHOT",
        "coords": "-1305.2 177.1 11.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2034",
        "model": "#LASER",
        "coords": "-1114.3 -602.0 26.0",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1320",
        "model": "#PYTHON",
        "coords": "-306.7 -551.2 10.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1321",
        "model": "#FLAME",
        "coords": "-302.7 -551.2 10.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1322",
        "model": "#LASER",
        "coords": "-298.7 -551.2 10.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1323",
        "model": "#MINIGUN",
        "coords": "-294.7 -551.2 10.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1324",
        "model": "#ROCKETLA",
        "coords": "-290.7 -551.2 10.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1320",
        "model": "#PYTHON",
        "coords": "206.2 -1273.7 19.2",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1321",
        "model": "#FLAME",
        "coords": "224.2 -1273.1 19.2",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1322",
        "model": "#LASER",
        "coords": "228.2 -1279.2 19.2",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1323",
        "model": "#MINIGUN",
        "coords": "226.0 -1268.6 20.1",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1324",
        "model": "#ROCKETLA",
        "coords": "231.7 -1264.4 20.1",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1320",
        "model": "#PYTHON",
        "coords": "-821.1 1344.7 66.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1321",
        "model": "#FLAME",
        "coords": "-825.1 1344.7 66.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1322",
        "model": "#LASER",
        "coords": "-830.1 1344.7 66.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1323",
        "model": "#MINIGUN",
        "coords": "-833.1 1344.7 66.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1324",
        "model": "#ROCKETLA",
        "coords": "-839.0 1351.6 66.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2034",
        "model": "#LASER",
        "coords": "-1114.3 -602.0 26.0",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2223",
        "model": "#COLT45",
        "coords": "$2248 $2249 $2250",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$2224",
        "model": "#COLT45",
        "coords": "$2248 $2249 $2250",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$2289",
        "model": "#RUGER",
        "coords": "$2361 $2362 $2363",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$2462",
        "model": "#UZI",
        "coords": "455.9854 -531.2479 10.7576",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$2729",
        "model": "#RUGER",
        "coords": "190.5261 885.2347 13.7132",
        "type": "2 (PICKUP_ON_STREET)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4253",
        "model": "#BOMB",
        "coords": "-1058.6 325.9 11.2",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4539",
        "model": "#UZI",
        "coords": "-347.8 -527.2 12.7",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4978",
        "model": "#TEC9",
        "coords": "-336.6208 -572.994 11.6022",
        "type": "2 (PICKUP_ON_STREET)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4980",
        "model": "#TEC9",
        "coords": "-336.6208 -572.994 11.6022",
        "type": "2 (PICKUP_ON_STREET)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4978",
        "model": "#PYTHON",
        "coords": "-401.7512 -566.0168 19.5804",
        "type": "2 (PICKUP_ON_STREET)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4980",
        "model": "#PYTHON",
        "coords": "-374.4366 -587.5957 25.3355",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4980",
        "model": "#SHOTGSPA",
        "coords": "-374.4366 -587.5957 25.3355",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$5523",
        "model": "#LASER",
        "coords": "-1129.9 66.3 11.0",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$5671",
        "model": "#MINIGUN",
        "coords": "-1184.17 102.62 17.5",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$6386",
        "model": "#SNIPER",
        "coords": "$6387 $6388 $6389",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$6391",
        "model": "#UZI",
        "coords": "-43.07554 -1052.056 10.47165",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$6411",
        "model": "#SNIPER",
        "coords": "$6440 $6441 $6442",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$6543",
        "model": "#M4",
        "coords": "-973.5544 -518.9319 10.926",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$6544",
        "model": "#SHOTGSPA",
        "coords": "-898.9763 -549.0946 22.432",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1319",
        "model": "#CHNSAW",
        "coords": "-310.7 -551.2 10.3",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1319",
        "model": "#CHNSAW",
        "coords": "210.2 -1274.7 19.2",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1319",
        "model": "#CHNSAW",
        "coords": "-817.1 1344.7 66.4",
        "type": "15 (PICKUP_ON_STREET_SLOW)",
        "areCoordsLiterals": True
    },
    {
        "var": "$1307",
        "model": "#KNIFECUR",
        "coords": "468.5 -54.2 15.7",
        "type": "2 (PICKUP_ON_STREET)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4234",
        "model": "#PYTHON",
        "coords": "$4329 $4330 $4331",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$4235",
        "model": "#SHOTGSPA",
        "coords": "$4332 $4333 $4334",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$4236",
        "model": "#M60",
        "coords": "$4335 $4336 $4337",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$4237",
        "model": "#INGRAMSL",
        "coords": "$4338 $4339 $4340",
        "type": "3 (PICKUP_ONCE)",
        "areCoordsLiterals": False
    },
    {
        "var": "$4345",
        "model": "#M60",
        "coords": "-1105.9 335.3 11.1",
        "type": "1 (PICKUP_IN_SHOP)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4346",
        "model": "#ROCKETLA",
        "coords": "-1105.9 330.3 11.1",
        "type": "1 (PICKUP_IN_SHOP)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4347",
        "model": "#MINIGUN",
        "coords": "-1105.9 325.3 11.1",
        "type": "1 (PICKUP_IN_SHOP)",
        "areCoordsLiterals": True
    },
    {
        "var": "$4348",
        "model": "#BOMB",
        "coords": "-1105.9 320.3 11.1",
        "type": "1 (PICKUP_IN_SHOP)",
        "areCoordsLiterals": True
    }
]

MODEL_TO_NAME = {
    '#CHNSAW': 'Chainsaw',
    '#UZI': 'Uzi',
    '#BAT': 'Baseball Bat',
    '#MINIGUN': 'Minigun',
    '#PYTHON': 'Colt Python',
    '#LASER': '.308 Sniper',
    '#NITESTICK': 'Nightstick',
    '#M4': 'M4 Rifle',
    '#M60': 'M60',
    '#BUDDYSHOT': 'Stubby Shotgun',
    '#SHOTGSPA': 'Shotgun',
    '#CHROMEGUN': 'Shotgun',
    '#MOLOTOV': 'Molotov Cocktail',
    '#FLAME': 'Flamethrower',
    '#ROCKETLA': 'Rocket Launcher',
    '#SNIPER': 'Sniper Rifle',
    '#INGRAMSL': 'Mac - 10',
    '#KATANA': 'Katana',
    '#GRENADE': 'Grenade',
    '#MACHETE': 'Machete',
    '#COLT45': 'Pistol',
    '#TEC9': 'Tec-9',
    '#CLEAVER': 'Meat Cleaver',
    '#BOMB': 'Remote Grenade',
    '#KNIFECUR': 'Knife',
    '#BRASSKNUCKLE': 'Brass Knuckles',
    '#GOLFCLUB': 'Golf Club',
    '#RUGER': 'Kruger Rifle',
}

# http://gtamodding.ru/wiki/Номера_оружия
def parsePickups ():
    global PARSED_PICKUPS

    lines = pickups.split('\n')
    items = []

    for line in lines:
        line = line.strip()

        if line.startswith('Pickup.Create'):
            match = re.search(r'^Pickup\.Create\((\$\d+), (#[A-Za-z\d_]+), (\d+), ([^,]+), ([^,]+), ([^\)]+)\)$', line)
        elif line.startswith('032B:'):
            match = re.search(r'^032B: (\$\d+) = create_weapon_pickup (#[A-Za-z\d_]+) (\d+) ammo \d+ at ([^ ]+) ([^ ]+) ([^ ]+)$', line)
        else:
            continue

        if not match:
            continue

        var, model, type_, x, y, z = match.groups()

        type_ = int(type_, 10)

        areCoordsLiterals = 0

        if x[0] != '$':
            x = float(x)
            areCoordsLiterals += 1

        if y[0] != '$':
            y = float(y)
            areCoordsLiterals += 1

        if z[0] != '$':
            z = float(z)
            areCoordsLiterals += 1

        areCoordsLiterals = areCoordsLiterals == 3

        items.append({
            'var':    var,
            'model':  model,
            'coords': f'{ x } { y } { z }',
            'type':   f'{ type_ } ({ PICKUP_TYPES[type_] })',
            'areCoordsLiterals': areCoordsLiterals,
        })

    PARSED_PICKUPS = items

    # print(toJson(items))

# parsePickups()

'''
Rocket Launcher
[ -0.84925257217708, 0.39748267509005 ]
[ -995.1,            -1178.1          ]


Chainsaw
[ -0.53779363632336, 0.3520538111473 ]  
[ 30.0,              -1330.9         ]    

// -----------------------------------

M60      / -1744.9 -288.9 / -1.0711187285984 0.66447109999056   // westmost
RGrenade / 556.6 207.4    / -0.37829099068412 0.82352834941204  // eastmost
Molotov  / -755.7 1347.5  / -0.77719431356854 1.1653082038674   // northmost
Knife    / 118.7, -1546.1 / -0.51067326131195 0.28493780245492  // southmost

TL: -1744.9  1347.5
BR:   556.6 -1546.1

TL: -1.0711187285984  1.1653082038674
BR: -0.37829099068412 0.28493780245492
'''


ALL_USEFUL_PICKUPS = '''
#HEALTH -113.2 -975.7 10.4          | In front of Ocean View Hospital                                                | 
#HEALTH -1139.4 55.4 11.2           | Behind the wall next to the blown up building near Junk Yard                   | 
#HEALTH -1290.9 91.9 26.9           | On top of the garbage conveyor in Junk Yard                                    | 
#HEALTH -1399.4 -865.9 20.9         | On the second floor of the airport                                             | 
#HEALTH -225.1 -1158.1 9.1          | To the left of the entrance to Ocean Bay Marina                                | 
#HEALTH -330.702 -573.366 11.6      | In the storage room on the ground floor of Vercetti Estate                     | 
#HEALTH -404.0 -588.0 11.6          | In the corridor of the first floor of Vercetti Estate                          | 
#HEALTH -406.2503 -566.4947 19.5804 | In the room to the right of the main staircase in Vercetti Estate              | 
#HEALTH -478.1 1438.5 16.1          | On the dirt bike track                                                         | 
#HEALTH -655.1 -1506.3 8.1          | Down the stairs at the Boatyard                                                | 
#HEALTH -675.0 1263.3 25.1          | On the roof of the building where Ammu-Nation is located                       | 
#HEALTH -692.4 -1283.8 11.1         | Under the ship's ramp in Viceport                                              | 
#HEALTH -711.7 -501.7 11.3          | On the sidewalk of the bridge between Starfish Island and Little Havana        | 
#HEALTH -821.8 1144.8 26.1          | On the roof of Schuman Health Care Center                                      | 
#HEALTH -822.6 1137.3 12.4          | In the yard of the Schuman Health Care Center                                  | 
#HEALTH -834.2 740.6 11.3           | At the pharmacy to the west of Vice City Fire Department                       | 
#HEALTH -851.4 -78.8 11.5           | At Ryton Aide Pharmacy                                                         | 
#HEALTH -885.4 -483.4 13.1          | On the stairs of West Haven Community Healthcare Center                        | 
#HEALTH -925.1 -638.3 16.0          | On the roof of one of the buildings behind The Cherry Popper Ice Cream Company | 
#HEALTH 10.7 1099.0 16.6            | Near the fountain in front of an abandoned house on Prawn Island               | 
#HEALTH 377.4 467.7 11.6            | To the left of the building opposite Pay'n'Spray behind the trash container    | 
#HEALTH 384.3 756.6 11.7            | At the pharmacy in front of Shady Palms Hospital                               | 
#HEALTH 385.3 1210.9 19.4           | In a big glass of Sprunk at North Point Mall                                   | 
#HEALTH 456.2 -471.4 16.6           | On the roof of the building to the left of the Vice City Police Department     | 
#HEALTH 469.6 697.4 11.7            | In the yard of Shady Palms Hospital                                            | 
#HEALTH 85.3 402.7 19.8             | On the bridge at Leaf Links Golf Club                                          | 
---
#BODYARMOUR -1058.9 -240.6 18.2        | On the roof of Print Works                                                                       | 
#BODYARMOUR -1171.0 -457.4 10.7        | Near one of the houses near Escobar International Airport                                        | 
#BODYARMOUR -1177.0 -915.3 14.9        | In the parking lot to the right of Vice City Transport Police near Escobar International Airport | 
#BODYARMOUR -1695.6 -289.4 29.7        | At the top of the right tower at Fort Baxter Air Base                                            | 
#BODYARMOUR -336.0 -573.7 11.6         | In the storage room on the ground floor of Vercetti Estate                                       | 
#BODYARMOUR -406.2992 -564.582 19.5804 | In the room to the right of the main staircase in Vercetti Estate                                | 
#BODYARMOUR -567.6 1370.36 16.4        | On the roof of a building near the dirt bike track                                               | 
#BODYARMOUR -625.5 622.2 11.7          | Behind The Greasy Chopper bar                                                                    | 
#BODYARMOUR -70.8 510.6 11.6           | On the course at Leaf Links Golf Club                                                            | 
#BODYARMOUR -733.5 -1294.7 12.4        | On the steps of a building in Viceport                                                           | 
#BODYARMOUR -921.9 722.9 11.0          | In the alley to the left of the pizzeria                                                         | 
#BODYARMOUR 148.8 -349.9 8.7           | On the ground floor of StarView Heights                                                          | 
#BODYARMOUR 205.7 -885.7 12.2          | Near the pool next to the pink skyscraper                                                        | 
#BODYARMOUR 350.2 884.8 25.5           | On the second floor of the blue building near North Point Mall                                   | 
#BODYARMOUR 4.9 -1239.2 19.2           | On the stairs of the building to the left of Pay'n'Spray                                         | 
#BODYARMOUR 416.1 517.7 11.2           | In the gazebo in the courtyard of the house to the left of the Vice City Police Department       | 
#BODYARMOUR 42.8 951.1 11.0            | Behind the fence opposite the main entrance to InterGlobal Studios                               | 
#BODYARMOUR 430.8 162.1 11.8           | Near the basketball court in the courtyard of the house to the right of the pizzeria             | 
#BODYARMOUR 520.2 -171.2 13.9          | Near the entrance to Standing Vice Point                                                         | 
#BODYARMOUR 535.3 1214.1 18.9          | To the left of the building opposite the main entrance to North Point Mall                       | 
#BODYARMOUR 214.2 -1275.7 19.2         | On the second floor of Ocean View Hotel                                                          | Collect 10 hidden packages
#BODYARMOUR -314.7 -551.2 10.3         | Left of Vercetti Estate                                                                          | Collect 10 hidden packages 
#BODYARMOUR -813.1 1344.7 66.4         | On the roof of the penthouse                                                                     | Collect 10 hidden packages
---
#BRIBE -1015.9 -627.9 11.2 | In the alley behind the yellow Rockstar banner opposite the Screw This store                    | 
#BRIBE -822.7 1304.5 11.7  | In front of the penthouse entrance                                                              | 
#BRIBE -900.69 251.4 17.1  | Hanging in the air at the end of the block where Kaufman Cabs is located                        | 
#BRIBE -906.3 -834.0 15.7  | Near the diving board behind Sunshine Autos                                                     | 
#BRIBE -937.9 -114.1 17.0  | Near the diving board behind Pay'n'Spray                                                        | 
#BRIBE -973.7 61.0 10.4    | In the alley next to the houses to the right of Kaufman Cabs                                    | 
#BRIBE 116.0 -1313.1 4.4   | In the underpass behind the Ocean View Hotel                                                    | 
#BRIBE 382.7 364.1 10.8    | In the alley opposite the safehouse located to the left of the Pay'n'Spray                      | 
#BRIBE 393.7 -660.6 10.7   | At the far end of the alley behind the buildings to the left of the Vice City Police Department | 
#BRIBE 393.9 -60.2 11.5    | Through the canal behind the Malibu Club                                                        | 
#BRIBE 422.4 971.2 12.1    | Between the bridge and North Point Mall                                                         | 
#BRIBE 470.7 70.1 10.8     | Behind the building behind the Malibu Club                                                      | 
#BRIBE 89.1 887.4 10.5     | On the road opposite the secondary entrance to InterGlobal Studios                              | 
---
#ADRENALINE -1022.1 -547.0 11.2 | On the next block behind The Cherry Popper Ice Cream Company                                   | 
#ADRENALINE -1095.1 99.4 12.3   | Behind the house across from the pizzeria near Kaufman Cabs                                    | 
#ADRENALINE -342.2 -591.5 36.9  | On the roof of Vercetti Estate                                                                 | 
#ADRENALINE -366.6 -500.3 11.3  | Opposite the entrance to Vercetti Estate                                                       | 
#ADRENALINE -37.7 -938.3 10.5   | On the ground floor of Washington Mall                                                         | 
#ADRENALINE -381.2 1065.2 13.0  | Opposite Eight-Ten VCN                                                                         | 
#ADRENALINE -730.1 1226.3 24.2  | On the roof of the building where Ammu-Nation is located                                       | 
#ADRENALINE -839.0 740.6 11.3   | At the pharmacy to the west of Vice City Fire Department                                       | 
#ADRENALINE -857.1 -83.6 11.5   | At Ryton Aide Pharmacy                                                                         | 
#ADRENALINE -882.0 111.2 9.3    | Behind the high-rise building located next to the bridge leading to Leaf Links Golf Club       | 
#ADRENALINE -967.1 -62.6 11.0   | In the parking space of one of the houses behind Pay'n'Spray                                   | 
#ADRENALINE 385.6 752.3 11.7    | At the pharmacy in front of Shady Palms Hospital                                               | 
#ADRENALINE 425.6 221.1 16.2    | On the balcony of one of the motel buildings to the right of the pizzeria near the Malibu Club | 
#ADRENALINE 428.4 947.5 13.2    | Between the bridge and North Point Mall                                                        | 
#ADRENALINE 448.6 16.6 11.0     | Behind Malibu Club                                                                             | 
#ADRENALINE 471.1 -444.1 10.6   | In the alley behind the houses to the left of the Vice City Police Department                  | 
----
#KILLFRENZY -1011.37 -170.64 10.99     | In the alley northeast of Print Works                                                                                              | 
#KILLFRENZY -1100.625 1453.43 8.73     | To the right of Hyman Memorial Stadium                                                                                             | 
#KILLFRENZY -1143.48 -410.87 10.95     | On the basketball court southwest of Print-Works                                                                                   | 
#KILLFRENZY -1176.341 -702.975 22.662  | On the roof of the building behind the banners in front of the Vice Surf banner near the entrance to Escobar International Airport | 
#KILLFRENZY -1234.83 -90.378 11.43     | Near the short red bridge near Junk Yard                                                                                           | 
#KILLFRENZY -1435.29 -833.645 30.05989 | On the roof of Escobar International Airport                                                                                       | 
#KILLFRENZY -1483.47 -881.677 14.87    | At Escobar International Airport                                                                                                   | 
#KILLFRENZY -1519.33 -292.236 14.86    | To the right of Fort Baxter Air Base                                                                                               | 
#KILLFRENZY -194.701 -1085.067 15.66   | Near the building behind Ocean View Hospital                                                                                       | 
#KILLFRENZY -34.13 -948.707 21.772     | In the Washington Mall rooftop parking lot                                                                                         | 
#KILLFRENZY -366.44 -1742.1 11.426     | In a ruined hut in the ocean near Ocean Bay Marina                                                                                 | 
#KILLFRENZY -448.796 1249.27 11.75     | In the courtyard of V.A.J Finance                                                                                                  | 
#KILLFRENZY -508.768 1149.203 18.172   | On the stairs of the building to the left of Eight-Ten VCN                                                                         | 
#KILLFRENZY -626.642 -1354.85 16.373   | On the very first ship in Viceport                                                                                                 | 
#KILLFRENZY -674.22 1162.7 28.15       | On the stairs opposite the building where Ammu-Nation is located                                                                   | 
#KILLFRENZY -679.66 -419.712 10.469    | On Starfish Island in the courtyard of a house next to the bridge leading to Little Havana                                         | 
#KILLFRENZY -789.41 592.56 11.1        | Behind Moist Palms Hotel                                                                                                           | 
#KILLFRENZY -890.184 -489.655 36.2     | On the roof of West Haven Community Healthcare Center                                                                              | 
#KILLFRENZY -908.317 744.149 11.092    | In the alley to the left of the pizzeria                                                                                           | 
#KILLFRENZY -956.113 -1206.33 14.86    | Behind the Hooker Inn Express                                                                                                      | 
#KILLFRENZY -983.373 -353.997 13.84    | In the alley southeast of Print Works                                                                                              | 
#KILLFRENZY 144.449 -545.234 14.751    | In the courtyard of high-rise buildings across the street from StarView Heights                                                    | 
#KILLFRENZY 217.247 261.372 8.71       | On the pier near the bridge leading to Leaf Links Golf Club                                                                        | 
#KILLFRENZY 218.22 -1613.76 11.06      | Next to the road near the lighthouse                                                                                               | 
#KILLFRENZY 234.86 34.22 9.98          | In a round dead end                                                                                                                | 
#KILLFRENZY 3.426 -1147.0 10.45        | In the next block to the left of Pay'n'Spray                                                                                       | 
#KILLFRENZY 300.673 1324.88 22.919     | Near the building located northwest of the main entrance to North Point Mall                                                       | 
#KILLFRENZY 370.63 1125.86 26.5        | On the second floor of North Point Mall                                                                                            | 
#KILLFRENZY 468.656 -1608.79 11.03     | On the beach next to the lighthouse                                                                                                | 
#KILLFRENZY 479.69 1110.18 17.33       | To the left of the main entrance to North Point Mall                                                                               | 
#KILLFRENZY 587.795 1206.26 15.64      | Behind the building opposite the main entrance to North Point Mall                                                                 | 
#KILLFRENZY 593.315 -352.826 13.711    | Behind Standing Vice Point                                                                                                         | 
#KILLFRENZY 624.26 -230.158 23.915     | On the pool tower behind Standing Vice Point                                                                                       | 
#KILLFRENZY 68.702 -1119.231 10.458    | In the courtyard of a pink house next to a gas station near the Washington Mall                                                    | 
#KILLFRENZY 85.623 -1259.86 17.092     | On the roof of a building a block behind Ocean View Hotel                                                                          | 
---
#Package 479.6 -1718.5 15.6   | At the entrance to the lighthouse                                                                      |
#Package 708.4 -498.2 12.3    | In a cabin on the beach                                                                                |
#Package -213.0 -1647.1 13.1  | On the rocks in the ocean near Ocean Bay Marina                                                        |
#Package -368.4 -1733.2 11.6  | In a ruined hut in the ocean near Ocean Bay Marina                                                     |
#Package -104.3 -1600.3 10.4  | Behind the building to the right of the helipad near Ocean Bay Marina                                  |
#Package -234.7 -1082.6 13.6  | Near the building behind Ocean View Hospital                                                           |
#Package 88.0 -991.7 19.1     | On the roof of a building next to the red Washington Mall sign and gas station                         |
#Package 205.4 -888.9 12.1    | Near the pool next to the pink skyscraper                                                              |
#Package 183.1 -652.9 10.8    | Near the bridge in front of the Bunch of Tools store                                                   |
#Package 370.9 -469.5 13.8    | At the Vice City Police Department                                                                     |
#Package 298.8 -278.5 11.9    | Behind the Spand Express building next to the construction site                                        |
#Package 321.8 -774.3 22.8    | On the roof of one of the buildings located along the alley behind the Ocean View Hotel                |
#Package 491.8 -45.3 10.0     | Behind Malibu Club                                                                                     |
#Package 472.8 116.0 11.2     | Under the motel stairs to the right of the pizzeria near the Malibu Club                               |
#Package 379.6 212.9 11.3     | In the next block north of the pizzeria                                                                |
#Package 290.1 295.4 13.5     | In a villa next to the bridge leading to Leaf Links Golf Club                                          |
#Package 470.9 1123.6 24.5    | On the second floor of North Point Mall                                                                |
#Package 407.6 1018.2 25.3    | On the second floor of the Gash store in North Point Mall                                              |
#Package 561.6 1157.1 18.9    | Behind the building opposite the main entrance to North Point Mall                                     |
#Package 891.8 873.8 16.4     | On the beach challenging track                                                                         |
#Package 353.7 -564.3 56.4    | On the roof of a tall building behind the Vice City Police Department                                  |
#Package 306.9 1177.5 17.4    | On the lower level of the North Point Mall parking lot                                                 |
#Package 271.3 932.9 9.8      | Under the bridge next to North Point Mall                                                              |
#Package 328.7 717.2 22.8     | On the pool tower next to the tall arched hotel                                                        |
#Package 473.3 16.4 33.0      | On the roof of the building behind the Malibu Club                                                     |
#Package 352.5 282.2 19.6     | On the roof of a building next to the safehouse and Pay'n'Spray                                        |
#Package 70.1 -479.6 13.6     | In the shower near high-rise buildings across the street from StarView Heights                         |
#Package 53.6 -446.5 7.6      | Under the bridge near StarView Heights                                                                 |
#Package 266.3 -249.9 36.1    | On a red beam at a construction site                                                                   |
#Package 413.9 1217.4 18.4    | In one of the recesses of North Point Mall                                                             |
#Package -172.4 -1341.3 3.9   | In the Ocean Bay Marina car park                                                                       |
#Package -233.1 -931.2 9.8    | Under the bridge between Ocean Beach and Viceport                                                      |
#Package 69.7 -796.6 11.7     | Behind the safehouse opposite Hotel Harrison                                                           |
#Package 107.5 -551.9 14.7    | In the courtyard of high-rise buildings across the street from StarView Heights                        |
#Package 233.9 -132.2 8.0     | On the pier behind the building opposite the construction site                                         |
#Package 424.5 89.3 11.3      | In a pizzeria near Malibu Club                                                                         |
#Package 401.6 431.1 11.4     | In the courtyard of the building opposite safehouse and Pay'n'Spray                                    |
#Package 193.9 678.8 12.9     | In the bushes to the right of the entrance to the tall arched hotel                                    |
#Package 589.4 36.0 16.7      | Behind the WK Chariot Hotel                                                                            |
#Package 519.9 -135.4 35.2    | On the roof of the building opposite the Malibu Club                                                   |
#Package -41.8 922.4 19.4     | On the roof of one of the buildings at InterGlobal Studios                                             |
#Package -16.1 991.7 10.9     | In Stage B at InterGlobal Studios                                                                      |
#Package 60.7 916.5 10.8      | In the alley on the road opposite the secondary entrance to InterGlobal Studios                        |
#Package -68.9 1124.0 17.0    | Behind the green abandoned building on Prawn Island                                                    |
#Package 82.7 1113.8 18.7     | In yellow abandoned building on Prawn Island                                                           |
#Package 70.5 599.3 14.5      | Under the viewing platform on the course at Leaf Links Golf Club                                       |
#Package 162.4 246.4 12.2     | Under the bridge leading to Leaf Links Golf Club                                                       |
#Package 43.1 -150.9 12.2     | On the yellow bridge connecting two courses at Leaf Links Golf Club                                    |
#Package -46.6 257.7 24.5     | On the course at Leaf Links Golf Club                                                                  |
#Package 43.4 -15.0 17.3      | On a small island on the second course at Leaf Links Golf Club                                         |
#Package -236.9 -588.1 10.3   | On the pier to the left of Vercetti Estate                                                             |
#Package -519.0 -599.3 10.3   | Near the pink fence to the right of Vercetti Estate                                                    |
#Package -580.5 -422.6 19.8   | Behind the house with Rockstar pool northwest of Vercetti Estate                                       |
#Package -310.4 -415.5 10.1   | In a small round pool near the house opposite Vercetti Estate                                          |
#Package -245.4 -323.8 10.2   | Near the entrance to the house in the northeast of Vercetti Estate                                     |
#Package -246.9 1219.5 10.9   | Behind the building to the right of Eight-Ten VCN                                                      |
#Package -451.0 1286.6 12.6   | Under the monument in the courtyard of V.A.J Finance                                                   |
#Package -764.3 1266.0 11.5   | In the alley near the entrance to the penthouse                                                        |
#Package -1550.1 1403.1 8.7   | In the parking lot behind Hyman Memorial Stadium                                                       |
#Package -790.8 1119.4 9.8    | Left of Schuman Health Care Center                                                                     |
#Package -451.5 1119.7 61.7   | On the roof of Eight-Ten VCN                                                                           |
#Package -567.4 776.1 22.8    | In the office of a tall building next to the hobo cabin                                                |
#Package -898.7 430.4 10.9    | Behind Moist Palms Hotel                                                                               |
#Package -979.2 266.7 8.9     | At the basement entrance in the alley to the left of Kaufman Cabs                                      |
#Package -856.3 228.5 12.9    | On the roof of the building at the end of the block where Kaufman Cabs is located                      |
#Package -1072.5 351.7 11.2   | In the red barn at Phil's Place                                                                        |
#Package -1161.6 431.1 11.0   | On the pier behind Phil's Place                                                                        |
#Package -975.1 191.9 12.6    | Behind Kaufman Cabs                                                                                    |
#Package -1033.4 44.0 11.1    | In the courtyard of houses to the right of the pizzeria                                                |
#Package -994.0 -250.3 10.7   | Behind the fence opposite Print Works                                                                  |
#Package -1104.9 -120.9 20.1  | On the roof of the gray building to the right of Print Works                                           |
#Package -1131.6 -355.4 15.0  | At the entrance to the green house southwest of Print Works                                            |
#Package -1195.2 -317.7 10.9  | In Laundromat southwest of Print Works                                                                 |
#Package -1093.7 -600.1 26.0  | On the cornice of a yellow Kaufman Cabs banner                                                         |
#Package -1179.9 -576.3 12.0  | To the left of the yellow Rockstar banner next to Café Robina                                          |
#Package -1018.2 -874.1 17.9  | On the second floor of Sunshine Autos                                                                  |
#Package -855.3 -631.8 11.3   | In the 24/7 store to the left of The Cherry Popper Ice Cream Company                                   |
#Package -1179.2 -718.8 22.8  | Behind the banners in front of the Vice Surf banner near the entrance to Escobar International Airport |
#Package -802.9 -1184.6 11.1  | Near the yellow house not far from the ship                                                            |
#Package -620.8 -1342.4 16.3  | On the very first ship in Viceport                                                                     |
#Package -1024.6 -1494.6 19.4 | By Chartered Libertine Lines ship                                                                      |
#Package -1090.2 -1199.2 11.2 | In a large area with garages to the left of Pay'n'Spray                                                |
#Package -829.2 -1461.0 12.6  | Near the cargo trailer next to the main building of the Vice City Port Authority                       |
#Package -1160.6 -1333.8 14.9 | Inside a hangar with a pier                                                                            |
#Package -1369.3 -1255.7 18.2 | On the helipad near the runway at Escobar International Airport                                        |
#Package -1280.9 -1146.5 22.2 | On the roof of one of the hangars near the runway at Escobar International Airport                     |
#Package -1773.8 -1053.2 14.8 | Near a large passenger plane in a hangar at Escobar International Airport                              |
#Package -1187.3 -1041.4 14.8 | In the parking lot to the right of Vice City Transport Police near Escobar International Airport       |
#Package -1477.3 -881.0 32.4  | On the roof of Escobar International Airport                                                           |
#Package -1561.8 -1059.5 14.8 | Near the plane next to the ramp at Escobar International Airport                                       |
#Package -1349.1 -1090.4 24.5 | On the ramp at Escobar International Airport                                                           |
#Package -1567.3 -1055.5 21.3 | On the plane next to the ramp at Escobar International Airport                                         |
#Package -1366.4 -928.0 20.8  | At the entrance to the ramp on the second floor of Escobar International Airport                       |
#Package -1523.5 -819.1 14.8  | On the ground floor of Escobar International Airport                                                   |
#Package -1829.1 -887.6 14.8  | Behind the empty hangars near the runway at Escobar International Airport                              |
#Package -1726.5 -419.2 14.8  | Near the far plane behind the building opposite Escobar International Airport                          |
#Package -1737.2 -299.2 14.8  | Behind the Fort Baxter Air Base sign                                                                   |
#Package -1328.0 -537.1 13.9  | Behind the last banners in front of Escobar International Airport                                      |
#Package -1063.5 -965.5 14.8  | Behind the large fuel tanks in front of Sunshine Autos                                                 |
#Package -1265.8 -1346.9 29.6 | On the roof of the Freight and Cargo Terminal building at Escobar International Airport                |
---
#KNIFECUR     468.5 -54.2 15.7            | On the second floor of Malibu Club                                                                     | 
#NITESTICK    402.4 -488.3 12.4           | In the Vice City Police Department                                                                     | 
#M4           -330.9 -569.7 11.6          | In the storage room on the ground floor of Vercetti Estate                                             | 
#CHROMEGUN    -335.9 -569.5 11.6          | In the storage room on the ground floor of Vercetti Estate                                             | 
#CHNSAW       30.0 -1330.9 13.0           | In the motel room to the right of Pay'n'Spray                                                          | 
#BAT          206.7 -1254.4 12.0          | Behind Ocean View Hotel                                                                                | 
#COLT45       -228.4 -1318.2 9.1          | To the left of the entrance to Ocean Bay Marina                                                        | 
#COLT45       340.5 -249.5 12.5           | On the first floor of the construction site                                                            | 
#CHROMEGUN    42.3 -959.2 21.8            | In the Washington Mall rooftop parking lot                                                             | 
#CHROMEGUN    568.9 -449.3 11.1           | Next to the bench by the beach                                                                         | 
#TEC9         287.9 50.7 10.8             | Behind the house in a round dead end                                                                   | 
#GRENADE      362.2 -500.5 12.3           | Behind Vice City Police Department                                                                     | 
#CLEAVER      402.6 102.5 11.4            | Behind the pizzeria near the Malibu Club                                                               | 
#RUGER        418.9 589.9 18.3            | On the roof at the back of the villa                                                                   | 
#KATANA       476.9 1014.9 19.2           | In the pantry of Tarbrush Café in North Point Mall                                                     | 
#BRASSKNUCKLE 224.0 -1207.5 11.0          | In the alley behind the Ocean View Hotel                                                               | 
#KNIFECUR     118.7 -1546.1 10.8          | Behind Maison Wenifall hotel                                                                           | 
#MACHETE      56.6 -459.3 11.4            | On the sidewalk on the bridge between Vice Point and Starfish Island                                   | 
#UZI          5.4 -1277.0 10.4            | Behind Pay'n'Spray                                                                                     | 
#UZI          157.0 -895.3 12.3           | Behind pink skyscraper                                                                                 | 
#BOMB         556.6 207.4 14.5            | Behind one of the high rise buildings on the beach                                                     | 
#M4           -32.8 1019.2 13.0           | In Stage B at InterGlobal Studios                                                                      | 
#UZI          17.3 1145.7 23.5            | On the balcony of an abandoned building on Prawn Island                                                | 
#GOLFCLUB     95.0 279.2 21.8             | Behind the Leaf Links Golf Club entrance                                                               | 
#FLAME        -546.0 -418.9 9.8           | In the Rockstar pool near one of the houses on Starfish Island                                         | 
#SNIPER       -476.4 -571.2 12.9          | In the maze to the right of Vercetti Estate                                                            | 
#KATANA       -554.11 -547.7 10.7         | In the garage of the house to the right of Vercetti Estate                                             | 
#MOLOTOV      -755.7 1347.5 11.8          | In Tacopalypse restaurant next to the penthouse                                                        | 
#UZI          -545.8 694.6 11.0           | Under the stairs leading to the hobo cabin                                                             | 
#M4           -980.4 118.7 9.3            | In the courtyard among small houses in Little Haiti                                                    | 
#M4           -1221.0 -641.6 11.7         | Behind the banners in front of the Vice Surf banner near the entrance to Escobar International Airport | 
#SNIPER       -742.1 -949.9 9.9           | On a bridge support between Ocean Beach and Viceport                                                   | 
#ROCKETLA     -995.1 -1178.1 13.6         | In the pool at the Hooker Inn Express                                                                  | 
#INGRAMSL     -713.3 -1466.0 11.2         | Behind the fence across the street from the Boatyard                                                   | 
#FLAME        -1015.1 -1392.9 11.5        | Near the building next to Chartered Libertine Lines                                                    | 
#SHOTGSPA     -1359.0 -742.2 14.9         | Behind the Vice Surf banner in front of Escobar International Airport                                  | 
#M60          -1744.9 -288.9 29.7         | At the top of the left tower at Fort Baxter Air Base                                                   | 
#GRENADE      -939.8 -464.9 10.9          | On the basketball court in the back of the West Haven Community Healthcare Center                      | 
#PYTHON       -1182.7 -61.1 11.4          | Near the short red bridge near Junk Yard                                                               | 
#BUDDYSHOT    -1305.2 177.1 11.4          | Behind the hangar at Junk Yard                                                                         | 
#LASER        -1114.3 -602.0 26.0         | On the roof of a building opposite the yellow Rockstar banner near Escobar International Airport       | 
#MINIGUN      -1184.17 102.62 17.5        | On the second floor of the blown up building next to Junk Yard                                         | 
#PYTHON       -401.7512 -566.0168 19.5804 | In the room to the right of the main staircase in Vercetti Estate                                      | 

// Ocean View 2nd floor:
#CHNSAW   210.2 -1274.7 19.2 | On the second floor of Ocean View Hotel | Collect 20 hidden packages
#PYTHON   206.2 -1273.7 19.2 | On the second floor of Ocean View Hotel | Collect 30 hidden packages
#FLAME    224.2 -1273.1 19.2 | On the second floor of Ocean View Hotel | Collect 40 hidden packages
#LASER    228.2 -1279.2 19.2 | On the second floor of Ocean View Hotel | Collect 50 hidden packages
#MINIGUN  226.0 -1268.6 20.1 | On the second floor of Ocean View Hotel | Collect 60 hidden packages
#ROCKETLA 231.7 -1264.4 20.1 | On the second floor of Ocean View Hotel | Collect 70 hidden packages

// Left to Vince Penthouse:
#CHNSAW   -310.7 -551.2 10.3 | Left of Vercetti Estate | Collect 20 hidden packages
#PYTHON   -306.7 -551.2 10.3 | Left of Vercetti Estate | Collect 30 hidden packages
#FLAME    -302.7 -551.2 10.3 | Left of Vercetti Estate | Collect 40 hidden packages
#LASER    -298.7 -551.2 10.3 | Left of Vercetti Estate | Collect 50 hidden packages
#MINIGUN  -294.7 -551.2 10.3 | Left of Vercetti Estate | Collect 60 hidden packages
#ROCKETLA -290.7 -551.2 10.3 | Left of Vercetti Estate | Collect 70 hidden packages

// Penthouse in downtown:
#CHNSAW   -817.1 1344.7 66.4 | On the roof of the penthouse | Collect 20 hidden packages
#PYTHON   -821.1 1344.7 66.4 | On the roof of the penthouse | Collect 30 hidden packages
#FLAME    -825.1 1344.7 66.4 | On the roof of the penthouse | Collect 40 hidden packages
#LASER    -830.1 1344.7 66.4 | On the roof of the penthouse | Collect 50 hidden packages
#MINIGUN  -833.1 1344.7 66.4 | On the roof of the penthouse | Collect 60 hidden packages
#ROCKETLA -839.0 1351.6 66.4 | On the roof of the penthouse | Collect 70 hidden packages

// [PAID] Phil's Place:
#M60      -1105.9 335.3 11.1 | In the courtyard of Phil's Place | Complete mission Boomshine Saigon
#ROCKETLA -1105.9 330.3 11.1 | In the courtyard of Phil's Place | Complete mission Boomshine Saigon
#MINIGUN  -1105.9 325.3 11.1 | In the courtyard of Phil's Place | Complete mission Boomshine Saigon
#BOMB     -1105.9 320.3 11.1 | In the courtyard of Phil's Place | Complete mission Boomshine Saigon

// PSG-1 (laser)    102.499992 264.4 22 // [UNREACHABLE] sniper rifle behind wall in the golf club
'''

PRICES_AND_NAMES = '''
#BRASSKNUCKLE - 10    - Brass Knuckle
#SCREWDRIVER  - 10    - Screw Driver
#GOLFCLUB     - 10    - Golf Club
#NITESTICK    - 10    - Night Stick
#KNIFECUR     - 10    - Knife
#BAT          - 10    - Baseball Bat
#HAMMER       - 10    - Hammer
#CLEAVER      - 10    - Cleaver
#MACHETE      - 10    - Machete
#KATANA       - 10    - Katana
#CHNSAW       - 10    - Chainsaw
#GRENADE      - 1000  - Grenade
#BOMB         - 1000  - Detonator Grenade
#TEARGAS      - 1000  - Tear Gas
#MOLOTOV      - 500   - Molotov
#ROCKETLA     - 8000  - Rocket Launcher
#COLT45       - 250   - Colt .45 (Pistol)
#PYTHON       - 400   - Python (.357)
#CHROMEGUN    - 1200  - Chrome Shotgun
#SHOTGSPA     - 1250  - Spaz Shotgun (S.P.A.S. 12)
#BUDDYSHOT    - 1250  - Stubby Shotgun
#TEC9         - 800   - Tec-9
#UZI          - 800   - Uzi 9mm (Uz-I)
#INGRAMSL     - 650   - Ingram Mac 10
#MP5LNG       - 1200  - MP5 (MP)
#M4           - 5000  - M4
#RUGER        - 400   - Ruger (Kruger)
#SNIPER       - 10000 - Sniper Rifle
#LASER        - 10000 - PSG-1 (.308 Sniper)
#FLAME        - 8000  - Flame Thrower
#M60          - 8000  - M60
#MINIGUN      - 10000 - Minigun
#CAMERA       - 500   - Camera
#HEALTH       - 20    - Health
#BODYARMOUR   - 10    - Armor
#ADRENALINE   - 10    - Adrenaline
#BRIBE        - NO    - Bribe  
#KILLFRENZY   - NO    - Rampage
#Package      - NO    - Package
'''

def normCoords ():
    parsePickups()

    gameCoords = [ -1744.9, 1347.5, 556.6, -1546.1 ]
    mapCoords  = [ -0.37829099068412, 0.28493780245492, -1.0711187285984, 1.1653082038674 ]

    gx1, gy1, gx2, gy2 = gameCoords
    mx1, my1, mx2, my2 = mapCoords

    scaleMX = 1 / abs(mx2 - mx1)
    scaleMY = 1 / abs(my2 - my1)

    for p in ALL_PICKUPS:
        lng = p['longitude']
        lat = p['latitude']

        if lng < mx2 or lng > mx1 or lat < my1 or lat > my2:
            print('Skip', toJson(p))
            continue

        absX = 1 - abs(lng - mx1) * scaleMX
        absY = 1 - abs(lat - my1) * scaleMY

        x = gx1 + abs(gx2 - gx1) * absX
        y = gy2 + abs(gy2 - gy1) * (1 - absY)

        if x < gx1 or x > gx2 or y < gy2 or y > gy1:
            print('Skip', toJson(p))
            continue

        # ------------------------

        bestDist = None
        best = None

        for pp in PARSED_PICKUPS:
            if not pp['areCoordsLiterals'] or pp.get('isBusy'):
                continue

            name = MODEL_TO_NAME.get(pp['model'])

            if name != p['title']:
                continue

            coords = [ float(c) for c in pp['coords'].split(' ') ]
            ppx = coords[0]
            ppy = coords[1]

            dist = math.sqrt(pow(x - ppx, 2) + pow(y - ppy, 2))

            if bestDist is None or bestDist > dist:
                bestDist = dist
                best = pp

        if best:
            best['isBusy'] = True
        else:
            print('NOT FOUND!', toJson(p))
            continue

        # print(p)
        print(p['title'], best['model'], bestDist, best['coords'])


            # if lng == -1.0711187285984 and pp['model'] == '#M60' and ppx == -1744.9:
            #     print(x, ppx)
            #     print(y, ppy)


    print('--------')

    for pp in PARSED_PICKUPS:
        if pp['areCoordsLiterals'] and not pp.get('isBusy'):
            print(pp['model'])


        # print(lng, lat, x, y)

    

        # print(newLng, newLat)

    # newGX1 = 0
    # newGY1 = 0
    # newGX2 = abs(gx2 - gx1)
    # newGY2 = abs(gy2 - gy1)

    # print(gx1, gy1, gx2, gy2)
    # print(newGX1, newGY1, newGX2, newGY2)

    # newMX1 = 0
    # newMY1 = 0
    # newMX2 = abs(mx2 - mx1)
    # newMY2 = abs(my2 - my1)

    # print(mx1, my1, mx2, my2)
    # print(newMX1, newMY1, newMX2, newMY2)

    # gDistX = abs(gx1 - gx2)
    # gDistY = abs(gy1 - gy2)

    # mDistX = abs(mx1 - mx2)
    # mDistY = abs(my1 - my2)

    # mpgx = mDistX / gDistX
    # mpgy = mDistY / gDistY
    # gpmx = gDistX / mDistX
    # gpmy = gDistY / mDistY

    # print(gDistX, gDistY)
    # print(mDistX, mDistY)

    # print(gDistX / mDistX)
    # print(gDistY / mDistY)

    # mExpX1 = 1.1 - abs(mx1)
    # mExpY1 = 1.2 - abs(my1)
    # mExpX2 = 0.4 - abs(mx2)
    # mExpY2 = 0.3 - abs(my2)


    # mExpX1 / mpgx

# normCoords()

'''
ALL PICKUP TYPES:
- #INGRAMSL
- #M4
- #COLT45
- #BAT
- #LASER
- #PYTHON
- #ROCKETLA
- #CLEAVER
- #BOMB
- #SNIPER
- #M60
- #BUDDYSHOT
- #NITESTICK
- #TEC9
- #MACHETE
- #RUGER
- #GOLFCLUB
- #SHOTGSPA
- #CHROMEGUN
- #GRENADE
- #KNIFECUR
- #MINIGUN
- #UZI
- #BRASSKNUCKLE
- #FLAME
- #CHNSAW
- #KATANA
- #MOLOTOV
---
- #HEALTH
- #BODYARMOUR
- #ADRENALINE
- #BRIBE
- #KILLFRENZY
---
- #PICKUPSAVE
- #BRIEFCASE' 
- #KEYCARD
- #INFO
- #CELLPHONE
- #CRAIGPACKAGE
---
- Package
- Available Asset
- Unavailable Asset
- Clothes
- Asset Money
- Cash
'''

def parseStaticPickups ():
    lines = MAIN_SCM.split('\n')
    items = []

    code = []

    for line in lines:
        line = line.strip()

        if line.startswith('Pickup.Create'):
            match = re.search(r'^Pickup\.Create\((\$\d+), (#[A-Za-z\d_]+), (\d+), ([\-\d\.]+), ([\-\d\.]+), ([\-\d\.]+)\)$', line)
        elif line.startswith('032B:'):
            match = re.search(r'^032B: (\$\d+) = create_weapon_pickup (#[A-Za-z\d_]+) (\d+) ammo \d+ at ([\-\d\.]+) ([\-\d\.]+) ([\-\d\.]+)$', line)
        else:
            continue

        if not match:
            continue

        var, model, type_, x, y, z = match.groups()

        if not model in [
            '#INGRAMSL',
            '#M4',
            '#COLT45',
            '#BAT',
            '#LASER',
            '#PYTHON',
            '#ROCKETLA',
            '#CLEAVER',
            '#BOMB',
            '#SNIPER',
            '#M60',
            '#BUDDYSHOT',
            '#NITESTICK',
            '#TEC9',
            '#MACHETE',
            '#RUGER',
            '#GOLFCLUB',
            '#SHOTGSPA',
            '#CHROMEGUN',
            '#GRENADE',
            '#KNIFECUR',
            '#MINIGUN',
            '#UZI',
            '#BRASSKNUCKLE',
            '#FLAME',
            '#CHNSAW',
            '#KATANA',
            '#MOLOTOV',

            '#HEALTH',
            '#BODYARMOUR',
            '#ADRENALINE',
            '#BRIBE',
            '#KILLFRENZY',
        ]:
            continue

        items.append((model, f'{ x } { y } { z }'))

    items2 = []

    for line in PACKAGES.split('\n'):
        line = line.strip()

        if not line:
            continue

        x, y, z = line.split(' ')

        items2.append(('Package', f'{ x } { y } { z }'))

    assert len(items2) == 100

    items += items2

    del items2

    for model, coords in items:
        logLine = f'{ model } { coords }'

        chunk = []

        code.append(f'if  // { logLine }')
        code.append(f'    048C: is_any_pickup_at_coords { coords }')
        code.append('then')

        for c in logLine:
            code.append(f'    0AD9: write_formatted_text "%c" in_file FILE_HANDLE data { hex(ord(c)) }')

        code.append(f'    0AD9: write_formatted_text "%c" in_file FILE_HANDLE data 0xA')
        code.append('end\n')
        code.append('wait 0')

        code.append('\n'.join(chunk))

    code = '\n'.join(code)

    print(code)

# parseStaticPickups()

AREAS = '''
Downtown, 0, -1613.03, 413.128, 0.0, -213.73, 1677.32, 300.0, 1
Vice Point, 0, 163.656, -351.153, 0.0, 1246.03, 1398.85, 300.0, 1
Washington Beach, 0, -103.97, -930.526, 0.0, 1246.03, -351.153, 300.0, 1
Ocean Beach, 0, -253.206, -1805.37, 0.0, 1254.9, -930.526, 300.0, 1
Escobar International Airport, 0, -1888.21, -1779.61, 0.0, -1208.21, 230.39, 300.0, 1
Starfish Island, 0, -748.206, -818.266, 0.0, -104.505, -241.467, 300.0, 1
Prawn Island, 0, -213.73, 797.605, 0.0, 163.656, 1243.47, 300.0, 1
Leaf Links Golf Club, 0, -213.73, -241.429, 0.0, 163.656, 797.605, 300.0, 1
Junk Yard, 1, -1396.76, -42.9113, 0.0, -1208.21, 230.39, 300.0, 1
Viceport, 0, -1208.21, -1779.61, 0.0, -253.206, -898.738, 300.0, 1
Little Havana, 0, -1208.21, -898.738, 0.0, -748.206, -241.467, 300.0, 1
Little Haiti, 0, -1208.21, -241.467, 0.0, -578.289, 412.66, 300.0, 1
'''

def findMarkerVars ():
    lines = MAIN_SCM.split('\n')
    coordMap = {}

    for line in lines:
        line = line.strip()

        if line.startswith('Pickup.Create'):
            match = re.search(r'^Pickup\.Create\((\$\d+), (#[A-Za-z\d_]+), (\d+), ([\-\d\.]+), ([\-\d\.]+), ([\-\d\.]+)\)$', line)
        elif line.startswith('032B:'):
            match = re.search(r'^032B: (\$\d+) = create_weapon_pickup (#[A-Za-z\d_]+) (\d+) ammo \d+ at ([\-\d\.]+) ([\-\d\.]+) ([\-\d\.]+)$', line)
        else:
            continue

        if not match:
            continue

        var, model, type_, x, y, z = match.groups()

        key = f'{ model } { x } { y } { z }'

        coordMap[key] = [ var, int(type_, 10) ]

    # ----------------------------------

    lines = PRICES_AND_NAMES.split('\n')

    pan = {}

    for line in lines:
        line = line.strip()

        if not line:
            continue

        model, price, name = [ v.strip() for v in line.split(' - ') ]

        if price == 'NO':
            price = None
        else:
            price = int(price, 10)

        pan[model] = [ name, price ]

        print(model, price, name)

    # ----------------------------------

    lines = AREAS.split('\n')

    areas = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        items = [ v.strip() for v in line.split(',') ]

        areas.append([
            items[0],
            float(items[2]),
            float(items[3]),
            float(items[5]),
            float(items[6]),
        ])

    # ----------------------------------

    lines = ALL_USEFUL_PICKUPS.split('\n')

    packageCount = 1

    for origLine in lines:
        line = origLine.strip()

        if not line or line[0] != '#':
            print(origLine)
            continue

        parts = line.split(' | ')

        assert len(parts) in [ 1, 2 ]

        if len(parts) == 1:
            line    = parts[0].strip()
            comment = ''
        else:
            line    = parts[0].strip()
            comment = parts[1].strip()

        if line.startswith('#Package'):
            var   = 'null'
            price = 'null'

            items = splitSpaces(line)

            x = items[1]
            y = items[2]
            z = items[3]

            model = 'null'
            name  = f'Package #{ packageCount }'

            packageCount += 1
        else:
            items = splitSpaces(line)

            model = items[0]
            x     = items[1]
            y     = items[2]
            z     = items[3]

            key = f'{ model } { x } { y } { z }'

            var, type_ = coordMap[key]

            name, price = pan[model]

            if type_ != 1:
                price = 'null'

        coordX = float(x)
        coordY = float(y)
        coordZ = float(z)

        areaName2 = 'null'

        for areaName, x1, y1, x2, y2 in areas:
            if coordX >= x1 and coordY >= y1 and coordX <= x2 and coordY <= y2:
                areaName2 = areaName
                break

        print(f'{areaName2} | {var:<5} | {price:>5} | { name } | { model } | { x } | { y } | { z } | { comment }')


# findMarkerVars()

'''
$1850 #TOPFUN -1235.171 -1235.171 14.77
$1859 #TOPFUN 307.9 1254.6 27.5
$1851 #TOPFUN 718.465 701.3998 12.394

$1835 #PIZZABOY 413.8 97.7 10.5

$1995 #SPARROW -569.1451 851.0923 22.8402
$1996 #SPARROW 28.4463 -1311.761 16.4712
$1997 #SPARROW 375.845 332.9194 11.5155
$1998 #SPARROW -886.5938 236.5693 13.9773

$1986 #SANCHEZ  -425.8 1407.0 9.8
$1846 #LANDSTAL -426.0 1412.5 10.5
$1838 #PCJ600   507.4 -308.8 12.8
$1837 #STALLION 127.0 -1158.0 32.0

---

RC Raider Pickup (#TOPFUN)      0x974B94 (time)
RC Baron Race (#TOPFUN)         0x974B8C (time)
RC Bandit Race (#TOPFUN)        0x974B90 (time)

Pizza Boy (#PIZZABOY)           0x978780 (count)

Downtown Chopper Checkpoint     0x974BB0 (time)
Ocean Beach Chopper Checkpoint  0x974BB4 (time)
Vice Point Chopper Checkpoint   0x974BB8 (time)
Little Haiti Chopper Checkpoint 0x974BBC (time)

Trial By Dirt (#SANCHEZ)        0x974BC4 (time)
Test Track (#LANDSTAL)          0x974BC8 (time)
PCJ Playground (#PCJ600)        0x974BC0 (time)
Cone Crazy (#STALLION)          0x974BCC (time)
'''

# $795 '-1487.781 -1044.546 18.707',  '-1479.985352 -1044.624390 14.944997',
# $796 '-1352.695 -755.212 28.673',   '-1352.745483 -726.111389 14.867734',
# $797 '-1216.49 -911.833 19.0',      '-1223.269897 -913.997742 14.964717',
# $798 '-1252.139 -1054.685 22.016',  '-1264.058472 -1064.394409 14.867970',
# $799 '-1551.685 -1075.674 19.121',  '-1559.473511 -1078.058472 14.868018',
# $800 '-1595.712 -1272.881 19.068',  '-1602.965576 -1275.311890 14.905317',
# $801 '-1553.337 -1230.952 17.194',  '-1550.612305 -1228.528076 14.868028',
# $802 '-1340.022 -998.257 19.115',   '-1331.907349 -998.485596 14.924657',
# $803 '24.721 897.801 25.103',       '35.706345 895.109619 20.902271',
# $804 '317.2051 -223.2012 42.3731',  '322.956909 -273.155029 36.024715',
# $805 '-674.345 1162.422 29.916',    '-674.323303 1130.241821 11.289219',
# $806 '-529.84 830.062 98.717',      '-530.028137 824.362122 97.510437',
# $807 '-839.022 1153.526 31.94',     '-839.065308 1134.957886 25.357754',
# $808 '-312.447 1109.196 47.741',    '-306.743256 1121.386841 41.748192',
# $809 '-1011.583 -30.098 15.181',    '-1014.422180 -23.761742 11.110842',
# $810 '-942.702 -114.506 15.181',    '-949.748047 -114.632866 11.024787',
# $811 '-900.789 260.804 15.915',     '-900.808960 267.521851 11.916437',
# $812 '-1041.895 -569.323 21.855',   '-1043.034424 -558.693481 17.172630',
# $813 '208.993 -963.672 19.967',     '201.526733 -963.553467 16.567635',
# $814 '46.115 -964.415 25.883',      '31.027618 -963.678223 21.772991',
# $815 '435.8542 -334.3212 15.8977',  '437.228119 -326.224854 10.580140',
# $816 '110.481 -1230.6 35.67',       '109.309067 -1231.879150 34.210484',
# $817 '7.435 -1245.895 17.752',      '7.480590 -1235.126221 10.543128',
# $818 '9.103 -1326.505 20.361',      '8.982981 -1317.943726 16.591671',
# $819 '-321.028 -1379.498 10.929',   '-320.987579 -1372.047241 8.313258',
# $820 '-321.028 -1276.589 10.929',   '-320.824097 -1269.507568 8.372373',
# $821 '218.05 -1152.0 12.84',        '217.616943 -1155.751465 10.922762',
# $822 '259.056 -945.833 12.84',      '260.124603 -942.133179 10.524857',
# $823 '444.5 -118.4 16.0',           '455.190643 -118.361557 10.614019',
# $824 '284.4732 -494.1143 16.0',     '292.462219 -499.245728 10.053788',
# $825 '370.79 -709.863 19.895',      '375.568665 -699.355896 10.949533',
# $826 '461.589 -522.23 18.931',      '464.839203 -507.189728 11.068032',
# $827 '454.105 -504.736 18.931',     '455.954590 -494.343933 11.040046',
# $828 '460.91 -383.362 14.222',      '462.058929 -377.084961 10.305201',
# $829 '259.041 -480.608 14.688',     '250.479141 -477.466156 11.960499',
# $830 '-346.818 -290.741 12.926',    '-351.363281 -290.697235 10.314652',

items = [
    '-1036.487793 -849.031860 13.085196',
    '479.6 -1718.5 15.6',
    '708.4 -498.2 12.3',
    '-213.0 -1647.1 13.1',
    '-368.4 -1733.2 11.6',
    '-104.3 -1600.3 10.4',
    '-234.7 -1082.6 13.6',
    '88.0 -991.7 19.1',
    '205.4 -888.9 12.1',
    '183.1 -652.9 10.8',
    '370.9 -469.5 13.8',
    '298.8 -278.5 11.9',
    '321.8 -774.3 22.8',
    '491.8 -45.3 10.0',
    '472.8 116.0 11.2',
    '379.6 212.9 11.3',
    '290.1 295.4 13.5',
    '470.9 1123.6 24.5',
    '407.6 1018.2 25.3',
    '561.6 1157.1 18.9',
    '891.8 873.8 16.4',
    '353.7 -564.3 56.4',
    '306.9 1177.5 17.4',
    '271.3 932.9 9.8',
    '328.7 717.2 22.8',
    '473.3 16.4 33.0',
    '352.5 282.2 19.6',
    '70.1 -479.6 13.6',
    '53.6 -446.5 7.6',
    '266.3 -249.9 36.1',
    '413.9 1217.4 18.4',
    '-172.4 -1341.3 3.9',
    '-233.1 -931.2 9.8',
    '69.7 -796.6 11.7',
    '107.5 -551.9 14.7',
    '233.9 -132.2 8.0',
    '424.5 89.3 11.3',
    '401.6 431.1 11.4',
    '193.9 678.8 12.9',
    '589.4 36.0 16.7',
    '519.9 -135.4 35.2',
    '-41.8 922.4 19.4',
    '-16.1 991.7 10.9',
    '60.7 916.5 10.8',
    '-68.9 1124.0 17.0',
    '82.7 1113.8 18.7',
    '70.5 599.3 14.5',
    '162.4 246.4 12.2',
    '43.1 -150.9 12.2',
    '-46.6 257.7 24.5',
    '43.4 -15.0 17.3',
    '-236.9 -588.1 10.3',
    '-519.0 -599.3 10.3',
    '-580.5 -422.6 19.8',
    '-310.4 -415.5 10.1',
    '-245.4 -323.8 10.2',
    '-246.9 1219.5 10.9',
    '-451.0 1286.6 12.6',
    '-764.3 1266.0 11.5',
    '-1550.1 1403.1 8.7',
    '-790.8 1119.4 9.8',
    '-451.5 1119.7 61.7',
    '-567.4 776.1 22.8',
    '-898.7 430.4 10.9',
    '-979.2 266.7 8.9',
    '-856.3 228.5 12.9',
    '-1072.5 351.7 11.2',
    '-1161.6 431.1 11.0',
    '-975.1 191.9 12.6',
    '-1033.4 44.0 11.1',
    '-994.0 -250.3 10.7',
    '-1104.9 -120.9 20.1',
    '-1131.6 -355.4 15.0',
    '-1195.2 -317.7 10.9',
    '-1093.7 -600.1 26.0',
    '-1179.9 -576.3 12.0',
    '-1018.2 -874.1 17.9',
    '-855.3 -631.8 11.3',
    '-1179.2 -718.8 22.8',
    '-802.9 -1184.6 11.1',
    '-620.8 -1342.4 16.3',
    '-1024.6 -1494.6 19.4',
    '-1090.2 -1199.2 11.2',
    '-829.2 -1461.0 12.6',
    '-1160.6 -1333.8 14.9',
    '-1369.3 -1255.7 18.2',
    '-1280.9 -1146.5 22.2',
    '-1773.8 -1053.2 14.8',
    '-1187.3 -1041.4 14.8',
    '-1477.3 -881.0 32.4',
    '-1561.8 -1059.5 14.8',
    '-1349.1 -1090.4 24.5',
    '-1567.3 -1055.5 21.3',
    '-1366.4 -928.0 20.8',
    '-1523.5 -819.1 14.8',
    '-1829.1 -887.6 14.8',
    '-1726.5 -419.2 14.8',
    '-1737.2 -299.2 14.8',
    '-1328.0 -537.1 13.9',
    '-1063.5 -965.5 14.8',
    '-1265.8 -1346.9 29.6',
]

offset = 0x821EEC

 


# for i, item in enumerate(items):
#     x, y, z = item.split(' ')

#     print(f'''
#     if
#         1@ == { i }
#     then 
#         // 0A8D: 17@ = read_memory 0x{offset:X} size 4 virtual_protect 1
#         // 0AD1: show_formatted_text_highpriority "%d. %f %f %f (%d)" TIME 10000 { i + 1 } { item } 17@
#         0AD1: show_formatted_text_highpriority "%d. %f %f %f" TIME 10000 { i + 1 } { item }
#         04E4: request_collision { x } { y } 
#         03CB: load_scene { item }
#         038B: load_all_models_now
#         wait 30
#         0055: set_player_coordinates $PLAYER_CHAR at { item }
#     end''')

#     offset += 4

# import struct
# nums = [ 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0 ]  # slot 7
# nums = [ 479.6, -1718.5, 15.6 ]
# nums = [ float(x) for x in '479.6 -1718.5 15.6'.split(' ') ]  # Block 8 Pickups 75504
# nums2 = struct.pack(f'<{ len(nums) }f', *nums)
# print(len(nums), formatHex(nums2))
# exit()

def findPatterns2 (data, pattern):
    result = []
    start  = 0

    while True:
        try:
            index = data.index(pattern, start)
        except:
            break

        result.append(index)

        start = index + len(pattern)

    return result

r'''
data = readBin(r"C:\Users\Berrigan\Documents\GTA Vice City User Files\GTAVCsf6.b")
pattern = b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'
indices = findPatterns2(data, pattern)

data = readBin(r"C:\Users\Berrigan\Documents\GTA Vice City User Files\GTAVCsf3.b")


# slot: 8, count: 9
# 101452 00 00 00 00 00 00 00 00 F4 06 00 00 03 9
# 105708 21 00 01 01 00 00 01 00 03 00 05 00 00 9
# 106100 00 00 00 00 05 00 00 00 00 00 80 3F 00 9

# slot: 5, count: 8
# 104420 00 00 80 3F 04 00 00 00 00 00 00 00 00 8
# 105652 4C 01 01 00 00 00 01 00 00 00 00 00 03 8
# 106044 00 00 00 00 04 00 00 00 00 00 80 3F 00 8
# 135252 28 00 33 00 0C 00 00 00 00 00 00 00 00 8
# 195680 28 00 33 00 0C 00 00 00 00 00 00 00 00 8

# slot: 3, count: 4

for index in indices:
    chunk = data[index:index + len(pattern) + 1]

    num = int.from_bytes(chunk, 'little')
    num = num.bit_count()

    if chunk[:12] != pattern and num == 4:
        print(index, formatHex(chunk), num)

# print(indices)
'''

r'''
class Matcher:
    def __init__ (self):
        self.datas  = None
        self.size   = None
        self.cursor = None

    def match (self, datas):
        self.datas  = datas
        self.size   = len(datas[0])
        self.cursor = 0

        while not self.isEnd():
            start = self.cursor
            bytez = self.getNext()

            if not self.areSame(bytez):
                self.showDiffs(start)

    def isEnd (self):
        return self.cursor >= self.size

    def getNext (self):
        if self.cursor >= self.size:
            return None

        bytez = [ d[self.cursor:self.cursor + 1] for d in self.datas ]

        self.cursor += 1

        return bytez

    def areSame (self, bytez):
        return len(set(bytez)) == 1

    def showDiffs (self, start):
        while True:
            bytez = self.getNext()

            if self.isEnd() or self.areSame(bytez):
                print(f'{ start }:')

                for data in self.datas:
                    bytez = data[start:self.cursor]

                    print(f'- { formatHex(bytez) }')

                print(' ')

                break

files = [
    [ 10,  r"C:\Users\Berrigan\Documents\GTA Vice City User Files\samples\GTAVCsf7_10.b" ],
    [ 11,  r"C:\Users\Berrigan\Documents\GTA Vice City User Files\samples\GTAVCsf7_11.b" ],
    [ 12,  r"C:\Users\Berrigan\Documents\GTA Vice City User Files\samples\GTAVCsf7_12.b" ],
    [ 30,  r"C:\Users\Berrigan\Documents\GTA Vice City User Files\samples\GTAVCsf7_30.b" ],
    [ 70,  r"C:\Users\Berrigan\Documents\GTA Vice City User Files\samples\GTAVCsf7_70.b" ],
    [ 100, r"C:\Users\Berrigan\Documents\GTA Vice City User Files\samples\GTAVCsf7_100.b" ],
]

for i, info in enumerate(files):
    info[1] = readBin(info[1])

Matcher().match([ f[1] for f in files ])
'''

PACKAGE_COORDS = [
    '479.6 -1718.5 15.6',
    '708.4 -498.2 12.3',
    '-213.0 -1647.1 13.1',
    '-368.4 -1733.2 11.6',
    '-104.3 -1600.3 10.4',
    '-234.7 -1082.6 13.6',
    '88.0 -991.7 19.1',
    '205.4 -888.9 12.1',
    '183.1 -652.9 10.8',
    '370.9 -469.5 13.8',
    '298.8 -278.5 11.9',
    '321.8 -774.3 22.8',
    '491.8 -45.3 10.0',
    '472.8 116.0 11.2',
    '379.6 212.9 11.3',
    '290.1 295.4 13.5',
    '470.9 1123.6 24.5',
    '407.6 1018.2 25.3',
    '561.6 1157.1 18.9',
    '891.8 873.8 16.4',
    '353.7 -564.3 56.4',
    '306.9 1177.5 17.4',
    '271.3 932.9 9.8',
    '328.7 717.2 22.8',
    '473.3 16.4 33.0',
    '352.5 282.2 19.6',
    '70.1 -479.6 13.6',
    '53.6 -446.5 7.6',
    '266.3 -249.9 36.1',
    '413.9 1217.4 18.4',
    '-172.4 -1341.3 3.9',
    '-233.1 -931.2 9.8',
    '69.7 -796.6 11.7',
    '107.5 -551.9 14.7',
    '233.9 -132.2 8.0',
    '424.5 89.3 11.3',
    '401.6 431.1 11.4',
    '193.9 678.8 12.9',
    '589.4 36.0 16.7',
    '519.9 -135.4 35.2',
    '-41.8 922.4 19.4',
    '-16.1 991.7 10.9',
    '60.7 916.5 10.8',
    '-68.9 1124.0 17.0',
    '82.7 1113.8 18.7',
    '70.5 599.3 14.5',
    '162.4 246.4 12.2',
    '43.1 -150.9 12.2',
    '-46.6 257.7 24.5',
    '43.4 -15.0 17.3',
    '-236.9 -588.1 10.3',
    '-519.0 -599.3 10.3',
    '-580.5 -422.6 19.8',
    '-310.4 -415.5 10.1',
    '-245.4 -323.8 10.2',
    '-246.9 1219.5 10.9',
    '-451.0 1286.6 12.6',
    '-764.3 1266.0 11.5',
    '-1550.1 1403.1 8.7',
    '-790.8 1119.4 9.8',
    '-451.5 1119.7 61.7',
    '-567.4 776.1 22.8',
    '-898.7 430.4 10.9',
    '-979.2 266.7 8.9',
    '-856.3 228.5 12.9',
    '-1072.5 351.7 11.2',
    '-1161.6 431.1 11.0',
    '-975.1 191.9 12.6',
    '-1033.4 44.0 11.1',
    '-994.0 -250.3 10.7',
    '-1104.9 -120.9 20.1',
    '-1131.6 -355.4 15.0',
    '-1195.2 -317.7 10.9',
    '-1093.7 -600.1 26.0',
    '-1179.9 -576.3 12.0',
    '-1018.2 -874.1 17.9',
    '-855.3 -631.8 11.3',
    '-1179.2 -718.8 22.8',
    '-802.9 -1184.6 11.1',
    '-620.8 -1342.4 16.3',
    '-1024.6 -1494.6 19.4',
    '-1090.2 -1199.2 11.2',
    '-829.2 -1461.0 12.6',
    '-1160.6 -1333.8 14.9',
    '-1369.3 -1255.7 18.2',
    '-1280.9 -1146.5 22.2',
    '-1773.8 -1053.2 14.8',
    '-1187.3 -1041.4 14.8',
    '-1477.3 -881.0 32.4',
    '-1561.8 -1059.5 14.8',
    '-1349.1 -1090.4 24.5',
    '-1567.3 -1055.5 21.3',
    '-1366.4 -928.0 20.8',
    '-1523.5 -819.1 14.8',
    '-1829.1 -887.6 14.8',
    '-1726.5 -419.2 14.8',
    '-1737.2 -299.2 14.8',
    '-1328.0 -537.1 13.9',
    '-1063.5 -965.5 14.8',
    '-1265.8 -1346.9 29.6',
]

PACKAGE_COORDS = [
    [ float(i) for i in x.split(' ') ]
    for x in PACKAGE_COORDS
]

pickupsFromSave = []

models = set()

class PuckupType (Enum):
    Weapon       = 1
    Money        = 2
    Info         = 3
    Health       = 4
    Adrenaline   = 5
    Armor        = 6
    Bribe        = 7
    Rampage      = 8
    LockedAsset  = 9
    AssetForSale = 10
    Clothes      = 11
    Package      = 12
    SaveTape     = 13

MODEL_ID_TO_NAME = {
    258: 'cellphone',
    259: 'brassknuckle',
    260: 'screwdriver',
    261: 'golfclub',
    262: 'nitestick',
    263: 'knifecur',
    264: 'bat',
    265: 'hammer',
    266: 'cleaver',
    267: 'machete',
    268: 'katana',
    269: 'chnsaw',
    270: 'grenade',
    271: 'teargas',
    272: 'molotov',
    273: 'missile',
    274: 'colt45',
    275: 'python',
    276: 'ruger',
    277: 'chromegun',
    278: 'shotgspa',
    279: 'buddyshot',
    280: 'm4',
    281: 'tec9',
    282: 'uzi',
    283: 'ingramsl',
    284: 'mp5lng',
    285: 'sniper',
    286: 'laser',
    287: 'rocketla',
    288: 'flame',
    289: 'M60',
    290: 'minigun',
    291: 'bomb',
    292: 'camera',
    293: 'fingers',
    294: 'minigun2',
    337: 'Money',
    365: 'info',
    366: 'health',
    367: 'adrenaline',
    368: 'bodyarmour',
    375: 'bribe',
    383: 'killfrenzy',
    406: 'property_locked',
    407: 'property_fsale',
    409: 'clothesp',
    410: 'package1',
    411: 'pickupsave',
}

MODEL_ID_TO_PICKUP_TYPE = {
    258: PuckupType.Weapon,
    259: PuckupType.Weapon,
    260: PuckupType.Weapon,
    261: PuckupType.Weapon,
    262: PuckupType.Weapon,
    263: PuckupType.Weapon,
    264: PuckupType.Weapon,
    265: PuckupType.Weapon,
    266: PuckupType.Weapon,
    267: PuckupType.Weapon,
    268: PuckupType.Weapon,
    269: PuckupType.Weapon,
    270: PuckupType.Weapon,
    271: PuckupType.Weapon,
    272: PuckupType.Weapon,
    273: PuckupType.Weapon,
    274: PuckupType.Weapon,
    275: PuckupType.Weapon,
    276: PuckupType.Weapon,
    277: PuckupType.Weapon,
    278: PuckupType.Weapon,
    279: PuckupType.Weapon,
    280: PuckupType.Weapon,
    281: PuckupType.Weapon,
    282: PuckupType.Weapon,
    283: PuckupType.Weapon,
    284: PuckupType.Weapon,
    285: PuckupType.Weapon,
    286: PuckupType.Weapon,
    287: PuckupType.Weapon,
    288: PuckupType.Weapon,
    289: PuckupType.Weapon,
    290: PuckupType.Weapon,
    291: PuckupType.Weapon,
    292: PuckupType.Weapon,
    293: PuckupType.Weapon,
    294: PuckupType.Weapon,
    337: PuckupType.Money,
    365: PuckupType.Info,
    366: PuckupType.Health,
    367: PuckupType.Adrenaline,
    368: PuckupType.Armor,
    375: PuckupType.Bribe,
    383: PuckupType.Rampage,
    406: PuckupType.LockedAsset,
    407: PuckupType.AssetForSale,
    409: PuckupType.Clothes,
    410: PuckupType.Package,
    411: PuckupType.SaveTape    
}

pickupLayout = {}

for filePath in [
    # r"C:\Users\Berrigan\Documents\GTA Vice City User Files\GTAVCsf7.b",
    # r"C:\Users\Berrigan\Documents\GTA Vice City User Files\GTAVCsf6.b"
    r"G:\Steam\steamapps\common\Grand Theft Auto Vice City\cleo\_misc\slot7_my_new_game_clean.b",
    r"G:\Steam\steamapps\common\Grand Theft Auto Vice City\cleo\_misc\slot6_downloaded_100p.b"
]:
    print('-' * 100)

    with openFile(filePath) as f:
        '''
        # Skip to Block 8 Pickups offset
        for i in range(8):
            size = f.u32()
            f.skip(size)

        blockSize = f.u32()

        assert blockSize == 17560

        subBlockSize = f.u32()

        assert subBlockSize == 0x4494
        '''

        baseOffset = f.tell()

        for i in range(336):
            # void CPickups::Save()

            # 12 - CVector - coords 
            # 4  - float   - revenue
            # 4  - i32     - pickup object entity
            # 4  - i32     - pickup extra object entity
            # 4  - u32     - quantity
            # 4  - u32     - timer
            # 2  - u16     - revenue rate
            # 2  - i16     - model index (ide)
            # 2  - u16     - index
            # 8  - char[8] - string to display in help box
            # 1  - u8      - type
            # 1  - bool    - isPickedUp
            # 1  - u8      - flags
            # 3  - char[3] - padding

            coordsOffset = f.tell() - baseOffset
            coords = f.f32(3)
            # coords = [ round(n, 5) for n in coords ]         

            f.skip(22)

            modelId = f.u16()

            f.skip(10)

            typeOffset = f.tell() - baseOffset
            type_ = f.u8()

            if abs(coords[0]) < 0.05 and abs(coords[1]) < 0.05 and abs(coords[2]) < 0.05 or type_ == 0 or modelId not in MODEL_ID_TO_PICKUP_TYPE:
                # if i not in pickupLayout:
                #     print(modelId, coords)
                continue

            isPickedUpOffset = f.tell() - baseOffset
            isPickedUp = f.u8()

            f.skip(4)

            # print(type_, coords)

            if i in pickupLayout:
                # assert pickupLayout[i]['modelId'] == modelId
                continue

            pickupLayout[i] = {
                'index':            i,
                'coords':           coords,
                'type':             MODEL_ID_TO_PICKUP_TYPE[modelId],
                'modelId':          modelId,
                'modelName':        MODEL_ID_TO_NAME[modelId],
                'inGameType':       type_,
                'coordsOffset':     coordsOffset,
                'typeOffset':       typeOffset,
                'isPickedUpOffset': isPickedUpOffset
            }

            print(toJson(pickupLayout[i]))

# print(toJson(pickupLayout))
exit()
print('-' * 100)

for i, coords in enumerate(PACKAGE_COORDS):
    found = None

    for coords2, coordsOffset, typeOffset, isPickedUpOffset in pickupsFromSave:
        if abs(coords[0] - coords2[0]) > 10:
            continue 

        if abs(coords[1] - coords2[1]) > 10:
            continue 

        if abs(coords[2] - coords2[2]) > 10:
            continue 

        found = f'{ coordsOffset } { typeOffset } { isPickedUpOffset }'

    assert found, coords

    print(found)

    PACKAGE_COORDS[i] = found

