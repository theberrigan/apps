import os
import sass  # pip install libsass

def count (dir):
    prevCwd = os.getcwd()
    dir = os.path.abspath(dir)
    os.chdir(dir)
    totalSize = 0;

    for item in os.listdir(dir):
        path = os.path.join(dir, item)

        if os.path.isdir(path):
            totalSize += count(path)
            continue

        if os.path.isfile(path) and item.lower().endswith('.scss'):
            if item[0] != '_':
                with open(path, 'r') as f:
                    data = f.read().strip().replace('@extend .no-select;', '@extend .no-select !optional;')
                    if data:
                        data = sass.compile(string=data, output_style='compressed')    
                    size = len(data)
                    totalSize += size
                    print(os.path.abspath(path), str(int(size / 1024)) + 'kb')        

            # size = os.path.getsize(path)

    os.chdir(prevCwd)
    return totalSize

print(str(int(count('./src') / 1024)) + 'kb')