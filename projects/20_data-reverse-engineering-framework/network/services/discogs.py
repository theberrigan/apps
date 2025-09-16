import os
import sys

from urllib.parse import urlencode as encodeURL, urlparse as parseURL, parse_qsl as parseQuery

import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))) 

from bfw.utils import *
from bfw.network.browser import Browser



# Request Token URL https://api.discogs.com/oauth/request_token
# Authorize URL     https://www.discogs.com/oauth/authorize
# Access Token URL  https://api.discogs.com/oauth/access_token
APP_CONSUMER_KEY    = ''
APP_CONSUMER_SECRET = ''
APP_OAUTH_CALLBACK  = 'bfw_oauth_cb'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'



class DiscogsAPI:
    @classmethod
    def _request (cls, method, url, secret=None, creds=None, headers=None):
        ts = getTimestamp(False)

        if isinstance(secret, str):
            secret = secret.strip()
        elif secret is None:
            secret = ''
        else:
            raise Exception('Secret must be of type str or None')

        if creds is None:
            creds = {}
        elif not isinstance(creds, dict):
            raise Exception('Credentials must be of type dict or None')

        creds = {
            'oauth_consumer_key':     APP_CONSUMER_KEY,
            'oauth_nonce':            ts,
            'oauth_signature':        APP_CONSUMER_SECRET + '&' + secret,
            'oauth_signature_method': 'PLAINTEXT',
            'oauth_timestamp':        ts,
        } | creds

        creds = [ f'{ k }={ toJson(str(v)) }' for k, v in creds.items() ]
        creds = ','.join(creds)

        if headers is None:
            headers = {}
        elif not isinstance(headers, dict):
            raise Exception('Headers must be of type dict or None')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'OAuth { creds }',
            'User-Agent': USER_AGENT
        } | headers

        try:
            return requests.request(method, url, headers=headers)
        except Exception as e:
            print('Failed to make a request to Discogs API:', e)

        return None

    @classmethod
    def _parseQuery (cls, query):
        if query is None:
            return None

        return dict(parseQuery(query))

    @classmethod
    def auth (cls):
        response = cls._request('GET', 'https://api.discogs.com/oauth/request_token', creds={
            'oauth_callback': APP_OAUTH_CALLBACK
        })

        if not response:
            print('Failed to get token:', response)
            return None

        response = cls._parseQuery(response.text)

        token       = response['oauth_token']
        secret      = response['oauth_token_secret']
        isConfirmed = response['oauth_callback_confirmed'] == 'true'

        if not token or not secret or not isConfirmed:
            print('Unexpected response:', token, secret, isConfirmed)
            return

        print(token, secret)

        url = 'https://discogs.com/oauth/authorize?' + encodeURL({
            'oauth_token': token
        })

        with Browser(url) as browser:
            response = browser.waitUrl(rf'\/{ APP_OAUTH_CALLBACK }')

        print(response)

        if response is None:
            print('Browser response is empty')
            return None

        # response = https://www.discogs.com/oauth/<oauth_callback>?oauth_token=<token>&oauth_verifier=<verifier>
        # response = https://www.discogs.com/oauth/<oauth_callback>?denied=<token>
        response = parseURL(response)
        params   = cls._parseQuery(response.query)

        deniedToken = params.get('denied')

        if deniedToken is not None:
            print('Denied by user:', deniedToken)
            return None

        resToken = params.get('oauth_token')
        verifier = params.get('oauth_verifier')

        print(resToken, verifier)

        if resToken != token or not verifier:
            print('Unexpected browser response:', resToken, verifier)
            return None

        response = cls._request('POST', 'https://api.discogs.com/oauth/access_token', secret=secret, creds={
            'oauth_token':    token,
            'oauth_verifier': verifier
        })

        if not response:
            print('Failed to request token:', response, response.status_code, response.content)
            return

        response = cls._parseQuery(response.text)

        token  = response['oauth_token']
        secret = response['oauth_token_secret']

        return {
            'token': token,
            'secret': secret
        }


def _test_ ():
    authData = DiscogsAPI.auth()

    token  = authData['token']
    secret = authData['secret']

    creds = {
        'oauth_consumer_key':     APP_CONSUMER_KEY,
        'oauth_nonce':            createUUID(),
        'oauth_token':            token,
        'oauth_signature':        APP_CONSUMER_SECRET + '&' + secret,
        'oauth_signature_method': 'PLAINTEXT',
        'oauth_timestamp':        getTimestamp(False)
    }

    creds = ','.join([ f'{ k }="{ v }"' for k, v in creds.items() ])

    response = requests.get('https://api.discogs.com/oauth/identity', headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'OAuth { creds }',
        'User-Agent': USER_AGENT
    })

    if response.ok:
        print(response.content)
    else:        
        print('Failed to request:', response, response.status_code, response.content)
    



__all__ = [

]

# https://api.discogs.com/database/search?q=adele



if __name__ == '__main__':
    _test_()