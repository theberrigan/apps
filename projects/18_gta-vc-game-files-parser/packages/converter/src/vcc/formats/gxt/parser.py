import re
from typing import List, Union

from ...common import bfw
from ...common.types import *
from ...common.consts import *

from .consts import *
from .types import *

from bfw.utils import *
from bfw.reader import *



# TODO: is it really UTF-16?
# TODO: "^" in messages



# https://www.grandtheftwiki.com/GXT
# https://gtamods.com/wiki/GXT
class GXTReader:
    @classmethod
    def fromFile (cls, filePath : str, parse : bool = False) -> dict:
        if not isFile(filePath):
            raise OSError(f'File does not exist: { filePath }')

        rawData = readBin(filePath)
        reader  = MemReader(rawData, filePath)

        return cls().read(reader, parse)

    def read (self, f : Reader, parse : bool = False) -> dict:
        blockName = f.read(4)
        blockSize = f.i32()

        assert blockName == b'TABL', 'Expected TABL block name'
        assert blockSize % GXT_TABLE_ENTRY_SIZE == 0, f'TABL block size expected to be a multiple of { GXT_TABLE_ENTRY_SIZE }'

        blockEntryCount = blockSize // GXT_TABLE_ENTRY_SIZE

        sections : List[Any] = [ None ] * blockEntryCount

        for i in range(blockEntryCount):
            sectionName = f.string(8).upper()
            keysOffset  = f.u32()

            assert i > 0 or sectionName == 'MAIN', 'First block name expected to be MAIN'

            sections[i] = {
                'name': sectionName,
                'keysOffset': keysOffset,
                'messages': {}
            }

        for entry in sections:
            f.seek(entry['keysOffset'])

            del entry['keysOffset']

            # Skip section name duplicate for non-MAIN sections
            if entry['name'] != 'MAIN':
                f.skip(8)

            blockName = f.read(4)
            blockSize = f.i32()

            assert blockName == b'TKEY', 'Expected TKEY block name'
            assert blockSize % GXT_TKEY_ENTRY_SIZE == 0, f'TKEY block size expected to be a multiple of { GXT_TKEY_ENTRY_SIZE }'

            blockEntryCount = blockSize // GXT_TKEY_ENTRY_SIZE

            for i in range(blockEntryCount):
                messageOffset = f.u32()
                messageKey    = f.string(8)

                entry['messages'][messageKey] = messageOffset

            blockName = f.read(4)
            blockSize = f.i32()

            assert blockName == b'TDAT', 'Expected TDAT block name'
            assert blockSize > 0, 'Expected non-empty TDAT block'

            messagesStart = f.tell()

            for messageKey, messageOffset in entry['messages'].items():
                f.seek(messagesStart + messageOffset)

                message = f.string(encoding='utf-16-le')

                if parse:
                    message = self.parseMessage(message)

                entry['messages'][messageKey] = message

        return { s['name']: s['messages'] for s in sections }

    def parseMessage (self, message : str) -> List[Union[int, str]]:
        # message = 'Press the ~h~~k~~PED_ANSWER_PHONE~~w~ to answer your cell ~B~phone~B~.'
        matches = list(re.finditer(GXT_TOKEN_REGEX, message))

        if not matches:
            return [ message ]

        stream      = []
        messageSize = len(message)
        strStart    = 0
        maxIndex    = len(matches) - 1
        keyTokenEnd = None

        for i, match in enumerate(matches):
            tokenValue = match.group(1).strip('~')
            tokenStart = match.start()
            tokenEnd   = match.end()

            if strStart < tokenStart:
                stream.append(message[strStart:tokenStart])

            strStart = tokenEnd

            token = GXT_TOKENS.get(tokenValue)

            if token:
                if token == GXTAction.Button:
                    keyTokenEnd = tokenEnd
                else:
                    stream.append(token)
            else:
                commandId = GXT_COMMAND_NAME_TO_ID.get(tokenValue)

                if not commandId:
                    raise ValueError(f'Unknown token: { tokenValue }')

                if keyTokenEnd != tokenStart:
                    raise ValueError(f'~{ tokenValue }~ must immediately follow the ~k~')

                keyTokenEnd = None

                stream.append((commandId << 16) | GXTAction.Button)

            if i == maxIndex and strStart < messageSize:
                stream.append(message[strStart:messageSize])

        # print(message, toJson(stream, pretty=False))

        return stream



def _test_ ():
    for filePath in iterFiles(GAME_DIR, True, [ GXT_EXT ]):
        print(filePath)
        gxt = GXTReader.fromFile(filePath, True)
        # print(toJson(gxt))
        print(' ')



__all__ = [
    'GXTReader',

    '_test_',
]



if __name__ == '__main__':
    _test_()
