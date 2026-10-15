#!/usr/bin/env python3
"""AUNEYA v0.5: challenge-bound, signed public Nightfall node observations.

No wallet access, chain writes, remote RPC, or assertion of consensus validity.
Requires v0.4 operator-pinned registry for verification.
"""

import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import sqlite3
import subprocess
import tempfile
import time

import auneya_trusted_node_identity_v04 as ident

VERSION = 'auneya-nightfall-operator-challenge-v0.5'
DOMAIN = b'AUNEYA-NIGHTFALL-PUBLIC-OBSERVATION-V0.5\x00'
GENESIS = '061a052d49607ff8f4b306c75d622ebd230cff4ec3a45a6dffc2f7738d4b20de'
HEX64 = re.compile(r'^[0-9a-f]{64}$')
NUM = re.compile(r'^(0|[1-9][0-9]{0,77})$')
FIELDS = {'network', 'genesis', 'protocol_version', 'tip_height', 'tip',
          'total_work', 'live_peers', 'best_peer_height', 'supply_invariant_ok',
          'loading', 'stalled_on_fork', 'reorg_in_flight'}
MAX_FILE = 8192


class ChallengeError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


def pairs(values):
    result = {}
    for k, v in values:
        if k in result:
            raise ChallengeError('duplicate JSON key')
        result[k] = v
    return result


def strict_json(data):
    if not isinstance(data, bytes) or len(data) > MAX_FILE:
        raise ChallengeError('invalid document size')
    try:
        return json.loads(data, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              ChallengeError('non-finite JSON')),
                          parse_float=lambda _: (_ for _ in ()).throw(
                              ChallengeError('floats forbidden')))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ChallengeError('invalid JSON') from exc


def read(path):
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_FILE:
        raise ChallengeError('unsafe or oversized input file')
    return strict_json(p.read_bytes())


def exclusive_write(path, value):
    p = Path(path)
    if p.exists() or p.is_symlink():
        raise ChallengeError('output exists; not overwriting')
    data = canonical(value) + b'\n'
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def check_challenge(c, now):
    if not isinstance(c, dict) or set(c) != {'protocol','kind','nonce','issued_at','expires_at','network','genesis'}:
        raise ChallengeError('challenge schema')
    if c['protocol'] != VERSION or c['kind'] != 'challenge' or not isinstance(c['nonce'], str) or not HEX64.fullmatch(c['nonce']):
        raise ChallengeError('challenge protocol or nonce')
    if c['network'] != 'mainnet' or c['genesis'] != GENESIS:
        raise ChallengeError('wrong Nightfall chain')
    start, end = c['issued_at'], c['expires_at']
    if type(start) is not int or type(end) is not int or not 1 <= end-start <= 600:
        raise ChallengeError('invalid challenge duration')
    if not start-30 <= now <= end+30:
        raise ChallengeError('stale or future challenge')
    return c


def new_challenge(now=None):
    now = int(time.time()) if now is None else now
    return {'protocol':VERSION, 'kind':'challenge', 'nonce':secrets.token_hex(32),
            'issued_at':now, 'expires_at':now+300,
            'network':'mainnet', 'genesis':GENESIS}


def check_status(value, c):
    if not isinstance(value, dict) or not FIELDS.issubset(value):
        raise ChallengeError('missing Nightfall status fields')
    if value['network'] != c['network'] or value['genesis'] != c['genesis']:
        raise ChallengeError('node on unexpected chain')
    if type(value['protocol_version']) is not int or value['protocol_version'] != 8:
        raise ChallengeError('incompatible Nightfall protocol')
    if not isinstance(value['tip'], str) or not HEX64.fullmatch(value['tip']):
        raise ChallengeError('malformed block hash')
    if not isinstance(value['total_work'], str) or not NUM.fullmatch(value['total_work']):
        raise ChallengeError('malformed cumulative work')
    for k in ('tip_height', 'live_peers', 'best_peer_height'):
        if type(value[k]) is not int or not 0 <= value[k] < 2**64:
            raise ChallengeError('malformed nonnegative counter: '+k)
    for k in ('supply_invariant_ok','loading','stalled_on_fork','reorg_in_flight'):
        if type(value[k]) is not bool:
            raise ChallengeError('malformed boolean: '+k)
    return {k:value[k] for k in sorted(FIELDS)}


