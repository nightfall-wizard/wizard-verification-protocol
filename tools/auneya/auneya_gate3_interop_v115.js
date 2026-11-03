#!/usr/bin/env node
'use strict';

/*
 * AUNEYA/WVP v1.15
 *
 * Independent cross-language verification
 * of v1.13 recipient-signed Gate 3 ACKs.
 *
 * No Python verification dependency.
 * No external npm packages.
 * No private signing key required.
 *
 * Does NOT independently verify v1.12 quorum.
 * Does NOT prove independent devices.
 * Does NOT activate a public network.
 * Does NOT activate economics.
 */

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const {
    parseLossless
} = require('./auneya_lossless_json_v14.js');

const LIMIT = 16 * 1024;
const MAX_INT = (1n << 63n) - 1n;

const DOMAIN = Buffer.from(
    'AUNEYA/WVP:GATE3-RECIPIENT-ACK:V1.13\0',
    'ascii'
);

const ANCHOR_CRYPTO_DOMAIN = Buffer.from(
    'AUNEYA/WVP:EXTERNAL-ANCHOR:V1.9\0',
    'ascii'
);

const FORMAT = 'auneya-gate3-recipient-ack-v1.13';

const OUTPUT =
    'wvp-auneya-gate3-cross-language-verdict-v1.15';

const FLOOR = 'auneya-recipient-highwater-v1.12';

const FIELDS = [
    'format',
    'chain_id',
    'sequence',
    'anchor_sha256',
    'capsule_sha256',
    'trust_sha256',
    'floor_sha256',
    'recipient_pin',
    'floor_status',
    'non_value_research_only',
    'independent_devices_proven',
    'external_retention_proven',
    'economic_activation'
];

function assert(condition, why) {
    if (!condition) {
        throw Error(why);
    }
}

function sha(raw) {
    return crypto
        .createHash('sha256')
        .update(raw)
        .digest('hex');
}

function hex(value) {
    return (
        typeof value === 'string' &&
        /^[a-f0-9]{64}$/.test(value)
    );
}

function object(value) {
    return (
        value !== null &&
        typeof value === 'object' &&
        !Array.isArray(value)
    );
}

function fields(value, expected) {
    return (
        object(value) &&
        Object.keys(value).sort().join('\u0000') ===
        [...expected].sort().join('\u0000')
    );
}

function canonical(value) {
    if (
        value === null ||
        typeof value === 'boolean'
    ) {
        return JSON.stringify(value);
    }

    if (typeof value === 'bigint') {
        return value.toString();
    }

    if (typeof value === 'number') {
        assert(
            Number.isSafeInteger(value),
            'unsafe numeric encoding'
        );

        return value.toString();
    }

    if (typeof value === 'string') {
        assert(
            /^[\x20-\x7e]*$/.test(value),
            'non-ASCII canonical field'
        );

        return JSON.stringify(value);
    }

    if (Array.isArray(value)) {
        return '[' +
            value.map(canonical).join(',') +
            ']';
    }

    assert(object(value), 'invalid JSON type');

    return '{' +
        Object.keys(value)
            .sort()
            .map(key =>
                canonical(key) +
                ':' +
                canonical(value[key])
            )
            .join(',') +
        '}';
}

function readFile(
    filename,
    maximum,
    privateFile = false
) {
    const parent = fs.lstatSync(
        path.dirname(path.resolve(filename))
    );

    assert(
        parent.isDirectory() &&
        !parent.isSymbolicLink(),
        'unsafe input directory'
    );

    if (privateFile) {
        assert(
            (parent.mode & 0o077) === 0,
            'private 0700 directory required'
        );
    }

    const flags =
        fs.constants.O_RDONLY |
        (fs.constants.O_NOFOLLOW || 0);

    const fd = fs.openSync(filename, flags);

    try {
        const before = fs.fstatSync(fd);

        assert(
            before.isFile() &&
            before.nlink === 1 &&
            before.size > 0 &&
            before.size <= maximum,
            'invalid regular bounded input'
        );

        if (privateFile) {
            assert(
                (before.mode & 0o077) === 0,
                'private 0600 public-key file required'
            );
        }

        const raw = Buffer.alloc(before.size);

        let offset = 0;

        while (offset < raw.length) {
            const n = fs.readSync(
                fd,
                raw,
                offset,
                raw.length - offset,
                offset
            );

            assert(n > 0, 'short read');

            offset += n;
        }

        const after = fs.fstatSync(fd);

        assert(
            after.size === before.size &&
            after.ino === before.ino &&
            after.dev === before.dev,
            'file changed during read'
        );

        return raw;
    } finally {
        fs.closeSync(fd);
    }
}

