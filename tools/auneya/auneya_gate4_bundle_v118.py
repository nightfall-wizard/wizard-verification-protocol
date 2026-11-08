#!/usr/bin/env python3
"""Offline, fail-closed, replayable WVP/AUNEYA v1.18 evidence contract."""

import argparse
import hashlib
import hmac
import json
import os
import re
import stat
import sys

from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

sys.path.insert(0, str(HERE))

import auneya_dual_v117 as dual

FORMAT = 'auneya-gate4-dual-evidence-v1.18'

SCHEMA = (
    ROOT / 'schemas' /
    'auneya-gate4-evidence-v1.18.schema.json'
)

SHA = re.compile(r'[0-9a-f]{64}\Z')

HEX = lambda raw: hashlib.sha256(raw).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}

    for k, v in pairs:
        need(
            k not in result,
            'duplicate JSON member'
        )
        result[k] = v

    return result


def json_canonical(obj):
    return (
        json.dumps(
            obj,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=True,
            allow_nan=False
        ) + '\n'
    ).encode('ascii')


def decode(raw, limit):
    need(
        1 < len(raw) <= limit and raw.endswith(b'\n'),
        'size or LF framing'
    )

    try:
        obj = json.loads(
            raw,
            object_pairs_hook=unique,
            parse_constant=lambda _: (
                (_ for _ in ()).throw(
                    ValueError('nonfinite')
                )
            )
        )

    except (
        UnicodeDecodeError,
        json.JSONDecodeError
    ) as exc:
        raise ValueError('invalid JSON') from exc

    need(
        json_canonical(obj) == raw,
        'noncanonical bytes'
    )

    return obj


def secure_read(path, limit):
    p = Path(path).absolute()
    info = p.parent.lstat()

    need(
        stat.S_ISDIR(info.st_mode)
        and not stat.S_ISLNK(info.st_mode),
        'unsafe parent directory'
    )

    fd = os.open(
        p,
        os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    )

    try:
        before = os.fstat(fd)

        need(
            stat.S_ISREG(before.st_mode)
            and before.st_nlink == 1
            and 0 < before.st_size <= limit,
            'invalid or oversized input'
        )

        with os.fdopen(os.dup(fd), 'rb') as stream:
            raw = stream.read(limit + 1)

        after = os.fstat(fd)

        need(
            len(raw) == before.st_size
            and before.st_size == after.st_size
            and before.st_mtime_ns == after.st_mtime_ns,
            'unstable input'
        )

        return raw

    finally:
        os.close(fd)


def secure_write(path, raw):
    p = Path(path).absolute()
    info = p.parent.lstat()

    need(
        stat.S_ISDIR(info.st_mode)
        and not stat.S_ISLNK(info.st_mode)
        and not (info.st_mode & 0o077),
        'output directory must be mode 0700'
    )

    fd = os.open(
        p,
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, 'O_NOFOLLOW', 0),
        0o600
    )

    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(raw)
            output.flush()
            os.fsync(output.fileno())

        dirfd = os.open(
            p.parent,
            os.O_RDONLY
        )

        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)

    except BaseException:
        p.unlink(missing_ok=True)
        raise


