import re


def normResPath (resPath):
    resPath = resPath.strip()

    if resPath:
        resPath = re.sub(r'[\\/]+', '/', resPath.lower())

        if resPath[0] == '/':
            resPath = resPath[1:]

    return resPath



def _test_ ():
    somePath1 = '\\\\DaTa\\//Res.Ext'
    somePath2 = 'data/res.ext'

    assert normResPath(somePath1) == somePath2



__all__ = [
    'normResPath',

    '_test_',
]



if __name__ == '__main__':
    _test_()
