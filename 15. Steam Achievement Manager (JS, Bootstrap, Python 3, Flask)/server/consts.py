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

SERVER_DIR   = os.path.join(ROOT_DIR, 'server')
STATIC_DIR   = os.path.join(ROOT_DIR, 'static')
FRONTEND_DIR = os.path.join(STATIC_DIR, 'frontend_old')
MISC_DIR     = os.path.join(ROOT_DIR, 'misc')

assert os.path.isdir(SERVER_DIR), 'Failed to find server dir'
assert os.path.isdir(STATIC_DIR), 'Failed to find static dir'
assert os.path.isdir(FRONTEND_DIR), 'Failed to find frontend dir'

STEAM_API_KEY = '<STEAM_API_KEY>'


__all__ = [
    'ROOT_DIR',
    'SERVER_DIR',
    'STATIC_DIR',
    'FRONTEND_DIR',
    'MISC_DIR',
    'STEAM_API_KEY',
]


if __name__ == '__main__':
    print(ROOT_DIR)
    print(SERVER_DIR)
    print(STATIC_DIR)
    print(FRONTEND_DIR)