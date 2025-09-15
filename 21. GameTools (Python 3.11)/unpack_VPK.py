# Valve VPK Extractor

from deps.utils import *
from deps.reader import *



SCRIPT_DIR = getDirPath(getAbsPath(__file__))
GAME_DIR = r'G:\Steam\steamapps\common\Portal 2\portal2'

VPK_SIGNATURE   = b'\x34\x12\xAA\x55'
VPK_HEADER_SIZE = 4 * 3

# Portal 2 (VPK v1)
# https://developer.valvesoftware.com/wiki/VPK_File_Format
def unpack (filePath, outputDir):
    print('Unpacking', filePath)

    with openFile(filePath) as f:
        signature = f.read(4)

        if signature != VPK_SIGNATURE:
            print('It is not a VPK file')
            return

        version = f.u32()

        if version != 1:
            print(f'Unsupported VPK version: { version }')
            return

        threeSize = f.u32()

        # print(threeSize)

        fileSize = f.getSize()

        hasDirOnly = (VPK_HEADER_SIZE + threeSize) == fileSize

        # print(hasDirOnly)

        while True:
            ext  = f.string()

            if not ext:
                break

            while True:
                path = f.string()

                if not path:
                    break

                while True:
                    name = f.string()

                    if not name:
                        break

                    dataCRC     = f.u32()
                    preloadSize = f.u16()  # if > 0 the preload data follows this struct
                    pakIndex    = f.u16()  # if == 0x7fff the data follows this struct
                    dataOffset  = f.u32()  # if == 0x7fff then dataOffset is rel to the end of this struct, otherwise it is abs to the start of external pak file with pakIndex
                    dataSize    = f.u32()  # totalDataSize = preloadSize + dataSize
                    terminator  = f.u16()  # always 0xffff

                    assert terminator == 0xffff

                    dirEnd = f.tell()

                    data = b''

                    if preloadSize > 0:
                        data = f.read(preloadSize)

                    if pakIndex == 0x7fff:
                        absOffset = dirEnd + dataOffset
                    else:
                        absOffset = dataOffset


                    assert not(pakIndex == 0x7fff and preloadSize and dataSize)

                    if preloadSize and dataSize and pakIndex != 0x7fff:
                        relPath = f'{path}/{ name }.{ ext }'

                        if relPath == 'resource/basemodui_scheme.res':
                            # print(data.decode('utf-8')) 
                            pakFileName = joinPath(GAME_DIR, f'pak01_{pakIndex:03d}.vpk')

                            with openFile(pakFileName) as f2:
                                f2.seek(absOffset)
                                data = (data + f2.read(dataSize)).decode('utf-8')

                                print(data)

                            return

                            # print(relPath, hex(terminator), preloadSize, hex(pakIndex))





    #     if PreloadBytes:
    #         readPreloadData()


    #         unsigned int CRC; // A 32bit CRC of the file's data.
    # unsigned short PreloadBytes; // The number of bytes contained in the index file.

    # // A zero based index of the archive this file's data is contained in.
    # // If 0x7fff, the data follows the directory.
    # unsigned short ArchiveIndex;

    # // If ArchiveIndex is 0x7fff, the offset of the file data relative to the end of the directory (see the header for more details).
    # // Otherwise, the offset of the data from the start of the specified archive.
    # unsigned int EntryOffset;

    # // If zero, the entire file is stored in the preload data.
    # // Otherwise, the number of bytes stored starting at EntryOffset.
    # unsigned int EntryLength;

    # const unsigned short Terminator = 0xffff;


        # print(ext, path, name, hex(crc), preloadSize, hex(pakIndex), dataOffset, dataSize, hex(terminator))


        # itemCount = f.u32()
        # metas = []

        # for i in range(itemCount):
        #     pathSize = f.u32()
        #     itemPath = f.string(pathSize, 'cp1251')

        #     decompSize, compSize, offset, unk4, unk5, unk6 = f.struct('<6I')

        #     # assert compSize > 0, f'{ decompSize }, { compSize }' 
        #     assert unk4 == 0

        #     metas.append(ItemMeta(itemPath, decompSize, compSize, offset, unk4, unk5, unk6))

        # dataStart = f.u32()

        # for meta in metas:
        #     f.seek(dataStart + meta.offset)

        #     # print(dataStart, f.tell())
        #     # print(meta.path, meta.offset, meta.compSize, meta.decompSize)

        #     data = f.read(meta.compSize or meta.decompSize)

        #     if meta.compSize:
        #         data = decompressData(data)

        #     outputPath = getAbsPath(joinPath(outputDir, meta.path))

        #     print('\t', outputPath)

        #     createDirs(getDirPath(outputPath))

        #     with open(outputPath, 'wb') as f2:
        #         f2.write(data)


def unpackAll (rootDir, outputDir):
    for filePath in iterFiles(rootDir, False, [ '.vpk' ]):
        unpack(filePath, outputDir)


if __name__ == '__main__':
    unpack(joinPath(GAME_DIR, 'pak01_dir.vpk'), joinPath(GAME_DIR, '__auto_unpacked'))
    unpack(joinPath(GAME_DIR, '_custom', 'pak01_dir.vpk'), joinPath(GAME_DIR, '_custom', '__auto_unpacked'))

    # unpackAll(GAME_DIR, joinPath(GAME_DIR, '__extracted'))