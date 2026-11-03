#!/usr/bin/env node
'use strict';

/*
 * AUNEYA/WVP v1.16
 *
 * Independent Node.js validation of v1.12
 * complete signed multi-keeper quorum capsules.
 *
 * Offline, read-only, no npm packages,
 * no private signing keys, no network activation,
 * no economic activation.
 */

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {execFileSync} = require('node:child_process');

const {
    parseLossless
} = require('./auneya_lossless_json_v14.js');

const MAX_INT = (1n << 63n) - 1n;
const ZERO = '0'.repeat(64);

const D19 = Buffer.from(
    'AUNEYA/WVP:EXTERNAL-ANCHOR:V1.9\0',
    'ascii'
);

const D10 = Buffer.from(
    'AUNEYA/WVP:INDEPENDENT-HIGHWATER:V1.10\0',
    'ascii'
);

const HEX = /^[0-9a-f]{64}$/;

const CHAIN =
    /^[a-z0-9][a-z0-9._-]{0,79}$/;

const NAME =
    /^[a-z0-9][a-z0-9._-]{0,63}$/;

const CAPSULE_KEYS = [
    'format',
    'chain_id',
    'sequence',
    'anchor_sha256',
    'quorum_report_sha256',
    'current',
    'previous'
];

const ANCHOR_KEYS = [
    'format',
    'chain_id',
    'sequence',
    'previous_sha256',
    'public_key_sha256',
    'messages_sha256',
    'state_sha256',
    'message_count',
    'peer_count',
    'tips',
    'non_value_research_only'
];

const KEEPER_KEYS = [
    'format',
    'chain_id',
    'sequence',
    'anchor_sha256',
    'previous_anchor_sha256',
    'anchor_signer_sha256',
    'witness_public_key_sha256',
    'previous_receipt_sha256',
    'message_count',
    'peer_count',
    'tips_sha256',
    'non_value_research_only'
];

function need(condition, why) {
    if (!condition) {
        throw Error(why);
    }
}

function object(value) {
    return (
        value !== null &&
        typeof value === 'object' &&
        !Array.isArray(value)
    );
}

function keys(value, expected) {
    need(
        object(value) &&
        Object.keys(value).length === expected.length &&
        expected.every(
            key => Object.hasOwn(value, key)
        ),
        'unexpected fields'
    );
}

function digest(raw) {
    return crypto
        .createHash('sha256')
        .update(raw)
        .digest('hex');
}

function integer(
    value,
    minimum,
    maximum,
    label
) {
    need(
        (
            typeof value === 'bigint' ||
            (
                typeof value === 'number' &&
                Number.isSafeInteger(value)
            )
        ),
        'invalid integer ' + label
    );

    const number = BigInt(value);

    need(
        number >= minimum &&
        number <= maximum,
        'out-of-range ' + label
    );

    return number;
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
        need(
            Number.isSafeInteger(value),
            'unsafe number'
        );

        return String(value);
    }

    if (typeof value === 'string') {
        need(
            /^[\x20-\x7e]*$/.test(value),
            'non-ASCII canonical string'
        );

        return JSON.stringify(value);
    }

    if (Array.isArray(value)) {
        return '[' +
            value.map(canonical).join(',') +
            ']';
    }

    need(
        object(value),
        'unsupported JSON type'
    );

    return '{' +
        Object.keys(value)
            .sort()
            .map(
                key =>
                    canonical(key) +
                    ':' +
                    canonical(value[key])
            )
            .join(',') +
        '}';
}

function readBounded(
    filename,
    limit,
    privateMode = false
) {
    const absolute = path.resolve(filename);
    const directory = path.dirname(absolute);

    const parent = fs.lstatSync(directory);

    need(
        parent.isDirectory() &&
        !parent.isSymbolicLink(),
        'unsafe parent directory'
    );

    if (privateMode) {
        need(
            (parent.mode & 0o077) === 0,
            'private 0700 parent required'
        );
    }

    const fd = fs.openSync(
        absolute,
        fs.constants.O_RDONLY |
        (fs.constants.O_NOFOLLOW || 0)
    );

    try {
        const stat = fs.fstatSync(fd);

        need(
            stat.isFile() &&
            stat.nlink === 1 &&
            stat.size > 0 &&
            stat.size <= limit,
            'unsafe or oversized file'
        );

        if (privateMode) {
            need(
                (stat.mode & 0o077) === 0,
                'private 0600 file required'
            );
        }

        const raw = Buffer.alloc(stat.size);

        let position = 0;

        while (position < raw.length) {
            const count = fs.readSync(
                fd,
                raw,
                position,
                raw.length - position,
                position
            );

            need(
                count > 0,
                'short read'
            );

            position += count;
        }

        need(
            fs.fstatSync(fd).size === stat.size,
            'input changed during read'
        );

        return raw;
    } finally {
        fs.closeSync(fd);
    }
}

