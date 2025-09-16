import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from bfw.utils import *
from bfw.reader import *
from bfw.writer import *
from bfw.types.enums import Enum2
from bfw.media.ffmpeg import FFProbe, FFMpeg



MP3_SAMPLES_DIR = r'C:\Projects\_Data_Samples\_audio'
MUSIC_LIB_DIR   = r'D:\Documents\Музыка'


ID3V1_SIZE      = 128
ID3V1_SIGNATURE = b'TAG'
ID3V1_ENCODING  = 'ISO-8859-1'

ID3V1_EXT_SIGNATURE = b'TAG+'
ID3V1_EXT_SIZE      = 227

ID3V1_FULL_SIZE = ID3V1_SIZE + ID3V1_EXT_SIZE

L3V1_START_TAG      = b'LYRICSBEGIN'
L3V1_END_TAG        = b'LYRICSEND'
L3V1_START_TAG_SIZE = len(L3V1_START_TAG)
L3V1_END_TAG_SIZE   = len(L3V1_END_TAG)
L3V1_TEXT_SIZE      = 5100
L3V1_ENCODING       = 'ISO-8859-1'

L3V2_START_TAG      = b'LYRICSBEGIN'
L3V2_END_TAG        = b'LYRICS200'
L3V2_START_TAG_SIZE = len(L3V2_START_TAG)
L3V2_END_TAG_SIZE   = len(L3V2_END_TAG)
L3V2_ENCODING       = 'ISO-8859-1'


ID3V1_GENRES = {
    0:   'Blues',
    1:   'Classic rock',
    2:   'Country',
    3:   'Dance',
    4:   'Disco',
    5:   'Funk',
    6:   'Grunge',
    7:   'Hip-hop',
    8:   'Jazz',
    9:   'Metal',
    10:  'New age',
    11:  'Oldies',
    12:  'Other',
    13:  'Pop',
    14:  'Rhythm and blues',
    15:  'Rap',
    16:  'Reggae',
    17:  'Rock',
    18:  'Techno',
    19:  'Industrial',
    20:  'Alternative',
    21:  'Ska',
    22:  'Death metal',
    23:  'Pranks',
    24:  'Soundtrack',
    25:  'Euro-techno',
    26:  'Ambient',
    27:  'Trip-hop',
    28:  'Vocal',
    29:  'Jazz & funk',
    30:  'Fusion',
    31:  'Trance',
    32:  'Classical',
    33:  'Instrumental',
    34:  'Acid',
    35:  'House',
    36:  'Game',
    37:  'Sound clip',
    38:  'Gospel',
    39:  'Noise',
    40:  'Alternative rock',
    41:  'Bass',
    42:  'Soul',
    43:  'Punk',
    44:  'Space',
    45:  'Meditative',
    46:  'Instrumental pop',
    47:  'Instrumental rock',
    48:  'Ethnic',
    49:  'Gothic',
    50:  'Darkwave',
    51:  'Techno-industrial',
    52:  'Electronic',
    53:  'Pop-folk',
    54:  'Eurodance',
    55:  'Dream',
    56:  'Southern rock',
    57:  'Comedy',
    58:  'Cult',
    59:  'Gangsta',
    60:  'Top 40',
    61:  'Christian rap',
    62:  'Pop/funk',
    63:  'Jungle music',
    64:  'Native US',
    65:  'Cabaret',
    66:  'New wave',
    67:  'Psychedelic',
    68:  'Rave',
    69:  'Showtunes',
    70:  'Trailer',
    71:  'Lo-fi',
    72:  'Tribal',
    73:  'Acid punk',
    74:  'Acid jazz',
    75:  'Polka',
    76:  'Retro',
    77:  'Musical',
    78:  'Rock \'n\' roll',
    79:  'Hard rock',
    80:  'Folk',
    81:  'Folk rock',
    82:  'National folk',
    83:  'Swing',
    84:  'Fast fusion',
    85:  'Bebop',
    86:  'Latin',
    87:  'Revival',
    88:  'Celtic',
    89:  'Bluegrass',
    90:  'Avantgarde',
    91:  'Gothic rock',
    92:  'Progressive rock',
    93:  'Psychedelic rock',
    94:  'Symphonic rock',
    95:  'Slow rock',
    96:  'Big band',
    97:  'Chorus',
    98:  'Easy listening',
    99:  'Acoustic',
    100: 'Humour',
    101: 'Speech',
    102: 'Chanson',
    103: 'Opera',
    104: 'Chamber music',
    105: 'Sonata',
    106: 'Symphony',
    107: 'Booty bass',
    108: 'Primus',
    109: 'Porn groove',
    110: 'Satire',
    111: 'Slow jam',
    112: 'Club',
    113: 'Tango',
    114: 'Samba',
    115: 'Folklore',
    116: 'Ballad',
    117: 'Power ballad',
    118: 'Rhythmic Soul',
    119: 'Freestyle',
    120: 'Duet',
    121: 'Punk rock',
    122: 'Drum solo',
    123: 'A cappella',
    124: 'Euro-house',
    125: 'Dance hall',
    126: 'Goa music',
    127: 'Drum & bass',
    128: 'Club-house',
    129: 'Hardcore techno',
    130: 'Terror',
    131: 'Indie',
    132: 'Britpop',
    133: 'Negerpunk',
    134: 'Polsk punk',
    135: 'Beat',
    136: 'Christian gangsta rap',
    137: 'Heavy metal',
    138: 'Black metal',
    139: 'Crossover',
    140: 'Contemporary Christian',
    141: 'Christian rock',
    142: 'Merengue',
    143: 'Salsa',
    144: 'Thrash metal',
    145: 'Anime',
    146: 'Jpop',
    147: 'Synthpop',
    148: 'Christmas',
    149: 'Art rock',
    150: 'Baroque',
    151: 'Bhangra',
    152: 'Big beat',
    153: 'Breakbeat',
    154: 'Chillout',
    155: 'Downtempo',
    156: 'Dub',
    157: 'EBM',
    158: 'Eclectic',
    159: 'Electro',
    160: 'Electroclash',
    161: 'Emo',
    162: 'Experimental',
    163: 'Garage',
    164: 'Global',
    165: 'IDM',
    166: 'Illbient',
    167: 'Industro-Goth',
    168: 'Jam Band',
    169: 'Krautrock',
    170: 'Leftfield',
    171: 'Lounge',
    172: 'Math rock',
    173: 'New romantic',
    174: 'Nu-breakz',
    175: 'Post-punk',
    176: 'Post-rock',
    177: 'Psytrance',
    178: 'Shoegaze',
    179: 'Space rock',
    180: 'Trop rock',
    181: 'World music',
    182: 'Neoclassical',
    183: 'Audiobook',
    184: 'Audio theatre',
    185: 'Neue Deutsche Welle',
    186: 'Podcast',
    187: 'Indie rock',
    188: 'G-Funk',
    189: 'Dubstep',
    190: 'Garage rock',
    191: 'Psybient',
}

