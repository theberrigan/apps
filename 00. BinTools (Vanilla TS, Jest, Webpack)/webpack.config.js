// noinspection JSCheckFunctionSignatures
// noinspection WebpackConfigHighlighting

const path = require('path');
const { DefinePlugin } = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const { BundleDeclarationsWebpackPlugin } = require('bundle-declarations-webpack-plugin/dist/index.js');



module.exports = (env, argv) => {
    const mode      = argv.mode || 'development';
    const isDev     = mode === 'development';
    const isProd    = mode === 'production';
    // const srcDir = path.resolve(__dirname, 'src');
    const distDir   = path.resolve(__dirname, 'dist');
    const staticDir = path.resolve(__dirname, 'static');

    const outputBaseName = 'lib';
    const outputJSName   = `${ outputBaseName }.js`;
    const outputDTSName  = `${ outputBaseName }.d.ts`;

    const config = {
        mode,
        resolve: {
            extensions: [ '.ts', '.js', '.css', '.scss', '.sass' ],
        },
        module: {
            rules: [
                {
                    test: /\.(js|ts)$/i,
                    use: 'ts-loader',
                    // include: srcDir,
                    exclude: [
                        /node_modules/,
                        /\.test\.(ts|js)$/
                    ],
                },
            ],
        },
        optimization: {
            minimize: !isDev
        },
        plugins: [
            new DefinePlugin({
                IS_PROD: isProd,
            }),
        ],
    };

    if (isDev) {
        config.devtool = 'inline-source-map';
        config.entry = './src/_dev/index.ts';
        config.output = {
            path: distDir,
            filename: `[name].[contenthash:20].js`,
        };
        config.devServer = {
            host: '0.0.0.0',
            port: 12013,
            hot: false,
            client: {
                logging: 'warn'
            },
            static: [
                staticDir
            ],
        };

        config.plugins.push(
            new HtmlWebpackPlugin({
                template: './src/_dev/index.html',
                hash: true
            })
        );
    } else {
        const entryPath = './src/main.ts';

        config.devtool = 'source-map';
        config.entry = entryPath;
        config.output = {
            path: distDir,
            filename: outputJSName,
            globalObject: 'globalThis',
            library: {
                type: 'umd',
                name: 'BinTools',
                umdNamedDefine: false,
            },
        };

        config.plugins.push(
            new CleanWebpackPlugin()
        );

        config.plugins.push(
            new BundleDeclarationsWebpackPlugin({
                entry: {
                    filePath: entryPath,
                    output: {
                        noBanner: true,
                    }
                },
                outFile: outputDTSName,
            })
        );
    }

    // module.exports = config;
    return config;
}
