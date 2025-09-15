// Global constants defined by Webpack DefinePlugin (see webpack.config.js)
declare const IS_PROD : boolean;

export const isProd = IS_PROD;

// ------------------------------------

export const isBrowser : boolean = (
    typeof window !== 'undefined' &&
    typeof window.document?.createElement === 'function'
);

export const isNode : boolean = !isBrowser;

export const isJSDom : boolean = (
    typeof navigator !== 'undefined' &&
    typeof navigator?.userAgent === 'string' &&
    /jsdom\//i.test(navigator.userAgent)
);