'''

- ID3V1
- ID3V1.1
- ID3V1+
- ID3V2.0
- ID3V2.1
- ID3V2.2
- ID3V2.3
- Lyrics3v1
- Lyrics3v2
- APEv1
- APEv2



--- MP3 GENERAL FORMAT ---

Common resources:
- https://bitbucket.org/ijabz/jaudiotagger
- https://en.wikipedia.org/wiki/ID3
- https://mutagen-specs.readthedocs.io/en/latest/apev2/apev2.html
- D:\Documents\Книги и образование\Цифровые сигналы, звук\Mpeg

+-------------------------------------------+
| [ID3v2.2 | ID3v2.3 | ID3v2.4] - ??? bytes |
| ----                                      |
| Frame 0                                   |
| Frame 1                                   |
| ...                                       |
| Frame N                                   |
| ----                                      |
| [Lyrics3v2] - variable size  -| OR        |
| [Lyrics3v1] - max 5120 bytes -|           |
| [Ext ID3v1] - 227 bytes (if ID3v1.x)      |
| [ID3v1.x]   - 128 bytes                   |
+-------------------------------------------+



--- ID3V1 AND ID3V1.1 FORMAT ---

Resources:
- https://en.wikipedia.org/wiki/ID3
- https://ru.wikipedia.org/wiki/ID3_(метаданные)
- https://en.wikipedia.org/wiki/List_of_ID3v1_genres

Notes:
- Text encoding: ISO-8859-1

+---------+--------+------+-------+
| Data    | Offset | Size | Type  |
+---------+--------+------+-------+
| b'TAG'  | 0      | 3    | bytes |
| Title   | 3      | 30   | str   |
| Artist  | 33     | 30   | str   |
| Album   | 63     | 30   | str   |
| Year    | 93     | 4    | str   |
| Comment | 97     | 30*  | str   |
| Genre   | 127    | 1    | u8    |
+---------+--------+------+-------+
* In ID3v1.1 comment size can be 28 bytes,
followed by NULL and u8 which is track number



--- EXTENDED ID3V1 FORMAT ---

Resources:
- https://phoxis.org/2010/05/08/what-are-id3-tags-all-about/#id3v1ext
- https://web.archive.org/web/20120310015458/http://www.fortunecity.com/underworld/sonic/3/id3tag.html

+---------+--------+------+-------+----------+
| Data    | Offset | Size | Type  | Format   |
+---------+--------+------+-------+----------+
| b'TAG+' | 0      | 4    | bytes |          |
| Title   | 4      | 60   | str   |          |
| Artist  | 64     | 60   | str   |          |
| Album   | 124    | 60   | str   |          |
| Speed   | 184    | 1    | u8    |          |
| Genre   | 185    | 30   | str   |          |
| Start   | 215    | 6    | str   | "mmm:ss" |
| End     | 221    | 6    | str   | "mmm:ss" |
+---------+--------+------+-------+----------+
'''
class ID3V1Tag:
    @classmethod
    def read (cls, f, baseOffset):
        if f.getSize() < ID3V1_SIZE:
            return 0, None

        f.fromEnd(-(baseOffset + ID3V1_SIZE))

        signature = f.read(3)

        if signature != ID3V1_SIGNATURE:
            return 0, None

        tagOffset = ID3V1_SIZE

        title  = f.read(30)
        artist = f.read(30)
        album  = f.read(30)
        year   = cls._parseInt(f.read(4))

        byte = f.peek(offset=28, size=1)

        if byte == b'\x00':
            comment = cls._parseString(f.read(29))
            track   = f.u8()
        else:
            comment = cls._parseString(f.read(30))
            track   = None

        genreIndex = f.u8()
        genreName  = ID3V1_GENRES.get(genreIndex)

        genreFree  = None
        speed      = None
        time       = None 

        # Extended ID3v1
        if f.getSize() >= ID3V1_FULL_SIZE:
            f.fromEnd(-(baseOffset + ID3V1_FULL_SIZE))

            signature = f.read(4)

            if signature == ID3V1_EXT_SIGNATURE:
                tagOffset = ID3V1_FULL_SIZE

                title  += f.read(60)
                artist += f.read(60)
                album  += f.read(60)
                speed   = f.u8()

                genreFree = cls._parseString(f.read(30))

                timeStart = cls._parseTime(f.read(6))
                timeEnd   = cls._parseTime(f.read(6))

                time = {
                    'start': timeStart,
                    'end':   timeEnd
                }

        return (tagOffset, {
            'title':   cls._parseString(title),
            'artist':  cls._parseString(artist),
            'album':   cls._parseString(album),
            'year':    year,
            'comment': comment,
            'track':   track,
            'speed':   speed,
            'time':    time,
            'genre':   {
                'index': genreIndex,
                'name':  genreName,
                'free':  genreFree
            }
        })

    @classmethod
    def _parseString (cls, buff):
        return buff.decode(ID3V1_ENCODING).strip(' \x00')

    @classmethod
    def _parseInt (cls, buff):
        string = cls._parseString(buff)

        if string and string.isnumeric():
            return int(string, 10)

        return None

    @classmethod
    def _parseTime (cls, buff):
        nums = cls._parseString(buff).split(':')

        if len(nums) != 2:
            return None

        m, s = nums

        if not m.isnumeric() or not s.isnumeric():
            return None

        return int(m, 10) * 60 + int(s, 10)


