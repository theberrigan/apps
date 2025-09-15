const cmd = require('node-cmd');
const path = require('path');
const fs = require('fs');

function exit () {
    console.log.apply(console, [ 'ERROR:' ].concat(Array.from(arguments)));
    process.exit();
}

const argv = process.argv.splice(2);
const env = (argv[0] || '--prod').substr(2).toLowerCase();

if (![ 'prod', 'stage' ].includes(env)) {
    exit('Unexpected deploy environment name:', env);
}

var configPath = './config/deploy/deploy.' + env + '.json';

var config = fs.readFileSync(
    configPath,
    {
        encoding: 'UTF-8'
    }
);

config = JSON.parse(config);

// ------------------

var distDir = path.resolve(config.dist);

if (!fs.existsSync(distDir)) {
    exit('Such directory doesn\'t exists:', distDir);
}

var deployCmd = [
    's3-deploy',
    '"' + path.join(distDir, '**') + '"',
    '--cwd',
    '"' + distDir + '"',
    '--region',
    config.region,
    '--bucket',
    config.bucket
];

if (config.gzip) {
    deployCmd.push('--gzip');
}

if (config.cache) {
    if (Number.isFinite(config.cache)) {
        deployCmd.push('--cache');
        deployCmd.push(config.cache);
    } else {
        exit('Unexpected \'cache\' value:', config.cache);
    }
}

if (config.immutable) {
    deployCmd.push('--immutable');
}

if (config.etag) {
    deployCmd.push('--etag');
    deployCmd.push(config.etag);
}

if (config.signatureVersion) {
    deployCmd.push('--signatureVersion');
    deployCmd.push(config.signatureVersion);
}

if (config.filePrefix) {
    deployCmd.push('--filePrefix');
    deployCmd.push(config.filePrefix);
}

if (config.profile) {
    deployCmd.push('--profile');
    deployCmd.push(config.profile);
}

if (config.private) {
    deployCmd.push('--private');
}

if (config.ext) {
    deployCmd.push('--ext');
    deployCmd.push(config.ext);
}

if (config.deleteRemoved) {
    deployCmd.push('--deleteRemoved');
}

var command = deployCmd.join(' ');

console.log('Deploy config:', configPath);
console.log('Dist dir:', distDir);
console.log('Command:', command);
console.log('\n', 's3-deploy working now...', '\n');

cmd.get(
    command,
    function (err, data, stderr) {
        console.log(err || data);
    }
);
