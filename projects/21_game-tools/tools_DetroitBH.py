# Detroit Become Human Tools

from sys import exit

from deps.utils import *
from deps.reader import *

from struct import unpack



GAME_DIR = r'G:\Steam\steamapps\common\Detroit Become Human'

def readU32BE (f, count=1):
    nums = unpack(f'>{ count }I', f.read(4 * count))

    if count == 1:
        return nums[0]

    return nums

def test ():
    files = {}

    for i in range(30):
        if i == 0:
            ext = '.dat'
        else:
            ext = f'.d{i:02}'

        files[i] = openFile(joinPath(GAME_DIR, 'BigFile_PC' + ext))

    _map = {}
    _map2 = {}
    _resCnt = 0
    _resGrps = {}

    with openFile(joinPath(GAME_DIR, 'BigFile_PC.idx')) as f:
        f.skip(101)

        count = readU32BE(f)

        for i in range(count):
            # unk4 is some size
            resType, _always1, unk3, offset, size, unk4, idx = readU32BE(f, 7)

            print(resType); exit()

            _resCnt += 1

            if unk3 not in _resGrps:
                _resGrps[unk3] = True

            # assert unk4 == 0, f'{idx} {offset} {size} {unk4}'

            file = files[idx]

            file.seek(offset)

            inQZIP = None
            str1 = file.read(4)
            str2 = None

            if str1 == b'QZIP':
                zero = file.read(1)

                assert zero == b'\x00'

                str2 = file.read(8)
                inQZIP = True
                # print(resType, _always1, unk3, offset, size, unk4, idx, str1, str2)
                # exit()
            elif str1 == b'segs':
                str2 = str1
                inQZIP = False
            else:
                str2 = str1 + file.read(4)
                inQZIP = False
                # print(resType, _always1, unk3, offset, size, unk4, idx, str2)

            assert inQZIP is not None
            assert str2 is not None

            str2 = str2.decode('utf-8')

            if str2 not in _map:
                _map[str2] = {
                    'inQZIP': inQZIP,
                    'ids': {}
                }
            else:
                assert inQZIP == _map[str2]['inQZIP']

            if resType not in _map[str2]['ids']:
                _map[str2]['ids'][resType] = 1
            else:
                _map[str2]['ids'][resType] += 1

            _map2[resType] = _map2.get(resType, 0) + size

            # if resType == 63 and idx == 12:
            #     print(resType, _always1, unk3, offset, size, unk4, idx, str2)

            # if idx == 1 and (offset < 783696626 < (offset + size)):
            #     print(resType, _always1, unk3, offset, size, unk4, idx, str2)

        # for key, info in _map.items():
        #     for key2, info2 in _map.items():
        #         if key == key2:
        #             continue

        #         for id1 in info['ids'].keys():
        #             for id2 in info2['ids'].keys():
        #                 if id1 == id2:
        #                     print(key, key2, id1)

        # _map2 = sorted(_map2.items(), key=lambda item: item[1], reverse=True)
        # _map2 = dict([ [ pair[0], formatSize(pair[1]) ] for pair in _map2 ])

        # print(toJson(_map))

        print(_resCnt, len(_resGrps))

        assert f.remaining() == 0






if __name__ == '__main__':
    test()

