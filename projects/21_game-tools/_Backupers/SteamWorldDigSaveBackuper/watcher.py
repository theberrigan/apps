import sys
import time

from zipfile import ZipFile, ZIP_DEFLATED

sys.path.insert(0, r'C:\Projects\PythonLib\python\v001')

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from bfw.utils import *



SCRIPT_DIR  = getDirPath(getAbsPath(__file__))
BACKUPS_DIR = joinPath(SCRIPT_DIR, 'backups')

SAVE_FILE_DIR = r'C:\Users\Berrigan\Documents\My Games\SteamWorld Dig'



class Timer:
    _timers = {}
    _nextId = 1

    @classmethod
    def create (cls, delay, fn, *args, **kwargs):
        assert delay >= 0

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
    def __init__ (self, saveDir):
        super().__init__()

        self.saveDir = saveDir
        self.timer   = None

    def on_any_event (self, event):
        if event.is_directory:
            return

        if event.event_type not in [ 'created', 'modified' ]:
            return

        if self.timer is not None:
            Timer.cancel(self.timer)

        self.timer = Timer.create(3, self.createBackup, self.saveDir)

    def createBackup (self, saveDir):
        print('createBackup', saveDir)

        backupDate = time.strftime('%Y-%m-%d_%H-%M-%S')
        backupName = f'{ backupDate }.zip'
        backupPath = joinPath(BACKUPS_DIR, backupName)

        with ZipFile(
            backupPath,
            mode          = 'w',
            compression   = ZIP_DEFLATED,
            allowZip64    = True,
            compresslevel = 9
        ) as zf:
            for filePath in iterFiles(saveDir, True):
                zf.write(filePath, getRelPath(filePath, saveDir))


def watch ():
    saveDir  = SAVE_FILE_DIR
    handler  = EventHandler(saveDir)
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



if __name__ == '__main__':
    main()
