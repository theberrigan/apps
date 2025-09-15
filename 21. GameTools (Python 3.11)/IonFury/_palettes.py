PALETTES = [
    {
        "type": "nofloorpalrange",
        "values": [ 1, 255 ]
    },

    {
        "id": 0,  # set paletteloaded |= PALETTE_MAIN
        "type": "basepalette",
        "path": "/palette/basepalette_000.raw"
    },
    {
        "id": 3,
        "type": "basepalette",
        "path": "/palette/3dr_480.raw"
    },

    # shade table
    {
        "id": 0,
        "type": "palookup",
        "path": "/palette/palookup_000.raw"
    },

    # 1/3 Alpha
    {
        "id": 0,
        "type": "blendtable",
        "path": "/palette/blendtable_000.raw"
    },

    # x/64 Alpha
    {
        "id": 1,
        "type": "blendtable",
        "path": "/palette/blendtable_001.raw"
    },
    {
        "id": 2,
        "type": "blendtable",
        "path": "/palette/blendtable_002.raw"
    },
    {
        "id": 3,
        "type": "blendtable",
        "path": "/palette/blendtable_003.raw"
    },
    {
        "id": 4,
        "type": "blendtable",
        "path": "/palette/blendtable_004.raw"
    },
    {
        "id": 5,
        "type": "blendtable",
        "path": "/palette/blendtable_005.raw"
    },
    {
        "id": 6,
        "type": "blendtable",
        "path": "/palette/blendtable_006.raw"
    },
    {
        "id": 7,
        "type": "blendtable",
        "path": "/palette/blendtable_007.raw"
    },
    {
        "id": 8,
        "type": "blendtable",
        "path": "/palette/blendtable_008.raw"
    },
    {
        "id": 9,
        "type": "blendtable",
        "path": "/palette/blendtable_009.raw"
    },
    {
        "id": 10,
        "type": "blendtable",
        "path": "/palette/blendtable_010.raw"
    },
    {
        "id": 11,
        "type": "blendtable",
        "path": "/palette/blendtable_011.raw"
    },
    {
        "id": 12,
        "type": "blendtable",
        "path": "/palette/blendtable_012.raw"
    },
    {
        "id": 13,
        "type": "blendtable",
        "path": "/palette/blendtable_013.raw"
    },
    {
        "id": 14,
        "type": "blendtable",
        "path": "/palette/blendtable_014.raw"
    },
    {
        "id": 15,
        "type": "blendtable",
        "path": "/palette/blendtable_015.raw"
    },
    {
        "id": 16,
        "type": "blendtable",
        "path": "/palette/blendtable_016.raw"
    },
    {
        "id": 17,
        "type": "blendtable",
        "path": "/palette/blendtable_017.raw"
    },
    {
        "id": 18,
        "type": "blendtable",
        "path": "/palette/blendtable_018.raw"
    },
    {
        "id": 19,
        "type": "blendtable",
        "path": "/palette/blendtable_019.raw"
    },
    {
        "id": 20,
        "type": "blendtable",
        "path": "/palette/blendtable_020.raw"
    },
    {
        "id": 21,
        "type": "blendtable",
        "path": "/palette/blendtable_021.raw"
    },
    {
        "id": 20,
        "type": "blendtable",
        "path": "/palette/blendtable_020.raw"
    },
    {
        "id": 21,
        "type": "blendtable",
        "path": "/palette/blendtable_021.raw"
    },
    {
        "id": 22,
        "type": "blendtable",
        "path": "/palette/blendtable_022.raw"
    },
    {
        "id": 23,
        "type": "blendtable",
        "path": "/palette/blendtable_023.raw"
    },
    {
        "id": 24,
        "type": "blendtable",
        "path": "/palette/blendtable_024.raw"
    },
    {
        "id": 25,
        "type": "blendtable",
        "path": "/palette/blendtable_025.raw"
    },
    {
        "id": 26,
        "type": "blendtable",
        "path": "/palette/blendtable_026.raw"
    },
    {
        "id": 27,
        "type": "blendtable",
        "path": "/palette/blendtable_027.raw"
    },
    {
        "id": 28,
        "type": "blendtable",
        "path": "/palette/blendtable_028.raw"
    },
    {
        "id": 29,
        "type": "blendtable",
        "path": "/palette/blendtable_029.raw"
    },
    {
        "id": 30,
        "type": "blendtable",
        "path": "/palette/blendtable_030.raw"
    },
    {
        "id": 31,
        "type": "blendtable",
        "path": "/palette/blendtable_031.raw"
    },

    {
        "type": "numalphatables",
        "value": 31
    },

    # Screen
    {
        "id": 129,
        "type": "blendtable",
        "path": "/palette/blendtable_129.raw",
        "blend": [ "ONE", "ONE_MINUS_SRC_COLOR" ]
    },

    # Multiply
    {
        "id": 130,
        "type": "blendtable",
        "path": "/palette/blendtable_130.raw",
        "blend": [ "ZERO", "SRC_COLOR" ]
    },

    # Additive (100% intensity)
    {
        "id": 255,
        "type": "blendtable",
        "path": "/palette/blendtable_255.raw",
        "blend": [ "ONE", "ONE" ]
    },

    {
        "id": 1,
        "type": "basepalette",
        "path": "/palette/basepalette_001.raw"
    },
    {
        "id": 2,
        "type": "basepalette",
        "path": "/palette/basepalette_002.raw"
    },
    {
        "id": 7,
        "type": "basepalette",
        "path": "/palette/basepalette_007.raw"
    },
    {
        "id": 8,
        "type": "basepalette",
        "path": "/palette/basepalette_008.raw"
    },

    {
        "id": 1,
        "type": "palookup",
        "path": "/palette/palookup_001.raw"
    },
    {
        "id": 2,
        "type": "palookup",
        "path": "/palette/palookup_002.raw"
    },
    {
        "id": 3,
        "type": "palookup",
        "path": "/palette/palookup_003.raw"
    },
    {
        "id": 4,
        "type": "palookup",
        "path": "/palette/palookup_004.raw"
    },
    {
        "id": 5,
        "type": "palookup",
        "path": "/palette/palookup_005.raw"
    },
    {
        "id": 6,
        "type": "palookup",
        "path": "/palette/palookup_006.raw"
    },
    {
        "id": 7,
        "type": "palookup",
        "path": "/palette/palookup_007.raw"
    },
    {
        "id": 8,
        "type": "palookup",
        "path": "/palette/palookup_008.raw"
    },
    {
        "id": 9,
        "type": "palookup",
        "path": "/palette/palookup_009.raw"
    },
    {
        "id": 10,
        "type": "palookup",
        "path": "/palette/palookup_010.raw"
    },
    {
        "id": 11,
        "type": "palookup",
        "path": "/palette/palookup_011.raw"
    },
    {
        "id": 12,
        "type": "palookup",
        "path": "/palette/palookup_012.raw"
    },
    {
        "id": 13,
        "type": "palookup",
        "path": "/palette/palookup_013.raw"
    },
    {
        "id": 14,
        "type": "palookup",
        "path": "/palette/palookup_014.raw"
    },
    {
        "id": 15,
        "type": "palookup",
        "path": "/palette/palookup_015.raw"
    },
    {
        "id": 16,
        "type": "palookup",
        "path": "/palette/palookup_016.raw"
    },
    {
        "id": 17,
        "type": "palookup",
        "path": "/palette/palookup_017.raw"
    },
    {
        "id": 18,
        "type": "palookup",
        "path": "/palette/palookup_018.raw"
    },
    {
        "id": 19,
        "type": "palookup",
        "path": "/palette/palookup_019.raw"
    },
    {
        "id": 20,
        "type": "palookup",
        "path": "/palette/palookup_020.raw"
    },
    {
        "id": 21,
        "type": "palookup",
        "path": "/palette/palookup_021.raw"
    },
    {
        "id": 22,
        "type": "palookup",
        "path": "/palette/palookup_022.raw"
    },
    {
        "id": 23,
        "type": "palookup",
        "path": "/palette/palookup_023.raw"
    },
    {
        "id": 25,
        "type": "palookup",
        "path": "/palette/palookup_025.raw"
    },
    {
        "id": 26,
        "type": "palookup",
        "path": "/palette/palookup_026.raw"
    },
    {
        "id": 27,
        "type": "palookup",
        "path": "/palette/palookup_027.raw"
    },
    {
        "id": 28,
        "type": "palookup",
        "path": "/palette/palookup_028.raw"
    },
    {
        "id": 29,
        "type": "palookup",
        "path": "/palette/palookup_029.raw"
    },
    {
        "id": 30,
        "type": "palookup",
        "path": "/palette/palookup_030.raw"
    },
    {
        "id": 31,
        "type": "palookup",
        "path": "/palette/palookup_031.raw"
    },
    {
        "id": 32,
        "type": "palookup",
        "path": "/palette/palookup_032.raw"
    },
    {
        "id": 33,
        "type": "palookup",
        "path": "/palette/palookup_033.raw"
    },
    {
        "id": 34,
        "type": "palookup",
        "path": "/palette/palookup_034.raw"
    },
    {
        "id": 35,
        "type": "palookup",
        "path": "/palette/palookup_035.raw"
    },
    {
        "id": 37,
        "type": "palookup",
        "copy": 25
    },
    {
        "id": 38,
        "type": "palookup",
        "path": "/palette/palookup_038.raw"
    },
    {
        "id": 39,
        "type": "palookup",
        "path": "/palette/palookup_039.raw"
    },
    {
        "id": 40,
        "type": "palookup",
        "path": "/palette/palookup_040.raw"
    },
    {
        "id": 41,
        "type": "palookup",
        "path": "/palette/palookup_041.raw"
    },
    {
        "id": 42,
        "type": "palookup",
        "copy": 1,
        "floorpal": True
    },
    {
        "id": 43,
        "type": "palookup",
        "copy": 2,
        "floorpal": True
    },
    {
        "id": 44,
        "type": "palookup",
        "copy": 3,
        "floorpal": True
    },
    {
        "id": 45,
        "type": "palookup",
        "copy": 4,
        "floorpal": True
    },
    {
        "id": 46,
        "type": "palookup",
        "copy": 5,
        "floorpal": True
    },
    {
        "id": 47,
        "type": "palookup",
        "copy": 6,
        "floorpal": True
    },
    {
        "id": 48,
        "type": "palookup",
        "copy": 7,
        "floorpal": True
    },
    {
        "id": 49,
        "type": "palookup",
        "copy": 8,
        "floorpal": True
    },
    {
        "id": 50,
        "type": "palookup",
        "copy": 9,
        "floorpal": True
    },
    {
        "id": 51,
        "type": "palookup",
        "copy": 10,
        "floorpal": True
    },
    {
        "id": 52,
        "type": "palookup",
        "copy": 11,
        "floorpal": True
    },
    {
        "id": 53,
        "type": "palookup",
        "copy": 12,
        "floorpal": True
    },
    {
        "id": 54,
        "type": "palookup",
        "path": "/palette/palookup_054.raw"
    },
    {
        "id": 55,
        "type": "palookup",
        "path": "/palette/palookup_055.raw"
    },
    {
        "id": 56,
        "type": "palookup",
        "path": "/palette/palookup_056.raw"
    },
    {
        "id": 57,
        "type": "palookup",
        "path": "/palette/palookup_057.raw"
    },
    {
        "id": 58,
        "type": "palookup",
        "path": "/palette/palookup_058.raw"
    },
    {
        "id": 59,
        "type": "palookup",
        "path": "/palette/palookup_059.raw"
    },
    {
        "id": 60,
        "type": "palookup",
        "path": "/palette/palookup_060.raw"
    },
    {
        "id": 61,
        "type": "palookup",
        "path": "/palette/palookup_061.raw"
    },
    {
        "id": 62,
        "type": "palookup",
        "path": "/palette/palookup_062.raw"
    },
    {
        "id": 63,
        "type": "palookup",
        "path": "/palette/palookup_063.raw"
    },
    {
        "id": 64,
        "type": "palookup",
        "path": "/palette/palookup_064.raw"
    },
    {
        "id": 65,
        "type": "palookup",
        "path": "/palette/palookup_065.raw"
    },
    {
        "id": 66,
        "type": "palookup",
        "path": "/palette/palookup_066.raw"
    },
    {
        "id": 67,
        "type": "palookup",
        "path": "/palette/palookup_067.raw"
    },
    {
        "id": 68,
        "type": "palookup",
        "path": "/palette/palookup_068.raw"
    },
    {
        "id": 69,
        "type": "palookup",
        "path": "/palette/palookup_069.raw"
    },
    {
        "id": 70,
        "type": "palookup",
        "path": "/palette/palookup_070.raw"
    },
    {
        "id": 71,
        "type": "palookup",
        "path": "/palette/palookup_071.raw"
    },
    {
        "id": 72,
        "type": "palookup",
        "path": "/palette/palookup_072.raw"
    },
    {
        "id": 73,
        "type": "palookup",
        "path": "/palette/palookup_073.raw"
    },
    {
        "id": 74,
        "type": "palookup",
        "path": "/palette/palookup_074.raw"
    },
    {
        "id": 75,
        "type": "palookup",
        "path": "/palette/palookup_075.raw"
    },
    {
        "id": 76,
        "type": "palookup",
        "path": "/palette/palookup_076.raw"
    },
    {
        "id": 77,
        "type": "palookup",
        "path": "/palette/palookup_077.raw"
    },
    {
        "id": 77,
        "type": "palookup",
        "path": "/palette/palookup_077.raw"
    },
    {
        "id": 78,
        "type": "palookup",
        "path": "/palette/palookup_078.raw"
    },
    {
        "id": 79,
        "type": "palookup",
        "path": "/palette/palookup_079.raw"
    },
    {
        "id": 80,
        "type": "palookup",
        "path": "/palette/palookup_080.raw"
    },
    {
        "id": 81,
        "type": "palookup",
        "path": "/palette/palookup_081.raw"
    },
    {
        "id": 82,
        "type": "palookup",
        "path": "/palette/palookup_082.raw"
    },
    {
        "id": 83,
        "type": "palookup",
        "path": "/palette/palookup_083.raw"
    },
    {
        "id": 84,
        "type": "palookup",
        "path": "/palette/palookup_084.raw"
    },
    {
        "id": 85,
        "type": "palookup",
        "path": "/palette/palookup_085.raw"
    },
    {
        "id": 86,
        "type": "palookup",
        "path": "/palette/palookup_086.raw"
    },
    {
        "id": 87,
        "type": "palookup",
        "path": "/palette/palookup_087.raw"
    },
    {
        "id": 88,
        "type": "palookup",
        "path": "/palette/palookup_088.raw"
    },
    {
        "id": 89,
        "type": "palookup",
        "path": "/palette/palookup_089.raw"
    },
    {
        "id": 90,
        "type": "palookup",
        "path": "/palette/palookup_090.raw"
    },
    {
        "id": 91,
        "type": "palookup",
        "path": "/palette/palookup_091.raw"
    },
    {
        "id": 92,
        "type": "palookup",
        "path": "/palette/palookup_092.raw"
    },
    {
        "id": 93,
        "type": "palookup",
        "path": "/palette/palookup_093.raw"
    },
    {
        "id": 94,
        "type": "palookup",
        "path": "/palette/palookup_094.raw"
    },
    {
        "id": 95,
        "type": "palookup",
        "path": "/palette/palookup_095.raw"
    },
    {
        "id": 96,
        "type": "palookup",
        "path": "/palette/palookup_096.raw"
    },
    {
        "id": 97,
        "type": "palookup",
        "path": "/palette/palookup_097.raw"
    },
    {
        "id": 98,
        "type": "palookup",
        "path": "/palette/palookup_098.raw"
    },
    {
        "id": 99,
        "type": "palookup",
        "path": "/palette/palookup_099.raw"
    },
    {
        "id": 100,
        "type": "palookup",
        "path": "/palette/palookup_100.raw"
    },
    {
        "id": 101,
        "type": "palookup",
        "path": "/palette/palookup_101.raw"
    },
    {
        "id": 102,
        "type": "palookup",
        "path": "/palette/palookup_102.raw"
    },
    {
        "id": 103,
        "type": "palookup",
        "path": "/palette/palookup_103.raw"
    },
    {
        "id": 104,
        "type": "palookup",
        "path": "/palette/palookup_104.raw"
    },
    {
        "id": 105,
        "type": "palookup",
        "path": "/palette/palookup_105.raw"
    },
    {
        "id": 106,
        "type": "palookup",
        "path": "/palette/palookup_106.raw"
    },
    {
        "id": 107,
        "type": "palookup",
        "path": "/palette/palookup_107.raw"
    },
    {
        "id": 108,
        "type": "palookup",
        "path": "/palette/palookup_108.raw"
    },
    {
        "id": 109,
        "type": "palookup",
        "path": "/palette/palookup_109.raw"
    },
    {
        "id": 110,
        "type": "palookup",
        "path": "/palette/palookup_110.raw"
    },
    {
        "id": 117,
        "type": "palookup",
        "path": "/palette/palookup_117.raw"
    },
    {
        "id": 118,
        "type": "palookup",
        "path": "/palette/palookup_118.raw",
        "floorpal": True
    },
    {
        "type": "makepalookup",
        "pal": 118,
        "color": [ 255, 255, 255 ],
        "remapself": True
    },
    {
        "id": 119,
        "type": "palookup",
        "path": "/palette/palookup_119.raw",
        "floorpal": True
    },
    {
        "id": 120,
        "type": "palookup",
        "path": "/palette/palookup_120.raw",
        "floorpal": True
    },
    {
        "id": 121,
        "type": "palookup",
        "path": "/palette/palookup_121.raw",
        "floorpal": True
    },
    {
        "type": "makepalookup",
        "pal": 121,
        "color": [ 255, 255, 255 ],
        "remapself": True
    },
    {
        "id": 122,
        "type": "palookup",
        "path": "/palette/palookup_122.raw",
        "floorpal": True
    },
    {
        "id": 123,
        "type": "palookup",
        "path": "/palette/palookup_123.raw",
        "floorpal": True
    },
    {
        "id": 124,
        "type": "palookup",
        "path": "/palette/palookup_124.raw",
        "floorpal": True
    },        
    {
        "type": "makepalookup",
        "pal": 124,
        "color": [ 255, 255, 255 ],
        "remapself": True
    },
    {
        "id": 125,
        "type": "palookup",
        "path": "/palette/palookup_125.raw"
    },
    {
        "id": 126,
        "type": "palookup",
        "path": "/palette/palookup_126.raw"
    },
    {
        "id": 127,
        "type": "palookup",
        "path": "/palette/palookup_127.raw"
    },
    {
        "id": 128,
        "type": "palookup",
        "path": "/palette/palookup_128.raw"
    },
    {
        "id": 129,
        "type": "palookup",
        "path": "/palette/palookup_129.raw"
    },
    {
        "id": 130,
        "type": "palookup",
        "path": "/palette/palookup_130.raw"
    },
    {
        "id": 131,
        "type": "palookup",
        "path": "/palette/palookup_131.raw"
    },
    {
        "id": 132,
        "type": "palookup",
        "path": "/palette/palookup_132.raw"
    },
    {
        "id": 133,
        "type": "palookup",
        "path": "/palette/palookup_133.raw"
    },
    {
        "id": 134,
        "type": "palookup",
        "path": "/palette/palookup_134.raw"
    },
    {
        "id": 135,
        "type": "palookup",
        "path": "/palette/palookup_135.raw"
    },
    {
        "id": 136,
        "type": "palookup",
        "path": "/palette/palookup_136.raw"
    },
    {
        "id": 137,
        "type": "palookup",
        "path": "/palette/palookup_137.raw"
    },
    {
        "id": 138,
        "type": "palookup",
        "path": "/palette/palookup_138.raw"
    },
    {
        "id": 139,
        "type": "palookup",
        "path": "/palette/palookup_139.raw"
    },
    {
        "id": 140,
        "type": "palookup",
        "path": "/palette/palookup_140.raw"
    },
    {
        "id": 141,
        "type": "palookup",
        "path": "/palette/palookup_141.raw"
    },
    {
        "id": 142,
        "type": "palookup",
        "path": "/palette/palookup_142.raw"
    },
    {
        "id": 143,
        "type": "palookup",
        "path": "/palette/palookup_143.raw"
    },
    {
        "id": 144,
        "type": "palookup",
        "path": "/palette/palookup_144.raw"
    },
    {
        "id": 145,
        "type": "palookup",
        "path": "/palette/palookup_145.raw"
    },
    {
        "id": 146,
        "type": "palookup",
        "path": "/palette/palookup_146.raw"
    },
    {
        "id": 147,
        "type": "palookup",
        "path": "/palette/palookup_147.raw"
    },
    {
        "id": 148,
        "type": "palookup",
        "path": "/palette/palookup_148.raw"
    },
    {
        "id": 149,
        "type": "palookup",
        "path": "/palette/palookup_149.raw"
    },
    {
        "id": 150,
        "type": "palookup",
        "path": "/palette/palookup_150.raw"
    },
    {
        "id": 151,
        "type": "palookup",
        "path": "/palette/palookup_151.raw"
    },
    {
        "id": 152,
        "type": "palookup",
        "path": "/palette/palookup_152.raw"
    },
    {
        "id": 153,
        "type": "palookup",
        "path": "/palette/palookup_153.raw"
    },
    {
        "id": 154,
        "type": "palookup",
        "path": "/palette/palookup_154.raw"
    },
    {
        "id": 155,
        "type": "palookup",
        "path": "/palette/palookup_155.raw"
    },
    {
        "id": 156,
        "type": "palookup",
        "path": "/palette/palookup_156.raw"
    },
    {
        "id": 157,
        "type": "palookup",
        "path": "/palette/palookup_157.raw"
    },
    {
        "id": 158,
        "type": "palookup",
        "path": "/palette/palookup_158.raw"
    },
    {
        "id": 159,
        "type": "palookup",
        "path": "/palette/palookup_159.raw"
    },
    {
        "id": 160,
        "type": "palookup",
        "path": "/palette/palookup_160.raw"
    },
    {
        "id": 161,
        "type": "palookup",
        "path": "/palette/palookup_161.raw"
    },
    {
        "id": 162,
        "type": "palookup",
        "path": "/palette/palookup_162.raw"
    },
    {
        "id": 163,
        "type": "palookup",
        "path": "/palette/palookup_163.raw"
    },
    {
        "id": 164,
        "type": "palookup",
        "path": "/palette/palookup_164.raw"
    },
    {
        "id": 165,
        "type": "palookup",
        "path": "/palette/palookup_165.raw"
    },
    {
        "id": 166,
        "type": "palookup",
        "path": "/palette/palookup_166.raw"
    },
    {
        "id": 167,
        "type": "palookup",
        "path": "/palette/palookup_167.raw"
    },
    {
        "id": 168,
        "type": "palookup",
        "path": "/palette/palookup_168.raw"
    },
    {
        "id": 169,
        "type": "palookup",
        "path": "/palette/palookup_169.raw"
    },
    {
        "id": 170,
        "type": "palookup",
        "path": "/palette/palookup_170.raw"
    },
    {
        "id": 171,
        "type": "palookup",
        "path": "/palette/palookup_171.raw"
    },
    {
        "id": 172,
        "type": "palookup",
        "path": "/palette/palookup_172.raw"
    },
    {
        "id": 173,
        "type": "palookup",
        "path": "/palette/palookup_173.raw"
    },
    {
        "id": 174,
        "type": "palookup",
        "path": "/palette/palookup_174.raw"
    },
    {
        "id": 175,
        "type": "palookup",
        "path": "/palette/palookup_175.raw"
    },
    {
        "id": 176,
        "type": "palookup",
        "path": "/palette/palookup_176.raw"
    },
    {
        "id": 177,
        "type": "palookup",
        "path": "/palette/palookup_177.raw"
    },
    {
        "id": 178,
        "type": "palookup",
        "path": "/palette/palookup_178.raw"
    },
    {
        "id": 179,
        "type": "palookup",
        "path": "/palette/palookup_179.raw"
    },
    {
        "id": 180,
        "type": "palookup",
        "path": "/palette/palookup_180.raw"
    },
    {
        "id": 181,
        "type": "palookup",
        "path": "/palette/palookup_181.raw"
    },
    {
        "id": 182,
        "type": "palookup",
        "path": "/palette/palookup_182.raw"
    },
    {
        "id": 183,
        "type": "palookup",
        "path": "/palette/palookup_183.raw"
    },

    # Fogpals
    # Bright to dark fog (smog)
    {
        "id": 200,
        "type": "fogpal",
        "color": [ 16, 16, 16 ]
    },
    {
        "id": 201,
        "type": "fogpal",
        "color": [ 8, 8, 8 ]
    },
    {
        "id": 202,
        "type": "fogpal",
        "color": [ 2, 2, 2 ]
    },
    # R G B Y M C - Intense
    {
        "id": 203,
        "type": "fogpal",
        "color": [ 16, 0, 0 ]
    },
    {
        "id": 204,
        "type": "fogpal",
        "color": [ 0, 16, 0 ]
    },
    {
        "id": 205,
        "type": "fogpal",
        "color": [ 0, 0, 16 ]
    },
    {
        "id": 206,
        "type": "fogpal",
        "color": [ 16, 16, 0 ]
    },
    {
        "id": 207,
        "type": "fogpal",
        "color": [ 16, 0, 16 ]
    },
    {
        "id": 208,
        "type": "fogpal",
        "color": [ 0, 16, 16 ]
    },
    # R G B Y M C - Dim
    {
        "id": 209,
        "type": "fogpal",
        "color": [ 8, 0, 0 ]
    },
    {
        "id": 210,
        "type": "fogpal",
        "color": [ 0, 8, 0 ]
    },
    {
        "id": 211,
        "type": "fogpal",
        "color": [ 0, 0, 8 ]
    },
    {
        "id": 212,
        "type": "fogpal",
        "color": [ 8, 8, 0 ]
    },
    {
        "id": 213,
        "type": "fogpal",
        "color": [ 8, 0, 8 ]
    },
    {
        "id": 214,
        "type": "fogpal",
        "color": [ 0, 8, 8 ]
    },

    # Less saturated  R G B Y M C
    # Red
    {
        "id": 215,
        "type": "fogpal",
        "color": [ 16, 8, 8 ]
    },
    {
        "id": 216,
        "type": "fogpal",
        "color": [ 12, 2, 2 ]
    },
    {
        "id": 217,
        "type": "fogpal",
        "color": [ 8, 2, 2 ]
    },
    # Green
    {
        "id": 218,
        "type": "fogpal",
        "color": [ 8, 16, 8 ]
    },
    {
        "id": 219,
        "type": "fogpal",
        "color": [ 2, 12, 2 ]
    },
    {
        "id": 220,
        "type": "fogpal",
        "color": [ 2, 8, 2 ]
    },
    # Blue
    {
        "id": 221,
        "type": "fogpal",
        "color": [ 8, 8, 16 ]
    },
    {
        "id": 222,
        "type": "fogpal",
        "color": [ 2, 2, 12 ]
    },
    {
        "id": 223,
        "type": "fogpal",
        "color": [ 2, 2, 8 ]
    },
    # Yellow
    {
        "id": 224,
        "type": "fogpal",
        "color": [ 16, 16, 8 ]
    },
    {
        "id": 225,
        "type": "fogpal",
        "color": [ 12, 12, 2 ]
    },
    {
        "id": 226,
        "type": "fogpal",
        "color": [ 8, 8, 2 ]
    },
    # Magenta
    {
        "id": 227,
        "type": "fogpal",
        "color": [ 16, 8, 16 ]
    },
    {
        "id": 228,
        "type": "fogpal",
        "color": [ 12, 2, 12 ]
    },
    {
        "id": 229,
        "type": "fogpal",
        "color": [ 8, 2, 8 ]
    },
    # Cyan
    {
        "id": 230,
        "type": "fogpal",
        "color": [ 8, 16, 16 ]
    },
    {
        "id": 231,
        "type": "fogpal",
        "color": [ 2, 12, 12 ]
    },
    {
        "id": 232,
        "type": "fogpal",
        "color": [ 2, 8, 8 ]
    }
]
