import { LOCALES } from './common';

export const CONFIG = {
    isProduction: true,
    locales: LOCALES,
    server: '//non-existing.com',
    contact_email: 'contact@textlake.com',
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
            appWebDomain: 'non-existing.textlake.com',
            identityPoolId: 'non-existing',
            signedInRedirectUrl: 'https://{host}/?route=/auth/handle-token',
            signedOutRedirectUrl: 'https://{host}/auth/sign-in'
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
            server: 'https://non-existing.textlake.com',
            endpoints: {
                sts: '/v1/sts'
            }
        }
    },
    payments: {
        stripe: {
            apiKey: 'non-existing'
        }
    }
};
