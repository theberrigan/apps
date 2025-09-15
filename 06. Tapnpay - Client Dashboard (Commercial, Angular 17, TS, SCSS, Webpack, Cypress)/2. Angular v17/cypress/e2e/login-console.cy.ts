describe('Login console', () => {
    it('Visits the рщьуз project page', () => {
        cy.visit('/');
        cy.wait(1000);
        cy.window().then((win) => {
            // @ts-ignore
            win.tnp.autoLoginSunpass();
        });
        cy.wait(500);
        assert(cy.get('.payment-method__method-popup-methods > :nth-child(2)').click());
        cy.wait(100);
        assert(cy.get('.payment-method__card-popup-header').contains('Please enter your credit/debit card details'));
        cy.get('.payment-method__card-popup-input_card').type('4242424242424242');
        cy.get('.payment-method__card-popup-input_expire').type('12/25');

    })
})
