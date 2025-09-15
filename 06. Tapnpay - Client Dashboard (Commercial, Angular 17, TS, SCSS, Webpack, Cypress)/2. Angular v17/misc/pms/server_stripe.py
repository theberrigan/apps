import os, json, time

import stripe
from flask import Flask, jsonify, request
from flask_cors import CORS

# Card declined

# https://stripe.com/docs/payments/save-and-reuse
# https://stripe.com/docs/payments/save-during-payment
# https://stripe.com/docs/api/payment_intents/confirm
# https://stripe.com/docs/payments/payment-intents/creating-payment-intents#creating-for-automatic
# https://stripe.com/docs/api/payment_intents/create#create_payment_intent-confirm
# https://stripe.com/docs/api/errors

stripe.api_key = 'non-existing'

app = Flask(__name__, static_url_path='', static_folder='./static')
CORS(app)

HOST = 'localhost'
PORT = 15100
HOSTNAME = 'http://{}:{}'.format(HOST, PORT)

'''
Добавление карты в список:
1. Пользователь нажимает "Credit/Debit Card" или "Add New Card", если уже добавлена хотя бы одна карта
2. Появляется интерфейс для ввода данных карты, пользователь всё вводит и нажимает "Ok"
3. Фронтенд делает запрос [GET /payment/stripe/setup-intent].
   На сервере создаётся SetupIntent с указанием customer.id через Stripe SDK.
   Получен SetupIntent. Во фронтенд отправляется поле 'client_secret' из SetupIntent.
4. Фронтенд отправляет данные карты и client_secret в специальный метод Stripe SDK - stripe.confirmCardSetup()
5. Допустим, Stripe API вернул status === 'succeeded', это значит, что на стороне страйпа
   карта прикреплена (attached) к customer'у. (но пока не выбрана в качестве предпочитаемого способа оплаты).
   Теперь метод getCards(), а, соответственно, и getPaymentMethod() будет возвращать список карт, в котором
   будет только что добавленная карта.
6. Интерфейс возвращается к лейауту со списком доступных способов оплаты, поэтому он хочет
   обновить список доступных карт и делает запрос [GET /payment/method]



Сохранение/изменение предпочитаемого способа оплаты пользователем:
1. Пользователь видит список доступных методов оплаты. Возможно, он только что добавил в этот список новую карту.
2. Пользователь кликает на желаемый способ оплаты и жмёт "Use as a Payment Method"
3. Интерфейс делает запрос на сервер [POST /payment/method].

   Если он выбрал carrier:
   requestBody = {
       payment_method_type: 'carrier',
       payment_method_id: null
   }

   Если он выбрал wallet:
   requestBody = {
       payment_method_type: 'wallet',
       payment_method_id: null
   }

   Если он выбрал одну из карт:
   requestBody = {
       payment_method_type: 'card',
       payment_method_id: '<string_card_id>'  // страйповский id карты, совпадает с getCards[i].id
   }
4. Сервер возвращает обновлённый payment method



Пользователь удаляет карту из списка:
1. Пользователь жмёт на крест у карты.
2. На сервер идёт запрос [DELETE /payment/method/<cardId>]
   Нельзя удалять карту, если она является текущим способом оплаты.
3. Сервер возвращает обновлённый payment method

'''


