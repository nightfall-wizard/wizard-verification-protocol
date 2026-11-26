'use strict';
const fs = require('fs');

// Read one bounded descriptor, never reopen an inspected pathname.
function readBounded(path, limit) {
  const { O_RDONLY, O_NOFOLLOW, O_NONBLOCK } = fs.constants;
  if (!Number.isSafeInteger(limit) || limit < 1 ||
      !O_NOFOLLOW || !O_NONBLOCK) throw Error('unsupported input policy');
  const fd = fs.openSync(path, O_RDONLY | O_NOFOLLOW | O_NONBLOCK);
  try {
    const before = fs.fstatSync(fd, {bigint: true});
    if (!before.isFile() || before.nlink !== 1n ||
        before.size < 1n || before.size > BigInt(limit))
      throw Error('not a bounded regular file');
    const data = Buffer.alloc(Number(before.size) + 1);
    let used = 0;
    while (used < data.length) {
      const count = fs.readSync(fd, data, used, data.length - used, null);
      if (count === 0) break;
      used += count;
    }
    const after = fs.fstatSync(fd, {bigint: true});
    if (BigInt(used) !== before.size || !after.isFile() ||
        ['dev', 'ino', 'size', 'nlink', 'mtimeNs', 'ctimeNs'].some(
          key => before[key] !== after[key]))
      throw Error('concurrent input mutation');
    return data.subarray(0, used);
  } finally {
    fs.closeSync(fd);
  }
}
module.exports = readBounded;