def local_status(port):
    if type(port) is not int or not 1 <= port <= 65535:
        raise ChallengeError('invalid local RPC port')
    try:
        with socket.create_connection(('127.0.0.1',port), timeout=4) as s:
            s.settimeout(4)
            s.sendall(b'{"method":"status","params":{},"id":1}\n')
            buf = bytearray()
            while b'\n' not in buf and len(buf) <= MAX_FILE:
                chunk = s.recv(1024)
                if not chunk:
                    break
                buf.extend(chunk)
    except (OSError, TimeoutError) as exc:
        raise ChallengeError('loopback RPC unavailable') from exc
    if len(buf) > MAX_FILE or not buf.endswith(b'\n') or buf.count(b'\n') != 1:
        raise ChallengeError('RPC response framing')
    answer = strict_json(bytes(buf.strip()))
    if not isinstance(answer, dict) or answer.get('id') != 1 or answer.get('error') is not None or not isinstance(answer.get('result'),dict):
        raise ChallengeError('RPC status response')
    return answer['result']


def signature(private, body):
    key = Path(private)
    if key.is_symlink() or not key.is_file() or key.stat().st_mode & 0o077:
        raise ChallengeError('private key must be regular 0600 file')
    with tempfile.TemporaryDirectory(prefix='auneya-v05-sign-') as td:
        message, output = Path(td)/'message', Path(td)/'sig'
        message.write_bytes(DOMAIN + canonical(body))
        try:
            p = subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(key.resolve()),
                                '-rawin','-in',str(message),'-out',str(output)],
                               capture_output=True,timeout=12)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ChallengeError('OpenSSL sign failure') from exc
        if p.returncode or not output.is_file() or len(output.read_bytes()) != 64:
            raise ChallengeError('Ed25519 sign failed')
        return output.read_bytes().hex()


def valid_sig(der, body, sig):
    if not isinstance(sig,str) or not re.fullmatch(r'[a-f0-9]{128}',sig):
        return False
    try:
        with tempfile.TemporaryDirectory(prefix='auneya-v05-verify-') as td:
            pub, msg, sg = Path(td)/'public.pem',Path(td)/'message',Path(td)/'sig'
            pub.write_bytes(ident.key_pem(der))
            msg.write_bytes(DOMAIN+canonical(body))
            sg.write_bytes(bytes.fromhex(sig))
            p = subprocess.run(['openssl','pkeyutl','-verify','-pubin','-inkey',str(pub),
                                '-sigfile',str(sg),'-rawin','-in',str(msg)],
                               capture_output=True, timeout=12)
            return p.returncode == 0
    except (ValueError, OSError, subprocess.TimeoutExpired):
        return False


def attest(challenge, node_id, private, status, now=None):
    now = int(time.time()) if now is None else now
    check_challenge(challenge, now)
    ident.check_node(node_id)
    clean = check_status(status,challenge)
    body = {'protocol':VERSION, 'kind':'attestation', 'challenge':challenge,
            'node_id':node_id, 'observed_at':now, 'status':clean}
    return {**body, 'signature_hex':signature(private,body)}


def verify_receipt(challenge, receipt, registry, now=None):
    now = int(time.time()) if now is None else now
    check_challenge(challenge,now)
    if not isinstance(receipt,dict) or set(receipt) != {'protocol','kind','challenge','node_id','observed_at','status','signature_hex'}:
        raise ChallengeError('receipt schema')
    if receipt['protocol'] != VERSION or receipt['kind'] != 'attestation' or receipt['challenge'] != challenge:
        raise ChallengeError('receipt not bound to challenge')
    ident.check_node(receipt['node_id'])
    observed = receipt['observed_at']
    if type(observed) is not int or not challenge['issued_at']-30 <= observed <= challenge['expires_at']+30 or observed > now+30:
        raise ChallengeError('receipt time outside challenge')
    clean = check_status(receipt['status'],challenge)
    if clean != receipt['status']:
        raise ChallengeError('receipt includes unknown status fields')
    with closing(ident.database(registry)) as db:
        db.execute('BEGIN IMMEDIATE')
        _, _, der, state = ident.get_locked(db,receipt['node_id'])
        if state != 'active':
            raise ChallengeError('revoked operator key')
        signed = {k:v for k,v in receipt.items() if k != 'signature_hex'}
        if not valid_sig(der,signed,receipt['signature_hex']):
            raise ChallengeError('untrusted or altered signed receipt')
    return receipt


