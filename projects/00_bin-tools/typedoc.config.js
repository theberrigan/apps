// https://typedoc.org/documents/Options.Configuration.html
const config = {
    entryPoints: [
        './src/main.ts',
    ],
    // plugin: [
    //     'typedoc-plugin-markdown'
    // ],
    // out: './docs/',
    outputs: [
        {
            name: 'json',
            path: "./docs/docs.json"
        }
    ]
};

export default config;
