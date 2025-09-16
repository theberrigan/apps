import sys
import re

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from bfw.utils import *
from bfw.registry import Registry, HKEY_CURRENT_USER, REG_TYPE_DWORD
from bfw.types.enums import Enum




U32_MAX = 0xFFFFFFFF


class DeviceType (Enum):
    No       = U32_MAX
    Mouse    = 0
    Keyboard = 1


# DeviceType.Mouse
MOUSE_KEYS = {
    U32_MAX: '',  # no button
    0:  'LMB',
    1:  'RMB',
    2:  'MMB',
    3:  'MB4',
    4:  'MB5',
    # 5-7
    8:  'MWHEEL_UP',
    9:  'MWHEEL_DOWN',    
}


# DeviceType.Keyboard
KEYBOARD_KEYS = {
    U32_MAX: '',  # no button
    2:  '1',
    3:  '2',
    4:  '3',
    5:  '4',
    6:  '5',
    7:  '6',
    8:  '7',
    9:  '8',
    10: '9',
    11: '0',
    12: '-',
    13: '=',
    14: 'BACKSPACE',  # TODO: ?
    15: 'TAB',
    16: 'Q',
    17: 'W',
    18: 'E',
    19: 'R',
    20: 'T',
    21: 'Y',
    22: 'U',
    23: 'I',
    24: 'O',
    25: 'P',
    26: '[',
    27: ']',
    28: 'ENTER',
    29: 'LCTRL',      # sneak
    30: 'A',
    31: 'S',
    32: 'D',
    33: 'F',
    34: 'G',          # activateprop
    35: 'H',
    36: 'J',
    37: 'K',
    38: 'L',
    39: ';',
    40: '\'',
    41: '`',          # (tilda)
    42: 'LSHIFT',     # run, precisionaim
    43: '\\',
    44: 'Z',          # dropitem, previous_ammo
    45: 'X',          # use2, surrender, next_ammo
    46: 'C',
    47: 'V',
    48: 'B',
    49: 'N',
    50: 'M',
    51: ',',
    52: '.',
    53: '/',
    54: 'RSHIFT',
    55: 'NUM_*',
    56: 'LALT',       # inventory
    57: 'SPACE',      # cover
    58: 'CAPS_LOCK',  # toggle_placement
    59: 'F1',         # TODO: ?
    60: 'F2',
    61: 'F3',
    62: 'F4',
    63: 'F5',
    64: 'F6',
    65: 'F7',
    66: 'F8',
    67: 'F9',
    68: 'F10',
    69: 'NUM_LOCK',
    70: 'SCROLL_LOCK',
    71: 'NUM_7',
    72: 'NUM_8',
    73: 'NUM_9',
    74: 'NUM_-',
    75: 'NUM_4',
    76: 'NUM_5',
    77: 'NUM_6',
    78: 'NUM_+',
    79: 'NUM_1',
    80: 'NUM_2',
    81: 'NUM_3',
    82: 'NUM_0',
    83: 'NUM_DEL',
    # 84-86
    87: 'F11',
    88: 'F12',
    156: 'NUM_ENTER',
    157: 'RCTRL',
    181: 'NUM_/',
    183: 'PRINT_SCREEN',
    184: 'RALT',
    197: 'PAUSE',
    199: 'HOME',
    200: 'ARROW_UP',
    201: 'PAGE_UP',
    203: 'ARROW_LEFT',
    205: 'ARROW_RIGHT',
    207: 'END',
    208: 'ARROW_DOWN',
    209: 'PAGE_DOWN',
    210: 'INSERT',
    211: 'DELETE',
    221: 'CTX',
}


