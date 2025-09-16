import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from bfw.utils import *
from bfw.reader import *



FMOD_SAMPLES_DIR = r'C:\Projects\_Data_Samples\fmod'



# https://www.ietf.org/rfc/rfc3602.txt
# https://aluigi.altervista.org/search.php?src=fsbext
# https://heavyironmodding.org/wiki/FMOD
class FMod:
    def __init__ (self):
        pass

    @classmethod
    def fromFile (cls, filePath):
        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._read(f)

    @classmethod
    def fromBuffer (cls, data):
        with MemReader(data) as f:
            return cls._read(f)

    @classmethod
    def _read (cls, f):
        signature = f.read(4)

        assert signature in [ b'FSB4', b'FSB5' ]

# ----------------------------

def tmp_unpack ():
    for filePath in iterFiles(r'E:\PSP_GAME\USRDIR', True, [ '.arc' ]):
        print(filePath)

        with openFile(filePath) as f:
            signature = f.read(4)

            if signature != b'\x10\xFA\x00\x00':
                raise Exception('Signature check failed')

            itemCount     = f.u32()
            contentOffset = f.u32()
            zero1         = f.u32()

            assert zero1 == 0

            items = [ None ] * itemCount

            for i in range(itemCount):
                nameHash   = f.u32()
                offset     = f.u32()
                compSize   = f.u32()
                decompSize = f.u32()

                items[i] = (nameHash, offset, compSize, decompSize)

            for nameHash, offset, compSize, decompSize in items:
                # print(offset, compSize, decompSize)

                f.seek(offset)

                data = f.read(compSize)

                if decompSize > 0:
                    try:
                        data = decompressData(data)
                    except:
                        pass

                    # assert len(data) == decompSize

                if b'FSB4' in data:
                    print(offset)

                # if data[:4] in [ b'FSB4', b'FSB5' ]:
                #     print(offset)

def samples_fs ():
    for rootDir in [
        FMOD_SAMPLES_DIR,
        r'G:\Steam\steamapps\common\WormsXHD\Data\Audio\PC'
    ]:
        for filePath in iterFiles(rootDir, True, [ '.fsb' ]):
            yield (filePath, filePath)

def samples_DXMD ():
    gameDir = r'G:\Steam\steamapps\common\Deus Ex Mankind Divided'

    for filePath in iterFiles(gameDir, True, [ '.pc_fsb', '.pc_fsbm' ]):
        with openFile(filePath) as f:
            signature = f.read(4)

            assert signature in [ b'SBSF', b'MBSF' ]

            f.seek(12)

            fsbSize = f.u32()

            if signature == b'SBSF':
                fsbSize -= 16
                f.seek(40)
            elif signature == b'MBSF':
                f.seek(24)

            data = f.read(fsbSize)

            assert len(data) == fsbSize, filePath

        yield (filePath, data)

def _test_ ():
    providers = [
        (samples_fs, FMod.fromFile),
        (samples_DXMD, FMod.fromBuffer),
    ]

    for provideFn, readFn in providers:
        for filePath, source in provideFn():
            print(filePath)
            readFn(source)
            print(' ')


__all__ = [
    'FMod'
]



if __name__ == '__main__':
    # _test_()
    tmp_unpack()
