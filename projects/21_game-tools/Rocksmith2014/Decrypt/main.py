"""
Rocksmith 2014 CLI tools
"""

import os
import zlib
from hashlib import md5
from io import BytesIO

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from construct import (
    Adapter,
    Bytes,
    BytesInteger,
    Const,
    Construct,
    GreedyRange,
    Int16ub,
    Int32ub,
    Int32ul,
    Struct,
    this,
)

# -------------------------------------------------------------------------------------------------------------------------

ARC_KEY = bytes.fromhex("C53DB23870A1A2F71CAE64061FDD0E1157309DC85204D4C5BFDF25090DF2572C")
ARC_IV = bytes.fromhex("E915AA018FEF71FC508132E4BB4CEB42")
ARC_CIPHER = Cipher(algorithms.AES(ARC_KEY), modes.CFB(ARC_IV))
MAC_KEY = bytes.fromhex("9821330E34B91F70D0A48CBD625993126970CEA09192C0E6CDA676CC9838289D")
WIN_KEY = bytes.fromhex("CB648DF3D12A16BF71701414E69619EC171CCA5D2A142E3E59DE7ADDA18A3A30")
PRF_KEY = bytes.fromhex("728B369E24ED0134768511021812AFC0A3C25D02065F166B4BCC58CD2644F29E")
CONFIG_KEY = bytes.fromhex("378B9026EE7DE70B8AF124C1E30978670F9EC8FD5E7285A86442DD73068C0473")

def decrypt_bom(data):
    decryptor = ARC_CIPHER.decryptor()
    return decryptor.update(data) + decryptor.finalize()


def encrypt_bom(data):
    encryptor = ARC_CIPHER.encryptor()
    return encryptor.update(data) + encryptor.finalize()


def aes_sng(key, iv):
    return Cipher(algorithms.AES(key), modes.CTR(iv))


def decrypt_sng(data, key):
    iv, data = data[8:24], data[24:]
    decryptor = aes_sng(key, iv).decryptor()
    decrypted = decryptor.update(data) + decryptor.finalize()
    length, payload = Int32ul.parse(decrypted[:4]), decrypted[4:]
    payload = zlib.decompress(payload)
    assert len(payload) == length
    return payload


def encrypt_sng(data, key):
    header = Int32ul.build(74) + Int32ul.build(3)
    iv = bytes(16)
    payload = Int32ul.build(len(data))
    payload += zlib.compress(data, zlib.Z_BEST_COMPRESSION)
    encryptor = aes_sng(key, iv).encryptor()
    encrypted = encryptor.update(payload) + encryptor.finalize()
    return header + iv + encrypted + bytes(56)


def decrypt_psarc(content):
    # TODO: profile, config
    content = content.copy()
    for k in content:
        if "songs/bin/macos/" in k:
            content[k] = decrypt_sng(content[k], MAC_KEY)
        elif "songs/bin/generic/" in k:
            content[k] = decrypt_sng(content[k], WIN_KEY)
    return content


def encrypt_psarc(content):
    # TODO: profile, config
    content = content.copy()
    for k in content:
        if "songs/bin/macos/" in k:
            content[k] = encrypt_sng(content[k], MAC_KEY)
        elif "songs/bin/generic/" in k:
            content[k] = encrypt_sng(content[k], WIN_KEY)
    return content

# -------------------------------------------------------------------------------------------------------------------------

ENTRY = Struct(
    "md5" / Bytes(16),
    "zindex" / Int32ub,
    "length" / BytesInteger(5),
    "offset" / BytesInteger(5),
)


class BOMAdapter(Adapter):
    def _encode(self, obj, context, path):
        data = Struct(
            "entries" / ENTRY[context.n_entries], "zlength" / GreedyRange(Int16ub)
        ).build(obj)
        return encrypt_bom(data)

    def _decode(self, obj, context, path):
        data = decrypt_bom(obj)
        return Struct(
            "entries" / ENTRY[context.n_entries], "zlength" / GreedyRange(Int16ub)
        ).parse(data)


VERSION = 65540
ENTRY_SIZE = ENTRY.sizeof()
BLOCK_SIZE = 2 ** 16
ARCHIVE_FLAGS = 4

