import os, json, time, requests
from base64 import b64encode

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_url_path='', static_folder='./static')
CORS(app)

# https://tnp-payment.eu.ngrok.io/
HOST = 'localhost'
PORT = 15100
HOSTNAME = 'http://{}:{}'.format(HOST, PORT)

PAYPAL_CLIENT_ID = 'non-existing'
PAYPAL_SECRET = 'non-existing'

def toBase64 (data):
    return b64encode(data.encode('utf-8')).decode('utf-8')

class PayPal:
    def __init__ (self):
        self.authData = None

    def auth (self):
        if self.authData:
            return

        response = requests.post('https://non-existing.paypal.com/v1/oauth2/token',
            headers={
                'Authorization': 'Basic {}'.format(toBase64(PAYPAL_CLIENT_ID + ':' + PAYPAL_SECRET))
            },
            data={
                'grant_type': 'client_credentials'
            }
        )

        self.authData = response.json()

    def createInvoiceOrder (self, reqData):
        self.auth()

        print('\n', json.dumps(reqData, indent=4, ensure_ascii=False), '\n')

        origin = 'https://tnp-dev.eu.ngrok.io'
        returnUrl = origin + reqData['return_url']
        cancelUrl = origin + reqData['cancel_url']

        response = requests.post('https://non-existing.paypal.com/v2/checkout/orders',
            headers=self.getHeaders(),
            json={
                'intent': 'CAPTURE',
                'application_context': {
                    'return_url': returnUrl,
                    'cancel_url': cancelUrl
                },
                'purchase_units': [
                    {
                        'amount': {
                            'currency_code': 'USD',
                            'value': '1.00'
                        }
                    }
                ]
            }
        )

        order = response.json()
        approveLink = [ link['href'] for link in order['links'] if link['rel'] == 'approve' ][0]

        return {
            'status': 'OK',
            'payment_complete': False,
            'transaction_id': '<transaction_id>',
            'payment_intent': None,
            'paypal_approve_link': approveLink
        }

    def createPBMOrder (self, reqData):
        self.auth()

        print('\n', json.dumps(reqData, indent=4, ensure_ascii=False), '\n')

        origin = 'https://tnp-dev.eu.ngrok.io'
        returnUrl = origin + reqData['return_url']
        cancelUrl = origin + reqData['cancel_url']

        response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders',
            headers=self.getHeaders(),
            json={
                'intent': 'CAPTURE',
                'application_context': {
                    'return_url': returnUrl,
                    'cancel_url': cancelUrl
                },
                'purchase_units': [
                    {
                        'amount': {
                            'currency_code': 'USD',
                            'value': '1.00'
                        }
                    }
                ]
            }
        )

        order = response.json()
        approveLink = [ link['href'] for link in order['links'] if link['rel'] == 'approve' ][0]

        return {
            'status': 'OK',
            'payment_complete': False,
            'transaction_id': '<transaction_id>',
            'lpn': None,
            'lps': None,
            'payment_intent': None,
            'paypal_approve_link': approveLink
        }

    def getHeaders (self, headers=None):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self.authData['access_token']),
            **(headers or {})
        }


paypal = PayPal()

# ENDPOINTS
# -------------------------------------------------

@app.route('/account-invoices', methods=[ 'POST' ])
def paypalCreateInvoiceOrder ():
    reqData = json.loads(request.data)
    response = paypal.createInvoiceOrder(reqData)
    return jsonify(response)

@app.route('/pay-by-mail/<pbmId>', methods=[ 'POST' ])
def paypalCreatePBMOrder (pbmId):
    reqData = json.loads(request.data)
    response = paypal.createPBMOrder(reqData)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=PORT)
