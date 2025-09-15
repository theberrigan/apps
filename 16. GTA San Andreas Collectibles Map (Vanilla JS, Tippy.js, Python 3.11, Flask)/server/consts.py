import os


def findRoot ():
    currentDir = os.path.dirname(os.path.abspath(__file__))
    prevDir = currentDir

    while True:
        if os.path.isfile(os.path.join(currentDir, '.root')):
            return currentDir

        parentDir = os.path.abspath(os.path.join(currentDir, '..'))

        if os.path.samefile(parentDir, prevDir):
            return None

        prevDir = currentDir
        currentDir = parentDir


ROOT_DIR = findRoot()

assert ROOT_DIR, 'Failed to find root dir'

SERVER_DIR    = os.path.join(ROOT_DIR, 'server')
STATIC_DIR    = os.path.join(ROOT_DIR, 'static')
DATA_DIR      = os.path.join(ROOT_DIR, 'data')
MAP_DATA_PATH = os.path.join(DATA_DIR, 'map_data.json')


assert os.path.isdir(SERVER_DIR), 'Failed to find server dir'
assert os.path.isdir(STATIC_DIR), 'Failed to find static dir'
assert os.path.isdir(DATA_DIR), 'Failed to find data dir'


HOST = '0.0.0.0'
PORT = 42398
LOCAL_HOSTNAME = 'http://{}:{}'.format(HOST, PORT)



__all__ = [
    'ROOT_DIR',
    'SERVER_DIR',
    'STATIC_DIR',
    'DATA_DIR',
    'MAP_DATA_PATH',
    'HOST',
    'PORT',
    'LOCAL_HOSTNAME',
]



if __name__ == '__main__':
    print(ROOT_DIR)
    print(SERVER_DIR)
    print(STATIC_DIR)