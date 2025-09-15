import os, sys
from collections import namedtuple
from common import GAME_DIR, formatJson
from line_reader import LineReader

FXP_PROJECT_DATA_BEGIN = 'FX_PROJECT_DATA:'
FXP_PROJECT_DATA_END = 'FX_PROJECT_DATA_END:'
FXP_SYSTEM_DATA = 'FX_SYSTEM_DATA:'



class FXPReader:
    def __init__ (self, filePath):
        self.filePath = filePath
        self.lineReader = LineReader(self.filePath)

    @staticmethod
    def create (filePath):
        reader = FXPReader(filePath)
        return reader

    def readDict (self, itemCount):
        skipEmptyLines = True
        data = []

        for i in range(itemCount):
            line = self.lineReader.readLine(skipEmptyLines)
            key, value = line.split(':', 1)
            data.append((key.strip(), value.strip()))
            skipEmptyLines = False

        return data


    def readSystemData (self):
        unk1 = self.lineReader.readLine()
        data = self.readDict(9)
        print(formatJson(data))
        sys.exit(0)

    def readProjectData (self):
        projectDataBigin = self.lineReader.readLine(True)

        assert projectDataBigin == FXP_PROJECT_DATA_BEGIN, 'Expected {}'.format(FXP_PROJECT_DATA_BEGIN)

        while True:
            line = self.lineReader.readLine(True)

            if line == None:
                raise Exception('Unexpected end of file')
            elif line == FXP_PROJECT_DATA_END:
                break
            elif line == FXP_SYSTEM_DATA:
                self.readSystemData()

        print(header)

    def parse (self):
        self.readProjectData()




if __name__ == '__main__':
    reader = FXPReader.create(os.path.join(GAME_DIR, 'models', 'effects.fxp'))
    reader.parse()