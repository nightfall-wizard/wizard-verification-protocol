'use strict';

const crypto = require('node:crypto');

const DOMAIN = Buffer.from(
    'AUNEYA/WVP:EXTERNAL-ANCHOR:V1.9\0',
    'ascii'
);

let raw = [];

process.stdin.on('data', part => {
    raw.push(part);

    if (
        raw.reduce(
            (sum, x) => sum + x.length,
            0
        ) > 2 * 1024 * 1024
    ) {
        process.exit(2);
    }
});

process.stdin.on('end', () => {
    try {
        const x = JSON.parse(
            Buffer.concat(raw).toString('utf8')
        );

        if (
            !['sign', 'verify'].includes(x.op)
        ) {
            throw Error('bad operation');
        }

        const key = Buffer.from(
            x.key_b64,
            'base64'
        );

        const payload = Buffer.from(
            x.payload_b64,
            'base64'
        );

        if (
            !key.length ||
            payload.length > 1024 * 1024
        ) {
            throw Error('size');
        }

        const msg = Buffer.concat([
            DOMAIN,
            payload
        ]);

        if (x.op === 'sign') {
            const sig = crypto.sign(
                null,
                msg,
                crypto.createPrivateKey(key)
            );

            if (sig.length !== 64) {
                throw Error('not ed25519');
            }

            process.stdout.write(
                sig.toString('base64')
            );
        } else {
            const sig = Buffer.from(
                x.signature_b64,
                'base64'
            );

            if (
                sig.length !== 64 ||
                !crypto.verify(
                    null,
                    msg,
                    crypto.createPublicKey(key),
                    sig
                )
            ) {
                throw Error('invalid signature');
            }

            process.stdout.write('VERIFIED');
        }
    } catch (_) {
        process.exitCode = 2;
    }
});