class Payment:
    def __init__ (self):
        '''
        Every TNP user must be mapped to Stripe customer.

        When user registered:
            user = crateTNPUser()
            customer = stripe.Customer.create()
            user.stripeCustomerId = customer.id
            user.saveToDB()

        When you query user from db:
            user = queryUserFromDB()
            if user.stripeCustomerId == null:
                customer = stripe.Customer.create()
                user.stripeCustomerId = customer.id
                user.saveToDB()
        '''
        # START: DB data
        self.customer = stripe.Customer.create()
        self.paymentMethodType = None
        self.paymentMethodId = None
        self.isSetupComplete = False
        self.minPaymentAmount = 50
        self.maxPaymentAmount = 5000
        # END: DB data

    # Get stripe customer object
    def getCustomer (self):
        return self.customer

    # Get full list of added cards
    def getCards (self):
        try:
            response = stripe.PaymentMethod.list(customer = self.customer.id, type = 'card')
            # Sort by creation date ASC
            cards = sorted(response['data'], key = lambda item: item['created'])
            return cards
        except Exception as e:
            print('Failed to fetch cards:', e)
            return []

    # Completely delete card on stripe's side
    def deleteCard (self, cardId):
        try:
            stripe.PaymentMethod.detach(cardId)
            return True
        except Exception as e:
            print('Failed to delete card:', e)
            return False

    # User tries to add new card, so create new setup intent and return client_secret to frontend
    def getStripeSetupIntentClientSecret (self):
        intent = stripe.SetupIntent.create(customer = self.customer.id)
        return intent.client_secret

    # Create payment intent and try to pay in one call
    # If payment done, it return payment intent with status 'succeeded'
    # If payment requires 3D secure, it return payment intent with status 'requires_action'
    # Also it can return other statuses
    def createStripePaymentIntent (self, amount, currency, paymentMethodId):
        try:
            return stripe.PaymentIntent.create(
                amount = amount,
                currency = currency,
                customer = self.customer.id,
                payment_method = paymentMethodId,
                off_session = False,  # Customer is on-session during checkout (Dunno wtf is this)
                confirm = bool(paymentMethodId)  # Confirm and charge payment immediately if paymentMethodId exists
            )
        except Exception as e:
            # json.dumps(paymentIntent, ensure_ascii=False, indent=4)
            app.logger.info(e)
            return None

    # Call it when you want to retrieve already existing payment intent from stripe
    def getStripePaymentIntent (self, paymentIntentId):
        try:
            return stripe.PaymentIntent.retrieve(paymentIntentId)
        except Exception as e:
            app.logger.info(e)
            return None


    def getPaymentConfig (self):
        paymentConfig = {
            'payment_verification_required': True,
            'min_payment_amount': 50,
            'max_payment_amount': 5000,
            'carrier': 'verizon',
        }

        return paymentConfig

    # Get user preferred payment method from DB and ALL added cards from stripe
    def getPaymentMethod (self):
        paymentMethod = {
            'payment_method_type': self.paymentMethodType,
            'payment_method_id': self.paymentMethodId,
            'is_setup_complete': self.isSetupComplete,
            'cards': self.getCards(),
        }

        return paymentMethod

    # Save payment method to DB
    def setPaymentMethod (self, paymentMethodType, paymentMethodId, isSetupComplete):
        self.paymentMethodType = paymentMethodType
        self.paymentMethodId = paymentMethodId
        self.isSetupComplete = isSetupComplete

    # Check if the card is attached to the user
    def isCardExists (self, cardId):
        return len([ card for card in self.getCards() if card['id'] == cardId ]) > 0

    # Check if the payment method is current
    def isCurrentPaymentMethod(self, paymentMethodType, paymentMethodId = None):
        if self.paymentMethodType == paymentMethodType:
            if self.paymentMethodType != 'card' or self.paymentMethodId == paymentMethodId:
                return True

        return False

    def getMinPaymentAmount (self):
        return self.minPaymentAmount

    def getMaxPaymentAmount (self):
        return self.maxPaymentAmount


# ----------------------------------------------------------------------------------------------------------------------

payment = Payment()

@app.route('/payment', methods=[ 'GET' ])
def getPaymentConfig ():
    return jsonify(payment.getPaymentConfig())

# Get current payment method
@app.route('/payment/method', methods=[ 'GET' ])
def getPaymentMethod ():
    return jsonify(payment.getPaymentMethod())

# Save payment method as current and return it
@app.route('/payment/method', methods=[ 'POST' ])
def setPaymentMethod ():
    reqData = json.loads(request.data)

    paymentMethodType = reqData['payment_method_type']
    paymentMethodId = reqData['payment_method_id'] if ('payment_method_id' in reqData) else None

    if paymentMethodType == 'card':
        if not paymentMethodId or not payment.isCardExists(paymentMethodId):
            return jsonify({ 'status': 'ERROR' })

    payment.setPaymentMethod(
        paymentMethodType,
        paymentMethodId,
        isSetupComplete = True  # Any POST /payment/method request marks the payment method as set
    )

    return jsonify({
        'status': 'OK',
        'payment_method': payment.getPaymentMethod()
    })