def validate_dual(d):

    digest_fields = (
        'capsule_sha256',
        'trust_sha256',
        'anchor_sha256',
        'quorum_report_sha256'
    )

    false_fields = (
        'independent_devices_proven',
        'external_retention_proven',
        'independent_audit_completed',
        'economic_activation',
        'mainnet_active'
    )

    expected = {
        'format',
        'chain_id',
        'sequence',
        'keeper_count',
        'required_quorum',
        'python_verified',
        'node_verified',
        'non_value_research_only',
        *digest_fields,
        *false_fields
    }

    need(
        type(d) is dict and set(d) == expected,
        'dual report fields'
    )

    need(
        d['format'] == 'auneya-dual-runtime-v1.17',
        'dual format'
    )

    need(
        type(d['chain_id']) is str
        and re.fullmatch(
            r'[a-z0-9][a-z0-9._-]{0,79}',
            d['chain_id']
        ) is not None,
        'chain id'
    )

    need(
        type(d['sequence']) is str
        and re.fullmatch(
            r'[1-9][0-9]{0,18}',
            d['sequence']
        ) is not None
        and int(d['sequence']) <= 2**63 - 1,
        'noncanonical sequence'
    )

    need(
        type(d['keeper_count']) is int
        and type(d['required_quorum']) is int
        and 2 <= d['required_quorum']
        <= d['keeper_count'] <= 16,
        'quorum bounds'
    )

    for key in digest_fields:
        need(
            type(d[key]) is str
            and SHA.fullmatch(d[key]) is not None,
            'invalid ' + key
        )

    for key in (
        'python_verified',
        'node_verified',
        'non_value_research_only'
    ):
        need(
            d[key] is True,
            'missing affirmative verifier result: ' + key
        )

    for key in false_fields:
        need(
            d[key] is False,
            'unsupported claim: ' + key
        )


def build(trust, capsule, expected):

    need(
        type(expected) is str
        and SHA.fullmatch(expected) is not None,
        'out-of-band expected SHA-256 required'
    )

    d = dual.run(
        SimpleNamespace(
            trust=trust,
            capsule=capsule,
            expected=expected
        )
    )

    validate_dual(d)

    schema_raw = secure_read(
        SCHEMA,
        32768
    )

    schema = json.loads(
        schema_raw,
        object_pairs_hook=unique
    )

    need(
        schema.get('$id') ==
        'https://github.com/nightfall-wizard/wizard-verification-protocol/schemas/auneya-gate4-evidence-v1.18.schema.json',
        'unknown schema'
    )

    pack = dict(
        format=FORMAT,
        dual=d,
        dual_sha256=HEX(
            json_canonical(d)
        ),
        schema_sha256=HEX(
            schema_raw
        ),
        capsule_sha256=d['capsule_sha256'],
        trust_sha256=d['trust_sha256'],
        non_value_research_only=True,
        independent_devices_proven=False,
        external_retention_proven=False,
        independent_audit_completed=False,
        economic_activation=False,
        mainnet_active=False
    )

    need(
        set(pack)
        == set(schema['required'])
        == set(schema['properties'])
        and schema['additionalProperties'] is False,
        'schema key contract drift'
    )

    return pack


def run(args):

    expected = build(
        args.trust,
        args.capsule,
        args.expected
    )

    raw = json_canonical(expected)

    if args.command == 'create':

        if args.output:
            secure_write(
                args.output,
                raw
            )

        sys.stdout.buffer.write(raw)

    else:

        actual_raw = secure_read(
            args.input,
            65536
        )

        actual = decode(
            actual_raw,
            65536
        )

        need(
            type(actual) is dict
            and set(actual) == set(expected),
            'bundle fields'
        )

        need(
            hmac.compare_digest(
                actual_raw,
                raw
            ),
            'evidence does not match fresh Python/Node verification'
        )

        need(
            secure_read(
                args.input,
                65536
            ) == actual_raw,
            'bundle changed'
        )

        print(
            'PASS: dual-verified, schema-bound, '
            'canonical and reproducible; '
            'external device independence NOT proven'
        )


def main():

    ap = argparse.ArgumentParser(
        description=__doc__
    )

    sub = ap.add_subparsers(
        dest='command',
        required=True
    )

    for verb in ('create', 'verify'):

        p = sub.add_parser(verb)

        p.add_argument(
            '--trust',
            required=True
        )

        p.add_argument(
            '--capsule',
            required=True
        )

        p.add_argument(
            '--expected',
            required=True,
            help='SHA-256 received from an independently trusted source'
        )

        if verb == 'create':
            p.add_argument('--output')

        else:
            p.add_argument(
                '--input',
                required=True
            )

    run(ap.parse_args())


if __name__ == '__main__':

    try:
        main()

    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        RuntimeError
    ) as exc:

        sys.exit(
            'REJECTED: ' + str(exc)
        )
