import { RequestFlags } from '../enums/request-flags.enum';

export const Endpoints : { [ key : string ] : any } = {
    'payment.get_payment_methods': {
        url: '/rest/v1/payments/{ quoteCode }',
        // params: {},
        // queryParams: {},
        // requestFlags: RequestFlags.Auth
    },
    'payment.get_sofort_quote_url': {
        url: '/rest/v1/payments/sofort/{ quoteCode }'
    },
    'payment.save_stripe_token': {
        url: '/rest/v1/payments/stripe/{ quoteCode }'
    },
    'quote.get_quote_summary': {
        url: '/rest/v1/quotes/{ quoteCode }'
    }
};