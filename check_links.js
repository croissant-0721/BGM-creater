const fs = require('fs');
const path = require('path');

const baseDir = '/Users/chuckmi/Documents/code/panqu-web';
const htmlPath = path.join(baseDir, 'billing_demo/client_billing.html');
const content = fs.readFileSync(htmlPath, 'utf8');

const regex = /(?:href|src)=["']([^"']+)["']/g;
let match;
const links = [];

console.log(`Checking links in ${htmlPath}...`);

while ((match = regex.exec(content)) !== null) {
    const link = match[1];
    if (link.startsWith('http') || link.startsWith('//')) {
        console.log(`[Remote] ${link} - SKIPPED`);
        continue;
    }

    // Resolve relative path
    const resolvedPath = path.join(path.dirname(htmlPath), link);
    const exists = fs.existsSync(resolvedPath);
    console.log(`[Local] ${link} -> ${resolvedPath} : ${exists ? 'OK' : 'MISSING'}`);
}
