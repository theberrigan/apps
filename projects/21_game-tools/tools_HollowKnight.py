# Hollow Knight Tools

from base64 import b64decode

# pip install cryptography
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

from deps.utils import *
from deps.reader import *



SAVE_DIR = r'C:\Users\Berrigan\AppData\LocalLow\Team Cherry\Hollow Knight'
ENCRYPTION_KEY = 'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'.encode('utf-8')



def decrypt (data):
    algorithm = algorithms.AES(ENCRYPTION_KEY)
    decryptor = Cipher(algorithm, modes.ECB(), default_backend()).decryptor()
    unpadder  = padding.PKCS7(algorithm.block_size).unpadder()

    data = decryptor.update(data)
    data = unpadder.update(data) + unpadder.finalize()

    return data

def decodeSaveFile (filePath):
    with openFile(filePath) as f:
        f.seek(25)

        dataSize = f.remaining() - 1

        data = f.read(dataSize)
        data = b64decode(data)
        data = decrypt(data)
        data = data.decode('utf-8')
        data = parseJson(data)

        writeJson(filePath + '.json', data, True)



if __name__ == '__main__':
    decodeSaveFile(joinPath(SAVE_DIR, 'user1.dat'))