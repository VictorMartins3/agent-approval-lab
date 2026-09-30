'use strict';
const fs = require('node:fs');
exports.save = (path, value) => fs.writeFileSync(path, value, 'utf8');
