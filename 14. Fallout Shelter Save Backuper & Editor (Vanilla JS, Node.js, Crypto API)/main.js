const path = require('path');
const fs = require('fs');



const SAVE_DIR = 'C:/Users/<USERNAME>/AppData/Local/FalloutShelter';  // %LOCALAPPDATA%
const SAVE_NAME_REGEX = /^Vault(\d+)\.sav$/i;
const BACKUPS_DIR = path.join(__dirname, 'backups');
const MAX_BACKUPS = 300;
const MIN_BACKUP_DELAY = 5 * 60 * 1000;  // 5min

const CRYPTO_ALGO = 'AES-CBC';
const CRYPTO_KEY  = 'a7ca9f3366d892c2f0bef417341ca971b69ae9f7bacccffcf43c62d1d7d021f9';
const CRYPTO_IV   = '7475383967656a693334307438397532';

const UNIX_EPOCH_TICKS = 621355968000000000;
const MS_PER_TICK = 10000;



const ticksToTime = (ticks) => {
    return (ticks - UNIX_EPOCH_TICKS) / MS_PER_TICK;
};

const hexToBin = (key) => {
    const bytes = key.match(/../g).map(b => parseInt(b, 16));

    return new Uint8Array(bytes).buffer;
};

const base64ToBin = (data) => {
    data = atob(data);

    const size  = data.length;
    const bytes = new Uint8Array(size);

    for (let i = 0; i < size; ++i) {
        bytes[i] = data.charCodeAt(i);
    }

    return bytes.buffer;
};

const binToBase64 = (data) => {
    if (data instanceof ArrayBuffer) {
        data = new Uint8Array(data);
    }

    data = data.reduce((str, code) => {
        return str + String.fromCharCode(code);
    }, '');

    return btoa(data);
};

const readTextFile = (filePath) => {
    return fs.readFileSync(filePath, 'utf-8');
};

const writeTextFile = (filePath, data) => {
    return fs.writeFileSync(filePath, data, 'utf-8');
};

const removeFile = (filePath) => {
    return fs.unlinkSync(filePath);
};

const getFileModTime = (filePath) => {
    return new Date(fs.statSync(filePath).mtime);
};

// fs.lstatSync(entityPath).isFile()
const isPathExists = (entityPath) => {
    return fs.existsSync(entityPath);
};

const copyFile = (srcPath, dstPath) => {
    fs.copyFileSync(srcPath, dstPath);
};

const createDirs = (dirPath) => {
    fs.mkdirSync(dirPath, {
        recursive: true
    });
};

