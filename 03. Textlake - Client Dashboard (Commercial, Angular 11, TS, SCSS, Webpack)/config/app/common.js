// Do not use modern ES6 modules syntax because this file is used by webpack config

// NOTE: locale.code must be in moment.js locale format
const LOCALES = [
    {
        code: 'en',
        name: 'English',
        isDefault: true
    },
    {
        code: 'es',
        name: 'Español'
    },
    {
        code: 'ru',
        name: 'Русский'
    },
    {
        code: 'pl',
        name: 'Polski'
    },
    {
        code: 'uk',
        name: 'Українська'
    }
];

exports.LOCALES = LOCALES;
