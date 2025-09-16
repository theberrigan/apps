const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');

const SRC_DIR = path.resolve(ROOT_DIR, 'src');

exports.root = (...args) => path.join(ROOT_DIR, ...args);

exports.relative = (filepath, toSrc) => path.relative(toSrc ? SRC_DIR : ROOT_DIR, filepath);

exports.assetPath = (filepath, filename) => {
    return (path.dirname(path.relative(SRC_DIR, filepath)) + '/' + (filename || path.basename(filepath) || '')).replace(/[\\\/]+/g, '/');
};

