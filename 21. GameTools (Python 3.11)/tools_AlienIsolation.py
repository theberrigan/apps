# Alien Isolation Tools

from sys import exit

from deps.utils import *
from deps.reader import *



GAME_DIR = r'G:\Steam\steamapps\common\Alien Isolation'
DATA_DIR = joinPath(GAME_DIR, 'DATA')

BML_SIGNATURE = b'xml\x00'

_tags = [
    'font',
    'language',
    'font_config',
]

_flags = []
_flagTags = {}

def parseBML (bmlPath):
    with openFile(bmlPath) as f:
        signature = f.read(4)

        if signature != BML_SIGNATURE:
            print('Wrong BML signature', signature)
            return

        isLastTag = False
        lastTag = None 

        for i in f.u32(658):
            isTagRead = False

            if i >= 2988 and i < f.getSize():
                f.seek(i)

                nums = []

                while True:
                    byte = f.u8()

                    if byte:
                        nums.append(str(byte))
                    else:
                        break

                print('    ' + ', '.join(nums))
            elif 2638 <= i <= 2982:
                f.seek(i)
                string = f.string()

                if string in _tags:
                    lastTag = string
                    isTagRead = True

                print('    ' + string)
            elif isLastTag:
                attrCount = i & 0xFF
                flags = i >> 8

                # hasAttrs = bool(flags & (1 << 1))  # ???
                hasNext = bool(flags & (1 << 2))
                hasChildren = bool(flags & (1 << 5))
 
                # assert hasChildren == (not (flags & 1))

                flags2 = flags & (219)

                for j in range(8):
                    bit = 1 << j
                    isSet = flags2 & bit

                    if isSet:
                        _flagTag = _flagTags[bit] = _flagTags.get(bit, {})
                        _flagTag[lastTag] = _flagTag.get(lastTag, 0) + 1

                if flags2 not in _flags:
                    _flags.append(flags2)

                print(f'--> { flags }; Has next: { hasNext }; Has children: { hasChildren }')
            else:
                print(i)

            isLastTag = isTagRead

        print(' ')
        print(f.tell())
        print('\n'.join(sorted([ f'{_f:8b} -- { _f }' for _f in _flags ])))
        print(toJson(_flagTags))



def parseBMLs (rootDir):
    for filePath in iterFiles(rootDir, True, [ '.bml' ]):
        # print(filePath)
        parseBML(filePath)


if __name__ == '__main__':
    # parseBMLs(DATA_DIR)
    parseBML(joinPath(DATA_DIR, 'FONT_CONFIG.BML'))
    # parseBML(joinPath(DATA_DIR, 'GBL_ITEM.BML'))

