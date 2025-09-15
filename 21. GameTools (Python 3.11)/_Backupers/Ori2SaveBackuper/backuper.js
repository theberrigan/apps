const path = require('path');
const fs = require('fs');

const SRC_DIR = 'C:/Users/Berrigan/AppData/Local/Ori and the Will of The Wisps';
const BKP_DIR = path.join(__dirname, 'backups');
const SAVEGAME_REGEX = /^saveFile(\d+)\.uberstate$/;
const BACKUP_REGEX = /^(\d+)_saveFile(\d+)\.uberstate$/;
const MAX_BACKUPS = 1000;


const formatDate = (date) => {
    return (
        String(date.getDate()).padStart(2, '0') + 
        '.' + 
        String(date.getMonth() + 1).padStart(2, '0') + 
        '.' + 
        String(date.getFullYear()) + 
        ' ' + 
        String(date.getHours()).padStart(2, '0') + 
        ':' + 
        String(date.getMinutes()).padStart(2, '0') +
        ':' + 
        String(date.getSeconds()).padStart(2, '0')
    );
};

const makeBackup = (slot, fileName, filePath) => {
    const maxBackups = Math.max(1, MAX_BACKUPS);
    const backupDir = path.join(BKP_DIR, `slot_${ slot }`);

    fs.mkdirSync(backupDir, { recursive: true });

    const backups = fs.readdirSync(backupDir).filter(item => item.endsWith('.uberstate')).sort();

    const lastIndex = (() => {
        if (backups.length) {
            const lastBackup = backups[backups.length - 1];
            const match = lastBackup.match(BACKUP_REGEX);

            if (match) {
                return Number(match[1]);
            }
        }

        return null;
    })();

    const backupIndex = lastIndex === null ? 1 : (lastIndex + 1);
    const backupName = String(backupIndex).padStart(16, '0') + '_' + fileName;
    const backupPath = path.join(backupDir, backupName);

    fs.copyFileSync(filePath, backupPath);

    console.log('Slot:', slot, '| Date:', formatDate(new Date()));
    console.log('Copy:', filePath, '-->', backupPath);

    backups.push(backupName);

    const backupsToDelete = backups.splice(0, backups.length - maxBackups);
       
    backupsToDelete.forEach(item => {
        const filePath = path.join(backupDir, item);

        fs.unlinkSync(filePath);

        console.log('Delete:', filePath);
    });

    console.log(' ');
};

const timers = {};

fs.watch(SRC_DIR, {
    recursive: false
}, (eventType, fileName) => {
    const filePath = path.join(SRC_DIR, fileName);
    const match = fileName.match(SAVEGAME_REGEX);

    if (!match || !fs.existsSync(filePath)) {
        return;
    }

    const slot = Number(match[1]);

    if (timers[slot]) {
        clearTimeout(timers[slot]);
    }

    timers[slot] = setTimeout(() => {
        timers[slot] = null;
        makeBackup(slot, fileName, filePath);
    }, 1500);
});