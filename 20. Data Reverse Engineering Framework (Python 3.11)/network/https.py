import os
import sys

from http.client import responses as HTTP_RESPONSES

import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *
from bfw.types.enums import Enum2



class HTTPMethod (Enum2):
    GET     = 'GET'
    POST    = 'POST'
    PUT     = 'PUT'
    HEAD    = 'HEAD'
    PATCH   = 'PATCH'
    DELETE  = 'DELETE'
    OPTIONS = 'OPTIONS'


class HTTPResult:
    def __init__ (self):
        self.response = None
        self.errorMsg = None
        self.hasError = False

    def setResponse (self, response):
        self.response = response

        if response is None or response.ok and 200 <= response.status_code <= 399:
            self.errorMsg = None
            self.hasError = False
        else:
            code = response.status_code
            msg  = HTTP_RESPONSES.get(code, 'Unknown error')

            self.errorMsg = f'{ code } { msg }'
            self.hasError = True

    def setErrorMsg (self, errorMsg):
        self.errorMsg = errorMsg
        self.hasError = errorMsg is not None

    def getErrorMsg (self):
        return self.errorMsg

    @property
    def isOk (self):
        return bool(self.response and not self.hasError)

    def getCode (self):
        if self.response:
            return self.response.status_code

        return 0

    def getJson (self):
        result = None
        isOk   = False

        if self.isOk:
            try:
                result = self.response.json()
                isOk   = True
            except Exception as e:
                result = str(e)
                isOk   = False

        return isOk, result

    def getText (self):
        if self.isOk:
            return self.response.text

        return None

    def getContent (self):
        if self.isOk:
            return self.response.content

        return None

    def getEncoding (self):
        if self.isOk:
            return self.response.encoding

        return None




class HTTP:
    @classmethod
    def request (
        cls,
        method,                  # HTTPMethod: GET | OPTIONS | HEAD | POST | PUT | PATCH | DELETE
        url,
        params         = None,   # Dictionary, list of tuples or bytes to send in the query string
        data           = None,   # Dictionary, list of tuples, bytes, or file-like object to send in the body
        json           = None,   # A JSON serializable Python object to send in the body
        files          = None,   # { 'name': file-like-objects } or { 'name': file-tuple }, where file-tuple is ('fileName', fileObj) or ('fileName', fileObj, 'contentType') or ('fileName', fileObj, 'contentType', customHeaders)
        auth           = None,   # Auth tuple to enable Basic/Digest/Custom HTTP Auth
        headers        = None,   # Dictionary of HTTP Headers to send
        cookies        = None,   # Dict or CookieJar object to send
        timeout        = None,   # Float or tuple (connect timeout, read timeout)
        proxies        = None,   # Dictionary mapping protocol to the URL of the proxy
        verify         = True,   # Whether verify the server's TLS certificate: bool or path to a CA bundle
        stream         = False,  # Should content be downloaded immediately
        cert           = None,   # Path to SSL client cert pem-file or tuple ('cert', 'key')
        allowRedirects = True
    ):
        result = HTTPResult()

        method = method.upper()

        assert HTTPMethod.hasValue(method)

        try:
            response = requests.request(
                method          = method,
                url             = url,
                params          = params,
                data            = data,
                json            = json,
                files           = files,
                auth            = auth,
                headers         = headers,
                cookies         = cookies,
                timeout         = timeout,
                proxies         = proxies,
                verify          = verify,
                stream          = stream,
                cert            = stream,
                allow_redirects = allowRedirects
            )

            result.setResponse(response)
        except Exception as e:
            result.setResponse(None)
            result.setErrorMsg(str(e))

        return result

    @classmethod
    def get (cls, *args, **kwargs):
        return cls.request(HTTPMethod.GET, *args, **kwargs)

    @classmethod
    def post (cls, *args, **kwargs):
        return cls.request(HTTPMethod.POST, *args, **kwargs)

    @classmethod
    def put (cls, *args, **kwargs):
        return cls.request(HTTPMethod.PUT, *args, **kwargs)

    @classmethod
    def head (cls, *args, **kwargs):
        return cls.request(HTTPMethod.HEAD, *args, **kwargs)

    @classmethod
    def patch (cls, *args, **kwargs):
        return cls.request(HTTPMethod.PATCH, *args, **kwargs)

    @classmethod
    def delete (cls, *args, **kwargs):
        return cls.request(HTTPMethod.DELETE, *args, **kwargs)

    @classmethod
    def options (cls, *args, **kwargs):
        return cls.request(HTTPMethod.OPTIONS, *args, **kwargs)



def _test_ ():
    # print(HTTP.getMessage(404))

    r = HTTP.get('http://ip.jsontest.com/')

    print(r.isOk)
    print(r.getErrorMsg())

    # isOk, result = r.getContent()

    # if isOk:
    #     print(result)

    print(r.getContent())

    print(r.getEncoding())



__all__ = [
    'HTTP'
]



if __name__ == '__main__':
    _test_()