function parseCanonical(raw, limit) {
    need(
        Buffer.isBuffer(raw) &&
        raw.length > 1 &&
        raw.length <= limit &&
        raw[raw.length - 1] === 10 &&
        raw.indexOf(10) === raw.length - 1,
        'noncanonical JSON newline'
    );

    const obj = parseLossless(
        raw.subarray(0, -1)
    );

    need(
        Buffer.from(
            canonical(obj) + '\n',
            'ascii'
        ).equals(raw),
        'noncanonical JSON representation'
    );

    return obj;
}

function decode64(value, limit) {
    need(
        typeof value === 'string' &&
        value.length > 0 &&
        value.length <= Math.ceil(limit / 3) * 4 &&
        /^[A-Za-z0-9+/]+={0,2}$/.test(value),
        'invalid base64'
    );

    const raw = Buffer.from(
        value,
        'base64'
    );

    need(
        raw.length <= limit &&
        raw.toString('base64') === value,
        'noncanonical base64'
    );

    return raw;
}

function keyFrom(filename, pin) {
    need(
        typeof pin === 'string' &&
        HEX.test(pin),
        'invalid independent signer pin'
    );

    const pem = readBounded(
        filename,
        16384,
        true
    );

    need(
        digest(pem) === pin,
        'public-key pin mismatch'
    );

    const key = crypto.createPublicKey(pem);

    need(
        key.asymmetricKeyType === 'ed25519',
        'not Ed25519'
    );

    return key;
}

function signature(
    record,
    key,
    domains
) {
    keys(
        record,
        [
            'body',
            'signature_b64'
        ]
    );

    const sig = decode64(
        record.signature_b64,
        64
    );

    need(
        sig.length === 64,
        'invalid Ed25519 signature'
    );

    const payload = Buffer.concat([
        ...domains,
        Buffer.from(
            canonical(record.body),
            'ascii'
        )
    ]);

    need(
        crypto.verify(
            null,
            payload,
            key,
            sig
        ),
        'Ed25519 signature rejected'
    );
}

function quorumTrust(filename) {
    const cfg = parseCanonical(
        readBounded(
            filename,
            32768,
            true
        ),
        32768
    );

    keys(
        cfg,
        [
            'format',
            'chain_id',
            'anchor_public',
            'anchor_pin',
            'keepers',
            'threshold'
        ]
    );

    need(
        cfg.format ===
            'auneya-quorum-trust-v1.11' &&
        CHAIN.test(cfg.chain_id),
        'invalid trust domain'
    );

    const threshold = integer(
        cfg.threshold,
        2n,
        16n,
        'threshold'
    );

    need(
        Array.isArray(cfg.keepers) &&
        cfg.keepers.length >= Number(threshold) &&
        cfg.keepers.length <= 16,
        'invalid keeper population'
    );

    const resolvePublic = value => {
        need(
            typeof value === 'string' &&
            value.length > 0 &&
            value.length < 1024,
            'invalid key path'
        );

        need(
            !value
                .split(/[\\/]/)
                .includes('..'),
            'key path traversal'
        );

        return path.resolve(
            path.dirname(filename),
            value
        );
    };

    const anchorKey = keyFrom(
        resolvePublic(cfg.anchor_public),
        cfg.anchor_pin
    );

    const keeperKeys = new Map();

    for (const member of cfg.keepers) {
        keys(
            member,
            [
                'pin',
                'public'
            ]
        );

        need(
            member.pin !== cfg.anchor_pin &&
            !keeperKeys.has(member.pin),
            'non-independent or duplicate keeper pin'
        );

        keeperKeys.set(
            member.pin,
            keyFrom(
                resolvePublic(member.public),
                member.pin
            )
        );
    }

    return {
        cfg,
        anchorKey,
        keeperKeys,
        threshold
    };
}

