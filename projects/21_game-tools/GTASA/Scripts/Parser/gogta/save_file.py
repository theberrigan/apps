import os, struct, math, sys, re, zlib, json

def readStruct (structFormat, descriptor):
    items = struct.unpack(structFormat, descriptor.read(struct.calcsize(structFormat)))
    return items[0] if len(items) == 1 else items


def getIndex (sequence, subSequence):
    try:
        return sequence.index(subSequence)
    except:
        return -1


def bytesToNullString (byteSeq):
    if not byteSeq:
        return ''

    nullIndex = getIndex(byteSeq, b'\x00')
    byteSeq = byteSeq[:nullIndex] if (nullIndex >= 0) else byteSeq

    return byteSeq.decode('ascii')

def parseSave ():
    # OFVIAC AUIFRVQS
    with open(r'C:\Users\Berrigan\Documents\GTA San Andreas User Files\GTASAsf1.b', 'rb') as f:
        structure = [
            ('signature',              '5s',   None),
            ('version',                'I',    None),
            ('saveName',               '100s', bytesToNullString),
            ('missionPack',            'B3x',  None),
            ('currentTown',            'I',    None),
            ('cameraCoordX',           'f',    None),
            ('cameraCoordY',           'f',    None),
            ('cameraCoordZ',           'f',    None),
            ('minuteLength',           'I',    None),
            ('weatherTimer',           'I',    None),
            ('gameMonth',              'B',    None),
            ('gameMonthDay',           'B',    None),
            ('gameHour',               'B',    None),
            ('gameMinute',             'B',    None),
            ('gameWeekday',            'B',    None),
            ('gameMonth2',             'B',    None),
            ('gameMonthDay2',          'B',    None),
            ('gameHour2',              'B',    None),
            ('gameMinute2',            'B',    None),
            ('timeCopyFlag',           'B',    bool),
            ('unk1',                   'H',    None),
            ('usedCheats',             'B3x',  bool),
            ('globalTimer',            'I',    None),  # -
            ('gameSpeed',              'f',    None),
            ('unk2',                   'f',    None),
            ('tickTime',               'f',    None),
            ('framesProcessed',        'I',    None),
            ('unk3',                   'H',    None),
            ('unk4',                   'H',    None),
            ('weatherId',              'H2x',    None),
            ('unk5',                   'I',    None),
            ('unk6',                   'I',    None),
            ('unk7',                   'I',    None),
            ('vehicleCamera',          'I',    None),
            ('onfootCamera',           'I',    None),
            ('currentInterior',        'I',    None),
            ('unk8',                   'B3x',    None),
            ('originalInteriorColor',  'I',    None),
            ('interiorColorFlag',      'B3x',    None),
            ('unk9',                   'f',    None),
            ('changedInteriorColor',   'I',    None),
            ('unk10',                  'I',    None),
            ('riotMode',               'B',    None),
            ('unk11',                  'B2x',    None),
            ('maxWantedLevel',         'I',    None),
            ('maxChaos',               'I',    None),
            ('unk12',                  'B',    None),
            ('isGerman',               'B',    None),
            ('censorFlag',             'B',    None),
            ('cinematicCameraHelp',    'B',    None),
            ('wYear',                  'H',    None),
            ('wMonth',                 'H',    None),
            ('wDayOfWeek',             'H',    None),
            ('wDay',                   'H',    None),
            ('wHour',                  'H',    None),
            ('wMinute',                'H',    None),
            ('wSecond',                'H',    None),
            ('wMilliseconds',          'H',    None),
            ('mapTargetMarker',        'I',    None),
            ('vehicleStealingHelp',    'B',    None),
            ('taxisHaveNitro',         'B',    None),
            ('prostitutesPayYou',      'Bx',   None),
        ]

        # f.seek(math.ceil(f.tell() / boundry) * boundry)
        structFormat = '<' + ''.join([ item[1] for item in structure ])

        data = {}

        for i, value in enumerate(readStruct(structFormat, f)):
            key, _, parseFunc = structure[i]

            if parseFunc:
                value = parseFunc(value)

            data[key] = value

        print(data)

        print(f.tell())

parseSave()

