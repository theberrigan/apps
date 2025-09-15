import zipfile, os, hashlib, json


GAME_DIR = r'G:\Games\Call Of Duty 2'
MAIN_DIR = os.path.join(GAME_DIR, 'main2')
RAW1_DIR = os.path.join(GAME_DIR, 'raw')
RAW2_DIR = os.path.join(GAME_DIR, 'raw2')


def getDataMD5 (data, lowerCase=True):
    checksum = hashlib.md5(data).hexdigest()

    return checksum.lower() if lowerCase else checksum.upper()


def extract ():
    os.makedirs(RAW_DIR, exist_ok=True)

    iwdIndex = 0 

    while True:
        path = os.path.join(MAIN_DIR, 'iw_{:0>2}.iwd'.format(iwdIndex))
        iwdIndex += 1

        if not os.path.isfile(path):
            break

        print(path)

        with zipfile.ZipFile(path, 'r') as iwd:
            iwd.extractall(RAW_DIR)


def compare (baseDirs):
    files = []

    for i, baseDir in enumerate(baseDirs):
        baseDir = baseDirs[i] = os.path.abspath(baseDir)
        dirFiles = []
        files.append((baseDir, dirFiles))

        for dirName, _, itemNames in os.walk(baseDir):
            for itemName in itemNames:
                itemPath = os.path.join(dirName, itemName)
                dirFiles.append(os.path.relpath(itemPath, baseDir))

    pathSets = [ set(item[1]) for item in files ]
    allFiles = pathSets[0].union(*pathSets[1:])
    absents = []

    for i, pathSet in enumerate(pathSets):
        absentFiles = list(allFiles - pathSet)

        absents.append([ baseDirs[i], absentFiles ])

        print(baseDirs[i])

        for absentFile in absentFiles:
            print('   ', absentFile)

    commonFiles = pathSets[0].intersection(*pathSets[1:])
    diffs = []

    for i, path in enumerate(commonFiles):
        isDiff = False
        lastHash = None

        for baseDir in baseDirs:
            absPath = os.path.join(baseDir, path)

            with open(absPath, 'rb') as f:
                dataHash = getDataMD5(f.read())

            if lastHash is not None and dataHash != lastHash:
                isDiff = True
                break

            lastHash = dataHash

        if isDiff:
            diffs.append(path)

    print(json.dumps({ 'absents': absents, 'diffs': diffs }, indent=4, ensure_ascii=False))



compare([ RAW1_DIR, RAW2_DIR ])