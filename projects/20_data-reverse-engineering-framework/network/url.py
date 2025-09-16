import os
import sys
import re

from urllib.parse import urlparse, parse_qsl, urlencode

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))) 

from bfw.utils import *


#                             (0 proto        )    (1 loc    )(2 path ) (3 param) (4 h)
URL_ABS_REGEX = re.compile(r'^([a-z\d\-\+\.]+:)\/\/([^\/\?#]+)([^\?#]+)?(\?[^#]*)?(#.*)?$', flags=re.I)

#                             (0 path ) (1 param) (2 h)
URL_REL_REGEX = re.compile(r'^([^\?#]+)?(\?[^#]*)?(#.*)?$', flags=re.I)

#                          ((0 domain      )|(0 IPv4              )|(0 IPv6             ))    (1 p) 
HOST_REGEX = re.compile(r'^((?:[a-z\d\.\-]+)|(?:\d+\.\d+\.\d+\.\d+)|(?:\[[\da-f:\.\/]+\]))(?::(\d*))?$', flags=re.I)

class InvalidURL (Exception):
    pass


class URLParams:
    pass

'''

https://alwinb.github.io/url-specification/
https://url.spec.whatwg.org/

URL is a subset of URI

4248 - Telnet
4266 - Gopher

1738 - Uniform Resource Locators (URL)
    O 4248 - The telnet URI Scheme
    O 4266 - The gopher URI Scheme
    U 1808 - Relative Uniform Resource Locators
        O 3986 - Uniform Resource Identifier (URI): Generic Syntax
            U 6874 - Representing IPv6 Zone Identifiers in Address Literals and Uniform Resource Identifiers
        U 2368 - The mailto URL scheme
            O 6068 - The 'mailto' URI Scheme
        U 2396 - Uniform Resource Identifiers (URI): Generic Syntax
            O 3986 - Uniform Resource Identifier (URI): Generic Syntax
            U 2732 - Format for Literal IPv6 Addresses in URL's
                O 3986 - Uniform Resource Identifier (URI): Generic Syntax
    U 2368 - The mailto URL scheme
    U 2396 - Uniform Resource Identifiers (URI): Generic Syntax
    U 3986 - Uniform Resource Identifier (URI): Generic Syntax
    U 6196 - Moving mailserver: URI Scheme to Historic
    U 6270 - The 'tn3270' URI Scheme
    U 8089 - The "file" URI Scheme

3492 - Punycode: A Bootstring encoding of Unicode for Internationalized Domain Names in Applications (IDNA)
    U 5890 - Internationalized Domain Names for Applications (IDNA): Definitions and Document Framework
    U 5891 - Internationalized Domain Names in Applications (IDNA): Protocol

https://www.rfc-editor.org/rfc/rfc3986.html
https://www.rfc-editor.org/rfc/rfc3987.html

'''

'''
In general:
<url> = <scheme>:<scheme-specific-part>

<url>:
- chars to encode: 0x80-0xFF, 0x00-0x1F, 0x7F, [ <>"#%{}|\\^~[]`]
- a-z0-9$-_.+!*'(),

<scheme>:
- CI
- a-z0-9-+. - allowed, don't encode
- ;/?:@=& - can be reserved in particular scheme, these chars must be encoded

<scheme-specific-part>:
- interpretation depends on the scheme

//<user>:<password>@<host>:<port>/<url-path>

<user>:
- optional
- :@/ must be encoded
- empty user name or password is different than no user name or password

<password>:
- optional with user
- :@/ must be encoded
- there is no way to specify a password without specifying a user name
- empty user name or password is different than no user name or password

Domains names:
- https://www.rfc-editor.org/rfc/rfc1034.html#section-3.5
- https://www.rfc-editor.org/rfc/rfc1123.html#page-13

'''

# https://alwinb.github.io/url-specification/
# https://www.rfc-editor.org/rfc/rfc1738.html
# https://www.rfc-editor.org/rfc/rfc1630.html

