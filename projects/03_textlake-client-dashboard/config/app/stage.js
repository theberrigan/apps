import { LOCALES } from './common';

export const CONFIG = {
    isProduction: true,
    locales: LOCALES,
    server: 'http://non-existing',
    contact_email: 'contact@textellar.com',
    passwordRequirements: {
        minLength: 8,
        specialCharacters: false,
        lowercaseLetters: true,
        uppercaseLetters: true,
        digits: true
    },
    cookie: {
        domain: 'non-existing',
        secure: 'auto'
    },
    aws: {
        cognito: {
            region: 'non-existing',
            userPoolId: 'non-existing',
            clientId: 'non-existing',
            appWebDomain: 'non-existing',
            identityPoolId: 'non-existing',
            signedInRedirectUrl: 'http://{host}/?route=/auth/handle-token',
            signedOutRedirectUrl: 'http://{host}/auth/sign-in'
        },
        iot: {
            debug: false,
            topics: {
                user: 'tsm/users/{userId}',
                company: 'tsm/companies/{companyId}',
                identity: 'tsm/identities/{identityId}'
            }
        },
        apiGateway: {
            server: 'https://non-existing.amazonaws.com',
            endpoints: {
                sts: '/dev/sts'
            }
        }
    },
    payments: {
        stripe: {
            apiKey: 'non-existing'
        }
    }
};
