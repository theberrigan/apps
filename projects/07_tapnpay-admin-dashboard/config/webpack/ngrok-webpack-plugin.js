const { spawn } = require('child_process');

class NgrokWebpackPlugin {
    constructor (options = {}) {
        this.pluginName = this.constructor.name;
        this.options = options;
        this.isWatchMode = false;
        this.isRunning = false;
    }

    apply (compiler) {
        const isDev = compiler.options.mode === 'development';

        compiler.hooks.watchRun.tapAsync(this.pluginName, (compilation, callback) => {
            this.isWatchMode = true;
            callback();
        });

        compiler.hooks.afterEmit.tapAsync(this.pluginName, async (compilation, callback) => {
            if (!this.isWatchMode || this.isRunning) {
                return callback();
            }

            const ngrok = spawn('./misc/utils/ngrok.exe', [ 'start', '--all', '--log', 'stdout', '--config', './config/ngrok/ngrok.yml' ]);

            ngrok.stdout.on('data', (data) => {
                // console.log(`stdout: ${ data }`);
            });

            ngrok.stderr.on('data', (data) => {
                console.error(`stderr: ${ data }`);
            });

            ngrok.on('close', (code) => {
                console.log(`ngrok exited with code ${ code }`);
            });

            this.isRunning = true;

            process.once('exit', () => {
                ngrok.kill();
            });

            process.once('SIGINT', () => {
                process.exit(0);
            });

            callback();
        });
    }
}

module.exports = {
    NgrokWebpackPlugin
};
