const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const webpack = require('webpack');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const { PostcssCliResources } = require('@angular-devkit/build-angular/src/angular-cli-files/plugins/webpack');
const MomentLocalesPlugin = require('moment-locales-webpack-plugin');
const moment = require('moment');
const beautifyJs = require('js-beautify').js;

const { NgrokWebpackPlugin } = require('./ngrok-webpack-plugin');

const {
    LOCALES,
    resolveDistAsset,
    getRelativeToRoot,
    isFile,
    resolvePath,
    isObject,
    isPlainObject,
    isFunction
} = require('../../misc/scripts/helpers');

// --------------------------------

const normalizeLoaders = rules => {
    for (let rule of rules) {
        if (rule.loader) {
            rule.use = [
                {
                    loader: rule.loader,
                    options: rule.options  // may be undefined
                }
            ];

            delete rule.loader;
            delete rule.options;
        } else if (rule.use) {
            for (let i = 0; i < rule.use.length; i++) {
                const useEntry = rule.use[i];

                if (typeof(useEntry) === 'string') {
                    rule.use[i] = {
                        loader: useEntry
                    };
                }
            }
        }
    }

    return rules;
};

const compare = (compareWhat, compareWith) => {
    if (compareWith instanceof RegExp) {
        return compareWith.test(compareWhat);
    } else if (typeof(compareWith) === 'string') {
        return compareWhat.toLowerCase() === compareWith.toLowerCase();
    } else if (typeof(compareWith) === 'function') {
        return compareWith(compareWhat);
    } else {
        throw new Error('Unexpected compareWith argument type');
    }
};

// Finds use entry in the normalized by normalizeLoaders() config.rules
const findUseEntryByName = (rules, toFind, findOne) => {
    const foundUseEntries = [];

    for (let rule of rules) {
        if (!rule.use) {
            continue;
        }

        for (let i = 0; i < rule.use.length; i++) {
            const useEntry = rule.use[i];

            if (compare(useEntry.loader, toFind)) {
                if (findOne) {
                    return useEntry;
                }

                foundUseEntries.push(useEntry);
            }
        }
    }

    return findOne ? null : foundUseEntries;
};

const findPluginByName = (plugins, toFind, findOne) => {
    const foundPlugins = [];

    for (let i = 0; i < plugins.length; i++) {
        const plugin = plugins[i];

        if (compare(plugin.constructor.name, toFind)) {
            const pluginWrap = {
                parent: plugins,
                key: i,
                plugin
            };

            if (findOne) {
                return pluginWrap;
            }

            foundPlugins.push(pluginWrap);
        }
    }

    return findOne ? null : foundPlugins;
};


const ejectConfig = config => {
    config = JSON.stringify(config, (key, value) => {
        if (value && isPlainObject(value)) {
            return Object.keys(value).reduce((acc, k) => {
                acc[ `<key>${ k }</key>` ] = value[k];
                return acc;
            }, {});
        }

        if (value instanceof RegExp) {
            return `<regexp>/${ value.source }/${ value.flags }</regexp>`;
        }

        if (isObject(value) && !isPlainObject(value)) {
            return `<instance>new ${ value.constructor.name }(/* truncated options */)</instance>`;
        }

        if (isFunction(value)) {
            return `<function>${ value.toString() }</function>`;
        }

        if (typeof(value) === 'string') {
            return `<string>${ value }</string>`;
        }

        return value;
    }, '    ');

    config = config.replace(/"<(key|function|regexp|instance|string)>((?!<\/\1>).*)<\/\1>"/g, (match, type, content) => {
        const asSingleQuotedString = str => `'${ str.replace(/'/g, "\\'") }'`;

        switch (type) {
            case 'function':
                return content.replace(/\\n/g, '\n');
            case 'regexp':
                return content.replace(/\\\\/g, '\\');
            case 'key':
                return /^[a-z\d_$]+$/i.test(content) ? content : asSingleQuotedString(content);
            case 'string':
                return asSingleQuotedString(content);
        }

        return content;
    });

    const parsedFilename = path.parse(__filename);

    const outputPath = path.resolve(__dirname, `./${ parsedFilename.name }.ejected${ parsedFilename.ext }`);

    fs.writeFileSync(outputPath, 'module.exports = ' + beautifyJs(config, {
        indent_size: 4
    }));

    console.log('\nOriginal webpack config ejected to:', getRelativeToRoot(outputPath), '\n');
    process.exit(0);
};


// --------------------------------