function readCanonical(filename, maximum) {
    const raw = readFile(filename, maximum);

    const obj = parseLossless(raw);

    assert(
        object(obj) &&
        raw.equals(
            Buffer.from(
                canonical(obj) + '\n',
                'ascii'
            )
        ),
        'noncanonical JSON framing'
    );

    return {
        raw,
        obj
    };
}

function verify(options) {
    const expected = options['expected-head'];
    const pin = options.pin;

    assert(
        hex(expected) && hex(pin),
        'independent expected head and recipient pin required'
    );

    const {
        raw,
        obj
    } = readCanonical(
        options.receipt,
        LIMIT
    );

    const head = sha(raw);

    assert(
        head === expected,
        'external ACK head mismatch: rollback or substitution'
    );

    assert(
        fields(
            obj,
            ['body', 'signature_b64']
        ),
        'unexpected ACK fields'
    );

    const body = obj.body;

    assert(
        fields(body, FIELDS),
        'unexpected signed ACK body fields'
    );

    assert(
        body.format === FORMAT &&
        body.non_value_research_only === true &&
        body.independent_devices_proven === false &&
        body.external_retention_proven === false &&
        body.economic_activation === false,
        'unsafe receipt claims'
    );

    assert(
        typeof body.chain_id === 'string' &&
        /^[a-z0-9][a-z0-9._-]{0,79}$/.test(
            body.chain_id
        ),
        'invalid research chain identity'
    );

    assert(
        (
            typeof body.sequence === 'number' &&
            Number.isSafeInteger(body.sequence)
        ) ||
        typeof body.sequence === 'bigint',
        'invalid integer sequence'
    );

    const sequence = BigInt(body.sequence);

    assert(
        sequence >= 1n &&
        sequence <= MAX_INT,
        'sequence outside signed 63-bit range'
    );

    assert(
        [
            'initialized',
            'advanced',
            'unchanged'
        ].includes(body.floor_status),
        'floor status'
    );

    for (const name of [
        'anchor_sha256',
        'capsule_sha256',
        'trust_sha256',
        'floor_sha256',
        'recipient_pin'
    ]) {
        assert(
            hex(body[name]),
            'invalid digest: ' + name
        );
    }

    assert(
        body.recipient_pin === pin,
        'recipient pin mismatch'
    );

    const pem = readFile(
        options['recipient-public'],
        16384,
        true
    );

    assert(
        sha(pem) === pin,
        'public key PEM pin mismatch'
    );

    const key = crypto.createPublicKey(pem);

    assert(
        key.asymmetricKeyType === 'ed25519',
        'recipient key is not Ed25519'
    );

    const b64 = obj.signature_b64;

    assert(
        typeof b64 === 'string' &&
        /^[A-Za-z0-9+/]{86}==$/.test(b64),
        'invalid Ed25519 base64'
    );

    const signature = Buffer.from(
        b64,
        'base64'
    );

    assert(
        signature.length === 64 &&
        signature.toString('base64') === b64,
        'noncanonical Ed25519 signature'
    );

    const payload = Buffer.concat([
        ANCHOR_CRYPTO_DOMAIN,
        DOMAIN,
        Buffer.from(
            canonical(body),
            'ascii'
        )
    ]);

    assert(
        crypto.verify(
            null,
            payload,
            key,
            signature
        ),
        'recipient signature verification failed'
    );

    if (options.capsule) {
        const proof = readFile(
            options.capsule,
            4 * 1024 * 1024
        );

        assert(
            sha(proof) === body.capsule_sha256,
            'different capsule digest'
        );
    }

    if (options.floor) {
        const floor = readCanonical(
            options.floor,
            4096
        );

        const value = floor.obj;

        assert(
            value.format === FLOOR &&
            value.chain_id === body.chain_id &&
            BigInt(value.sequence) === sequence &&
            value.anchor_sha256 ===
                body.anchor_sha256 &&
            value.trust_sha256 ===
                body.trust_sha256 &&
            value.last_capsule_sha256 ===
                body.capsule_sha256 &&
            sha(floor.raw) === body.floor_sha256,
            'recipient floor commitment mismatch'
        );
    }

    return {
        format: OUTPUT,

        status:
            'AUTHENTICATED_RECIPIENT_RESEARCH_ACK',

        chain_id: body.chain_id,

        sequence_decimal:
            sequence.toString(),

        ack_sha256: head,

        recipient_pin: pin,

        capsule_sha256:
            body.capsule_sha256,

        external_head_matched: true,

        recipient_signature_verified: true,

        quorum_independently_verified: false,

        independent_devices_proven: false,

        external_retention_proven: false,

        economic_activation: false,

        non_value_research_only: true
    };
}