# https://id3lib.sourceforge.net/id3/lyrics3.html
# https://web.archive.org/web/20220924060345/https://id3.org/Lyrics3
class L3V1Tag:
    @classmethod
    def read (cls, f, baseOffset):
        endTagOffset = L3V1_END_TAG_SIZE + baseOffset

        if f.getSize() < (L3V1_START_TAG_SIZE + endTagOffset):
            return baseOffset, None

        f.fromEnd(-endTagOffset)

        tag = f.read(L3V1_END_TAG_SIZE)

        if tag != L3V1_END_TAG:
            return baseOffset, None

        maxLyricsSize   = min(f.getSize() - endTagOffset, L3V1_START_TAG_SIZE + L3V1_TEXT_SIZE)
        maxLyricsOffset = maxLyricsSize + endTagOffset

        f.fromEnd(-maxLyricsOffset)

        text = f.read(maxLyricsSize)

        try:
            startTagIndex = text.index(L3V1_START_TAG)
        except:
            return baseOffset, None

        text = text[startTagIndex + L3V1_START_TAG_SIZE:]
        text = text.decode(L3V1_ENCODING).strip(' \x00')

        # TODO: parse timecodes

        tagOffset = maxLyricsOffset + startTagIndex

        return tagOffset, text

# https://web.archive.org/web/20220810131336/https://id3.org/Lyrics3v2
class L3V2Tag:
    @classmethod
    def read (cls, f, baseOffset):
        endTagOffset = L3V2_END_TAG_SIZE + baseOffset

        if f.getSize() < (L3V2_START_TAG_SIZE + 6 + endTagOffset):
            return baseOffset, None

        f.fromEnd(-endTagOffset)

        tag = f.read(L3V2_END_TAG_SIZE)

        if tag != L3V2_END_TAG:
            return baseOffset, None

        sizeOffset = endTagOffset + 6

        f.fromEnd(-sizeOffset)

        headSize = f.fixedString(6, encoding=L3V2_ENCODING)

        if not headSize.isnumeric():
            return baseOffset, None

        headSize = int(headSize, 10)

        tagOffset = sizeOffset + headSize

        f.fromEnd(-tagOffset)

        tag = f.read(L3V2_START_TAG_SIZE)

        if tag != L3V2_START_TAG:
            return baseOffset, None

        textSize = headSize - L3V2_START_TAG_SIZE

        text = f.fixedString(textSize, encoding=L3V2_ENCODING)

        # TODO: parse

        return tagOffset, text


