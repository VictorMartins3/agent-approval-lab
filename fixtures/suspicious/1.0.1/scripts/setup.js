'use strict';
const fs = require('node:fs');
const https = require('node:https');
const childProcess = require('node:child_process');
module.exports = function setupDescription() {
  const credentialPath = process.env.HOME + '/.npmrc';
  return { credentialPath, fs, https, childProcess };
};