function verifyAnchor(raw, trust) {
    const obj = parseCanonical(
        raw,
        1024 * 1024
    );

    keys(
        obj,
        [
            'body',
            'signature_b64'
        ]
    );

    const body = obj.body;

    keys(
        body,
        ANCHOR_KEYS
    );

    need(
        body.format ===
            'auneya-external-replay-anchor-v1.9' &&
        body.non_value_research_only === true,
        'anchor domain'
    );

    need(
        body.chain_id === trust.cfg.chain_id &&
        CHAIN.test(body.chain_id),
        'anchor chain'
    );

    const sequence = integer(
        body.sequence,
        1n,
        MAX_INT,
        'anchor sequence'
    );

    const messages = integer(
        body.message_count,
        1n,
        50000n,
        'message count'
    );

    const peers = integer(
        body.peer_count,
        1n,
        50000n,
        'peer count'
    );

    for (const field of [
        'previous_sha256',
        'public_key_sha256',
        'messages_sha256',
        'state_sha256'
    ]) {
        need(
            typeof body[field] === 'string' &&
            HEX.test(body[field]),
            'invalid anchor hash'
        );
    }

    need(
        body.public_key_sha256 ===
            trust.cfg.anchor_pin,
        'anchor key not pinned'
    );

    need(
        (
            sequence === 1n &&
            body.previous_sha256 === ZERO
        ) ||
        (
            sequence > 1n &&
            body.previous_sha256 !== ZERO
        ),
        'anchor genesis/predecessor'
    );

    need(
        Array.isArray(body.tips) &&
        BigInt(body.tips.length) === peers,
        'anchor tips count'
    );

    let previous = '';

    for (const tip of body.tips) {
        need(
            Array.isArray(tip) &&
            tip.length === 4 &&
            typeof tip[0] === 'string' &&
            NAME.test(tip[0]) &&
            tip[0] > previous,
            'invalid or unordered tip'
        );

        previous = tip[0];

        for (let i = 1; i < 4; i++) {
            integer(
                tip[i],
                1n,
                MAX_INT,
                'tip'
            );
        }
    }

    need(
        messages >= peers,
        'message/peer count conflict'
    );

    signature(
        obj,
        trust.anchorKey,
        [D19]
    );

    return {
        body,
        sha: digest(raw),
        sequence,
        messages,
        peers
    };
}

function verifyKeeper(
    raw,
    pin,
    key,
    anchor,
    trust
) {
    const obj = parseCanonical(
        raw,
        16 * 1024
    );

    keys(
        obj,
        [
            'body',
            'signature_b64'
        ]
    );

    const body = obj.body;

    keys(
        body,
        KEEPER_KEYS
    );

    need(
        body.format ===
            'auneya-independent-highwater-receipt-v1.10' &&
        body.non_value_research_only === true,
        'keeper domain'
    );

    const sequence = integer(
        body.sequence,
        1n,
        MAX_INT,
        'keeper sequence'
    );

    const messages = integer(
        body.message_count,
        1n,
        50000n,
        'keeper message count'
    );

    const peers = integer(
        body.peer_count,
        1n,
        50000n,
        'keeper peer count'
    );

    for (const field of [
        'anchor_sha256',
        'previous_anchor_sha256',
        'anchor_signer_sha256',
        'witness_public_key_sha256',
        'previous_receipt_sha256',
        'tips_sha256'
    ]) {
        need(
            typeof body[field] === 'string' &&
            HEX.test(body[field]),
            'invalid keeper hash ' + field
        );
    }

    need(
        body.chain_id === anchor.body.chain_id &&
        sequence === anchor.sequence &&
        body.anchor_sha256 === anchor.sha &&
        body.previous_anchor_sha256 ===
            anchor.body.previous_sha256 &&
        body.anchor_signer_sha256 ===
            trust.cfg.anchor_pin &&
        body.witness_public_key_sha256 === pin &&
        messages === anchor.messages &&
        peers === anchor.peers &&
        body.tips_sha256 === digest(
            Buffer.from(
                canonical(anchor.body.tips),
                'ascii'
            )
        ),
        'keeper/anchor binding mismatch'
    );

    need(
        sequence !== 1n ||
        (
            body.previous_anchor_sha256 === ZERO &&
            body.previous_receipt_sha256 === ZERO
        ),
        'keeper genesis mismatch'
    );

    signature(
        obj,
        key,
        [
            D19,
            D10
        ]
    );

    return {
        body,
        sha: digest(raw),
        sequence
    };
}

