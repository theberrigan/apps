
def bigint ():
    for byteOrder in [ 'little', 'big' ]:
        for size in [ None, 20 ]:
            for posNum in [
                0,
                1,
                255,
                256,
                0x7FFF,
                0x80FF,
                2 ** 32 - 1,
                2 ** 32,
                2 ** 64 - 1,
                2 ** 64,
                2 ** 128 - 1,
                2 ** 128,
            ]:
                assert posNum >= 0, posNum

                if posNum == 0:
                    nums = [ posNum ]
                else:
                    nums = [ posNum, -posNum ]

                for num in nums:
                    isSigned = num < 0

                    if size is None:
                        curSize = 1
                        enc = None

                        while True:
                            try:
                                enc = num.to_bytes(curSize, byteOrder, signed=isSigned)
                                break
                            except:
                                curSize += 1
                    else:
                        curSize = size
                        enc = num.to_bytes(curSize, byteOrder, signed=isSigned)  # .hex(' ')

                    b = ', 0x'.join(enc.hex(' ').split(' '))
                    bo = str(byteOrder == "big").lower()
                    iss = str(isSigned).lower()

                    print(f'''    num = { num }n;''')
                    if size is None:
                        print(f'''    size = null;''')
                    else:
                        print(f'''    size = { size };''')
                    print(f'''    bigEndian = { bo };''')
                    print(f'''    isSigned = { iss };''')
                    print(f'''    bytes = bigIntToBin(num, size, bigEndian);''')
                    print(f'''    expect(bytes).toEqual(new Uint8Array([ 0x{ b } ]));''')
                    print(f'''    expect(binToBigInt(bytes, isSigned, bigEndian) === num).toBe(true);''')
                    print('')

def copyAnyArrayBuffer ():
    ref = [ 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 ]
    _ref = ', '.join([ str(n) for n in ref ])

    print(f'''    const u8aAB     = new Uint8Array([ { _ref } ]);''')
    print(f'''    const sourceAB  = u8aAB.buffer;''')
    print(f'''    const sourceSAB = new SharedArrayBuffer(u8aAB.byteLength);''')
    print(f'''    const u8aSAB    = new Uint8Array(sourceSAB);''')
    print(f'''    u8aSAB.set(u8aAB);''')
    print(f'')
    print(f'''    let source : ArrayBuffer | SharedArrayBuffer;''')
    print(f'''    let destOffset : number;''')
    print(f'''    let destSize : number;''')
    print(f'''    let sourceOffset : number;''')
    print(f'''    let sourceSize : number;''')
    print(f'''    let forceUnshare : boolean;''')
    print(f'''    let result : ArrayBuffer | SharedArrayBuffer;''')
    print(f'''    let resultU8A : Uint8Array;''')
    print(f'')

    for isShared in [ True, False ]:
        if isShared:
            _source = 'sourceSAB'
        else:
            _source = 'sourceAB'

        for destOffset in [ 0, 2 ]:
            for destSize in [ 8, 12 ]:
                for sourceOffset in [ 4 ]:
                    for sourceSize in [ 6 ]:
                        for forceUnshare in [ True, False ]:
                            _forceUnshare = str(forceUnshare).lower()
                            print(f'''    result = copyAnyArrayBuffer({ _source }, { destOffset }, { destSize }, { sourceOffset }, { sourceSize }, { _forceUnshare });''')
                            print(f'''    resultU8A = new Uint8Array(result);''')

                            if forceUnshare or not isShared:
                                print(f'''    expect(result).toBeInstanceOf(ArrayBuffer);''')
                            else:
                                print(f'''    expect(result).toBeInstanceOf(SharedArrayBuffer);''')

                            curRef = [ 0 ] * destSize

                            for i in range(sourceSize):
                                curRef[destOffset + i] = ref[sourceOffset + i]

                            curRef = ', '.join([ str(n) for n in curRef ])

                            print(f'''    expect(resultU8A).toEqual(new Uint8Array([ { curRef } ]));''')

                            print('')


        # print('')

def numToHex ():
    for posNum in [ 0, 1, 2 ** 8 - 1, 2 ** 8, 2 ** 16 - 1, 2 ** 16, 0xDEADBEEF, 2 ** 32 ]:
        assert isinstance(posNum, int)

        if posNum > 0:
            nums = [ posNum, -posNum ]
        else:
            nums = [ posNum ]

        for num in nums:
            for upperCase in [ False, True ]:
                for byteCount in [ -1, 0, 1, 2, 4, 8 ]:
                    for addPrefix in [ False, True ]:
                        for prefix in [ '', '0x' ]:
                            isNeg  = num < 0
                            numFmt = abs(num)

                            numFmt = f'{numFmt:x}'

                            if byteCount == 0:
                                if len(numFmt) % 2:
                                    numFmt = '0' + numFmt
                            elif byteCount > 0:
                                bc = byteCount * 2
                                numFmt = f'{numFmt:>0{bc}}'

                            if upperCase:
                                numFmt = numFmt.upper()
                            else:
                                numFmt = numFmt.lower()

                            if addPrefix:
                                numFmt = prefix + numFmt

                            if isNeg:
                                numFmt = '-' + numFmt

                            uc = str(upperCase).lower()
                            ap = str(addPrefix).lower()

                            print(f'''    expect(numToHex({num}, { uc }, { byteCount }, { ap }, '{ prefix }')).toEqual('{ numFmt }');''')


def allCPChars (encodings):
    print('''const ENCODED_STRINGS = {''')

    for encoding in encodings:
        charCodes = []

        for charCode in range(256):
            if charCode < 0x80:
                charCodes.append(charCode)
                continue

            try:
                bytes([ charCode ]).decode(encoding)
                charCodes.append(charCode)
            except:
                # print('Skip', charCode)
                continue

        # charCodes = ', '.join([ f'0x{c:02X}' for c in charCodes ])

        print(f'''    '{ encoding }': new Uint8Array([''')

        line = []
        maxIndex = len(charCodes) - 1

        for i, charCode in enumerate(charCodes):
            line.append(charCode)

            if (i + 1) % 16 == 0 or i == maxIndex:
                codes = ', '.join([ f'0x{c:02X}' for c in line ])
                print(f'''        {codes},''')
                line = []

        print(f'''    ]),''')

    print('''};''')

allCPChars([
    'cp866',
    'cp1251',
    'cp1252',
    'utf-16le',
    'utf-16be',
])