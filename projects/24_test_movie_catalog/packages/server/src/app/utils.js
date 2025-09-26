import fs from 'fs';



export const readJson = (filePath) => {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
};