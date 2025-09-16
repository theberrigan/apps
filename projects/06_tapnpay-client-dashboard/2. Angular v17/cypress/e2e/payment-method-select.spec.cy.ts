describe('My First Test', () => {
    it('Select payment method', () => {
        cy.wait(500);
        cy.get('.popup__content').contains('Now let’s set up your payment method. Please choose your payment method from the options below.');
        cy.get('.payment-method__method-popup-methods > :nth-child(1)').click();
        cy.get('.popup__controls > .button').click();
    });
});