# https://docs.python.org/3/library/urllib.parse.html
# protocol://user:password@sub.domain.com:443/path/to/smth?a=1&a=2&q=Hello#hash-string
class URL:
    def __init__ (self, url):
        self._proto       = None
        self._credentials = None
        self._userName    = None
        self._password    = None
        self._host        = None
        self._hostName    = None
        self._port        = None
        self._origin      = None
        self._path        = None
        self._params      = None
        self._hash        = None

        if isinstance(url, URL):
            self._copyFrom(url)
        elif isStr(url):
            self._parseURL(url, False)
        elif url is not None:
            raise Exception('URL must be a string, a URL object or None')

    def __iter__ (self):
        return iter({
            'proto':       self._proto,
            'credentials': self._credentials,
            'userName':    self._userName,
            'password':    self._password,
            'host':        self._host,
            'hostName':    self._hostName,
            'port':        self._port,
            'origin':      self._origin,
            'path':        self._path,
            'params':      self._params,
            'hash':        self._hash,
        }.items())

    @property
    def proto (self):
        return self._proto

    @proto.setter
    def proto (self, proto):
        self._proto  = self._parseProto(proto)
        self._origin = self._buildOrigin()

    @property
    def credentials (self):
        return self._credentials

    @credentials.setter
    def credentials (self, credentials):
        self._userName, \
        self._password    = self._parseCredentials(credentials)
        self._credentials = self._buildCredentials()
        self._origin      = self._buildOrigin()

    @property
    def userName (self):
        return self._userName

    @userName.setter
    def userName (self, userName):
        self._userName    = self._parseUserName(userName)
        self._credentials = self._buildCredentials()
        self._origin      = self._buildOrigin()

    @property
    def password (self):
        return self._password

    @password.setter
    def password (self, password):
        self._password    = self._parsePassword(password)
        self._credentials = self._buildCredentials()
        self._origin      = self._buildOrigin()

    @property
    def host (self):
        return self._host

    @host.setter
    def host (self, host):
        self._hostName, \
        self._port   = self._parseHost(host)
        self._host   = self._buildHost()
        self._origin = self._buildOrigin()

    @property
    def hostName (self):
        return self._hostName

    @hostName.setter
    def hostName (self, hostName):
        self._hostName = self._parseHostName(hostName)
        self._host     = self._buildHost()
        self._origin   = self._buildOrigin()

    @property
    def port (self):
        return self._port

    @port.setter
    def port (self, port):
        self._port   = self._parsePort(port)
        self._host   = self._buildHost()
        self._origin = self._buildOrigin()

    @property
    def origin (self):
        return self._origin

    @origin.setter
    def origin (self, origin):
        self._parseURL(origin, True)

    @property
    def path (self):
        return self._path

    @path.setter
    def path (self, path):
        self._path = self._parsePath(path)

    @property
    def params (self):
        return self._params

    @params.setter
    def params (self, params):
        self._params = self._parseParams(params)

    @property
    def hash (self):
        return self._hash

    @hash.setter
    def hash (self, hash_):
        self._hash = self._parseHash(hash_)

    def _copyFrom (self, url : 'URL'):
        self._proto       = url._proto
        self._credentials = url._credentials
        self._userName    = url._userName
        self._password    = url._password
        self._host        = url._host
        self._hostName    = url._hostName
        self._port        = url._port
        self._origin      = url._origin
        self._path        = url._path
        self._params      = url._params  # TODO: deep copy
        self._hash        = url._hash

    def _parseURL (self, url, originOnly):
        url   = url.strip()

        parts = re.match(URL_ABS_REGEX, url)

        if parts:
            parts = parts.groups()
        else:
            parts = re.match(URL_REL_REGEX, url)

            if parts:
                parts = (None, None) + parts.groups()

        if not parts:
            raise InvalidURL('Invalid URL')

        proto, loc, path, params, hash_ = parts

        self._proto       = self._parseProto(proto)
        self._userName, \
        self._password, \
        self._hostName, \
        self._port        = self._parseLocation(loc)
        self._credentials = self._buildCredentials()
        self._host        = self._buildHost()
        self._origin      = self._buildOrigin()

        if not originOnly:
            self._path   = self._parsePath(path)
            self._params = self._parseParams(params)
            self._hash   = self._parseHash(hash_)        

    def _parseProto (self, proto):
        # TODO: validate proto

        return proto.lower() if proto else None

    def _parseLocation (self, loc):
        loc    = loc.split('@')
        locLen = len(loc)

        if locLen == 1:
            creds = None
            host  = loc[0]
        elif locLen == 2:
            creds = loc[0]
            host  = loc[1]
        else:
            raise InvalidURL('Invalid location')

        return self._parseCredentials(creds) + self._parseHost(host)

    def _parseCredentials (self, creds):
        if creds is None:
            return None, None

        userName = None
        password = None

        if creds:
            creds    = creds.split(':')
            credsLen = len(creds)

            if credsLen == 1:
                userName = creds[0]
                password = None
            elif credsLen == 2:
                userName = creds[0]
                password = creds[1]
            else:
                raise InvalidURL('Invalid credentials')

        return (
            self._parseUserName(userName),
            self._parsePassword(password)
        )

    def _buildCredentials (self):
        userName = self.userName or ''
        password = self.password or ''

        if userName or password:
            return f'{ userName }:{ password }'

        return None

    def _parseUserName (self, userName):
        # TODO: validate user name

        return userName

    def _parsePassword (self, password):
        # TODO: validate password

        return password

    def _parseHost (self, host):
        if host is not None and not isinstance(host, str):
            raise InvalidURL('Invalid host')

        if not host:
            host = ''

        host = host.strip()

        hostName = None
        port     = None

        if host:
            match = re.match(HOST_REGEX, host)

            if not match:
                raise InvalidURL('Invalid host')

            match = match.groups()

            hostName = self._parseHostName(match[0])
            port     = self._parsePort(match[1])

        return hostName, port

    def _buildHost (self):
        host = self.hostName

        if self.port is not None:
            host += f':{ self.port }'
        
        return host

    def _parseHostName (self, hostName):
        # TODO: validate host name
        # TODO: to lower case

        return hostName

    def _parsePort (self, port : int | str | None) -> int | None:
        if port is None:
            return None

        if isStr(port):
            port = port.strip()

            if port.isnumeric():
                port = int(port, 10)
            elif port:
                raise InvalidURL('Invalid port')
            else:
                return None

        if not isInt(port) or not (0 <= port < 0xFFFF):
            raise InvalidURL('Invalid port')

        return port

    def _buildOrigin (self):
        origin = self.proto or ''

        origin += '//'

        creds = self.credentials

        if creds is not None:
            origin += f'{ creds }@'

        origin += self.host

        return origin

    def _parsePath (self, path):
        # TODO: validate path

        return path

    # string, dict, or URLParams
    def _parseParams (self, params):
        # TODO: validate params

        return params

    def _parseHash (self, hash_):
        # TODO: validate hash

        return hash_




def _test_ ():
    url_1 = 'protocol://user:password@sub.domain.com:443/путь/куда/то?a=1&a=2&q=Hello#hash-string'
    url_2 = 'http://[1fff:0:a88:85a3::ac1f]:8001/index.html'
    url_3 = 'http://192.168.0.1:8001/index.html'

    url = URL(url_1)

    print(toJson(dict(url)))

    url = URL(url_2)

    print(toJson(dict(url)))

    url = URL(url_3)

    print(toJson(dict(url)))





__all__ = [

]



if __name__ == '__main__':
    _test_()