HEADER = Struct(
    "MAGIC" / Const(b"PSAR"),
    "VERSION" / Const(Int32ub.build(VERSION)),
    "COMPRESSION" / Const(b"zlib"),
    "header_size" / Int32ub,
    "ENTRY_SIZE" / Const(Int32ub.build(ENTRY_SIZE)),
    "n_entries" / Int32ub,
    "BLOCK_SIZE" / Const(Int32ub.build(BLOCK_SIZE)),
    "ARCHIVE_FLAGS" / Const(Int32ub.build(ARCHIVE_FLAGS)),
    "bom" / BOMAdapter(Bytes(this.header_size - 32)),
)


def read_entry(stream, n, bom):
    entry = bom.entries[n]
    stream.seek(entry.offset)
    zlength = bom.zlength[entry.zindex :]

    # print(zlength)

    data = BytesIO()
    length = 0
    for z in zlength:
        if length == entry.length:
            break

        # print(stream.tell(), z)

        chunk = stream.read(BLOCK_SIZE if z == 0 else z)
        try:
            chunk = zlib.decompress(chunk)
        except zlib.error:
            print(entry.length)
            pass

        data.write(chunk)
        length += len(chunk)

    data = data.getvalue()
    assert len(data) == entry.length
    print('-' * 100)
    return data


def create_entry(name, data):
    zlength = []
    output = BytesIO()

    for i in range(0, len(data), BLOCK_SIZE):
        raw = data[i : i + BLOCK_SIZE]
        compressed = zlib.compress(raw, zlib.Z_BEST_COMPRESSION)
        if len(compressed) < len(raw):
            output.write(compressed)
            zlength.append(len(compressed))
        else:
            output.write(raw)
            zlength.append(len(raw) % BLOCK_SIZE)

    return {
        "md5": md5(name.encode()).digest() if name != "" else bytes(16),
        "zlength": zlength,
        "length": len(data),
        "data": output.getvalue(),
    }


def create_bom(entries):
    offset, zindex, zlength = 0, 0, []
    for entry in entries:
        entry["offset"] = offset
        entry["zindex"] = zindex
        offset += len(entry["data"])
        zindex += len(entry["zlength"])
        zlength += entry["zlength"]

    header_size = 32 + ENTRY_SIZE * len(entries) + 2 * len(zlength)
    for entry in entries:
        entry["offset"] += header_size

    return {"entries": entries, "zlength": zlength, "header_size": header_size}


class PSARC(Construct):
    def __init__(self, crypto=True):
        self.crypto = crypto
        super().__init__()

    def _parse(self, stream, context, path):
        header = HEADER.parse_stream(stream)
        listing, *entries = [
            read_entry(stream, i, header.bom) for i in range(header.n_entries)
        ]
        listing = listing.decode().splitlines()
        content = dict(zip(listing, entries))
        if self.crypto:
            content = decrypt_psarc(content)
        return content

    def _build(self, content, stream, context, path):
        if self.crypto:
            content = encrypt_psarc(content)

        names = list(sorted(content.keys(), reverse=True))
        data = ["\n".join(names).encode()] + [content[k] for k in names]

        entries = [create_entry(n, e) for n, e in zip([""] + names, data)]
        bom = create_bom(entries)

        header = HEADER.build(
            {"header_size": bom["header_size"], "n_entries": len(entries), "bom": bom}
        )

        stream.write(header)
        for e in entries:
            stream.write(e["data"])

# -------------------------------------------------------------------------------------------------------------------------


def path2dict(path):
    n = len(path) + 1
    d = {}
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            fullpath = os.path.join(dirpath, filename)
            with open(fullpath, "rb") as fh:
                d[fullpath[n:]] = fh.read()
    return d


def dict2path(d, dest="."):
    for filepath, data in d.items():
        filename = os.path.join(dest, filepath)
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(filename, "wb") as fh:
            fh.write(data)


def unpack(filename, crypto):
    with open(filename, "rb") as fh:
        content = PSARC(crypto).parse_stream(fh)
    # print(content.keys())
    # destdir = os.path.splitext(os.path.basename(filename))[0]
    # dict2path(content, destdir)


def pack(directory, crypto):
    content = path2dict(directory)
    dest = os.path.basename(directory) + ".psarc"
    with open(dest, "wb") as fh:
        PSARC(crypto).build_stream(content, fh)


# unpack(r'G:\Steam\steamapps\common\Rocksmith2014\cache.psarc', True)
pack(r'G:\Steam\steamapps\common\Rocksmith2014\_PSARCs\my\cache.psarc_extracted\cache', True)