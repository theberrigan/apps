import sys
import time

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from bfw.utils import *
from bfw.reader import *



SCRIPT_DIR  = getDirPath(getAbsPath(__file__))
BACKUPS_DIR = joinPath(SCRIPT_DIR, 'backups')

SAVE_FILE_PATH = r'C:\Users\Berrigan\Documents\My Games\Life Is Strange\Saves\LISSave2.sav'


# https://github.com/VakhtinAndrey/lis-save-editor
def parseSaveFile (savePath):
    with openFile(savePath) as f:
        unk1     = f.u32()
        dataSize = f.u32()

        assert dataSize == f.remaining()

        headerSize   = f.u32()
        saveDataSize = f.u32()
        unk2         = f.u32()

        saveDataEnd = 8 + saveDataSize
        namesOffset = saveDataEnd

        f.seek(namesOffset)

        nameCount = f.u32()

        names = []

        for i in range(nameCount):
            size = f.u32()
            name = f.string(size)

            names.append(name)

        f.seek(8 + headerSize)

        props = {}

        while f.tell() < saveDataEnd: 
            nameIndex = f.u32()
            name      = names[nameIndex]

            if name == 'None':
                break

            typeIndex  = f.u32()
            typeName   = names[typeIndex]
            propSize   = f.u32()
            arrayIndex = f.u32()

            value = None

            match typeName:
                case 'StructProperty':
                    structNameIndex = f.u32()
                    structName      = names[structNameIndex]

                    f.skip(propSize)

                case 'StrProperty':
                    size = f.i32()

                    if size < 0:
                        size = -size * 2
                        encoding = 'utf-16-le'
                    else:
                        encoding = 'utf-8'

                    value = f.string(size, encoding=encoding)

                case 'ArrayProperty':
                    f.skip(propSize)

                case 'IntProperty':
                    value = f.i32()

                case 'FloatProperty':
                    value = f.f32()

                case 'BoolProperty':
                    value = bool(f.u8())

                case 'ByteProperty':
                    enumNameIndex  = f.i32()
                    enumValueIndex = f.i32()
                    enumName       = names[enumNameIndex]
                    enumValue      = names[enumValueIndex]

                case _:
                    raise Exception('Unknown type')

            props[name] = value

    return props


def getCheckpointName (savePath):
    try:
        props = parseSaveFile(savePath)
    except:
        props = {}

    return props.get('CheckPointID', 'Unnamed')


class Timer:
    _timers = {}
    _nextId = 1

    @classmethod
    def create (cls, delay, fn, *args, **kwargs):
        assert  delay >= 0

        callTime = time.time() + delay

        timerId = cls._nextId

        cls._nextId += 1

        cls._timers[timerId] = (callTime, fn, args, kwargs)

        cls.check()

        return timerId

    @classmethod
    def cancel (cls, timerId):
        if timerId in cls._timers:
            del cls._timers[timerId]

    @classmethod
    def cancelAll (cls):
        cls._timers = {}

    @classmethod
    def check (cls):
        checkTime = time.time()

        timers = list(cls._timers.items())

        for timerId, (callTime, fn, args, kwargs) in timers:
            if callTime <= time.time():
                del cls._timers[timerId]

                fn(*args, **kwargs)

        return time.time() - checkTime


class EventHandler (FileSystemEventHandler):
    def __init__ (self, filePath):
        super().__init__()

        self.fileName = getBaseName(filePath).lower()
        self.timer    = None

    def on_any_event (self, event):
        if event.is_directory:
            return

        if event.event_type not in [ 'created', 'modified' ]:
            return

        filePath = event.src_path
        fileName = getBaseName(filePath).lower()

        if fileName != self.fileName:
            return

        if self.timer is not None:
            Timer.cancel(self.timer)

        self.timer = Timer.create(1, self.createBackup, filePath)

    def createBackup (self, filePath):
        print('createBackup', filePath)

        data = readBin(filePath)
        data = compressData(data)

        saveName = getFileName(filePath)
        saveExt  = getExt(filePath)        

        cheackpoint = getCheckpointName(filePath)

        backupDate = time.strftime('%Y-%m-%d_%H-%M-%S')
        backupName = f'{ saveName }__{ backupDate }__{ cheackpoint }{ saveExt }'
        backupPath = joinPath(BACKUPS_DIR, backupName)

        createDirs(BACKUPS_DIR)

        writeBin(backupPath, data)


def watch ():
    saveDir  = getDirPath(SAVE_FILE_PATH)
    handler  = EventHandler(SAVE_FILE_PATH)
    observer = Observer()

    observer.schedule(handler, saveDir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(max(0, 1 - Timer.check()))
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def main ():
    watch()
    # print(getCheckpointName(SAVE_FILE_PATH))



if __name__ == '__main__':
    main()