module.exports = (config, buildOptions) => {
    // console.log(buildOptions);
    // process.exit(0);
    config.module.rules = normalizeLoaders(config.module.rules);

    // ejectConfig(config);

    // PATCH CONFIG
    // -------------------------------

    // AWS SDK requires fs and tls
    config.node = {
        fs: 'empty',
        tls: 'empty'
    };

    if (config.devServer) {
        config.devServer.disableHostCheck = true;
    }


    const resourcesRule = config.module.rules.find(rule => /(.*(svg|png|woff)){3,}/.test(rule.test.source));

    if (!resourcesRule) {
        throw new Error('Resource rule is not found');
    }

    const fileLoaderUseEntry = findUseEntryByName([ resourcesRule ], /file-loader/, true);

    if (!fileLoaderUseEntry) {
        throw new Error('Use entry of file loader is not found in resource rule');
    }

    fileLoaderUseEntry.options.name = filename => resolveDistAsset(filename, '[name].[hash:20].[ext]');
    fileLoaderUseEntry.options.esModule = false;  // https://stackoverflow.com/a/59075858

    const postcssLoaderUseEntries = findUseEntryByName(config.module.rules, /postcss-loader/);

    if (!postcssLoaderUseEntries.length) {
        throw new Error('postcss-loader use entries not found');
    }

    postcssLoaderUseEntries.forEach((useEntry) => {
        const pluginsFactory = useEntry.options.plugins;

        if (typeof(pluginsFactory) !== 'function') {
            console.warn('Found postcss-loader without pluginsFactory');
            return;
        }

        useEntry.options.plugins = loader => {
            const plugins = pluginsFactory(loader);

            if (!Array.isArray(plugins)) {
                console.warn('postcss-loader pluginsFactory is not an array');
                return plugins;
            }

            return plugins.map(plugin =>  {
                if (typeof(plugin) === 'function' && plugin.toString().startsWith('(root)')) {
                    return PostcssCliResources({
                        baseHref: buildOptions.baseHref,
                        deployUrl: buildOptions.deployUrl,
                        resourcesOutputPath: '',
                        loader,
                        rebaseRootRelative: buildOptions.rebaseRootRelativeCssUrls,
                        filename: filename => resolveDistAsset(filename, '[name].[hash:20].[ext]'),
                        emitFile: buildOptions.platform !== 'server',
                    });
                }

                return plugin;
            });
        };
    });

    const localesHashes = (() => {
        const hashes = {};
        const localesDir = resolvePath('src/assets/locale');

        fs.readdirSync(localesDir).forEach(item => {
            const localePath = path.join(localesDir, item);
            const { name, ext } = path.parse(item.toLowerCase());

            if (isFile(localePath) && ext === '.json') {
                const fileContent = fs.readFileSync(localePath, { encoding: 'utf8' });
                hashes[name] = crypto.createHash('md5').update(fileContent.toString(), 'utf8').digest('hex');
            }
        });

        return hashes;
    })();

    config.module.rules.push({
        test: /\.html$/i,
        loader: 'html-loader',
        options: {
            minimize: false
        }
    });


    config.plugins.push(
        new CopyWebpackPlugin([
            {
                from: 'node_modules/d3-graphviz/node_modules/@hpcc-js/wasm/dist/*.wasm',
                to: '[name].[ext]'
            },
            {
                from: './src/favicon.ico',
                to: './favicon.ico'
            },
            {
                from: './src/robots.txt',
                to: './robots.txt'
            },
            {
                from: './src/assets/locale/',
                to: './assets/locale/',
                transform: (content, filePath) => {
                    const ext = filePath.split(/\.([a-z\d]+)$/i)[1].toLowerCase();

                    switch (ext) {
                        case 'json':
                            return JSON.stringify(JSON.parse(content.toString()));
                        case 'html':
                            return content;
                        default:
                            return content;
                    }
                }
            },
        ]),
        // strip unnecessary locales for moment.js
        new MomentLocalesPlugin({
            localesToKeep: LOCALES,
        }),
        new webpack.DefinePlugin({
            APP_VERSION: JSON.stringify(require(resolvePath('package.json')).version),
            APP_RELEASE_DATE: JSON.stringify(moment().format('D MMM YYYY HH:mm')),
            LOCALES_HASHES: JSON.stringify(localesHashes)
        }),
        // new AngularEmbedPreloadAssetsWebpackPlugin({
        //     indexFile: buildOptions.index
        // })
    );

    if (config.mode === 'development') {
        config.plugins.push(new NgrokWebpackPlugin({
            configPath: './config/ngrok/ngrok.yml'
        }));
    }

    const ngtools = findUseEntryByName(config.module.rules, /@ngtools[\\\/]webpack/, true);

    if (!ngtools) {
        throw new Error('ngtools use entry is not found');
    }

    const { AngularCompilerPlugin } = require(ngtools.loader);

    const compilerPlugin = findPluginByName(config.plugins, 'AngularCompilerPlugin', true);

    if (!compilerPlugin) {
        throw new Error('AngularCompilerPlugin is not found');
    }

    const compilerPluginOptions = compilerPlugin.plugin.options;
    delete compilerPluginOptions.logger;  // will be recreated

    compilerPluginOptions.directTemplateLoading = false;

    compilerPlugin.parent[compilerPlugin.key] = new AngularCompilerPlugin(compilerPluginOptions);

    return config;
};