ACTIONS = {
    'move_up':          'Идти вперед',                 # W
    'move_down':        'Идти назад',                  # S
    'move_left':        'Идти влево',                  # A
    'move_right':       'Идти вправо',                 # D
    'use':              'Взаимодействовать',           # E
    'use2':             'Ловкие действия',             # X
    'pickup':           'Взять',                       # F
    'cover':            'Укрытие',                     # SPACE
    'dragbody':         'Тащить тело',                 # B
    'melee':            'Ближний бой',                 # MB5
    'activateprop':     'Использовать предмет',        # G, MB4
    'takedisguise':     'Маскировка',                  # T
    'run':              'Бежать',                      # LSHIFT
    'aim':              'Целиться',                    # RMB
    'shoot':            'Выстрелить',                  # LMB
    'reload':           'Перезарядить',                # R
    'instinct':         'Инстинкт',                    # Q
    'camswitch':        'Позиция камеры',              # V
    'sneak':            'Присесть',                    # LCTRL
    'holster':          'Убрать оружие',               # H, MMB
    'precisionaim':     'Точное прицеливание',         # LSHIFT
    'zoomin':           'Приблизить',                  # MWHEEL_UP
    'zoomout':          'Отдалить',                    # MWHEEL_DOWN
    'dropitem':         'Бросить предмет',             # Z
    'inventory':        'Снаряжение',                  # I, LALT
    'surrender':        'Сдаться',                     # X
    'toggle_placement': 'Размещение предмета',         # CAPS_LOCK
    'next_ammo':        'Следующий тип боеприпасов',   # X
    'previous_ammo':    'Предыдущий тип боеприпасов',  # Z
    'walkslow':         'Медленно идти',               # NUM_*
    'concealretrieve':  'Достать из/спрятать в кейс',  # Y
    'notebook_map':     'Открыть карту',               # TAB
}


class Action:
    @classmethod
    def parse (cls, action):
        name, index, suffix = action.rsplit('_', maxsplit=2)

        index = int(index, 10)

        assert action.islower()
        assert index in [ 0, 1 ]

        return name, index, suffix

    @classmethod
    def create (cls, action, value):
        name, index, suffix = cls.parse(action)

        item = cls()

        item.fullName = action
        item.name     = name
        item.index    = index
        item.suffix   = suffix

        if suffix == 'dev':
            item.device = value
        elif suffix == 'nr':
            item.code = value

        return item

    def __init__ (self):
        self.fullName = None
        self.name     = None
        self.index    = None
        self.suffix   = None
        self.code     = None
        self.device   = None


def fromReg (gameName):
    params = {}

    with Registry(HKEY_CURRENT_USER) as reg:
        key = reg.openKey(f'SOFTWARE/IO Interactive/{ gameName }/Input')

        for item in key.iterValues():
            assert item.type == REG_TYPE_DWORD

            param = Action.create(item.name, item.value)

            params[param.fullName] = param

    actions = []

    for param in params.values():
        if param.suffix == 'dev':
            continue

        param2 = params[f'{ param.name }_{ param.index }_dev']

        param.device = param2.device

        actions.append(param)

    return actions


def fromRegFile (filePath):
    text = readText(filePath, encoding='utf-16le')

    lines = text.split('\n')

    wasSection = False

    actions = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if not wasSection:
            if line == r'[HKEY_CURRENT_USER\SOFTWARE\IO Interactive\HITMAN3\Input]':
                wasSection = True

            continue

        match = re.match(r'^"([a-z\d_]+)"=dword:([\da-f]{8})$', line, flags=re.I)

        assert match, line

        name = match.group(1)
        code = int(match.group(2), 16)

        actions.append(Action.create(name, code))

    return actions


def printReg (gameName):
    actions = fromReg(gameName)
    actions = [ a for a in actions ]

    actions.sort(key=lambda i: i.code)

    pjp(actions)

    # for action in actions:
    #     print(f'{CODE_TO_NAME[action.code]:<16} {action.name}')


def main ():
    printReg('HITMAN3')
    printReg('HITMAN')
    # pjp(fromRegFile(r'C:\Users\Berrigan\Desktop\1.reg'))



if __name__ == '__main__':
    main()