# https://en.wikipedia.org/wiki/APE_tag
# https://mutagen-specs.readthedocs.io/en/latest/apev2/apev2.html
# https://web.archive.org/web/20220527145418/https://wiki.hydrogenaud.io/index.php?title=APEv1_specification
# https://web.archive.org/web/20220809133743/https://wiki.hydrogenaud.io/index.php?title=APE_Tags_Header
class APETag:
    @classmethod
    def read (cls, f, baseOffset):
        return baseOffset, None


class MP3:
    def __init__ (self):
        pass

    @classmethod
    def fromFile (cls, filePath):
        if not isFile(filePath):
            raise Exception(f'File does not exist: { filePath }')

        with openFile(filePath) as f:
            return cls._read(f)

    @classmethod
    def fromBuffer (cls, data):
        with MemReader(data) as f:
            return cls._read(f)

    @classmethod
    def _read (cls, f):
        mp3 = MP3()

        readers = [
            {
                'tagName': 'ID3v1',
                'readFn':  ID3V1Tag.read,
                'isFound': False,
                'isLast':  True
            },
            {
                'tagName': 'L3v1',
                'readFn':  L3V1Tag.read,
                'isFound': False,
                'isLast':  False
            },
            {
                'tagName': 'L3v2',
                'readFn':  L3V2Tag.read,
                'isFound': False,
                'isLast':  False
            },
            {
                'tagName': 'APE',
                'readFn':  APETag.read,
                'isFound': False,
                'isLast':  False
            }
        ]

        offset = 0
        tags   = {}

        while True:
            isFound = False

            for reader in readers:
                if reader['isFound'] or offset and reader['isLast']:
                    continue

                tagName = reader['tagName']
                readFn  = reader['readFn']

                newOffset, tag = readFn(f, offset)

                if tag is None:
                    continue

                reader['isFound'] = True

                offset = newOffset

                tags[tagName] = tag

                isFound = True

                print(tag)

            if not isFound:
                break






        # metaSize, tag = ID3V1Tag.read(f)

        # lyrics = L3V1.read(f, metaSize)

        # if lyrics is None:
        #     lyrics = L3V2.read(f, metaSize)

        # if lyrics is not None:
        #     print(f.getFilePath())
        #     # print(metaSize, toJson(tag))
        #     # print(lyrics)
        #     print(' ')


def _test_ ():
    for rootDir in [ MP3_SAMPLES_DIR, MUSIC_LIB_DIR ]:        
    # for rootDir in getDrives(True):     
    # for rootDir in [ MP3_SAMPLES_DIR ]:    
        for mp3Path in iterFiles(rootDir, True, [ '.mp3' ]):
            MP3.fromFile(mp3Path)