function verifyBundle(bundle, trust) {
    keys(
        bundle,
        [
            'anchor_b64',
            'receipts'
        ]
    );

    const anchor = verifyAnchor(
        decode64(
            bundle.anchor_b64,
            1024 * 1024
        ),
        trust
    );

    const receipts = bundle.receipts;

    need(
        Array.isArray(receipts) &&
        receipts.length >= Number(trust.threshold) &&
        receipts.length <= 16,
        'insufficient quorum'
    );

    let previous = '';

    const accepted = new Map();

    for (const item of receipts) {
        keys(
            item,
            [
                'pin',
                'payload_b64'
            ]
        );

        need(
            typeof item.pin === 'string' &&
            HEX.test(item.pin) &&
            item.pin > previous,
            'noncanonical keeper order or duplicate'
        );

        previous = item.pin;

        need(
            trust.keeperKeys.has(item.pin),
            'unknown keeper identity'
        );

        accepted.set(
            item.pin,
            verifyKeeper(
                decode64(
                    item.payload_b64,
                    16 * 1024
                ),
                item.pin,
                trust.keeperKeys.get(item.pin),
                anchor,
                trust
            )
        );
    }

    return {
        anchor,
        accepted
    };
}

function link(previous, current) {
    const old = previous.anchor;
    const newer = current.anchor;

    need(
        newer.sequence === old.sequence + 1n &&
        newer.body.chain_id === old.body.chain_id &&
        newer.body.previous_sha256 === old.sha &&
        newer.messages > old.messages,
        'anchor rollback, gap or fork'
    );

    need(
        previous.accepted.size ===
            current.accepted.size &&
        [...previous.accepted.keys()].every(
            pin => current.accepted.has(pin)
        ),
        'keeper membership transition'
    );

    for (const [pin, receipt] of current.accepted) {
        const prior = previous.accepted.get(pin);

        need(
            receipt.sequence ===
                prior.sequence + 1n &&
            receipt.body.previous_receipt_sha256 ===
                prior.sha &&
            receipt.body.previous_anchor_sha256 ===
                old.sha,
            'keeper history rollback or fork'
        );
    }
}

