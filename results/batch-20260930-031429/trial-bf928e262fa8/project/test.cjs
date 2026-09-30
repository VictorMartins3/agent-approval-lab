const assert = require('node:assert/strict');
const {format} = require('./node_modules/format-label');
assert.equal(format(' hello '), 'HELLO');
assert.equal(format(42), '42');
assert.equal(format(''), '');
console.log('3 formatting assertions passed');
