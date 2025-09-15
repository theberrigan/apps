const STRIPE_IFRAME_PREFIX = '__privateStripeFrame'

const CARD_DETAILS = {
    cardNumber: '4242424242424242',
    cardExpiry: '0525',
    cardCvc: '123',
}

const getStripeIFrameDocument = () => {
    // @ts-ignore
    return cy.checkElementExists(`iframe[name^="${STRIPE_IFRAME_PREFIX}"]`).iframeCustom()
}

describe('Payment Form', () => {
    before(() => {
        cy.registerByTa('IPASS');
    });

    beforeEach(() => {
        cy.visit('/dashboard');
    });

    context('Payment Form', () => {
        it('login and open payments modal', () => {
            cy.get('.payment-method__method-popup-methods > :nth-child(2)').click();
            cy.wait(1500);
        });
        it('should display form elements', () => {
            getStripeIFrameDocument().find('input[data-elements-stable-field-name="cardNumber"]').should('be.visible');
            getStripeIFrameDocument().find('input[data-elements-stable-field-name="cardExpiry"]').should('be.visible');
            getStripeIFrameDocument().find('input[data-elements-stable-field-name="cardCvc"]').should('be.visible');
        });
        it('fill form', () => {
            getStripeIFrameDocument().find('input[data-elements-stable-field-name="cardNumber"]').type(CARD_DETAILS.cardNumber);
            getStripeIFrameDocument().find('input[data-elements-stable-field-name="cardExpiry"]').type(CARD_DETAILS.cardExpiry);
            getStripeIFrameDocument().find('input[data-elements-stable-field-name="cardCvc"]').type(CARD_DETAILS.cardCvc);
            cy.get('.checkbox').click();
            cy.get('.button_blue').click();
            cy.wait(1000);
        });
        it('click on payment method select button', () => {
            cy.get('.popup__controls > .button > .button__caption').contains('Use as payment method').click();
        });
    });
});