# Detach card from user if it is not a current payment method
@app.route('/payment/method/<cardId>', methods=[ 'DELETE' ])
def deletePaymentMethod (cardId):
    if not cardId:
        return jsonify({ 'status': 'ERROR' })

    paymentMethod = payment.getPaymentMethod()

    # Do not delete current payment method!
    if paymentMethod['payment_method_type'] == 'card' and paymentMethod['payment_method_id'] == cardId:
        return jsonify({ 'status': 'ERROR' })

    # Return status OK if card is not attached to a customer
    isCardAttached = False

    for card in paymentMethod['cards']:
        if card['id'] == cardId:
            isCardAttached = True
            break

    if isCardAttached and not payment.deleteCard(cardId):
        return jsonify({ 'status': 'ERROR' })

    return jsonify({
        'status': 'OK',
        'payment_method': payment.getPaymentMethod()
    })


# If the user tries to add a new card, we must first create a new setup intent
@app.route('/payment/stripe/setup-intent', methods=[ 'GET' ])
def stripeGetSetupIntent ():
    clientSecret = payment.getStripeSetupIntentClientSecret()

    return jsonify({ 'clientSecret': clientSecret })


# Requested when user tries to pay invoices or pbm using card or wallet (e.g. Google/Apple Pay)
@app.route('/payment/stripe/payment-intent', methods=[ 'POST' ])
def stripeGetPaymentIntent ():
    reqData = json.loads(request.data)
    paymentMethodType = reqData['payment_method_type']  # 'card' | 'wallet'
    paymentMethodId = reqData['payment_method_id']      # null | <card_id> (string)
    target = reqData['target']                          # 'pbm' | 'invoices'
    invoices = reqData['invoices']                      # null | Invoice[]
    pbmId = reqData['pbm_id']                           # null | <pbm_id> (string)

    # Return error if customer doesn't have the card
    if paymentMethodType == 'card' and not payment.isCardExists(paymentMethodId):
        return jsonify({
            'status': 'ERROR',
            'error_code': 'payment_method_not_exists',
            'payment_intent': None
        })

    # Return error if payment method mismatch
    # Ensure user tries to pay with current payment method saved on the server
    if not payment.isCurrentPaymentMethod(paymentMethodType, paymentMethodId):
        return jsonify({
            'status': 'ERROR',
            'error_code': 'payment_method_mismatch',
            'payment_intent': None
        })

    # Ensure payment method id is correct
    if paymentMethodType != 'card':
        paymentMethodId = None

    amount = 0
    currency = 'USD'

    if target == 'pbm':
        pbm = { 'amount': 50 } # pbm got from DB
        amount = pbm['amount']
    elif target == 'invoices':
        # calc amount based on 'invoices' (invoices have format like POST /account-invoices)
        amount = 50
    else:
        return jsonify({
            'status': 'ERROR',
            'error_code': 'unknown_target',
            'payment_intent': None
        })

    minAmount = payment.getMinPaymentAmount()
    maxAmount = payment.getMaxPaymentAmount()

    # If amount is zero respond with OK (eg. all invoice transactions are disputed, nothing to pay)
    if amount <= 0:
        return jsonify({
            'status': 'OK',
            'payment_intent': None
        })
    elif amount < minAmount or amount > maxAmount:
        return jsonify({
            'status': 'ERROR',
            'error_code': 'limit_error',
            'payment_intent': None
        })

    # Create payment setup and try to pay immediately (in one call)
    paymentIntent = payment.createStripePaymentIntent(amount, currency, paymentMethodId)

    app.logger.info(paymentIntent)

    # Payment failed
    if not paymentIntent:
        return jsonify({
            'status': 'ERROR',
            'error_code': 'payment_error',
            'payment_intent': None
        })

    # See https://stripe.com/docs/payments/intents#intent-statuses
    # Possible statuses: 'succeeded', 'processing', 'requires_action', 'requires_confirmation', 'requires_payment_method', 'canceled'
    # requires_payment_method - can occur in two cases: card is declined by bank or
    #                           we didn't set customer's card as payment method in
    #                           payment.createStripePaymentIntent()
    # requires_confirmation - is not an error, can occur if 'confirm' flag is False
    #                         in payment.createStripePaymentIntent()
    status = paymentIntent['status']

    # --- CARD PAYMENT ---
    if paymentMethodType == 'card':
        # PAYMENT COMPLETE
        # Don't return payment_intent if payment complete
        # Not sure about 'processing' status here, it shouldn't occur
        # when user makes payment with card, may be interpret it as an error?
        if status in [ 'succeeded', 'processing' ]:
            # NOTE: mark 'pbm' or 'invoices' as paid
            return jsonify({
                'status': 'OK',
                'payment_intent': None
            })

        # PAYMENT NOT COMPLETE and requires 3D secure auth on frontend, so send payment_intent to frontend
        elif status in [ 'requires_action' ]:
            # NOTE: link paymentIntent with 'pbm' or 'invoices'
            return jsonify({
                'status': 'OK',
                'payment_intent': paymentIntent
            })

        # Interpret all of the following statuses as an error
        elif status in [ 'canceled', 'requires_payment_method', 'requires_confirmation' ]:
            return jsonify({
                'status': 'ERROR',
                'error_code': 'payment_error',
                'payment_intent': None
            })

    # --- WALLET PAYMENT ---
    elif paymentMethodType == 'wallet':
        # Since paymentIntent for wallet payment always created w/o payment_method,
        # the only expected status on this stage is 'requires_payment_method'
        if status == 'requires_payment_method':
            return jsonify({
                'status': 'OK',
                'payment_intent': paymentIntent
            })

        # All other statuses are unexpected and interpreted as an error
        elif status in [ 'succeeded', 'processing', 'canceled', 'requires_confirmation', 'requires_action' ]:
            return jsonify({
                'status': 'ERROR',
                'error_code': 'payment_error',
                'payment_intent': None
            })

    # --- UNEXPECTED PAYMENT METHOD ---
    else:
        return jsonify({
            'status': 'ERROR',
            'error_code': 'unexpected_payment_method',
            'payment_intent': None
        })


    # This shouldn't be reachable, this is unexpected state
    return jsonify({
        'status': 'ERROR',
        'error_code': 'unknown_error',
        'payment_intent': None
    })

