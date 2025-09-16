const path = require('path');
const fs = require('fs');

const SAVE_DIR = 'C:/Users/Berrigan/AppData/LocalLow/Buckshot Software/Project Warlock/Steam/76561198069115891';
const SAVE_FILE_NAME = 'gamesave';
const SAVE_FILE_PATH = path.join(SAVE_DIR, SAVE_FILE_NAME);
const BACKUPS_DIR = path.join(__dirname, 'backups');
const MAX_BACKUPS = 200;
const MIN_BACKUP_DELAY = 5 * 60 * 1000;  // 5min

let throttleTimer = null;
let lastBackupInfo = null;

const main = () => {
    lastBackupInfo = getLastBackupInfo();

    if (!fs.existsSync(SAVE_DIR)) {
        console.warn(`Save dir doesn't exist: ${ SAVE_DIR }`);
        process.exit(0);
    }

    fs.watch(SAVE_DIR, (eventType, fileName) => {
        if (!fileName) {
            return;
        }

        if (fileName.toLowerCase() !== SAVE_FILE_NAME.toLowerCase()) {
            return;
        }

        if (throttleTimer !== null) {
            clearTimeout(throttleTimer);
        }

        throttleTimer = setTimeout(() => {
            throttleTimer = null;
            makeBackup();
        }, 1000);
    });
};

const makeBackup = () => {
    if (!fs.existsSync(SAVE_FILE_PATH)) {
        return;
    }

    let data = fs.readFileSync(SAVE_FILE_PATH, 'utf8');

    try {
        data = JSON.parse(data);
    } catch (e) {
        return;
    }

    const level = data.StringData?.find(i => i.Key === 'CurrentLevel')?.Value || 'unknown';
    const lives = data.IntData?.find(i => i.Key === 'Lives')?.Value || 0;
    const date  = getFileModTime(SAVE_FILE_PATH);

    if ((date.getTime() - lastBackupInfo.time) < MIN_BACKUP_DELAY && lastBackupInfo.level === level && lastBackupInfo.lives >= lives) {
        return;
    }

    const backupName = `${ formatSafeDate(date) }__${ level }__${ lives }.json`;
    const backupPath = path.join(BACKUPS_DIR, backupName);

    createBackupsDir();

    fs.copyFileSync(SAVE_FILE_PATH, backupPath);

    lastBackupInfo = {
        time: Date.now(),
        level,
        lives
    };

    console.log('Created:', backupName);

    const maxBackups = Math.min(300, Math.max(1, MAX_BACKUPS));
    const backups = getBackups();
    const toDelete = backups.slice(0, Math.max(0, backups.length - maxBackups))

    toDelete.forEach(backupName => {
        fs.unlinkSync(path.join(BACKUPS_DIR, backupName));

        console.log('Deleted:', backupName);
    });

    console.log(' ');

    // process.exit(0);
};

const getLastBackupInfo = () => {
    createBackupsDir();

    const backups = getBackups();

    if (!backups.length) {
        return {
            time: 0,
            level: '',
            lives: 0
        };
    }

    const lastBackupName = backups.pop();

    const [ level, lives ] = dropExt(lastBackupName).split('__').slice(1);
    const date = getFileModTime(path.join(BACKUPS_DIR, lastBackupName));

    return {
        time: date.getTime(),
        level,
        lives: Number(lives)
    };
};

const createBackupsDir = () => {
    fs.mkdirSync(BACKUPS_DIR, {
        recursive: true
    });
};

const getBackups = () => {
    createBackupsDir();

    return fs.readdirSync(BACKUPS_DIR).sort();
};

const getFileModTime = (filePath) => {
    return new Date(fs.statSync(filePath).mtime);
};

const dropExt = (itemPath) => {
    return path.parse(itemPath).name;
};

const formatSafeDate = (date) => {
    const year  = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day   = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const mins  = String(date.getMinutes()).padStart(2, '0');
    const secs  = String(date.getSeconds()).padStart(2, '0');

    return `${ year }-${ month }-${ day }_${ hours }-${ mins }-${ secs }`;
};

main();

/*
NewGame 0
ProgressSaved 0
SavedGame 1 0
Lives 0
MaxHealth 120
CharLevel 3 5
UnlockedLevels 0
CurrentEpisode 1
*/