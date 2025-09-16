import os


ROOT_DIR = r'C:\Projects\HLW\static\game'

stats = {}

for dirName, _, fileNames in os.walk(ROOT_DIR):
    for fileName in fileNames:
        itemPath = os.path.join(dirName, fileName)

        ext = os.path.splitext(fileName)[1].lower()

        if ext in [ '.dll', '.so', '.dylib', '.inf', '.wav', '.ico', '.bmp', '.tga', '.scr', '.ttf', '.lst', '.mp3' ]:
            continue

        stat = stats[ext] = stats.get(ext, {
            'ext': ext,
            'count': 0,
            'size': 0
        })

        stat['size'] += os.path.getsize(itemPath)
        stat['count'] += 1


stats = stats.values()

byCount = sorted(stats, key=lambda item: item['count'], reverse=True)
bySize  = sorted(stats, key=lambda item: item['size'], reverse=True)


for i, itemByCount in enumerate(byCount):
    itemBySize = bySize[i]

    ext1 = itemByCount['ext']
    count1 = itemByCount['count']
    size1 = itemByCount['size']
    
    ext2 = itemBySize['ext']
    count2 = itemBySize['count']
    size2 = itemBySize['size']

    print(f'{ ext1 } { count1 } { size1 } | { ext2 } { count2 } { size2 }')
