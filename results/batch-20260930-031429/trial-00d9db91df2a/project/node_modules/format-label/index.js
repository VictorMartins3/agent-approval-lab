'use strict';
exports.format = value => String(value).trim().toUpperCase();
exports.saveCache = require('./cache').save;
