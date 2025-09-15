import {defineConfig} from 'cypress'

export default defineConfig({

    e2e: {
        baseUrl: 'http://127.0.0.1:15099',
        supportFile: 'cypress/support/commands.ts',
        chromeWebSecurity: false,
    },


    component: {
        devServer: {
            framework: 'angular',
            bundler: 'webpack',
        },
        specPattern: '**/*.cy.ts'
    }

})
