import os, json, time, requests
from base64 import b64encode
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS

import braintree

'''
Braintree очень похож на Stripe. У него тоже есть SDK для разных языков, для фронтенда и бекэнда.

1. Для каждого нашего пользователя нужно создать Braintree Customer'a. Затем полученный customer_id
   нужно использовать с разными вызовами Braintree SDK. Прямо как у Stripe. (см. метод getVenmoCustomerId ниже)
2. Фронтенд один раз запрашивает у нашего сервера Client Token, который будет использоваться
   для прямых обращений к Braintree API в обход нашего сервера.
   Сервер генерирует Client Token с помощью специального метода Braintree SDK и возвращает во фронтенд.
   Каждый такой токен должен быть связан с Customer'ом. (см. метод getClientToken ниже)
3. Фронтенд выполняет флоу привязки Venmo Payment Method'а через Braintree и, в случае успеха,
   получает Braintree Payment Method Nonce. Этот Nonce можно много кратно использовать на нашем сервере
   для оплаты, но мы не будем использовать его напрямую.
4. Фронтенд передаёт Nonce на сервер. Сервер привязывает Nonce к Customer'у и получает id этой связи,
   который называется Braintree Payment Method Token. (см. метод setupBraintreePaymentMethod ниже).
   То есть: payment_method_nonce + braintree_customer = payment_method_token
   Именно этот токен мы будем использовать для всех манипуляций с этим payment method'ом (оплата, отвязывание...)
   Кроме того этот payment_method_token нужно использовать в качестве payment_method_id в нашем payment config:
   payment_config = {
       payment_method_type: 'VENMO',
       payment_method_id: payment_method_token
   }
   (Перед привязыванием нового токена к кастомеру, нужно отвязать старый, если он есть)
   --- Привязывание Venmo завершено ---
5. Оплата. Фронтенд стандартными способами передаёт pbm или инвойсы на оплату.
   Сервер создаёт транзакцию и отправляет её в settlement. (см. методы pbmSubmitPayment и invoicesSubmitPayment)
   isOk = response.is_success && response.transaction.status == "submitted_for_settlement"
   Во фронтенд вернуть { payment_complete: isOk, ... }
   Каждый раз, когда тебе нужно узнать оплачена ли какая-то транзакция, нужно делать запрос к Braintree,
   так как вебхуков для транзакции нет. Может стоит кешировать ответ в нашей базе, как минимум для Settled-транзакций?
   --- Оплата завершена ---
'''

app = Flask(__name__, static_url_path='', static_folder='./static')
CORS(app)

HOST = 'localhost'
PORT = 15100
LOCAL_HOSTNAME = 'http://{}:{}'.format(HOST, PORT)
REMOTE_HOSTNAME = 'https://non-existing.ngrok.io/'

print(f'\n{LOCAL_HOSTNAME} or {REMOTE_HOSTNAME}\n')

BT_MERCHANT_ID = 'non-existing'
BT_PUBLIC_KEY = 'non-existing'
BT_PRIVATE_KEY = 'non-existing'


def toBase64(data):
    return b64encode(data.encode('utf-8')).decode('utf-8')