# When [POST /payment/stripe/payment-intent] above retrieves payment_intent
# with status 'requires_action' from stripe, it sends payment_intent
# to the frontend for 3D Secure auth.
# Frontend performs 3D and then send payment_intent_id to this endpoint to complete payment.
# Also this endpoint requested when wallet payment complete in the browser.
# This is unreliable mechanism, so IT SHOULD BE REPLACED WITH WEBHOOKS
@app.route('/payment/stripe/payment-intent/complete', methods=[ 'POST' ])
def stripeCompletePaymentIntent ():
    reqData = json.loads(request.data)
    paymentIntentId = reqData['payment_intent_id']
    paymentIntent = payment.getStripePaymentIntent(paymentIntentId)

    if not paymentIntent or paymentIntent['status'] != 'succeeded':
        # NOTE: dunno, may be decline 'pbm' or cancel 'invoices' payment
        return jsonify({ 'status': 'ERROR' })

    # NOTE: mark 'pbm' or 'invoices' as paid
    return jsonify({ 'status': 'OK' })

'''
# Requested when payment error occurred or user canceled payment while paying with a wallet
@app.route('/payment/stripe/payment-intent/cancel', methods=[ 'POST' ])
def stripeCompletePaymentIntent ():
    reqData = json.loads(request.data)
    paymentIntentId = reqData['payment_intent_id']

    # In case if pbm payment decline it
    # See warning message here https://stripe.com/docs/stripe-js/elements/payment-request-button#html-js-complete-payment

    return jsonify({ 'status': 'OK' })
'''

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=PORT)

# asdasdsasdss