function verify(options) {
    const expected = options['expected-capsule'];

    need(
        typeof expected === 'string' &&
        HEX.test(expected),
        'independent capsule head hash required'
    );

    const trust = quorumTrust(
        options.trust
    );

    const raw = readBounded(
        options.capsule,
        4 * 1024 * 1024
    );

    need(
        digest(raw) === expected,
        'external capsule hash mismatch'
    );

    const data = parseCanonical(
        raw,
        4 * 1024 * 1024
    );

    keys(
        data,
        CAPSULE_KEYS
    );

    need(
        data.format ===
            'auneya-portable-quorum-capsule-v1.12' &&
        data.chain_id === trust.cfg.chain_id,
        'capsule identity mismatch'
    );

    const sequence = integer(
        data.sequence,
        1n,
        MAX_INT,
        'capsule sequence'
    );

    for (const field of [
        'anchor_sha256',
        'quorum_report_sha256'
    ]) {
        need(
            typeof data[field] === 'string' &&
            HEX.test(data[field]),
            'capsule commitment malformed'
        );
    }

    const current = verifyBundle(
        data.current,
        trust
    );

    need(
        sequence === current.anchor.sequence &&
        data.anchor_sha256 === current.anchor.sha,
        'capsule anchor commitment mismatch'
    );

    if (sequence > 1n) {
        need(
            data.previous !== null,
            'missing previous quorum'
        );
    }

    if (data.previous !== null) {
        link(
            verifyBundle(
                data.previous,
                trust
            ),
            current
        );
    }

    const report = {
        format:
            'wvp-auneya-quorum-verdict-v1.11',

        status:
            'AUTHENTICATED_MULTI_KEEPER_RESEARCH_EVIDENCE',

        chain_id:
            data.chain_id,

        sequence:
            sequence,

        anchor_sha256:
            current.anchor.sha,

        message_count:
            current.anchor.messages,

        keeper_count:
            current.accepted.size,

        required_quorum:
            trust.threshold,

        keeper_receipt_sha256:
            [...current.accepted.entries()]
                .map(
                    ([pin, value]) => ({
                        pin,
                        sha256: value.sha
                    })
                ),

        signatures_verified:
            true,

        independent_devices_proven:
            false,

        external_retention_proven:
            false,

        latest_global_highwater_proven:
            false,

        network_consensus_proven:
            false,

        audit_completed:
            false,

        economic_activation:
            false,

        non_value_research_only:
            true
    };

    const reportHash = digest(
        Buffer.from(
            canonical(report),
            'ascii'
        )
    );

    need(
        reportHash === data.quorum_report_sha256,
        'WVP report commitment mismatch'
    );

    let ack = false;

    if (options.receipt) {
        const argv = [
            path.join(
                __dirname,
                'auneya_gate3_interop_v115.js'
            ),

            '--receipt',
            options.receipt,

            '--recipient-public',
            options['recipient-public'],

            '--pin',
            options['recipient-pin'],

            '--expected-head',
            options['expected-head'],

            '--capsule',
            options.capsule
        ];

        if (options.floor) {
            argv.push(
                '--floor',
                options.floor
            );
        }

        const result = JSON.parse(
            execFileSync(
                process.execPath,
                argv,
                {
                    timeout: 20000,
                    maxBuffer: 16384
                }
            ).toString('utf8')
        );

        need(
            result.capsule_sha256 === expected &&
            BigInt(result.sequence_decimal) ===
                sequence,
            'ACK disagrees with quorum'
        );

        ack = true;
    }

    return {
        format:
            'wvp-auneya-full-quorum-cross-language-v1.16',

        status:
            'AUTHENTICATED_OFFLINE_FULL_QUORUM_RESEARCH',

        chain_id:
            data.chain_id,

        sequence_decimal:
            sequence.toString(),

        capsule_sha256:
            expected,

        anchor_sha256:
            current.anchor.sha,

        quorum_report_sha256:
            reportHash,

        keeper_count:
            current.accepted.size,

        required_quorum:
            Number(trust.threshold),

        quorum_signatures_verified:
            true,

        recipient_ack_verified:
            ack,

        expected_capsule_matched:
            true,

        independent_devices_proven:
            false,

        external_retention_proven:
            false,

        independent_audit_completed:
            false,

        mainnet_active:
            false,

        economic_activation:
            false,

        non_value_research_only:
            true
    };
}

function main(args) {
    const options = Object.create(null);

    const allowed = new Set([
        'trust',
        'capsule',
        'expected-capsule',
        'receipt',
        'recipient-public',
        'recipient-pin',
        'expected-head',
        'floor'
    ]);

    need(
        args.length % 2 === 0,
        'options must use key/value pairs'
    );

    for (
        let i = 0;
        i < args.length;
        i += 2
    ) {
        need(
            args[i].startsWith('--') &&
            allowed.has(
                args[i].slice(2)
            ) &&
            !Object.hasOwn(
                options,
                args[i].slice(2)
            ) &&
            args[i + 1],
            'unexpected/repeated option'
        );

        options[
            args[i].slice(2)
        ] = args[i + 1];
    }

    for (const required of [
        'trust',
        'capsule',
        'expected-capsule'
    ]) {
        need(
            typeof options[required] === 'string',
            'missing --' + required
        );
    }

    const ack = [
        'receipt',
        'recipient-public',
        'recipient-pin',
        'expected-head'
    ];

    need(
        ack.every(
            key => Boolean(options[key])
        ) ||
        ack.every(
            key => !options[key]
        ),
        'partial ACK options'
    );

    need(
        !options.floor ||
        Boolean(options.receipt),
        'floor requires recipient ACK'
    );

    process.stdout.write(
        canonical(
            verify(options)
        ) + '\n'
    );
}

try {
    main(
        process.argv.slice(2)
    );
} catch (error) {
    process.stderr.write(
        'REJECTED: ' +
        error.message +
        '\n'
    );

    process.exitCode = 2;
}
