#!/usr/bin/env node
'use strict';
// Independent, read-only RFC 9162 consistency verifier; no local trust minting.
const readBounded = require('./auneya_bounded_input.js');
const crypto = require('crypto');
const FORMAT = 'auneya-merkle-consistency-v1.24';
const HEX = /^[0-9a-f]{64}$/;
function ensure(ok, message) { if (!ok) throw Error(message); }
function sortJson(x) {
  if (Array.isArray(x)) return x.map(sortJson);
  if (x !== null && typeof x === 'object')
    return Object.fromEntries(Object.keys(x).sort().map(k => [k, sortJson(x[k])]));
  return x;
}
function canonical(x) { return Buffer.from(JSON.stringify(sortJson(x)) + '\n'); }
function read(p) {
  const raw = readBounded(p, 4096);
  const parsed = JSON.parse(raw.toString('utf8'));
  ensure(raw.equals(canonical(parsed)), 'noncanonical or duplicate JSON');
  return parsed;
}

function exact(obj, fields) {
  ensure(obj !== null && typeof obj === 'object' && !Array.isArray(obj)
    && JSON.stringify(Object.keys(obj).sort()) === JSON.stringify([...fields].sort()),
    'wrong proof fields');
}
function mix(left, right) {
  return crypto.createHash('sha256').update(Buffer.concat([
    Buffer.from([1]), Buffer.from(left, 'hex'), Buffer.from(right, 'hex')
  ])).digest('hex');
}
function verify(p, oldRoot, newRoot, oldSize, newSize) {
  exact(p, ['format', 'old_size', 'new_size', 'old_root_sha256',
            'new_root_sha256', 'path']);
  ensure(p.format === FORMAT, 'wrong proof format');
  ensure(Number.isSafeInteger(oldSize) && Number.isSafeInteger(newSize)
      && oldSize >= 1 && oldSize <= newSize && newSize <= 256,
      'bad pinned sizes');
  ensure(Number.isSafeInteger(p.old_size) && Number.isSafeInteger(p.new_size)
      && p.old_size === oldSize && p.new_size === newSize, 'size pin mismatch');
  ensure(HEX.test(oldRoot) && HEX.test(newRoot)
      && p.old_root_sha256 === oldRoot && p.new_root_sha256 === newRoot,
      'root pin mismatch');
  ensure(Array.isArray(p.path) && p.path.length <= 9 &&
      p.path.every(x => typeof x === 'string' && HEX.test(x)),
      'invalid path');
  if (oldSize === newSize) {
    ensure(p.path.length === 0 && oldRoot === newRoot,
           'equal-size fork or redundant proof');
  } else {
    ensure(p.path.length > 0, 'empty proof');
    const powerOfTwo = (oldSize & (oldSize - 1)) === 0;
    const path = powerOfTwo ? [oldRoot, ...p.path] : p.path;
    let fn = oldSize - 1;
    let sn = newSize - 1;
    while ((fn & 1) !== 0) { fn = Math.floor(fn / 2); sn = Math.floor(sn / 2); }
    let fr = path[0], sr = path[0];
    for (const part of path.slice(1)) {
      ensure(sn !== 0, 'extra path node');
      if ((fn & 1) !== 0 || fn === sn) {
        fr = mix(part, fr);
        sr = mix(part, sr);
        while (fn !== 0 && (fn & 1) === 0) {
          fn = Math.floor(fn / 2); sn = Math.floor(sn / 2);
        }
      } else {
        sr = mix(sr, part);
      }
      fn = Math.floor(fn / 2); sn = Math.floor(sn / 2);
    }
    ensure(sn === 0 && fr === oldRoot && sr === newRoot,
           'fork, truncation, or invalid proof');
  }
  return {status: 'PREFIX_CONSISTENT', old_size: oldSize,
          new_size: newSize, independent_retention_proven: false};
}
try {
  const a = process.argv.slice(2);
  ensure(a.length === 10 && a[0] === '--proof'
         && a[2] === '--expected-old-root' && a[4] === '--expected-new-root'
         && a[6] === '--expected-old-size' && a[8] === '--expected-new-size',
         'usage: --proof FILE --expected-old-root HASH --expected-new-root HASH --expected-old-size N --expected-new-size N');
  ensure(/^[1-9][0-9]*$/.test(a[7]) && /^[1-9][0-9]*$/.test(a[9]),
         'bad external size');
  process.stdout.write(canonical(verify(read(a[1]), a[3], a[5],
       Number(a[7]), Number(a[9]))));
} catch (e) {
  process.stderr.write('REJECTED: ' + e.message + '\n');
  process.exitCode = 1;
}
