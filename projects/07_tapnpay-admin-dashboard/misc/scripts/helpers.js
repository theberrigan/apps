const fs = require('fs');
const path = require('path');

const { LOCALES } = require('../../config/app/common');



const ROOT_DIR = (() => {
    let dir = __dirname;
    const disk = path.parse(dir).root;

    while (true) {
        if (fs.readdirSync(dir).includes('package.json')) {
            return dir;
        } else if (dir === disk) {
            return null;
        }

        dir = path.resolve(dir, '..');
    }
})();

const SRC_DIR = path.resolve(ROOT_DIR, 'src');

const normalizeSlashes = filename => filename.replace(/[\/\\]+/g, '/');

const resolvePath = relativePath => normalizeSlashes(path.resolve(ROOT_DIR, relativePath));

const getRelativeToRoot = absPath => normalizeSlashes(path.relative(ROOT_DIR, absPath));

const resolveDistAsset = (filename, outputName = null) => {
    const assetRelDir = path.dirname(path.relative(SRC_DIR, filename));
    return normalizeSlashes(assetRelDir + '/' + (outputName || path.basename(filename)));
};

const isFile = filePath => {
    try {
        return fs.lstatSync(filePath).isFile();
    } catch (e) {
        return false;
    }
};

const getType = entity => Object.prototype.toString.call(entity).slice(8, -1).toLowerCase();

const isFunction = f => typeof(f) === 'function';

const isNumber = n => typeof(n) === 'number';

const isString = n => typeof(n) === 'string';

const isFinite = (() => Number.isFinite || (n => isNumber(n) && window.isFinite(n)))();

const isInt = n => isNumber(n) && isFinite(n) && n === parseInt(n, 10);

const isFloat = n => isNumber(n) && isFinite(n) && n !== parseInt(n, 10);

const isIntString = s => isString(s) && isInt(Number(s));

const isFloatString = s => isString(s) && isFloat(Number(s));

const isArray = (() => Array.isArray)();  // TODO: add polyfill

// [], new Array, null, Math, window => false
// {}, new (class A{}), new Object => true
const isObject = o => o !== null && typeof(o) === 'object' && !isArray(o) && getType(o) === 'object';

// [], new Array, null, Math, window, new (class A{}) => false
// {}, new Object => true
const isPlainObject = obj => {
    if (isObject(obj)) {
        if (isFunction(Object.getPrototypeOf)) {
            const proto = Object.getPrototypeOf(obj);
            return proto === Object.prototype || proto === null;
        }

        return (
            isFunction(obj.constructor) &&
            isObject(obj.constructor.prototype) &&
            obj.constructor.prototype.hasOwnProperty('isPrototypeOf')
        );
    }

    return false;
};


module.exports = {
    ROOT_DIR,
    SRC_DIR,
    LOCALES: LOCALES.map(locale => locale.code),
    normalizeSlashes,
    resolveDistAsset,
    resolvePath,
    getRelativeToRoot,
    isFile,
    isObject,
    isPlainObject,
    isFunction,
    isString,
    isFinite,
    isArray
};

/*
const items = [
    1,
    1.1,
    'String',
    {},
    new (class A {}),
    [],
    null,
    undefined,
    NaN,
    Infinity,
    -Infinity,
    window,
    document,
    Math,
    Symbol('Hello')
];
*/