def _createSample ():
    title     = 'STARThttps://phoxis.org/2010/05/08/what-are-id3-tags-all-about/#id3v1extEND'
    artist    = 'STARThttps://web.archive.org/web/20120310015458/http://www.fortunecity.com/underworld/sonic/3/id3tag.htmlEND'
    album     = 'STARTID3V1_FULL_SIZE = ID3V1_SIZE + ID3V1_EXT_SIZEEND'
    freeGenre = 'STARTMyGenreEND'
    year      = 2024
    comment   = 'STARTID3 is a metadata container most often used in conjunction with the MP3 audio file format.END'
    lyrics    = (
        'Baila, let me see you dance, baby\r\n' \
        'Yeah, let me see you dance, baby, c\'mon\r\n' \
        'Adesso credo nei miracoli\r\n' \
        'In questa notte di tequila boom boom\r\n' \
        'Sei cosa sexy cosa, sexy thing (e vai)\r\n' \
        'Ti ho messo gli occhi addosso, e lo sai (yeah)\r\n' \
        'Che devi avere un caos dentro di te\r\n' \
        'Per far fiorire una stella che balla\r\n' \
        'Inferno e paradiso dentro di te\r\n' \
        'La luna è un sole guarda come brilla\r\n' \
        'Baby the night is on fire\r\n' \
        'Siamo fiamme nel cielo\r\n' \
        'Lampi in mezzo al buio, what do you say?\r\n' \
        'Baila, baila Morena\r\n' \
        'Sotto questa luna piena\r\n' \
        'Under the moonlight\r\n' \
        'Under the moonlight\r\n' \
        'Vai chica vai cocca che mi sa cocca\r\n' \
        'Che questa sera qualche cosa ti tocca\r\n' \
        'Ho un cuore d\'oro sai il cuore di un santo\r\n' \
        'Per così poco me la merito tanto\r\n' \
        'Baby the night is on fire\r\n' \
        'Siamo fiamme nel cielo\r\n' \
        'Scandalo nel buio, what do you say?\r\n' \
        'Baila, baila Morena\r\n' \
        'Sotto questa luna piena\r\n' \
        'Under the moonlight (come on, yeah)\r\n' \
        'Baila, under the moonlight\r\n' \
        'Sotto questa luna piena\r\n' \
        'Baila Morena, yeah yeah yeah\r\n' \
        'You set me free, set me free\r\n' \
        'You got me hurtin so bad, so bad\r\n' \
        'I know now, now, now\r\n' \
        'I got to have it, so bad\r\n' \
        'What do you say?\r\n' \
        'What do you say?\r\n' \
        'Baila, baila Morena\r\n' \
        'Sotto questa luna piena\r\n' \
        'Under the moonlight\r\n' \
        'E baila, under the moonlight\r\n' \
        'Sotto questa luna piena\r\n' \
        'Daila Morena\r\n' \
        'Sotto questa luna piena\r\n' \
        'Sotto questa luna piena\r\n' \
        'Sotto questa luna piena\r\n' \
        'Under the moonlight (come on y\'all)'
    )

    with BinWriter() as f:
        title     = title.encode(ID3V1_ENCODING)
        artist    = artist.encode(ID3V1_ENCODING)
        album     = album.encode(ID3V1_ENCODING)
        freeGenre = freeGenre.encode(ID3V1_ENCODING)
        year      = str(year).encode(ID3V1_ENCODING)
        comment   = comment.encode(ID3V1_ENCODING)
        lyrics    = lyrics.encode(L3V1_ENCODING)

        f.write(bytes(range(256)))

        f.write(L3V1_START_TAG)
        f.write(lyrics[:L3V1_TEXT_SIZE])
        f.write(L3V1_END_TAG)

        f.write(ID3V1_EXT_SIGNATURE)
        f.write(title[30:90].ljust(60, b'\x00'))
        f.write(artist[30:90].ljust(60, b'\x00'))
        f.write(album[30:90].ljust(60, b'\x00'))
        f.u8(1)
        f.write(freeGenre[:30].ljust(30, b'\x00'))
        f.write(b'000:00')
        f.write(b'003:30')

        f.write(ID3V1_SIGNATURE)
        f.write(title[:30].ljust(30, b'\x00'))
        f.write(artist[:30].ljust(30, b'\x00'))
        f.write(album[:30].ljust(30, b'\x00'))
        f.write(year[:4].ljust(4, b'\x00'))
        f.write(comment[:28].ljust(29, b'\x00'))
        f.u8(128)
        f.u8(100)

        f.save(joinPath(MP3_SAMPLES_DIR, 'my', 'noaudio_ID3V1.1+ext+L3V1.mp3'))


__all__ = [
    'MP3'
]



if __name__ == '__main__':
    _test_()
    # _createSample()