def record_once(path, receipts):
    """Persist verified witness IDs atomically; reject repeated proof use."""
    p = Path(path)
    if p.is_symlink() or (p.exists() and (not p.is_file() or p.stat().st_mode & 0o077)):
        raise ChallengeError('replay ledger must be a private regular file')
    old = os.umask(0o077)
    try:
        with closing(sqlite3.connect(str(p), timeout=5)) as db:
            db.execute('PRAGMA busy_timeout=5000')
            db.execute('PRAGMA synchronous=FULL')
            db.execute('CREATE TABLE IF NOT EXISTS receipts('
                       'nonce TEXT NOT NULL, node_id TEXT NOT NULL, '
                       'receipt_hash TEXT NOT NULL, PRIMARY KEY(nonce,node_id))')
            db.commit()
            if p.stat().st_mode & 0o077:
                raise ChallengeError('private file permissions not enforced')
            db.execute('BEGIN IMMEDIATE')
            try:
                for r in receipts:
                    db.execute('INSERT INTO receipts VALUES (?,?,?)',
                               (r['challenge']['nonce'],r['node_id'],
                                hashlib.sha256(canonical(r)).hexdigest()))
                db.commit()
            except sqlite3.IntegrityError as exc:
                db.rollback()
                raise ChallengeError('replayed or duplicated signed observation') from exc
    finally:
        os.umask(old)


def compare_verified(a,b):
    x,y=a['status'],b['status']
    if a['node_id']==b['node_id']:
        raise ChallengeError('two distinct pinned operator identities required')
    if a['challenge']!=b['challenge']:
        raise ChallengeError('observations not from same challenge')
    if x['tip_height']==y['tip_height'] and x['tip']!=y['tip']:
        verdict = 'SAME_HEIGHT_FORK_CONFLICT'
    elif x['tip']==y['tip'] and (x['total_work']!=y['total_work'] or x['tip_height']!=y['tip_height']):
        verdict = 'INCONSISTENT_TIP_CLAIMS'
    elif (x['tip']==y['tip'] and x['tip_height']==y['tip_height'] and
          x['total_work']==y['total_work']):
        verdict = 'MATCHING_TIP_CLAIMS'
    else:
        verdict = 'INCOMPARABLE_HEIGHTS_NOT_A_FORK_PROOF'
    unsafe = any(s['loading'] or s['stalled_on_fork'] or s['reorg_in_flight'] or
                 not s['supply_invariant_ok'] or s['live_peers']==0 for s in (x,y))
    return {'protocol':VERSION,'result':verdict,'node_ids':sorted([a['node_id'],b['node_id']]),
            'reported_risk_flags':unsafe,'cryptographic_chain_validation':False,
            'operator_independence_proven':False,'mainnet_mutated':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('challenge');a.add_argument('--out',required=True)
    a=sub.add_parser('attest')
    for n in ('challenge','node-id','private','out'):a.add_argument('--'+n,required=True)
    a.add_argument('--rpc-port',type=int,default=17881)
    a=sub.add_parser('verify')
    for n in ('challenge','receipt','registry','replay-db'):a.add_argument('--'+n,required=True)
    a=sub.add_parser('compare')
    for n in ('challenge','receipt-a','receipt-b','registry','replay-db'):a.add_argument('--'+n,required=True)
    args=p.parse_args()
    try:
        if args.command=='challenge':
            c=new_challenge();exclusive_write(args.out,c);print(json.dumps(c,indent=2))
        elif args.command=='attest':
            c=read(args.challenge)
            r=attest(c,args.node_id,args.private,local_status(args.rpc_port))
            exclusive_write(args.out,r)
            print(json.dumps({'created':args.out,'node_id':args.node_id,'signed':True}))
        elif args.command=='verify':
            r=verify_receipt(read(args.challenge),read(args.receipt),args.registry)
            record_once(args.replay_db,[r])
            print(json.dumps({'result':'SIGNATURE_AND_CONTEXT_VALID','node_id':r['node_id'],
                              'consensus_validated':False}))
        else:
            c=read(args.challenge)
            a=verify_receipt(c,read(args.receipt_a),args.registry)
            b=verify_receipt(c,read(args.receipt_b),args.registry)
            analysis=compare_verified(a,b)
            record_once(args.replay_db,[a,b])
            print(json.dumps(analysis,indent=2))
    except (ChallengeError, ident.IdentityError, sqlite3.Error, OSError, ValueError) as exc:
        p.exit(2,'FAIL-CLOSED: '+str(exc)+'\n')


if __name__=='__main__':
    main()
