const webpack = require('webpack');
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const autoprefixer = require('autoprefixer');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const helper = require('../helper');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

const ENV = process.env.NODE_ENV = process.env.ENV = 'production';

module.exports = {
    mode: ENV,
    entry: [
        './src/css/main.scss',
        './src/main.ts',
    ],
    output: {
        publicPath: '/',
        path: helper.root('dist/prod'),
        filename: '[name].js?[hash]',
        chunkFilename: '[name].component.js?[hash]',
    },
    resolve: {
        extensions: [
            '.html',
            '.js', '.ts',
            '.css', '.scss', '.sass',
            '.jpeg', '.jpg', '.png', '.gif', '.bmp',
            '.svg', '.woff', '.woff2', '.eot', '.ttf', '.otf',
            '.json'
        ]
    },
    module: {
        rules: [
            {
                test: /\.html$/i,
                use: {
                    loader: 'html-loader',
                    options: {
                        minimize: true,
                        removeComments: true,
                        collapseWhitespace: true,
                        conservativeCollapse: false,
                        removeAttributeQuotes: false,
                        keepClosingSlash: false,
                        minifyJS: true,
                        minifyCSS: true,
                        removeScriptTypeAttributes: true,
                        removeStyleTypeAttributes: true,
                        caseSensitive: true,
                        collapseBooleanAttributes: true,
                        collapseInlineTagWhitespace: false,
                    }
                }
            },
            {
                test: /\.(js|ts)$/i,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'babel-loader',
                        options: {
                            presets: [
                                [
                                    '@babel/preset-env',
                                    {
                                        modules: 'commonjs',
                                        // debug: true,
                                        useBuiltIns: 'usage'   // auto polyfilling
                                    }
                                ]
                            ]
                        }
                    },
                    {
                        loader: 'ts-loader',
                        options: {
                            configFile: 'tsconfig.json'
                        }
                    }
                ]
            },
            {
                test: /\.(css|scss|sass)$/i,
                use: [
                    {
                        loader: 'style-loader',
                        options: {
                            sourceMap: false
                        }
                    },
                    {
                        loader: 'css-loader',
                        options: {
                            sourceMap: false
                        }
                    },
                    {
                        loader: 'csso-loader',
                        options: {
                            sourceMap: false
                        }
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            plugins: [ autoprefixer() ]
                        }
                    },
                    {
                        loader: 'sass-loader',
                        options: {
                            sourceMap: false
                        }
                    }
                ]
            },
            {
                test: /\.(jpe?g|png|gif|bmp|svg|woff|woff2|ttf|otf|eot)$/i,
                use: [
                    {
                        loader: 'url-loader',
                        options: {
                            limit: 10240,
                            fallback: 'file-loader',
                            // Inject files with size less than 'limit' as data-url,
                            // otherwise use 'fallback'-loader and pass to it the following options
                            name: filename => helper.assetPath(filename, '[name].[ext]?[hash]')
                        }
                    }
                ]
            },
        ]
    },
    optimization: {
        minimizer: [
            new UglifyJsPlugin({
                uglifyOptions: {
                    compress: false,  // don't use, coz GSAP animation becomes incorrect (wtf?!)
                    output: {
                        comments: false,
                        beautify: false
                    }
                },
                sourceMap: false,
                cache: true,
                parallel: true
            })
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './src/index.html',
            hash: false,
            minify: {
                minifyCSS: true,
                caseSensitive: true,
                collapseBooleanAttributes: true,
                collapseInlineTagWhitespace: true,
                collapseWhitespace: true,
                removeComments: true,
                useShortDoctype: true
            }
        }),
        new CopyWebpackPlugin([
            {
                from: './src/favicon.ico',
                to: './favicon.ico'
            },
            {
                from: './src/robots.txt',
                to: './robots.txt'
            },
            {
                from: './src/sitemap.xml',
                to: './sitemap.xml'
            },
            {
                from: './src/locale/',
                to: './locale/',
                transform: (content, filepath) => {
                    switch (path.extname(filepath).toLowerCase()) {
                        case '.html':
                            return content;  // TODO: minimize
                        case '.json':
                            return JSON.stringify(JSON.parse(content));
                        default:
                            return content;
                    }
                }
            },
        ])
    ]
};