const path = require('path');
const fs = require('fs');

const SRC_DIR = 'C:/Program Files (x86)/Steam/userdata/108850163/337000/remote/';
const BKP_DIR = path.join(__dirname, 'backups');
const SAVEGAME_REGEX = /^DXNGsavegame\d+\.dat$/;
const BACKUP_REGEX = /^(DXNGsavegame\d+\.dat)_\d+$/;
const MAX_BACKUPS = 5;

const timers = {};

fs.watch(SRC_DIR, {
    recursive: false
}, (eventType, fileName) => {
    const filePath = path.join(SRC_DIR, fileName);

    if (!SAVEGAME_REGEX.test(fileName) || !fs.existsSync(filePath)) {
        return;
    }

    if (timers[fileName]) {
        clearTimeout(timers[fileName]);
    }

    timers[fileName] = setTimeout(() => {
        timers[fileName] = null;
        makeBackup(fileName, filePath);
    }, 1500);
});

const makeBackup = (fileName, filePath) => {
    const maxBackups = Math.min(99, Math.max(1, MAX_BACKUPS));
    const backups = fs.readdirSync(BKP_DIR).filter(item => item.startsWith(fileName)).sort();
    const backupsToDelete = backups.splice(0, backups.length - maxBackups + 1);

    if (backupsToDelete.length) {        
        backupsToDelete.forEach(item => {
            const filePath = path.join(BKP_DIR, item);
            fs.unlinkSync(filePath);
            console.log('Delete:', filePath);
        });

        backups.forEach((item, i) => {
            const oldSavePath = path.join(BKP_DIR, item);
            const newSavePath = path.join(BKP_DIR, item.slice(0, -2) + String(i + 1).padStart(2, '0'));
            fs.renameSync(oldSavePath, newSavePath);
            console.log('Rename:\n   ', oldSavePath, '\n   ', newSavePath);
        });
    }

    const backupFilePath = path.join(BKP_DIR, fileName + '_' + String(backups.length + 1).padStart(2, '0'));
    fs.copyFileSync(filePath, backupFilePath);
    console.log('Copy:\n   ', filePath, '\n   ', backupFilePath, '\n---------------------------------------------------------------');
};