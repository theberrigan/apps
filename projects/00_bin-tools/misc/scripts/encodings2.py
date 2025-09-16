for charCode in range(0x80, 0x100):
    charByte = bytes([ charCode ])

    try:
        char = charByte.decode('cp866')
    except:
        # print('Skip', charCode)
        continue

    uniCharBytes = char.encode('utf-16le')

    assert len(uniCharBytes) == 2

    uniCharCode = int.from_bytes(uniCharBytes, 'little', signed=False)

    print(f'    \'\\u{uniCharCode:04X}\': 0x{charCode:02X},')