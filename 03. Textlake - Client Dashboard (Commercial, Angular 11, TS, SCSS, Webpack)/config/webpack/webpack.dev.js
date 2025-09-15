var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var CopyWebpackPlugin = require('copy-webpack-plugin');
var autoprefixer = require('autoprefixer');
var helpers = require('../../misc/scripts/helpers');

// - Конфигурирование тайпскрипты
// - Как шарить модули при лейзи лодинге и где их подгружать
// - Можно ли создавать более глубокую иерархию лейзи-лоадинга
// - http-интерцепторы
// - Приделать тестирование jest
// - Приделать тестирование e2e
// - разобраться с соурсмапами

// Правила:
// 1. Лоадеры подгружают только те файлы, который импортированы внутрь других
// 2. Лоадеры, расположенные один за другим в массиве запускаются с последнего к первому,
//    а предыдущий лоадер передаёт результат своей работы следующему (конвейер)

// awesome-typescript-loader
// angular2-template-loader
// angular-router-loader
// html-loader - принимет html-код в виде строки и в автономный модуль (module.exports = "<html_code>")
// file-loader - получает путь к ресурсу (изображение или шрифт) и помещает его в нужную директорию
// raw-loader
// csso-loader
// sass-loader
// css-loader - принимает содержимое css-файла в виде строки и возвращает js-код
// style-loader

console.log('\nApp root dir:', helpers.ROOT_DIR, '\n\n');

module.exports = {
    mode: 'development',
    stats: 'errors-only',
    entry: {
        polyfills: helpers.srcPath('polyfills.ts'),
        vendor:    helpers.srcPath('vendor.ts'),
        app:       helpers.srcPath('main.ts')
    },
    output: {
        path: helpers.distPath(),
        publicPath: '/',
        filename: '[name].base.[hash].js',        // name of base modules (entries)
        chunkFilename: '[name].module.[hash].js'  // name of lazy loaded modules 
    },
    resolve: {
        extensions: [
            '.ts', '.js', '.json',
            '.scss', '.css',
            '.jpg', '.jpeg', '.gif', '.png', '.bmp', '.svg', '.ico',
            '.woff', '.woff2', '.ttf', '.otf', '.eot'
        ],
        alias: {
            config: helpers.configPath('app', 'config.dev.json')
        }
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: [
                    {
                        loader: 'awesome-typescript-loader',
                        options: { 
                            configFileName: helpers.root('tsconfig.json')
                        }
                    },
                    'angular2-template-loader',
                    'angular-router-loader'
                ]
            },

            // Pack all html templates
            {
                test: /\.html$/,
                loader: 'html-loader'
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
                    'style-loader',
                    'css-loader',
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
                        loader: 'sass-loader'      // scss string -> css string
                    }
                ]
            },

            // Optimize css
            {
                test: /\.css$/,
                include: helpers.srcPath(),
                loader: [
                    'style-loader',
                    'css-loader',
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
            }
        ]
    },
    plugins: [
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
            hash: false
        }),
        // new ExtractTextPlugin('[name]_[hash].css'),
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
    ],
    // Dev Options
    devtool: 'cheap-module-eval-source-map',
    devServer: {
        historyApiFallback: true,
        stats: 'errors-only',
        compress: true,
        inline: true,
        host: '127.0.0.1',
        port: 82,
        open: true,
        openPage: 'payments/15ced29a-b32b-4084-a067-19481049ee93',
        watchOptions: /([\\]+|\/)(node_modules|webpack|docs|dist|dev|\.idea)([\\]+|\/)/
    }
};