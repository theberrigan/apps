import os
from common import bytesToNullString, formatBytes, readStruct, formatJson

class AudioReader:
    def __init__ (self, gameDir):
        self.gameDir = gameDir
        self.audioDir = os.path.join(self.gameDir, 'audio')
        self.configDir = os.path.join(self.audioDir, 'config')
        self.streamsDir = os.path.join(self.audioDir, 'streams')
        self.sfxDir = os.path.join(self.audioDir, 'sfx')
        self.streams = None


    @staticmethod
    def create (gameDir):
        reader = AudioReader(gameDir)
        return reader


    def readFileNames (self, filePath, strLength):
        if not os.path.isfile(filePath):
            raise Exception('File doesn\'t exist: {}'.format(filePath))

        fileSize = os.path.getsize(filePath)

        if (fileSize % strLength) != 0:
            print('WARN: File has unexpected size: {}'.format(filePath))

        itemCount = fileSize // strLength
        items = {}

        with open(filePath, 'rb') as f:
            for i in range(itemCount):
                name = bytesToNullString(f.read(strLength))
                items[i] = name

        return items


    def readLookupConfig (self, filePath, fileNames):
        if not os.path.isfile(filePath):
            raise Exception('File doesn\'t exist: {}'.format(filePath))

        fileSize = os.path.getsize(filePath)

        totalCount = 0
        streams = {}

        with open(filePath, 'rb') as f:
            while f.tell() < fileSize:
                # name = formatBytes(f.read(12))
                # print(name)
                # TODO: What is 3x bytes 
                fileIndex, offset, size = readStruct('<B3xII', f)
                fileName = fileNames[fileIndex]

                totalCount += 1

                if fileName not in streams:
                    streams[fileName] = { 
                        'count': 0,
                        'size': 0
                    }

                streams[fileName]['count'] += 1
                streams[fileName]['size'] += size

                # print(fileIndex, fileName, offset, size)

        print(totalCount, formatJson(streams))

    def unpack (self):
        streams = self.readFileNames(os.path.join(self.configDir, 'StrmPaks.dat'), 16)
        packs = self.readFileNames(os.path.join(self.configDir, 'PakFiles.dat'), 52)
        self.readLookupConfig(os.path.join(self.configDir, 'TrakLkup.dat'), streams)
        print('-' * 100)
        self.readLookupConfig(os.path.join(self.configDir, 'BankLkup.dat'), packs)
        print('-' * 100)