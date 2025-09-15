import os, json, sys

def readJson (filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read().strip()
        try:
            return json.loads(data)
        except:
            print('Can\'t parse json file:', filepath)
            return dict()


def writeJson (filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))

def findProjectRoot ():
    dir = os.path.dirname(os.path.realpath(__file__))

    while True:
        if os.path.isfile(os.path.join(dir, 'package.json')):
            break

        newDir = os.path.realpath(os.path.join(dir, '..'))

        if newDir == dir:
            dir = None
            break

        dir = newDir

    return dir


ROOT_DIR = findProjectRoot()

if not ROOT_DIR:
    print('Project root directory s not found')
    sys.exit(0)

LOCALES_DIR = os.path.realpath(os.path.join(ROOT_DIR, './src/assets/locale/'))
LOCALES_UPDATE_SOURCE_DIR = os.path.realpath(os.path.join(LOCALES_DIR, './update_locale/'))

if not os.path.isdir(LOCALES_DIR) or not os.path.isdir(LOCALES_UPDATE_SOURCE_DIR):
    print('One of the locale directories does not exist')
    sys.exit(0)

def collectLocalesToUpdate ():
    dest = [ item for item in os.listdir(LOCALES_DIR) if item.lower().endswith('.json') ]
    src = [ item for item in dest if os.path.exists(os.path.join(LOCALES_UPDATE_SOURCE_DIR, item)) ]
    return [ (os.path.join(LOCALES_DIR, item), os.path.join(LOCALES_UPDATE_SOURCE_DIR, item)) for item in src ]

localesToUpdate = collectLocalesToUpdate()

if not localesToUpdate:
    print('No locales to update')
    sys.exit(0)


def getDeletedKeys (srcData, destData):
    deletedKeys = []

    def walk (srcData, destData, keyPath = ''):
        for key, value in srcData.items():
            curKeyPath = '{}.{}'.format(keyPath, key) if keyPath else key

            if key not in destData:
                deletedKeys.append(curKeyPath)
            elif isinstance(value, dict) and isinstance(destData[key], dict):
                walk(value, destData[key], curKeyPath)

    walk(srcData, destData)

    return deletedKeys


def mergeData (srcData, destData):
    def walk (srcData, destData):
        for key, value in srcData.items():
            if key not in destData:
                print(key)
                continue
            elif isinstance(value, str) and isinstance(destData[key], str):
                destData[key] = value
            elif isinstance(value, dict) and isinstance(destData[key], dict):
                walk(value, destData[key])

    walk(srcData, destData)

    return destData


for destPath, srcPath in localesToUpdate:
    srcData = readJson(srcPath)
    destData = readJson(destPath)

    deletedKeys = getDeletedKeys(srcData, destData)

    if deletedKeys:
        print('Deleted keys in {} ({}):'.format(os.path.basename(srcPath), len(deletedKeys)))

        for key in deletedKeys:
            print('- {}'.format(key))

    destData = mergeData(srcData, destData)

    writeJson(destPath, destData)