const listDirFiles = (dirPath) => {
    if (!isPathExists(dirPath)) {
        return [];
    }

    return fs.readdirSync(dirPath);
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

class SaveEditor {
    constructor (method, key) {
        this._method   = method;
        this._key      = key;
        this._u8dec    = new TextDecoder('utf-8');
        this._u8enc    = new TextEncoder('utf-8');
        this._data     = null;
        this._savePath = null;
    }

    static async fromFile (savePath) {
        const data = readTextFile(savePath);

        return SaveEditor.create(data, savePath);
    }

    static async fromData (data) {
        return SaveEditor.create(data);
    }

    static async create (data = null, savePath = null) {
        const rawKey = hexToBin(CRYPTO_KEY);
        const method = {
            name: CRYPTO_ALGO,
            iv: hexToBin(CRYPTO_IV)
        };
        const actions = [ 'encrypt', 'decrypt' ];

        const key = await crypto.subtle.importKey('raw', rawKey, method, true, actions);

        const editor = new SaveEditor(method, key);

        if (data !== null) {
            await editor.setup(data, savePath);
        }

        return editor;
    }

    static async edit (savePath, fn) {
        const editor = await SaveEditor.fromFile(savePath);

        await fn(editor);

        const backupPath = savePath + '.se_bkp';

        copyFile(savePath, backupPath);

        await editor.save();
    }

    async setup (data, savePath = null) {
        this._savePath = savePath;
        await this.decode(data);
    }

    async save (savePath = null) {
        savePath ||= this._savePath;

        if (!savePath) {
            throw new Error('Path to save to is not specified');
        }

        const data = await this.encode();

        writeTextFile(savePath, data);
    }

    async decode (data) {
        data = base64ToBin(data);
        data = await crypto.subtle.decrypt(this._method, this._key, data);
        data = this._u8dec.decode(data);
        data = JSON.parse(data);

        this._data = data;

        return data;
    }

    async encode () {
        this.checkData();

        let data = this._data;

        data = JSON.stringify(data);
        data = this._u8enc.encode(data);
        data = await crypto.subtle.encrypt(this._method, this._key, data);
        data = binToBase64(data);

        return data;
    }

    getData () {        
        return this._data;
    }

    checkData () {        
        if (this._data === null) {
            throw new Error('Data not set');
        }
    }

    getSaveTime () {
        this.checkData();

        return ticksToTime(this._data.timeMgr.timeSaveDate);
    }

    setNuka (value) {
        this.checkData();

        this._data.vault.storage.resources.Nuka = value;
    }

    setQuantumNuka (value) {
        this.checkData();

        this._data.vault.storage.resources.NukaColaQuantum = value;
    }

    setLunchbox (value) {
        this.checkData();

        this._data.vault.storage.resources.Lunchbox = value;
        this._data.vault.storage.bonus.Lunchbox = value;
        this._data.StatsWindow.vaultData.collectedRes.Lunchbox = value;
        this._data.vault.LunchBoxesCount = value;
    }
}

class SaveBackuper {
    constructor () {
        this.timers = {};
        this.backupInfos = {};
    }

    static watch () {
        new SaveBackuper().watch();
    }

    watch () {
        fs.watch(SAVE_DIR, (eventType, fileName) => {        
            if (!fileName) {
                return;
            }

            const filePath = path.join(SAVE_DIR, fileName);

            if (!isPathExists(filePath)) {
                return;
            }

            const match = fileName.match(SAVE_NAME_REGEX);

            if (!match) {
                return;
            }

            const vaultId = Number(match[1]);

            if (!Number.isFinite(vaultId)) {
                return;
            }

            if (this.timers[vaultId] !== null) {
                clearTimeout(this.timers[vaultId]);
            }

            this.timers[vaultId] = setTimeout(() => {
                this.timers[vaultId] = null;
                this.createBackup(vaultId, filePath);
            }, 1000);
        });
    }

    async createBackup (vaultId, savePath) {
        if (!isPathExists(savePath)) {
            return;
        }

        const backupDir = path.join(BACKUPS_DIR, String(vaultId));
        const saveData  = readTextFile(savePath);

        if (!this.backupInfos[vaultId]) {
            this.backupInfos[vaultId] = this.getLastBackupInfo(backupDir);
        }

        const lastBackupInfo = this.backupInfos[vaultId];
        const saveFileDate   = new Date();

        if ((saveFileDate.getTime() - lastBackupInfo.time) < MIN_BACKUP_DELAY) {
            return;
        }

        const backupName = `${ formatSafeDate(saveFileDate) }.sav`;
        const backupPath = path.join(backupDir, backupName);

        this.createBackupDir(backupDir);

        writeTextFile(backupPath, saveData);

        this.backupInfos[vaultId] = {
            time: saveFileDate.getTime()      
        };

        console.log(`[${ vaultId }] Created:`, backupName);

        const maxBackups = Math.min(300, Math.max(1, MAX_BACKUPS));
        const backups    = this.getBackups(backupDir);
        const toDelete   = backups.slice(0, Math.max(0, backups.length - maxBackups));

        toDelete.forEach(backupName => {
            removeFile(path.join(backupDir, backupName));

            console.log(`[${ vaultId }] Deleted:`, backupName);
        });

        console.log(' ');
    }

    getLastBackupInfo (backupDir) {
        this.createBackupDir(backupDir);

        const backups = this.getBackups(backupDir);

        if (!backups.length) {
            return {
                time: 0
            };
        }

        const lastBackupName = backups.pop();
        const lastBackupPath = path.join(backupDir, lastBackupName);
        const lastBackupTime = getFileModTime(lastBackupPath);

        return {
            time: lastBackupTime
        };
    }

    createBackupDir (backupDir) {
        createDirs(backupDir);
    }

    getBackups (backupDir) {
        this.createBackupDir(backupDir);

        return listDirFiles(backupDir).sort();
    }
}

const main = async () => {
    SaveBackuper.watch();

    /*const savePath = path.join(SAVE_DIR, 'Vault2.sav');

    SaveEditor.edit(savePath, async (editor) => {
        // editor.setNuka(0);
        // editor.setQuantumNuka(0);
        // editor.setLunchbox(600);
        console.log(JSON.stringify(editor._data, null, 4));
    });*/
};

main();

