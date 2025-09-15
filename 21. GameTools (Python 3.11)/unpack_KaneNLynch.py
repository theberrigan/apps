import os, struct, zlib, math


def align (descriptor, alignment):
    descriptor.seek(math.ceil(descriptor.tell() / alignment) * alignment)


def readNullTerminatedString (descriptor, alignment = 0):
    string = b''

    while True:
        byte = descriptor.read(1)

        if byte == b'\x00':
            break
        else:
            string += byte

    if alignment > 0:
        align(descriptor, alignment)

    return string.decode('utf-8')


def printTable (header, items):
    print('{} items\n'.format(len(items)))

    maxLengths = [ len(item) for item in header ]

    for row in items:
        for i, value in enumerate(row):
            maxLengths[i] = max(maxLengths[i], len(str(value)))

    header = [ item.ljust(maxLengths[i]) for i, item in enumerate(header) ]
    sep = '-+-'.join([ '-' * len(item) for item in header ])

    print(sep)
    print(' | '.join(header))
    print(sep)

    for row in items:
        rowValues = []

        for i, value in enumerate(row):
            if type(value) == int:
                rowValues.append(str(value).rjust(maxLengths[i]))
            else:
                rowValues.append(str(value).ljust(maxLengths[i]))

        print(' | '.join(rowValues))

    print(sep)



# https://audiocoding.ru/articles/2008-05-22-wav-file-structure/
def parseWavFile (wavFilePath): 
    wavFileBasePath, ext = os.path.splitext(wavFilePath)

    if ext.lower() != '.wav':
        raise Exception('Not a WAV file: {}'.format(wavFilePath))

    if not os.path.isfile(wavFilePath):
        raise Exception('WAV file doesn\'t exist: {}'.format(wavFilePath))

    whdFilePath = '{}.whd'.format(wavFileBasePath)

    if not os.path.isfile(whdFilePath):
        raise Exception('WHD file doesn\'t exist: {}'.format(whdFilePath))

    audioItems = []

    with open(whdFilePath, 'rb') as whd:
        contentSize, fileSize, unk1, unk2 = struct.unpack('<4I', whd.read(16))

        _tableHeader = ('_startOffset', 'unk1', 'entryOffset', 'unk3_1', 'unk3_2', 'unk4', 'unk5', 'unk6', 'wavSize', 'unk7', 'wavOffset', 'unk9', 'unk10', 'unk11', 'unk12', 'unk13', 'unk14', 'unk15', 'filePath')
        _tableItems = []

        while whd.tell() < contentSize:
            _startOffset = whd.tell()

            try:
                filePath = readNullTerminatedString(whd, 16)
            except:
                break

            unk1, entryOffset, unk3_1, unk3_2, unk4, unk5, unk6, wavSize, unk7, wavOffset, unk9, unk10, unk11, unk12, unk13, unk14, unk15 = struct.unpack('<2I2H13I', whd.read(64))

            audioItems.append({
                'wavOffset': wavOffset,
                'wavSize': wavSize,
                'filePath': filePath
            })

            _tableItems.append(( _startOffset, unk1, entryOffset, unk3_1, unk3_2, unk4, unk5, unk6, wavSize, unk7, wavOffset, unk9, unk10, unk11, unk12, unk13, unk14, unk15, filePath ))

            # print('Offset: {} Size: {}'.format(wavOffset, wavSize))

        printTable(_tableHeader, _tableItems)

    # print(audioItems)
    #                              wavSiz   wavOffse
    # 0 8352 1 128 32000 16 281502 281502 1 53964800 140751 2 3452816845 4 288 0 0 0
    # 0 8352 1 192 32000 16 293114 293114 1 21882112 146557 2 3452816845 4 288 0 0 0
    # 0 8352 1 192 32000 16 282078 282078 1 20958976 141039 2 3452816845 4 288 0 0 0
    # 0 8352 1 192 32000 16 259462 259462 1 21785344 129731 2 3452816845 0   0 0 0 0
    # 0 8352 1 192 32000 16 241016 241016 1 21847296 120508 2 3452816845 4 240 0 0 0


def parseSndFile (filePath):
    with open(filePath, 'rb') as f:
        contentSize, fileSize, unk1, unk2 = struct.unpack('<4I', f.read(16))

        f.seek(contentSize, 1)
        baseOffset = f.tell()

        data = f.read()

        uintCount = int(len(data) / 4)

        data = struct.unpack('<{}I'.format(uintCount), data)

        for i, uint in enumerate(data):
            print('{}: {}'.format(baseOffset + 4 * i, uint))

        # for offset, itemCount in [ (0x4a0, 6), (0xb60, 14) ]:
        #     f.seek(offset)
        #     for i in range(itemCount):
        #         str1 = readNullTerminatedString(f, 16)
        #         str2 = readNullTerminatedString(f, 16)
        #         str3 = readNullTerminatedString(f, 16)
        #         # print(str1)
        #         # print(str2)
        #         # print(str3)
        #         print(struct.unpack('<IHHIIIIIIIIIHHIIHHHHHHIII', f.read(16 * 5)))
        #     print('-' * 100)



filePath1 = './Scenes/AllLevels/Loader_Sequence.WAV'
filePath2 = './Scenes/KaneAndLynch.WAV'
# parseWavFile(filePath1)
# parseSndFile('./Scenes/AllLevels/Loader_Sequence.SND')
parseSndFile('./Scenes/CutScenes/M07/M07_A_Funeral.SND')