# Call of Juarez Gunslinger

import os
import re
import concurrent.futures

from sys import exit
from time import time
from zipfile import ZipFile
from threading import Event, Lock

# pip install pefile
import pefile

from deps.utils import *
from deps.reader import *



GAME_DIR = r'G:\Steam\steamapps\common\CoJ Gunslinger'
EXE_PATH = joinPath(GAME_DIR, 'CoJGunslinger.exe')

MAX_THREADS = os.cpu_count() or 4

# https://www.hexacorn.com/blog/2016/12/15/pe-section-names-re-visited/
# [ '.rdata', '.data', '.tls', '.text', '.rsrc', '.extra', '.reloc', '.generic' ]



def normalizeSectionName (name):
    name = re.sub(r'[^\x21-\x7e]+', '', name)
    name = '.' + (name or 'unknown').strip('.')

    return name.lower()

def findPassword (pakPath):
    def readGenericSection (f, offset, size):
        f.seek(offset)

        data = f.read(size)

        assert len(data) == size

        return ('.generic', offset, size, data)

    def getSectionPriority (name):
        sectionPriorities = [ '.rdata', '.data', '.tls', '.text', '.rsrc', '.extra', '.reloc', '.generic' ]

        try:
            return sectionPriorities.index(name)
        except:
            return len(sectionPriorities)

    def searchSection (pakPath, section, printLock, stopEvent):
        sectionName, sectionOffset, sectionSize, data = section
        sectionInfo = (sectionName, sectionOffset, sectionSize)
        defaultResult = False, (sectionInfo, None)

        print('Feature started for section:', sectionName, lock=printLock)

        minKeySize = 2
        maxKeySize = 32

        with ZipFile(pakPath) as pak:
            for baseOffset in range(0, max(0, sectionSize - minKeySize + 1)):
                for keySize in range(minKeySize, min(maxKeySize, sectionSize - baseOffset) + 1):
                    key = data[baseOffset:baseOffset + keySize]

                    try:
                        pak.open('data/car.scr', 'r', key).read()

                        return True, (sectionInfo, (key, baseOffset, keySize))
                    except:
                        pass

                    if stopEvent.is_set():
                        print('Feature cancelled', lock=printLock)
                        return defaultResult

        return defaultResult

    pe = pefile.PE(EXE_PATH)

    rawSections = []

    for section in pe.sections:
        name   = section.Name.decode('ascii').strip('\x00').lower()
        offset = section.PointerToRawData
        size   = section.SizeOfRawData
        data   = section.get_data()  # data[section.PointerToRawData:section.PointerToRawData + section.SizeOfRawData]

        rawSections.append((name, offset, size, data))

    rawSections.sort(key=lambda s: s[1])

    sections   = []
    lastOffset = 0

    with openFile(EXE_PATH) as f:
        maxIndex = len(rawSections) - 1

        for i, section in enumerate(rawSections):
            if section[1] > lastOffset:
                sections.append(readGenericSection(f, lastOffset, section[1] - lastOffset))

            sections.append(section)

            lastOffset = section[1] + section[2]

            if i == maxIndex and lastOffset < f.getSize():
                sections.append(readGenericSection(f, lastOffset, f.getSize() - lastOffset))

        totalSize = sum([ s[2] for s in sections ])

        assert totalSize == f.getSize()

    del pe
    del rawSections

    sections.sort(key=lambda s: getSectionPriority(s[0]))

    print('Sections:')

    for name, offset, size, *_ in sections:
        print(f'{ name } 0x{offset:08X} 0x{size:08X}')

    print(' ')
    print('Max threads:', MAX_THREADS)
    print(' ')

    # https://docs.python.org/3/library/concurrent.futures.html
    with concurrent.futures.ThreadPoolExecutor(MAX_THREADS) as pool:
        features = []

        stopEvent = Event()
        printLock = Lock()

        for section in sections:
            features.append(pool.submit(searchSection, pakPath, section, printLock, stopEvent))

        # state = concurrent.futures.wait(features, return_when=concurrent.futures.FIRST_COMPLETED)

        for feature in concurrent.futures.as_completed(features):
            isFound, (section, keyData) = feature.result()

            if isFound:
                stopEvent.set()
                pool.shutdown(False, cancel_futures=True)

                key, keyOffset, keySize = keyData

                print(
                    f'Key found in section { section[0] } ({ section[1] }, { section[2] }):\n' +
                    f'{ key } ({ keyOffset }, { keySize })'
                )

                break

            print('Key is not found in section', section[0])


