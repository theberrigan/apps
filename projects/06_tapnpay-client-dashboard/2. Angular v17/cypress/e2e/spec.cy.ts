describe('Payments methods', () => {
    it('Select payment method', () => {
        cy.visit('/');
        cy.wait(1000);
        cy.request('Get', 'https://mock-app.oriondev.org/test/create-account').then((response) => {
            cy.get('.auth__input').clear();
            cy.get('.auth__input').type(response.body.phone);
            cy.get('.button').click();
            cy.wait(1000);
            cy.request('Get', `https://mock-app.oriondev.org/test/pin/${response.body.phone}` + response.body.phone).then((response) => {
                cy.get('.auth__label > .auth__input').type(response.body);
                cy.get('.button').click();
        })});
        cy.wait(500);

    })
})
