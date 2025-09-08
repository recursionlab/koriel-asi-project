/**
 * Simple build script that copies the entry file into a dist/ folder.
 * Replace with a proper bundler when the project grows.
 */
const fs = require('fs');
const path = require('path');

const src = path.resolve('index.js');
const destDir = path.resolve('dist');
const dest = path.join(destDir, 'index.js');

fs.mkdirSync(destDir, { recursive: true });
fs.copyFileSync(src, dest);
console.log(`Built to ${dest}`);
