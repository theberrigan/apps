NULL_BYTE = b'\x00'

GAME_DIR = r'G:\Steam\steamapps\common\Grand Theft Auto San Andreas'

BLACKLISTED_EXTENSIONS = tuple(ext.lower() for ext in [ 'dll', 'exe', 'asi', 'ini', 'mpg', 'ico' ])

GAME_FILES = tuple(file.lower() for file in [
    'anim', 
    'audio', 
    'data', 
    'models', 
    'movies', 
    'text', 
    'eax.dll', 
    'gta-sa.exe', 
    'ogg.dll', 
    'stream.ini', 
    'vorbis.dll', 
    'vorbisFile.dll'
])