function generateVectors(folder) {
    fs.mkdirSync(
        folder,
        {
            recursive: true
        }
    );

    /*
     * RFC 8032 public test seed.
     * Never use as a real identity.
     */

    const seed = Buffer.from(
        '9d61b19deffd5a60ba844af492ec2cc4' +
        '4449c5697b326919703bac031cae7f60',
        'hex'
    );

    const der = Buffer.concat([
        Buffer.from(
            '302e020100300506032b657004220420',
            'hex'
        ),
        seed
    ]);

    const privateKey = crypto.createPrivateKey({
        key: der,
        format: 'der',
        type: 'pkcs8'
    });

    const publicKey = crypto.createPublicKey(
        privateKey
    );

    const pem = Buffer.from(
        publicKey.export({
            format: 'pem',
            type: 'spki'
        })
    );

    const body = {
        format: FORMAT,

        chain_id: 'auneya-gate3-test',

        sequence: 9007199254740993n,

        anchor_sha256: 'a'.repeat(64),

        capsule_sha256: 'b'.repeat(64),

        trust_sha256: 'c'.repeat(64),

        floor_sha256: 'd'.repeat(64),

        recipient_pin: sha(pem),

        floor_status: 'advanced',

        non_value_research_only: true,

        independent_devices_proven: false,

        external_retention_proven: false,

        economic_activation: false
    };

    const payload = Buffer.concat([
        ANCHOR_CRYPTO_DOMAIN,
        DOMAIN,
        Buffer.from(
            canonical(body),
            'ascii'
        )
    ]);

    const signature = crypto.sign(
        null,
        payload,
        privateKey
    );

    const ack = Buffer.from(
        canonical({
            body,
            signature_b64:
                signature.toString('base64')
        }) + '\n',
        'ascii'
    );

    const index = Buffer.from(
        canonical({
            format:
                'auneya-gate3-test-vector-index-v1.15',

            ack_sha256: sha(ack),

            recipient_pin: sha(pem),

            warning:
                'PUBLIC TEST KEY ONLY - NOT AN INDEPENDENT DEVICE IDENTITY'
        }) + '\n',
        'ascii'
    );

    fs.writeFileSync(
        path.join(folder, 'receipt.json'),
        ack
    );

    fs.writeFileSync(
        path.join(folder, 'recipient-public.pem'),
        pem
    );

    fs.writeFileSync(
        path.join(folder, 'index.json'),
        index
    );
}

function main(args) {
    if (
        args[0] === '--generate-vectors' &&
        args.length === 2
    ) {
        generateVectors(args[1]);

        process.stdout.write(
            'PASS: deterministic public test vectors generated\n'
        );

        return;
    }

    const options = Object.create(null);

    for (
        let i = 0;
        i < args.length;
        i += 2
    ) {
        assert(
            args[i]?.startsWith('--') &&
            args[i + 1] &&
            !Object.hasOwn(
                options,
                args[i].slice(2)
            ),
            'invalid or repeated CLI option'
        );

        const name = args[i].slice(2);

        assert(
            [
                'receipt',
                'recipient-public',
                'pin',
                'expected-head',
                'capsule',
                'floor'
            ].includes(name),
            'unknown CLI option'
        );

        options[name] = args[i + 1];
    }

    for (const name of [
        'receipt',
        'recipient-public',
        'pin',
        'expected-head'
    ]) {
        assert(
            typeof options[name] === 'string',
            'missing --' + name
        );
    }

    process.stdout.write(
        canonical(verify(options)) + '\n'
    );
}

try {
    main(process.argv.slice(2));
} catch (error) {
    process.stderr.write(
        'REJECTED: ' + error.message + '\n'
    );

    process.exitCode = 2;
}
