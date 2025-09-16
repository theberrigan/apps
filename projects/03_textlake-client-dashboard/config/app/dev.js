import { LOCALES } from './common';

export const CONFIG = {
    isProduction: false,
    locales: LOCALES,
    server: 'http://127.0.0.1:8080',
    contact_email: 'contact@textlake.com',
    passwordRequirements: {
        minLength: 8,
        specialCharacters: false,
        lowercaseLetters: true,
        uppercaseLetters: true,
        digits: true
    },
    cookie: {
        domain: '',
        secure: 'auto'
    },
    aws: {
        cognito: {
            region: 'non-existing',
            userPoolId: 'non-existing',
            clientId: 'non-existing',
            appWebDomain: 'non-existing.amazoncognito.com',
            identityPoolId: 'non-existing',
            signedInRedirectUrl: 'http://{host}/auth/handle-token',
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
            apiKey: '<REMOVED>'
        }
    }
};