'''
items = [
    (0x0000,  'dword'    ,   "version ID (checksum of a string describing the time of compilation)[1]"),
    (0x0004,  'char_100',    "save name (long names are truncated on the save/load screen)[2]"),
    (0x0068,  'byte'     ,   "current mission pack"),
    (0x0069,  'byte_3'  ,    "(Align)"),
    (0x006C,  'dword'    ,   "current town (island) (used when a replay playback is started/finished)"),
    (0x0070,  'float_3' ,    "camera coordinates (x,y,z)"),
    (0x007C,  'dword'    ,   "length (ms) of in-game minute"),
    (0x0080,  'dword'    ,   "weather timer"),
    (0x0084,  'byte'     ,   "current in-game month"),
    (0x0085,  'byte'     ,   "current in-game month day"),
    (0x0086,  'byte'     ,   "game hour"),
    (0x0087,  'byte'     ,   "game minute"),
    (0x0088,  'byte'     ,   "weekday"),
    (0x0089,  'byte'     ,   "current in-game month (copy)"),
    (0x008A,  'byte'     ,   "current in-game month day (copy)"),
    (0x008B,  'byte'     ,   "game hour (copy)"),
    (0x008C,  'byte'     ,   "game minute (copy)"),
    (0x008D,  'byte'     ,   "Boolean: time copy flag[3]"),
    (0x008E,  'word'     ,   "(unknown)"),
    (0x0090,  'byte'     ,   "Boolean: has ever cheated flag"),
    (0x0091,  'byte_3'  ,    "(Align)"),
    (0x0094,  'dword'    ,   "global timer"),
    (0x0098,  'float'    ,   "game speed"),
    (0x009C,  'float'    ,   "(unknown)"),
    (0x00A0,  'float'    ,   "tick time (time of an iteration of the major game loop)"),
    (0x00A4,  'dword'    ,   "number of the frames processed from the beginning of the game"),
    (0x00A8,  'word'     ,   "(unknown)"),
    (0x00AA,  'word'     ,   "(unknown)"),
    (0x00AC,  'word'     ,   "weather ID"),
    (0x00B0,  'dword'    ,   "(unknown)"),
    (0x00B4,  'dword'    ,   "(unknown)"),
    (0x00B8,  'dword'    ,   "(unknown)"),
    (0x00BC,  'dword'    ,   "vehicle camera view (opcode 09AD)"),
    (0x00C0,  'dword'    ,   "onfoot camera view"),
    (0x00C4,  'dword'    ,   "current interior"),
    (0x00C8,  'byte'     ,   "(unknown)"),
    (0x00CC,  'dword'    ,   "original interior color (?)"),
    (0x00D0,  'byte'     ,   "interior color flag (?)"),
    (0x00D4,  'float'    ,   "(unknown)"),
    (0x00D8,  'dword'    ,   "changed interior color (?)"),
    (0x00DC,  'dword'    ,   "(unknown)"),
    (0x00E0,  'byte'     ,   "Boolean: riot mode flag (opcode 06C8)"),
    (0x00E1,  'byte'     ,   "(unknown)"),
    (0x00E4,  'dword'    ,   "max wanted level (opcode 01F0)"),
    (0x00E8,  'dword'    ,   "max chaos[4]"),
    (0x00EC,  'byte'     ,   "(unknown)"),
    (0x00ED,  'byte'     ,   "is german lang (?) (opcode 040C)"),
    (0x00EE,  'byte'     ,   "censore flag[5]"),
    (0x011C,  'byte'     ,   "times left to display a cinematic camera help[6]"),
    (0x011E,  'word'     ,   "SYSTEMTIME wYear"),
    (0x0120,  'word'     ,   "SYSTEMTIME wMonth"),
    (0x0122,  'word'     ,   "SYSTEMTIME wDayOfWeek"),
    (0x0124,  'word'     ,   "SYSTEMTIME wDay"),
    (0x0126,  'word'     ,   "SYSTEMTIME wHour"),
    (0x0128,  'word'     ,   "SYSTEMTIME wMinute"),
    (0x012A,  'word'     ,   "SYSTEMTIME wSecond"),
    (0x012C,  'word'     ,   "SYSTEMTIME wMilliseconds"),
    (0x0130,  'dword'    ,   "Player target marker handle (handle of the red target icon in the map menu)"),
    (0x0134,  'byte'     ,   "Boolean: the vehicle stealing help was shown[7]"),
    (0x0135,  'byte'     ,   "Boolean: All taxis have nitro (opcode 0572 flag)"),
    (0x0136,  'byte'     ,   "Boolean: Prostitutes pay you (opcode 0A3D flag)"),
    (0x0137,  'byte'     ,   "(Align)"),
]

dataTypes = {
    'char': 1,
    'byte': 1,
    'word': 2,
    'dword': 4,
    'float': 4,
}

prevOffset = 0

for offset, dataFormat, desc in items:
    dataFormat = dataFormat.split('_')
    dataType = dataFormat[0]
    mult = int(dataFormat[1]) if len(dataFormat) == 2 else 1

    if offset != prevOffset:
        print(f'0x{offset :04X}', desc)
        break

    prevOffset += dataTypes[dataType] * mult

'''