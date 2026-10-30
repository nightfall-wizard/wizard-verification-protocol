'use strict';

/*
 * AUNEYA/WVP v1.8
 *
 * Domain-separated Ed25519 receipt signatures.
 * Built-in Node.js cryptography.
 * No npm packages.
 * No production networking.
 */

const crypto = require('node:crypto');

const DOMAIN = Buffer.from(
    'AUNEYA/WVP:RECEIPT:V1.8\0',
    'ascii'
);

const MAX_INPUT = 30000;
const MAX_PAYLOAD = 1024;
const MAX_KEY = 16384;

let chunks = [];
let total = 0;

process.stdin.on('data', chunk => {

    total += chunk.length;

    if (total > MAX_INPUT) {
        process.stderr.write(
            'FAIL-CLOSED: input budget exceeded\n'
        );
        process.exit(2);
    }

    chunks.push(chunk);
});

process.stdin.on('end', () => {

    try {

        const obj = JSON.parse(
            Buffer.concat(chunks).toString('utf8')
        );

        if (!obj || typeof obj !== 'object') {
            throw Error('invalid request');
        }

        const expectedFields = (
            obj.op === 'sign'
                ? 'key_b64,op,payload_b64'
                : 'key_b64,op,payload_b64,signature_b64'
        );

        if (
            Object.keys(obj).sort().join(',') !==
            expectedFields
        ) {
            throw Error('invalid request fields');
        }

        const payload = Buffer.from(
            obj.payload_b64,
            'base64'
        );

        if (
            payload.length === 0 ||
            payload.length > MAX_PAYLOAD
        ) {
            throw Error('payload budget exceeded');
        }

        const keyData = Buffer.from(
            obj.key_b64,
            'base64'
        );

        if (
            keyData.length === 0 ||
            keyData.length > MAX_KEY
        ) {
            throw Error('key budget exceeded');
        }

        const signedData = Buffer.concat([
            DOMAIN,
            payload
        ]);

        if (obj.op === 'sign') {

            const privateKey =
                crypto.createPrivateKey(keyData);

            if (
                privateKey.asymmetricKeyType !==
                'ed25519'
            ) {
                throw Error('incorrect key type');
            }

            const signature = crypto.sign(
                null,
                signedData,
                privateKey
            );

            process.stdout.write(
                signature.toString('base64')
            );

        } else if (obj.op === 'verify') {

            const publicKey =
                crypto.createPublicKey(keyData);

            const signature = Buffer.from(
                obj.signature_b64,
                'base64'
            );

            if (
                publicKey.asymmetricKeyType !==
                    'ed25519' ||
                signature.length !== 64
            ) {
                throw Error('invalid signature format');
            }

            if (!crypto.verify(
                null,
                signedData,
                publicKey,
                signature
            )) {
                throw Error('invalid signature');
            }

            process.stdout.write('VERIFIED');

        } else {

            throw Error('unsupported operation');

        }

    } catch (error) {

        process.stderr.write(
            'FAIL-CLOSED: ' +
            error.message +
            '\n'
        );

        process.exitCode = 2;

    }
});