class Controller:
    def __init__ (self):
        self.gateway = self.createGateway()

        # Типа данные текущего TNP из нашей БД
        self._currentUserData = {
            'id': str(uuid4()),
            'bt_customer_id': None,                 # id кастомера на стороне Braintree
            'bt_payment_method_token': None,        # Токен, который идентифицирует последний подключенный аккаунт Venmo
            'bt_payment_method_description': None,  # имя текущего подключенного аккаунта Venmo, отображается в UI
            'payment_method_type': None,
            'payment_method_id': None,
            'setup_complete': False
        }

    # Gateway для взаимодействия с Braintree
    # merchant_id, public_key и private_key нужно получить в дашборде BT
    # https://developer.paypal.com/braintree/docs/start/hello-server/python#install-and-configure
    def createGateway (self):
        return braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Sandbox,
                merchant_id=BT_MERCHANT_ID,
                public_key=BT_PUBLIC_KEY,
                private_key=BT_PRIVATE_KEY
            )
        )

    # Каждый пользователь TNP должен быть связан с Customer'ом на стороне Braintree, как у Stripe
    # Эта функция создаёт эту связь для текущего пользователя, если её ещё нет, и возвращает customerId
    def getVenmoCustomerId (self):
        venmoCustomerId = self._currentUserData['bt_customer_id']

        if not venmoCustomerId:
            # https://developer.paypal.com/braintree/docs/guides/customers#create
            result = self.gateway.customer.create({
                # Сюда можно добавить данные о пользователе (e.g. email, phone...)
            })

            if not result.is_success:
                return None  # failed to generate customer id

            venmoCustomerId = result.customer.id
            self._currentUserData['bt_customer_id'] = venmoCustomerId

        return venmoCustomerId

    # ------------------------------------------------
    # НОВЫЕ ЭНДПОИТЫ:
    # ------------------------------------------------

    # [API ENDPOINT]: GET /payment/braintree/client-token
    # Токен, который необходим фронтенду для взаимодействия с Braintree напрямую
    # В нашем случае обязательно должен быть связан с BT customer_id
    # Если вернёт clientToken == null (None в Python), то фронтенд покажет сообщение о тех. неполадках
    # https://developer.paypal.com/braintree/docs/guides/authorization/client-token
    # https://developer.paypal.com/braintree/docs/reference/request/client-token/generate#customer_id
    # https://developer.paypal.com/braintree/docs/start/hello-server/python#generate-a-client-token
    def getClientToken (self):
        venmoCustomerId = self.getVenmoCustomerId()

        clientToken = self.gateway.client_token.generate({
            'customer_id': venmoCustomerId
        })

        return { 'client_token': clientToken }

    # [API ENDPOINT]: PUT /payment/braintree/payment-method
    # Когда пользователь выбрал Venmo в качестве способа оплаты и подтвердил через приложение Venmo,
    # braintree выдаст payment method nonce. Фронтенд передаст этот nonce на этот эндпоинт.
    # Эндпоинт принимает новый Braintree payment method nonce, создаёт на его основе
    # новый Braintree payment method, привязанный к Braintree customer, в результате получает
    # Braintree payment method token - уникальный идентификатор payment method'а
    def setupBraintreePaymentMethod (self, reqData):
        # Данные запроса
        nonce = reqData['payment_method_nonce']

        # Braintree в случае с Venmo не позволяет узнать отличается ли текущий способ
        # оплаты от нового, поэтому, перед добавлением нового, нужно удалить старый.
        # Возможно, стоит сначала добавить новый payment method, и только в случае успеха отвязать старый
        currentToken = self._currentUserData['bt_payment_method_token']

        if currentToken:
            result = self.gateway.payment_method.delete(currentToken)

            if result.is_success:
                self._currentUserData['bt_payment_method_token'] = None
                self._currentUserData['bt_payment_method_description'] = None

        # Создать новый способ оплаты
        venmoCustomerId = self.getVenmoCustomerId()

        result = self.gateway.payment_method.create({
            'customer_id': venmoCustomerId,
            'payment_method_nonce': nonce,
            'options': {
                'make_default': True
            }
        })

        if not result.is_success:
            return {
                'status': 'ERROR',
                'payment_method_token': None,
                'description': None
            }

        newToken = result.payment_method.token
        description = result.payment_method.username  # Отображается в UI

        self._currentUserData['bt_payment_method_token'] = newToken
        self._currentUserData['bt_payment_method_description'] = description

        # Если в данный момент текущий способ оплаты Venmo, то нужно обновить его id
        if self._currentUserData['payment_method_type'] == 'VENMO':
            self._currentUserData['payment_method_id'] = newToken

        return {
            'status': 'OK',
            'payment_method_token': newToken,
            'description': description
        }

    # [API ENDPOINT]: DELETE /payment/braintree/payment-method/{token}
    # Отвязывает текущий способ оплаты Braintree
    def detachBraintreePaymentMethod (self, tokenToDelete):
        response = {
            'status': 'OK',
            'setup_complete': self._currentUserData['setup_complete'],
            'payment_method_type': self._currentUserData['payment_method_type'],
            'payment_method_id': self._currentUserData['payment_method_id'],
            'payment_verification_required': True,
            'min_payment_amount': 0,
            'max_payment_amount': 123456789
        }

        existingToken = self._currentUserData['bt_payment_method_token']

        if not tokenToDelete or tokenToDelete != existingToken:
            response['status'] = 'ERROR'
            return response

        # Запретить отвязывание Venmo, если это текущий способ оплаты (как с картами в Stripe)
        if self._currentUserData['payment_method_type'] == 'VENMO':
            response['status'] = 'ERROR'
            return response

        try:
            result = self.gateway.payment_method.delete(tokenToDelete)
            isOk = result.is_success
        except:  # braintree.exceptions.not_found_error.NotFoundError
            isOk = False

        # noinspection PyInterpreter
        if isOk:
            self._currentUserData['bt_payment_method_token'] = None
            self._currentUserData['bt_payment_method_description'] = None
            response['status'] = 'OK'
        else:
            response['status'] = 'ERROR'

        return response

    # ------------------------------------------------
    # АПГРЕЙДЫ СУЩЕСТВУЮЩИХ ЭНДПОИТОВ:
    # ------------------------------------------------

    # [API ENDPOINT]: GET /payment/options
    # В этот эндпоинт добавлен Venmo
    def getPaymentOptions (self):
        return {
            'dcb': {
                'enabled': True,
                'status': 'ELIGIBLE',
                'carrier': 'VERIZON'
            },
            'wallet': {
                'enabled': True
            },
            'paypal': {
                'enabled': True
            },
            'credit_card': {
                'enabled': True,
                'cards': []
            },
            'debit_card': {
                'enabled': True,
                'cards': []
            },
            'venmo': {
                'enabled': True,
                'payment_method_token': self._currentUserData['bt_payment_method_token'],  # string | null, Токен, который идентифицирует последний подключенный аккаунт Venmo
                'description': self._currentUserData['bt_payment_method_description']      # string | null, Имя текущего подключенного аккаунта Venmo, отображается в UI
            },
       }

    # [API ENDPOINT]: PUT /payment/config
    # Добавлена секция Venmo
    def updatePaymentConfig (self, reqData):
        # Данные запроса
        methodType = reqData['payment_method_type'] if ('payment_method_type' in reqData) else None
        methodId = reqData['payment_method_id'] if ('payment_method_id' in reqData) else None

        responseStatus = 'OK'

        if methodType == 'VENMO':
            # Если methodType == 'VENMO', то methodId - это Braintree payment method token
            # Если выбран Venmo, то methodId не должен быть null
            # Проверить, актуален ли payment method token, или фронтенд прислал старьё
            if methodId and methodId == self._currentUserData['bt_payment_method_token']:
                self._currentUserData['payment_method_type'] = methodType
                self._currentUserData['payment_method_id'] = methodId
                self._currentUserData['setup_complete'] = True
            else:
                responseStatus = 'ERROR'
        else:
            # Для всех остальных способов оплаты
            self._currentUserData['payment_method_type'] = methodType
            self._currentUserData['payment_method_id'] = methodId
            self._currentUserData['setup_complete'] = True

        return {
            'status': responseStatus,
            'setup_complete': self._currentUserData['setup_complete'],
            'payment_method_type': self._currentUserData['payment_method_type'],
            'payment_method_id': self._currentUserData['payment_method_id'],
            'payment_verification_required': True,
            'min_payment_amount': 0,
            'max_payment_amount': 123456789
        }

    # [API ENDPOINT]: POST /pay-by-mail/{pbmId}
    # Добавлена секция оплаты через Venmo
    # Просто создаётся Braintree transaction и сразу отправляется в settlement
    def pbmSubmitPayment (self, pbmId, reqData):
        # Данные запроса
        makePayment = reqData['make_payment']
        methodType = reqData['payment_method_type']
        methodId = reqData['payment_method_id']

        response = {
            'status': 'OK',
            'errorCode': 0,
            'payment_complete': False,
            'lpn': None,
            'lps': None,
            'transaction_id': None,
            'payment_intent': None,
        }

        if not makePayment:
            return response

        currentMethodType = self._currentUserData['payment_method_type']
        currentMethodId = self._currentUserData['payment_method_id']

        if not methodType or (methodType != currentMethodType) or (methodId != currentMethodId):
            response['status'] = 'ERROR'
            return response

        # Другие способы оплаты не реализованы
        if methodType != 'VENMO':
            return response

        pbmAmount = 532  # $5.32
        transactionAmount = f'{(pbmAmount / 100):.2f}'  # 532 -> "5.32"

        result = self.gateway.transaction.sale({
            'amount': transactionAmount,
            'payment_method_token': methodId,  # в случае Venmo текущий payment_method_id и есть payment_method_token
            'options': {
                'submit_for_settlement': True
            }
        })

        app.logger.info(result)

        if result.is_success:
            response['payment_complete'] = True
        else:
            response['status'] = 'ERROR'

        return response

    # [API ENDPOINT]: POST /account-invoices
    # Добавлена секция оплаты через Venmo
    # Просто создаётся Braintree transaction и сразу отправляется в settlement
    def invoicesSubmitPayment (self, reqData):
        # Данные запроса
        methodType = reqData['payment_method_type']
        methodId = reqData['payment_method_id']

        response = {
            'status': 'OK',
            'payment_complete': False,
            'transaction_id': None,
            'payment_intent': None,
        }

        currentMethodType = self._currentUserData['payment_method_type']
        currentMethodId = self._currentUserData['payment_method_id']

        if not methodType or (methodType != currentMethodType) or (methodId != currentMethodId):
            response['status'] = 'ERROR'
            return response

        # Другие способы оплаты не реализованы
        if methodType != 'VENMO':
            return response

        totalAmount = 1689  # $16.89
        transactionAmount = f'{(totalAmount / 100):.2f}'  # 1689 -> "16.89"

        result = self.gateway.transaction.sale({
            'amount': transactionAmount,
            'payment_method_token': methodId,  # в случае Venmo текущий payment_method_id и есть payment_method_token
            'options': {
                'submit_for_settlement': True
            }
        })

        app.logger.info(result)

        if result.is_success:
            response['payment_complete'] = True
        else:
            response['status'] = 'ERROR'

        return response

    # ------------------------------------------------
    # МОКИ СУЩЕСТВУЮЩИХ ЭНДПОИТОВ, НИКАКИХ ИЗМЕНЕНИЙ:
    # ------------------------------------------------

    # [API ENDPOINT]: GET /payment/config
    def getPaymentConfig (self):
        return {
            'status': 'OK',
            'setup_complete': self._currentUserData['setup_complete'],
            'payment_method_type': self._currentUserData['payment_method_type'],
            'payment_method_id': self._currentUserData['payment_method_id'],
            'payment_verification_required': True,
            'min_payment_amount': 0,
            'max_payment_amount': 123456789
        }


