/** @type {import('ts-jest').JestConfigWithTsJest} */

const config = {
    preset: 'ts-jest',
    transform: {
        '^.+\\.ts$': [
            'ts-jest',
            {
                tsconfig: '<rootDir>/tsconfig.test.json',
                diagnostics: {
                    ignoreCodes: [ 'TS151001' ],
                },
            },
        ],
    },
    globals: {
        IS_PROD: true
    },
    // setupFilesAfterEnv: [
    //     'jest-extended/all'
    // ]
}

module.exports = {
    projects: [
        {
            displayName: 'Browser Environment',
            testEnvironment: '<rootDir>/tests/setups/patched-jsdom-env.js',  // 'jsdom'
            setupFiles: [
                '<rootDir>tests/setups/browser.js',
            ],
            ...config
        },
        {
            displayName: 'Node.js Environment',
            testEnvironment: 'node',
            setupFiles: [
                '<rootDir>tests/setups/nodejs.js'
            ],
            ...config
        }
    ],
};