'''
COM_CONT CSNDEVNT 1023
DC_INFO  segs 29
CSNDEVNT COM_CONT 1023
segs DC_INFO  29

{
    "29": "24.5GB",    // QZIPped DC_INFO, standalone segs
    "2230": "11.5GB",  // QZIPped ETF_RAWL, can contain segs
    "1033": "10.9GB",  // QZIPped CSNDDATA
    "2033": "6.4GB",   // one of COM_CONT
    "2229": "3.1GB",   // QZIPped ETF_RAW_
    "4288": "344.0MB", 
    "18002": "289.4MB", 
    "63": "176.5MB", 
    "19000": "78.6MB", 
    "1016": "71.8MB", 
    "15000": "38.9MB", 
    "14000": "10.1MB", 
    "4254": "8.7MB", 
    "4091": "6.7MB", 
    "3": "1.8MB", 
    "1023": "1.0MB", 
    "2212": "831.3KB", 
    "1031": "750.2KB", 
    "14014": "484.1KB", 
    "42": "330.2KB", 
    "2137": "256.2KB", 
    "4137": "235.7KB", 
    "14003": "53.0KB", 
    "1022": "44.2KB", 
    "65": "19.4KB", 
    "2094": "18.0KB", 
    "2226": "17.3KB", 
    "19001": "13.8KB", 
    "1030": "11.2KB", 
    "1025": "8.3KB", 
    "1026": "6.2KB", 
    "4333": "5.1KB", 
    "4234": "3.9KB", 
    "20003": "3.3KB", 
    "4241": "3.2KB", 
    "2142": "3.2KB", 
    "1027": "2.3KB", 
    "4077": "1018B", 
    "2072": "459B", 
    "2172": "108B", 
    "2132": "78B"
}

{
    "GOGCCHK_": {
        "inQZIP": true, 
        "ids": {
            "19001": 218
        }
    }, 
    "NOCHK___": {
        "inQZIP": true, 
        "ids": {
            "19000": 1156
        }
    }, 
    "SBCHK___": {  // scripts
        "inQZIP": true, 
        "ids": {
            "63": 855
        }
    }, 
    "COM_CONT": {
        "inQZIP": false, 
        "ids": {
            "1016": 1327, 
            "1022": 445, 
            "18002": 128, 
            "3": 2649, 
            "1030": 128, 
            "4234": 46, 
            "15000": 48, 
            "2033": 24562, 
            "4288": 5479, 
            "1023": 23, 
            "2142": 47, 
            "4091": 80976, 
            "4137": 6, 
            "4333": 6, 
            "4254": 68, 
            "20003": 74, 
            "2094": 1, 
            "2132": 1, 
            "2137": 1, 
            "4077": 1, 
            "2172": 1, 
            "2072": 1
        }
    }, 
    "DC_INFO ": {
        "inQZIP": true, 
        "ids": {
            "29": 732
        }
    }, 
    "CSNDEVNT": {  // sound events
        "inQZIP": true, 
        "ids": {
            "1023": 11564, 
            "1031": 6747
        }
    }, 
    "CSNDRTPC": {  // smth with sound
        "inQZIP": true, 
        "ids": {
            "1025": 119
        }
    }, 
    "CSNDSWTC": {  // sound to material map?
        "inQZIP": true, 
        "ids": {
            "1026": 77
        }
    }, 
    "segs\u0001": {  // contains compressed data, BIKs
        "inQZIP": false, 
        "ids": {
            "29": 2533
        }
    }, 
    "ETF_RAW_": {  // gzipped data? 
        "inQZIP": true, 
        "ids": {
            "2229": 49016
        }
    }, 
    "ETF_RAWL": {  // gzipped data? also contains "segs"
        "inQZIP": true, 
        "ids": {
            "2230": 78923
        }
    }, 
    "VCCI_CHK": {  // a lot of variables, mb shader bindings?
        "inQZIP": true, 
        "ids": {
            "42": 12
        }
    }, 
    "GMK_COMG": {
        "inQZIP": true, 
        "ids": {
            "4241": 46
        }
    }, 
    "NAVM____": {
        "inQZIP": true, 
        "ids": {
            "14000": 79
        }
    }, 
    "EVENTS__": {  // some string events
        "inQZIP": true, 
        "ids": {
            "2212": 24555
        }
    }, 
    "MOGRAEMU": {  // high-entropy bin data
        "inQZIP": true, 
        "ids": {
            "14014": 15
        }
    }, 
    "CSNDSTAT": {  // some sound states
        "inQZIP": true, 
        "ids": {
            "1027": 27
        }
    }, 
    "CSNDDATA": {  // wave sound data with 0xFFFF codec
        "inQZIP": true, 
        "ids": {
            "1033": 80976
        }
    }, 
    "PTGRAPH_": {  // some graph
        "inQZIP": true, 
        "ids": {
            "14003": 12
        }
    }, 
    "FINALIZE": {  // smath with COLOR & GRAIN
        "inQZIP": true, 
        "ids": {
            "2226": 64
        }
    }, 
    "RAW_FILE": {  // MIDI files
        "inQZIP": true, 
        "ids": {
            "65": 4
        }
    }
}
'''