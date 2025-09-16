function generateFakeLicensePlate(stateCode: string): string {
    const state = stateCode.toUpperCase(); // Ensure state code is in uppercase

    // Generate a random alphanumeric sequence for the license plate
    const randomChars = generateRandomAlphanumeric(7); // Adjust the length as needed

    // Form the license plate title with the state code and random characters
    const licensePlate = `${state} ${randomChars}`;

    return licensePlate;
}

function generateRandomAlphanumeric(length: number): string {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';

    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        result += characters.charAt(randomIndex);
    }

    return result;
}

// Example usage:
const testStateCode = 'TX';
const fakeLicensePlate = generateFakeLicensePlate(testStateCode);
console.log(fakeLicensePlate);


describe('LoginByPin', () => {
    before(() => {

    });

    beforeEach(() => {
        cy.loginByTa('IPASS');
    });

    it('Check dashboard page labels and table', () => {
        cy.visit('/dashboard');
        cy.get('.page-panel__header').contains('Invoices');
    });

    it('Check dashboard page labels and table', () => {
        cy.visit('/dashboard/history');
        cy.get('.page-panel__header').contains('History');
    });

    it('Check Coverage', () => {
        cy.visit('/dashboard/coverage').then(() => {
            cy.get('.page-panel__header').contains('Coverage');
        });
    });

    it('Check Extend tapNpay Coverage', () => {
        cy.visit('/dashboard/extend-coverage').then(() => {
            cy.get('.page-panel__header').contains('Extend tapNpay Coverage');
        });
    });

    it('Check FAQ', () => {
        cy.visit('/dashboard/faq').then(() => {
            cy.get('.page-panel__header').contains('FAQ');
        });
    });

    it('Check Contact Us', () => {
        cy.visit('/dashboard/contact-us').then(() => {
            cy.get('.page-panel__header').contains('Contact Us');
        });
    });

    it('Check Terms & Conditions', () => {
        cy.visit('/dashboard/terms').then(() => {
            cy.get('.page-panel__header').contains('Terms & Conditions');
        });
    });

    it('Check main nav', () => {
        cy.visit('/dashboard');
        cy.get('.page-panel__user-trigger').click();
        cy.get('.page-panel__user-menu').should('be.visible');
        cy.get('.page-panel__user-menu > :nth-child(1)').contains('Edit Profile');
        cy.get('.page-panel__user-menu > :nth-child(2)').contains('Change Language');
        cy.get('.page-panel__user-menu > :nth-child(3)').contains('Logout');

        cy.get('.page-panel__user-menu > :nth-child(1)').click();
        cy.get('.page-panel__header').contains('Profile');

        cy.get('.profile__items > :nth-child(1)').contains('Manage Vehicles')
        cy.get('.profile__items > :nth-child(2)').contains('Change Payment Method');
        cy.get('.profile__items > :nth-child(3)').contains('Manage Membership');
        //cy.get('.profile__items > :nth-child(4)').contains('Deactivate Account');


        cy.get('.profile__items > :nth-child(1)').click();
        cy.get('.page-panel__header').contains('Vehicles');
        cy.get('.vehicles__list-item').should('have.length.greaterThan', 1);
        cy.wait(500);
        cy.get(':nth-child(1) > .vehicles__list-item > .vehicles__list-item-primary > :nth-child(1) > .lpn-name').click();
        cy.get('.popup__content').contains('License plate status history');
        cy.get('.popup__controls > .button').click();
        cy.get('.popup__content').should('not.exist');

        cy.get('.page-panel__controls > .button').should('be.visible');
        cy.get('.page-panel__controls > .button').click();
        cy.get('.popup__content').should('be.visible');
        cy.get('.input').type(fakeLicensePlate);
        cy.get('.button_blue').click();
        cy.get('.dashboard__fleet-lpn-popup-header').contains('Please provide vehicle(s) information');
        cy.get('.popup__controls > .button_blue').click();
        cy.wait(70);
        cy.get('.popup__content').should('not.exist');
        cy.get('.vehicles__list-item').should('have.value', fakeLicensePlate);

    })


    /*it('Check invoices page labels and table', () => {
        cy.get('.page-panel__header').contains('Invoices');
        cy.get('.table__header').contains('Invoice');
        cy.get('.table__header').contains('Total Amount');
        cy.get('.table__header').contains('Transactions');
        cy.get('.table__header').contains('Date');
    });
    it('Check invoices page table', () => {
        cy.get('.context-panel__box').contains('Total');
        cy.get('.button_white-blue > .button__caption').contains('Tap to Pay');
        cy.get('.button_white-blue').click();
        cy.wait(500);
        cy.get('.invoice-payment__label-text').contains('Please enter your Zip Code');
        cy.get('.invoice-payment__input').type('12345');
        cy.get('.button_blue').click();
        cy.wait(500);
        cy.get('.popup__content > span').contains('Success');
        cy.get('.popup__controls > .button').click();
        cy.wait(500);
        cy.get('.invoices-list__message').contains(' No outstanding invoices');
    });
      it('Open history page and check title', () => {
          cy.get(':nth-child(1) > :nth-child(2) > .dashboard-sidebar-nav-link').click();
          cy.wait(500);
          cy.get('.page-panel__header').contains('History');
          expect(cy.get('.history__tabs')).to.exist;
      });*/
});
