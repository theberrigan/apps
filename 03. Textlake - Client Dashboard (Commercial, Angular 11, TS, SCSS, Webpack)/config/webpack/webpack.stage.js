var webpack = require('webpack');
var UglifyJsPlugin = require('uglifyjs-webpack-plugin');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var CopyWebpackPlugin = require('copy-webpack-plugin');
var autoprefixer = require('autoprefixer');
var AngularCompilerPlugin = require('@ngtools/webpack').AngularCompilerPlugin;
var helpers = require('../../misc/scripts/helpers');

console.log('\nApp root dir:', helpers.ROOT_DIR, '\n\n');

module.exports = {
    mode: 'production',
    stats: 'errors-only',
    devtool: false,
    entry: {
        polyfills: helpers.srcPath('polyfills.ts'),
        vendor:    helpers.srcPath('vendor.ts'),
        app:       helpers.srcPath('main.ts')
    },
    output: {
        path: helpers.distPath('stage'),
        publicPath: '/',
        filename: '[name].base.[hash].js',
        chunkFilename: '[name].module.[hash].js'
    },
    resolve: {
        extensions: [
            '.ts', '.js', '.json',
            '.scss', '.css',
            '.jpg', '.jpeg', '.gif', '.png', '.bmp', '.svg', '.ico',
            '.woff', '.woff2', '.ttf', '.otf', '.eot'
        ],
        alias: {
            config: helpers.configPath('app', 'config.stage.json')
        }
    },
    module: {
        rules: [
            // Pack all html templates
            {
                test: /\.html$/,
                loader: 'html-loader',
                options: {
                    minimize: false,
                    removeComments: true,
                    removeCommentsFromCDATA: true,
                    removeCDATASectionsFromCDATA: true,
                    collapseWhitespace: true,
                    conservativeCollapse: false,
                    removeAttributeQuotes: false,
                    useShortDoctype: true,
                    keepClosingSlash: false,
                    minifyJS: true,
                    minifyCSS: true,
                    removeScriptTypeAttributes: true,
                    removeStyleTypeAttributes: true
                }
            },

            // Collect all images and fonts
            {
                test: /\.(png|jpe?g|gif|bmp|svg|ico|woff|woff2|ttf|otf|eot)$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: function (filepath) {
                                return helpers.getRelativeResourcePath(filepath, 'app/assets', '[name]_[hash].[ext]');
                            }
                        }
                    }
                ]

            },

            // Compile scss-files to optimized css
            {
                test: /\.scss$/,
                include: helpers.srcPath(),      //
                use: [
                    {
                        loader: 'style-loader'     // inject styles using tag <style>
                    },
                    {
                        loader: 'css-loader',       // generate js-code to resolve @import/url() in runtime
                        options: {
                            sourceMap: false
                        }
                    },
                    {
                        loader: 'csso-loader',      // optimize css
                        options: {
                            sourceMap: false
                        }
                    },
                    {
                        loader: 'postcss-loader',  // add vendor previxes for selectors and props
                        options: {
                            plugins: [
                                autoprefixer({
                                    browsers: [ 'ie >= 8', 'last 4 version' ]  // TODO: change
                                })
                            ]
                        }
                    },
                    {
                        loader: 'sass-loader',      // scss string -> css string
                        options: {
                            sourceMap: false
                        }
                    }
                ]
            },

            // Optimize css
            {
                test: /\.css$/,
                include: helpers.srcPath(),
                loader: [
                    {
                        loader: 'style-loader'     // inject styles using tag <style>
                    },
                    {
                        loader: 'css-loader',  // optiomized_css_string -> optiomized_css_string with resolved @import/url()
                        options: {
                            sourceMap: false
                        }
                    },
                    {
                        loader: 'csso-loader',  // css_string -> optiomized_css_string
                        options: {
                            sourceMap: false
                        }
                    },
                    {
                        loader: 'postcss-loader',  // add vendor previxes for selectors and props
                        options: {
                            plugins: [
                                autoprefixer({
                                    browsers: [ 'ie >= 8', 'last 4 version' ]  // TODO: change
                                })
                            ]
                        }
                    }
                ]
            },

            // AOT
            {
                test: /(?:\.ngfactory\.js|\.ngstyle\.js|\.ts)$/,
                loader: '@ngtools/webpack'
            }
        ]
    },
    optimization: {
        minimizer: [
            new UglifyJsPlugin({
                uglifyOptions: {
                    compress: true,
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
        new AngularCompilerPlugin({
            basePath: helpers.root(),
            tsConfigPath: helpers.root('tsconfig.stage.json'),
            entryModule: helpers.appPath('app.module#AppModule'),
            sourceMap: false
        }),
        new webpack.ContextReplacementPlugin(
            /angular(\\|\/)core/,
            helpers.srcPath(),
            {}
        ),
        new webpack.ProvidePlugin({
            'CONFIG': 'config'
        }),
        new HtmlWebpackPlugin({
            template: helpers.srcPath('index.html'),
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
                from: helpers.srcPath('locale'),
                to: 'locale',
                transform: function (content) {
                    return JSON.stringify(JSON.parse(content))
                }
            },
            {
                from: helpers.assetsPath('images', 'favicon.ico'),
                to: './favicon.ico'
            }
        ])
    ]
};