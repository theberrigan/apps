const fs = require('fs');
const path = require('path');
const csstree = require('css-tree');
const { validate: ValidateOptions } = require('schema-utils');
const { lookup: mimeLookup } = require('mime-types');

// https://webpack.js.org/contribute/plugin-patterns/
// https://webpack.js.org/contribute/writing-a-plugin
class AngularEmbedPreloadAssetsWebpackPlugin {
    constructor (options = {}) {
        this.pluginName = this.constructor.name;
        this.options = options;

        /*
        const schema = {
            type: 'object',
            properties: {
                test: {
                    type: 'string'
                }
            }
        };

        ValidateOptions(schema, options, { name: this.pluginName });
        */
    }

    apply (compiler) {
        const isDev = compiler.options.mode === 'development';

        compiler.hooks.afterEmit.tap(this.pluginName, (compilation) => {
            const outFs = isDev ? compiler.outputFileSystem : fs;
            const outputDir = compiler.options.output.path;
            const indexFileName = path.parse((this.options.indexFile || '').trim()).base || 'index.html';
            const indexFilePath = path.join(outputDir, indexFileName);

            if (!outFs.existsSync(outputDir)) {
                throw new Error(`webpackConfig.output.path doesn't exist: ${ outputDir }`);
            }

            if (!outFs.existsSync(indexFilePath)) {
                throw new Error(`index.html doesn't exist: ${ indexFilePath }`);
            }

            const assetPaths = compilation.getAssets().map(asset => {
                return path.join(outputDir, asset.name);
            });

            // const cssPaths = assetPaths.filter(filePath => /\.css$/i.test(filePath));
            // this.embedAssetsToCss(cssPaths, outputDir, outFs);

            const fontUrls = assetPaths
                .filter(filePath => /-(Regular|Medium|SemiBold|Bold)\.[A-Z\d]+\.woff2$/i.test(filePath))
                .map(fontPath => path.relative(outputDir, fontPath).replace(/[/\\]+/g, '/'));

            const preloadTags = fontUrls.map(fontUrl => {
                return `<link rel="preload" href="${ fontUrl }" as="font" type="font/woff2" crossorigin="anonymous">`;
            });

            const indexContent = compiler.outputFileSystem.readFileSync(indexFilePath).toString();
            const updatedIndexContent = indexContent.replace(/<\/head>/i, `${ preloadTags.join('\n') }\n</head>`);

            compiler.outputFileSystem.writeFileSync(indexFilePath, updatedIndexContent);
        });
    }

    embedAssetsToCss (cssPaths, outputDir, outFs) {
        cssPaths.forEach(cssPath => {
            if (!outFs.existsSync(cssPath)) {
                throw new Error(`CSS file presents in assets list but doesn't exist: ${ cssPath }`);
            }

            const cssDir = path.parse(cssPath).dir;
            const cssContent = outFs.readFileSync(cssPath).toString();
            const cssAst = csstree.parse(cssContent);

            let isSrcDecl = false;

            csstree.walk(cssAst, node => {
                if (node.type === 'Declaration') {
                    isSrcDecl = node.property === 'src';
                }

                if (isSrcDecl && node.type === 'Url' && node.value.type === 'String') {
                    let match = node.value.value.match(/^(['"]?)(.*)\1$/i);

                    if (!match) {
                        return;
                    }

                    const assetUrl = match[2].trim();

                    if (!assetUrl || /^(data:|https?:\/\/)/i.test(assetUrl)) {
                        return;
                    }

                    match = assetUrl.split(/[?#]/i);

                    if (!match) {
                        return;
                    }

                    const assetPath = match[0];

                    match = assetUrl.match(/(\.[A-Z\d\-_]+)$/i);

                    if (!match) {
                        return;
                    }

                    const ext = match[1].toLowerCase();
                    const mimeType = mimeLookup(ext) || 'application/octet-stream';
                    const assetPathPrefix = /^[/\\]/.test(assetPath[0]) ? outputDir : cssDir;
                    const assetAbsPath = path.resolve(assetPathPrefix, assetPath);
                    const encodedFontData = outFs.readFileSync(assetAbsPath).toString('base64');

                    node.value.value = JSON.stringify(`data:${ mimeType };base64,${ encodedFontData }`);
                }
            });

            outFs.writeFileSync(cssPath, csstree.generate(cssAst));
        });
    }
}

/*

// - embedding works only with emitted .css files
// - embedding breaks css source map

const options = {
    logLevel: 'verbose', // 'warning' | 'error'
    onFileDoesNotExist: 'error',  // 'warning' | 'skip'
    rules: [
        {
            action: 'preload', // | 'embed'
            indexFileName: 'index.html',
            assetUrlFilter: '',
            chooseOneFontExt: 'woff2 woff ttf otf eot svg',
            sizeLimit: {
                images: '900kb',
                fonts: '900kb',
                total: '5mb'
            },
            extraAssets: [
                {
                    url: '',
                    type: '',
                    mimeType: ''
                }
            ],
            extraAssetsFilePath: '/assets-to-preload.json',
            onBeforeFilters: () => {
                const data = {
                    totalSize: 0,
                    alreadyPreloadedAssets: [

                    ],
                    assets: [
                        {
                            type: 'image',
                            mimeType: '',
                            url: '',
                            filePath: '',
                            size: 0
                        }
                    ]
                };
            },
            onAfterFilters: () => {}
        },
        {
            action: 'embed',
            cssPathFilter: '',
            assetUrlFilter: '',
            encodeToBase64: true, // true | false
            removeSourceMap: true,
            deleteEmbeddedAsset: false
        }
    ]
};

// ---------------------------------------------------------------------------------------

compiler.outputFileSystem.

const fonts = assets.filter(filePath => /assets[\\/]+fonts[\\/]+.+-(Regular|Medium|SemiBold|Bold)\..*\.woff2$/i.test(filePath));
const tags = fonts.map(filePath => {
    return `<link rel="preload" href="${ filePath }" as="font" type="font/woff2" crossorigin="anonymous">`;
});

const indexHtml = assets.find(filePath => /[\\/]*index\.html$/i.test(filePath));
const indexHtmlFilePath = path.join(compiler.options.output.path, indexHtml);
const indexHtmlContent = compiler.outputFileSystem.readFileSync(indexHtmlFilePath).toString();

const updatedIndexHtmlContent = indexHtmlContent.replace(/<\/head>/i, `${ tags.join('\n') }\n</head>`);

compiler.outputFileSystem.writeFileSync(indexHtmlFilePath, updatedIndexHtmlContent);

console.log('Ok');

 */

module.exports = {
    AngularEmbedPreloadAssetsWebpackPlugin
};