# ENDPOINTS
# -------------------------------------------------

ctrl = Controller()


@app.route('/payment/config', methods=['GET'])
def getPaymentConfig ():
    return jsonify(ctrl.getPaymentConfig())


@app.route('/payment/options', methods=['GET'])
def getPaymentOptions ():
    return jsonify(ctrl.getPaymentOptions())


@app.route('/payment/config', methods=['PUT'])
def updatePaymentConfig ():
    reqData = json.loads(request.data)
    return jsonify(ctrl.updatePaymentConfig(reqData))


@app.route('/pay-by-mail/<pbmId>', methods=['POST'])
def pbmSubmitPayment (pbmId):
    reqData = json.loads(request.data)
    return jsonify(ctrl.pbmSubmitPayment(pbmId, reqData))


@app.route('/account-invoices', methods=['POST'])
def invoicesSubmitPayment ():
    reqData = json.loads(request.data)
    return jsonify(ctrl.invoicesSubmitPayment(reqData))


@app.route('/payment/braintree/client-token', methods=['GET'])
def getClientToken ():
    return jsonify(ctrl.getClientToken())


@app.route('/payment/braintree/payment-method', methods=['PUT'])
def setupBraintreePaymentMethod ():
    reqData = json.loads(request.data)
    return jsonify(ctrl.setupBraintreePaymentMethod(reqData))


@app.route('/payment/braintree/payment-method/<token>', methods=['DELETE'])
def detachBraintreePaymentMethod (token):
    return jsonify(ctrl.detachBraintreePaymentMethod(token))


if __name__ == '__main__':
    # ctrl.updatePaymentConfig({
    #     'payment_method_type': 'VENMO',
    #     'payment_method_id': 'fake-venmo-account-nonce'
    # })
    app.run(debug=True, host=HOST, port=PORT)
