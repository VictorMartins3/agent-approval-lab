'use strict';
exports.format = value => {
  const text = String(value);
  return text.trim().toUpperCase();
};