def findPasswordHardReset1 (zipPath, exePath):
    from zipfile import ZipFile
    import difflib
    import pefile

    pe = pefile.PE(exePath)

    sections  = []

    for section in pe.sections:
        name   = section.Name.decode('ascii').strip('\x00').lower()
        offset = section.PointerToRawData
        size   = section.SizeOfRawData
        data   = section.get_data()  # data[section.PointerToRawData:section.PointerToRawData + section.SizeOfRawData]
        rank   = difflib.SequenceMatcher(a=name.lower(), b='data').ratio()

        sections.append((name, offset, size, data, rank))

    sections.sort(key=lambda s: s[4], reverse=True)

    minKeySize = 2
    maxKeySize = 32

    with ZipFile(zipPath) as pak:
        for section in sections:
            print('Section', section[0])

            data     = section[3]
            dataSize = len(data)

            maxOffset = max(0, dataSize - minKeySize)
            percent   = None

            for offset in range(0, maxOffset):
                limit = min(dataSize - offset, maxKeySize) + 1

                for keySize in range(minKeySize, limit):
                    key = data[offset:offset + keySize]

                    try:
                        pak.open('data/levels/dlc1_Junkyard/dlc1_Junkyard.waypoints', 'r', key).read()
                        print('FOUND:', key, formatHex(key))
                        sys.exit()
                    except:
                        pass

                if maxOffset:
                    curPercent = round(offset / maxOffset * 100)
                else:
                    curPercent = 0

                if curPercent != percent and curPercent % 5 == 0:
                    print(f'{ curPercent }%')

                percent = curPercent

def swapBytes (seq):
    return bytes(reversed(list(seq)))


def findPassword2 (pakPath):
    def readGenericSection (f, offset, size):
        f.seek(offset)

        data = f.read(size)

        assert len(data) == size

        return ('.generic', offset, size, data)

    def getSectionPriority (name):
        sectionPriorities = [ '.rdata', '.data', '.tls', '.text', '.rsrc', '.extra', '.reloc', '.generic' ]

        try:
            return sectionPriorities.index(name)
        except:
            return len(sectionPriorities)

    pe = pefile.PE(EXE_PATH)

    rawSections = []

    for section in pe.sections:
        name   = section.Name.decode('ascii').strip('\x00').lower()
        offset = section.PointerToRawData
        size   = section.SizeOfRawData
        data   = section.get_data()  # data[section.PointerToRawData:section.PointerToRawData + section.SizeOfRawData]

        rawSections.append((name, offset, size, data))

    rawSections.sort(key=lambda s: s[1])

    sections   = []
    lastOffset = 0

    with openFile(EXE_PATH) as f:
        maxIndex = len(rawSections) - 1

        for i, section in enumerate(rawSections):
            if section[1] > lastOffset:
                sections.append(readGenericSection(f, lastOffset, section[1] - lastOffset))

            sections.append(section)

            lastOffset = section[1] + section[2]

            if i == maxIndex and lastOffset < f.getSize():
                sections.append(readGenericSection(f, lastOffset, f.getSize() - lastOffset))

        totalSize = sum([ s[2] for s in sections ])

        assert totalSize == f.getSize()

    del pe
    del rawSections

    # TODO: remove
    # sections = sections[4:]

    sections.sort(key=lambda s: getSectionPriority(s[0]))

    minKeySize = 2
    maxKeySize = 32

    totalBaseOffset = 0

    maxNameSize = max([ len(s[0]) for s in sections ])

    print('Sections:')

    for sectionName, sectionOffset, sectionSize, *_ in sections:
        totalBaseOffset += max(0, sectionSize - minKeySize)

        print(f'{sectionName:<{maxNameSize}} 0x{sectionOffset:08X} 0x{sectionSize:08X}')

    print(' ')

    with ZipFile(pakPath) as pak:
        files = [ i.filename for i in pak.infolist() if not i.is_dir() ]
        files = files[:3]  # try to read up to 3 files

        startTime = time()
        lastPercent = None
        doneBaseOffset = 0

        for sectionName, sectionOffset, sectionSize, data in sections:
            print('Section', sectionName)

            for baseOffset in range(0, max(0, sectionSize - minKeySize + 1)):
                doneBaseOffset += 1

                for keySize in range(minKeySize, min(maxKeySize, sectionSize - baseOffset) + 1):
                    chunk = data[baseOffset:baseOffset + keySize]

                    for key in [ chunk, swapBytes(chunk) ]:
                        try: 
                            for file in files:
                                pak.open(file, 'r', key).read()

                            print(
                                f'Key found in section { sectionName } ({ sectionOffset }, { sectionSize }):\n' +
                                f'{ repr(key) } ({ baseOffset }, { keySize })'
                            )

                            return
                        except:
                            pass

                percent = int(round(doneBaseOffset / totalBaseOffset * 100))

                if lastPercent != percent:
                    currentTime = time()
                    wastedTime  = currentTime - startTime

                    if lastPercent is None or percent == 0:
                        print(f'{ percent }%')
                    else:
                        remainingTime = wastedTime / percent * (100 - percent)

                        print(f'{ percent }% (wasted: { int(wastedTime) }s; remaining: { int(remainingTime) }s)')

                    lastPercent = percent

    print('Password is not found')



if __name__ == '__main__':
    # featTest()
    findPassword2(joinPath(GAME_DIR, 'coj4', 'Data0.pak'))

