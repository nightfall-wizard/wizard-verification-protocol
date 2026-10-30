'use strict';

// Independent Node.js Ed25519 verification.
// Verification payload is delivered through stdin.
// No network connection and no private key required.

const crypto = require('node:crypto');

const MAX_INPUT = 180000;

let chunks = [];
let total = 0;

process.stdin.on('data', c => {

  total += c.length;

  if (total > MAX_INPUT) {

    process.stderr.write(
      'bounded input exceeded\n'
    );

    process.exit(2);
  }

  chunks.push(c);
});

process.stdin.on('end', () => {

  try {

    const x = JSON.parse(
      Buffer.concat(chunks).toString('utf8')
    );

    if (
      !x ||
      Object.keys(x).sort().join(',') !==
      'key_b64,payload_b64,signature_b64'
    ) {
      throw Error('shape');
    }

    const key = crypto.createPublicKey(
      Buffer.from(x.key_b64, 'base64')
    );

    if (
      key.asymmetricKeyType !== 'ed25519'
    ) {
      throw Error('key type');
    }

    const payload = Buffer.from(
      x.payload_b64,
      'base64'
    );

    const sig = Buffer.from(
      x.signature_b64,
      'base64'
    );

    if (
      payload.length > 65536 ||
      sig.length !== 64
    ) {
      throw Error('limits');
    }

    const domain = Buffer.from(
      'AUNEYA/WVP:PEER:V1.6\0',
      'ascii'
    );

    const valid = crypto.verify(
      null,
      Buffer.concat([
        domain,
        payload
      ]),
      key,
      sig
    );

    if (!valid) {
      throw Error('signature invalid');
    }

    process.stdout.write(
      'ED25519_VALID\n'
    );

  } catch (e) {

    process.stderr.write(
      'FAIL-CLOSED: ' +
      e.message +
      '\n'
    );

    process.exitCode = 2;
  }
});
