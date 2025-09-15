import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) 

from bfw.utils import *



class PCGWAPI:
    _baseUrl = 'https://www.pcgamingwiki.com/w/api.php'

    @classmethod
    def fetchTables (cls, tables, fields):
        if isinstance(tables, str):
            tables = [ tables ]
        elif isinstance(tables, list):
            raise Exception('Tables must be a string or a list of string')

        tables = ','.join(tables)

        fields = [ f.strip() for f in fields if f.strip() ]
        fields = ','.join(fields)

        isOk, payload = HTTP.getJson(cls._baseUrl, params={
            'format': 'json',
            'action': 'cargoquery',
            'tables': tables,
            'fields': fields,
        })

        if not isOk:
            raise payload


        return payload

def _test_ ():
    pass



__all__ = [

]



if __name__ == '__main__':
    _test_()