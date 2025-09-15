const fs = require('fs');
const path = require('path');

const chalk = require('chalk');
const cmd = require('node-cmd');

const { resolvePath, getRelativeToRoot, isString, isFinite, isArray } = require('./helpers.js');


const exit = (...args) => {
    console.error(chalk.red('ERROR:'), ...args);
    process.exit();
};

const parseArgs = () => {
    const args = process.argv.slice(2);
    const parsedArgs = {};
    let prevKey = null;

    for (let arg of args) {
        const match = arg.match(/^-([a-z])$/i);

        if (match) {
            prevKey = match[1];
            parsedArgs[prevKey] = null;
        } else if (prevKey) {
            parsedArgs[prevKey] = arg;
            prevKey = null;
        } else {
            exit('Unexpected args');
        }
    }

    return parsedArgs;
};

const scriptArgs = parseArgs();
const configuration = scriptArgs.c;

if (!configuration) {
    exit(`Configuration is not specified (argument "-c")`);
}

console.log(chalk.blue('Configuration:'), configuration);

const configPath = resolvePath(`./config/deploy/deploy.${ configuration }.json`);

if (!fs.existsSync(configPath)) {
    exit('Config does not exist:', configPath);
}

console.log(chalk.blue('Using config:'), getRelativeToRoot(configPath));

const config = JSON.parse(fs.readFileSync(configPath, { encoding: 'UTF-8' }).toString());

if (!config.distPath) {
    exit('distPath is not specified in config');
}

const distPath = resolvePath(config.distPath);

if (!fs.existsSync(distPath)) {
    exit('distPath does not exist:', getRelativeToRoot(distPath));
}

if (fs.readdirSync(distPath).length === 0) {
    exit('distPath is empty:', getRelativeToRoot(distPath));
}

console.log(chalk.blue('Dist path:'), getRelativeToRoot(distPath));

const getStringConfigValue = (config, key) => isString(config[key]) && (config[key] || '').trim() || null;

const serializeCmdArg = arg => {
    arg = String(arg).trim();
    return /[\n\t\r\s\\\/]/.test(arg) ? JSON.stringify(arg) : arg;
};

const s3dLink = 'https://github.com/import-io/s3-deploy';

const region = getStringConfigValue(config, 'region');
const bucket = getStringConfigValue(config, 'bucket');

if (!region) {
    exit('"region" is not specified in config file');
}

if (!bucket) {
    exit('"bucket" is not specified in config file');
}

const deployCmd = [
    's3-deploy',
    JSON.stringify(path.posix.join(distPath, '**')),
    '--cwd',
    JSON.stringify(distPath),
    '--region',
    config.region,
    '--bucket',
    config.bucket
];

if (config.gzip) {
    deployCmd.push('--gzip');
    const gzipExtensions = getStringConfigValue(config, 'gzipExtensions');

    if (gzipExtensions) {
        deployCmd.push(serializeCmdArg(gzipExtensions));
    }
}

const usedTogetherCacheParams = [ 'cacheControl', 'cache', 'noCache', 'immutable' ].filter(param => config[param]);

if (usedTogetherCacheParams.length > 1) {
    exit(`Do not use together "${ usedTogetherCacheParams.join('", "') }". See:`, chalk.yellow(s3dLink));
}

if (config.cache) {
    if (isFinite(config.cache)) {
        deployCmd.push('--cache', config.cache);
    } else {
        exit(`Invalid "cache" value: ${ config.cache }. See:`, chalk.yellow(s3dLink));
    }
}

if (config.preventUpdates) {
    deployCmd.push('--preventUpdates');
}

if (config.immutable) {
    deployCmd.push('--immutable');
}

if (config.noCache) {
    deployCmd.push('--noCache');
}

const cacheControl = getStringConfigValue(config, 'cacheControl');

if (cacheControl) {
    deployCmd.push('--cacheControl', serializeCmdArg(cacheControl));
}

if (config.etag) {
    deployCmd.push('--etag');

    if (typeof(config.etag) !== 'boolean') {
        deployCmd.push(serializeCmdArg(config.etag));
    }
}

const signatureVersion = getStringConfigValue(config, 'signatureVersion');

if (signatureVersion) {
    deployCmd.push('--signatureVersion', serializeCmdArg(signatureVersion));
}

const filePrefix = getStringConfigValue(config, 'filePrefix');

if (filePrefix) {
    deployCmd.push('--signatureVersion', serializeCmdArg(filePrefix));
}

const profile = getStringConfigValue(config, 'profile');

if (profile) {
    deployCmd.push('--profile', serializeCmdArg(profile));
}

if (config.private) {
    deployCmd.push('--private');
}

if (config.deleteRemoved) {
    deployCmd.push('--deleteRemoved');

    if (isString(config.deleteRemoved)) {
        const deleteRemoved = getStringConfigValue(config, 'deleteRemoved');
        if (deleteRemoved) {
            deployCmd.push(deleteRemoved);
        }
    }
}

const index = getStringConfigValue(config, 'index');

if (index) {
    deployCmd.push('--index', serializeCmdArg(index));
}

const distId = getStringConfigValue(config, 'distId');

if (distId) {
    deployCmd.push('--distId', serializeCmdArg(distId));
}

if (isArray(config.invalidate) && config.invalidate.length) {
    const invalidate = config.invalidate.map(filepath => `'${ filepath }'`).join(' ');
    deployCmd.push('--invalidate', serializeCmdArg(invalidate));
}

const deployCmdString = deployCmd.join(' ');

console.log(chalk.blue('s3-deploy command:'), deployCmdString);

cmd.get(deployCmdString, (err, data, stderr) => {
    if (err) {
        return exit(err);
    }

    console.log(data);
});

// --distId
// --invalidate
