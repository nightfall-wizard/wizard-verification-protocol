#!/usr/bin/env node
'use strict';

// Independent read-only v1.23 Merkle inclusion verifier.
// No signing keys, no network, no disk writes.

const fs = require('fs');
const crypto = require('crypto');

function reject(ok, why) {
  if (!ok) throw Error(why);
}

function ordered(v) {
  if (Array.isArray(v)) {
    return v.map(ordered);
  }

  if (v !== null && typeof v === 'object') {
    return Object.fromEntries(
      Object.keys(v).sort().map(
        k => [k, ordered(v[k])]
      )
    );
  }

  return v;
}

function canonical(v) {
  return Buffer.from(
    JSON.stringify(ordered(v)) + '\n',
    'utf8'
  );
}

const HEX = /^[0-9a-f]{64}$/;

const FIELDS = [
  'chain_id',
  'sequence_decimal',
  'recipient_pin',
  'capsule_sha256',
  'ack_sha256',
  'floor_sha256',
  'anchor_sha256',
  'report_sha256'
].sort();

function exact(v, names) {
  reject(
    v &&
    !Array.isArray(v) &&
    typeof v === 'object' &&
    JSON.stringify(Object.keys(v).sort()) ===
      JSON.stringify([...names].sort()),
    'field set invalid'
  );
}

function read(p) {
  const st = fs.lstatSync(p);

  reject(
    st.isFile() &&
    st.nlink === 1 &&
    st.size > 0 &&
    st.size <= 524288,
    'bad proof input'
  );

  const b = fs.readFileSync(p);

  reject(
    b.length === st.size,
    'proof input changed'
  );

  const x = JSON.parse(
    b.toString('utf8')
  );

  reject(
    b.equals(canonical(x)),
    'noncanonical or duplicate JSON'
  );

  return x;
}

function hash(b) {
  return crypto.createHash('sha256')
    .update(b)
    .digest('hex');
}

function mix(a, b) {
  return hash(
    Buffer.concat([
      Buffer.from([1]),
      Buffer.from(a, 'hex'),
      Buffer.from(b, 'hex')
    ])
  );
}

function leaf(rec) {
  exact(rec, FIELDS);

  reject(
    typeof rec.chain_id === 'string' &&
    /^[a-zA-Z0-9._:-]{1,128}$/.test(rec.chain_id),
    'bad chain'
  );

  reject(
    typeof rec.sequence_decimal === 'string' &&
    /^(0|[1-9][0-9]{0,18})$/.test(rec.sequence_decimal) &&
    BigInt(rec.sequence_decimal) > 0n &&
    BigInt(rec.sequence_decimal) <= (2n**63n - 1n),
    'bad sequence'
  );

  for (const k of FIELDS.filter(
    x => x !== 'chain_id' &&
         x !== 'sequence_decimal'
  )) {
    reject(
      typeof rec[k] === 'string' &&
      HEX.test(rec[k]),
      'bad hash: ' + k
    );
  }

  return hash(
    Buffer.concat([
      Buffer.from([0]),
      canonical(rec)
    ])
  );
}

function split(n) {
  let k = 1;

  while (k * 2 < n) {
    k *= 2;
  }

  return k;
}

function verify(pr, pinned, size) {
  exact(pr, [
    'format',
    'size',
    'index',
    'record',
    'path',
    'root_sha256'
  ]);

  reject(
    pr.format === 'auneya-inclusion-proof-v1.23' &&
    Number.isSafeInteger(pr.size) &&
    Number.isSafeInteger(pr.index) &&
    pr.size >= 1 &&
    pr.size <= 256 &&
    pr.index >= 0 &&
    pr.index < pr.size &&
    Array.isArray(pr.path) &&
    pr.path.length <= 9,
    'bad proof shape'
  );

  reject(
    HEX.test(pinned) &&
    pr.root_sha256 === pinned &&
    pr.size === size,
    'external root/size mismatch'
  );

  let n = pr.size;
  let i = pr.index;

  const sides = [];

  while (n > 1) {
    const k = split(n);

    if (i < k) {
      sides.push('right');
      n = k;
    } else {
      sides.push('left');
      i -= k;
      n -= k;
    }
  }

  sides.reverse();

  reject(
    sides.length === pr.path.length,
    'wrong proof length'
  );

  let h = leaf(pr.record);

  for (let j = 0; j < sides.length; j++) {
    const s = pr.path[j];

    exact(s, ['side', 'hash']);

    reject(
      s.side === sides[j] &&
      typeof s.hash === 'string' &&
      HEX.test(s.hash),
      'wrong proof topology'
    );

    h = s.side === 'left'
      ? mix(s.hash, h)
      : mix(h, s.hash);
  }

  reject(
    h === pinned,
    'bad inclusion proof'
  );

  return {
    status: 'INCLUDED_IN_PINNED_ROOT',
    independent_retention_proven: false
  };
}

try {
  const args = process.argv.slice(2);

  reject(
    args.length === 6 &&
    args[0] === '--proof' &&
    args[2] === '--expected-root' &&
    args[4] === '--expected-size',
    'usage: --proof FILE --expected-root SHA256 --expected-size N'
  );

  reject(
    /^[1-9][0-9]*$/.test(args[5]),
    'bad size'
  );

  process.stdout.write(
    canonical(
      verify(
        read(args[1]),
        args[3],
        Number(args[5])
      )
    )
  );

} catch (e) {
  process.stderr.write(
    'REJECTED: ' + e.message + '\n'
  );

  process.exitCode = 1;
}
