import os, json

LOCALES_DIR = os.path.abspath('../../src/assets/locale')
PRIMARY_LOCALE_FILE = 'en.json'
PRIMARY_LOCALE_FILEPATH = os.path.join(LOCALES_DIR, PRIMARY_LOCALE_FILE)



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


def updateSecondary (primaryData, secondaryData):
    updatedKeys={}

    def walk (primaryData, secondaryData, keyPath=''):
        for key, value in primaryData.items():
            currentKeyPath = '{}.{}'.format(keyPath, key) if keyPath else key
            secondaryValue = None

            if key in secondaryData:
                secondaryValue = secondaryData[key]

            if isinstance(value, dict):
                if not isinstance(secondaryValue, dict):
                    secondaryValue = dict()

                secondaryData[key] = walk(value, secondaryValue, currentKeyPath)
            elif isinstance(value, str):
                if not isinstance(secondaryValue, str):
                    secondaryData[key] = '! {}'.format(value)
                    updatedKeys[currentKeyPath] = secondaryData[key]
            else:
                raise Exception('Unexpected value (dicts and string are only supported):', value)

        return secondaryData

    return (walk(primaryData, secondaryData), updatedKeys)


if __name__ == '__main__':
    if not os.path.isfile(PRIMARY_LOCALE_FILEPATH):
        print('File does not exist:', LOCALES_DIR)
        os.abort()

    primaryData = readJson(PRIMARY_LOCALE_FILEPATH)

    for item in os.listdir(LOCALES_DIR):
        filepath = os.path.join(LOCALES_DIR, item)

        if item.lower() == PRIMARY_LOCALE_FILE.lower() or not item.lower().endswith('.json') or not os.path.isfile(filepath):
            continue

        updatedData, updatedKeys = updateSecondary(primaryData, readJson(filepath))

        if len(updatedKeys) == 0:
            continue

        writeJson(filepath, updatedData)

        maxKeyLength = max(map(lambda x: len(x), updatedKeys.keys())) + 1

        print('\n{} ({} keys added):'.format(item, len(updatedKeys)))

        for key, value in updatedKeys.items():
            print('   ', '{}:'.format(key).ljust(maxKeyLength), value)
