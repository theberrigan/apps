// ***********************************************
// This example namespace declaration will help
// with Intellisense and code completion in your
// IDE or Text Editor.
// ***********************************************
// declare namespace Cypress {
//   interface Chainable<Subject = any> {
//     customCommand(param: any): typeof customCommand;
//   }
// }
//
declare namespace Cypress {
    interface Chainable<Subject = any> {
        registerByTa(taName: string): Chainable<any>;
    }

    interface Chainable<Subject = any> {
        loginByTa(taName: string): Chainable<any>;
    }


    interface Chainable<Subject = any> {
        iframeCustom(arg: any): Chainable<any>;
    }

    interface Chainable<Subject = any> {
        checkElementExists(selector: string): Chainable<any>;
    }
}

const exitingUsersPhones = {
    'NTTA': '10002224272',
    'SUNPASS': '11107354768',
    'FASTRAK': '11105665593',
    'IPASS': '11101927030',
    'TXHUB': '',

}

function formatPhoneNumber(input) {
    // Remove all non-numeric characters from the input string
    const numericOnly = input.replace(/\D/g, '');

    // Format the numeric string into the desired pattern
    const areaCode = numericOnly.substring(0, 3);
    const firstPart = numericOnly.substring(3, 6);
    const secondPart = numericOnly.substring(6, 10);

    return `(${areaCode}) ${firstPart}-${secondPart}`;
}


Cypress.Commands.add('registerByTa', (taName: string) => {
    let phone: string;
    switch (taName) {
        case 'NTTA':
            phone = '18554827672';
            break;
        case 'SUNPASS':
            phone = '18555172507';
            break;
        case 'FASTRAK':
            phone = '18555172927';
            break;
        case 'IPASS':
            phone = '18336440841';
            break;
        case 'GOODTOGO':
            phone = '18553911030';
            break;
        case 'TXHUB':
            phone = '18882066777';
            break;
        default:
            phone = '18554827672';
    }
    cy.visit('/');
    cy.wait(1000);

    const newAccountApi = 'http://mock-app.oriondev.org/probe/test/create-fleet-account';
    const pinApi = 'http://mock-app.oriondev.org/test/pin';

    const fullUrl = `${newAccountApi}/${phone}`;

    cy.intercept('/auth/token', (req) => {
        req.continue((res) => {
            //set token to local storage
            const token = res.body.token;
            localStorage.setItem('token', token);
        });
    });

    cy.session('auth', () => {
        cy.visit('/');
        cy.request('Get', fullUrl).then((response) => {
            cy.get('[data-cy="auth-phone-input"]').clear();
            let phone = response.body.phone;
            if (phone.startsWith('1')) {
                phone = phone.substring(1);
            }
            cy.get('[data-cy="auth-phone-input"]').as('phoneInput');
            cy.get('@phoneInput').type(phone).should('have.value', formatPhoneNumber(phone));
            cy.get('[data-cy="auth-submit-button"]').click();
            cy.wait(3000);
            const pinUrl = `${pinApi}/1${phone}`;

            cy.request('Get', pinUrl).then((response) => {
                const pin = response.body;
                cy.get('[data-cy="auth-pin-input"]').type(pin).should('have.value', pin);
                cy.get('[data-cy="auth-submit-button"]').click();
            })
        });
    });
});


Cypress.Commands.add('loginByTa', (taName: string) => {
    let fullPhone = exitingUsersPhones[taName];
    let phone: string = fullPhone.substring(1);

    const pinApi = 'http://mock-app.oriondev.org/test/pin';

    cy.session(`login_${taName}`, () => {
        cy.visit('/auth');
        cy.get('[data-cy="auth-phone-input"]').as('phoneInput');
        cy.get('@phoneInput').type(phone).should('have.value', formatPhoneNumber(phone));
        cy.get('[data-cy="auth-submit-button"]').click();
        cy.wait(1000);

        const pinUrl = `${pinApi}/${fullPhone}`;
        cy.request('Get', pinUrl).then((response) => {
            const pin = response.body;
            cy.get('[data-cy="auth-pin-input"]').type(pin).should('have.value', pin);
            cy.get('[data-cy="auth-submit-button"]').click();
            cy.wait(3000);
        })
    });
});

// @ts-ignore
Cypress.Commands.add('iframeCustom', {prevSubject: 'element'}, ($iframe) => {
    return new Cypress.Promise((resolve) => {
        $iframe.ready(function () {
            resolve($iframe.contents().find('body'))
        })
    })
})

Cypress.Commands.add('checkElementExists', (selector) => {
    return cy.get(selector).should('exist').then(cy.wrap)
})


// function customCommand(param: any): void {
//   console.warn(param);
// }
//
// NOTE: You can use it like so:
// Cypress.Commands.add('customCommand', customCommand);
//
// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************


// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })
