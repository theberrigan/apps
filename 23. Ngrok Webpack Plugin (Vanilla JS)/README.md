# Webpack Ngrok Plugin

Usage:
```js
const { NgrokWebpackPlugin } = require('./ngrok-webpack-plugin');

const config = {
    // ...
    plugins: [
        new NgrokWebpackPlugin({
            exePath: './path/to/ngrok.exe',
            configPath: './path/to/ngrok.yml'
        }),
    ],
    // ...
};
```