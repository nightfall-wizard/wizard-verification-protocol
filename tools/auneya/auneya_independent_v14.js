#!/usr/bin/env node
'use strict';

/*
 AUNEYA/WVP v1.4

 Independent, read-only Node.js verification
 of existing v1.2 portable evidence bundles.

 No npm packages.
 No Python verification dependency.
 No private keys.
 No wallet.
 No mainnet mutation.
*/

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {parseLossless} = require('./auneya_lossless_json_v14.js');

const assert = (ok, why) => {
  if (!ok) throw Error(why);
};

const H = b =>
  crypto.createHash('sha256').update(b).digest('hex');

const hex64 = s =>
  typeof s === 'string' &&
  /^[0-9a-f]{64}$/.test(s);

const hex128 = s =>
  typeof s === 'string' &&
  /^[0-9a-f]{128}$/.test(s);

const cp = (a, b) => {
  const x = Array.from(a, c => c.codePointAt(0));
  const y = Array.from(b, c => c.codePointAt(0));

  for (let i = 0; i < Math.min(x.length, y.length); i++) {
    if (x[i] !== y[i]) return x[i] - y[i];
  }

  return x.length - y.length;
};

const keys = o => Object.keys(o).sort(cp);

const object = v =>
  !!v &&
  typeof v === 'object' &&
  !Array.isArray(v);

const fields = (o, names) =>
  object(o) &&
  keys(o).join('|') === [...names].sort(cp).join('|');

const integer = v => Number.isSafeInteger(v) || typeof v === 'bigint';
const compareInt = (a,b) => BigInt(a)<BigInt(b) ? -1 : BigInt(a)>BigInt(b) ? 1 : 0;

function pjson(v) {
  if (v === null || typeof v === 'boolean') {
    return JSON.stringify(v);
  }

  if (typeof v === 'bigint') return v.toString();

  if (typeof v === 'number') {
    assert(integer(v), 'unsafe JSON integer or float');
    return String(v);
  }

  if (typeof v === 'string') {
    return JSON.stringify(v).replace(
      /[\u007f-\uffff]/g,
      c => '\\u' +
        c.charCodeAt(0).toString(16).padStart(4, '0')
    );
  }

  if (Array.isArray(v)) {
    return '[' + v.map(pjson).join(',') + ']';
  }

  assert(object(v), 'unsupported JSON value');

  return '{' + keys(v).map(
    k => pjson(k) + ':' + pjson(v[k])
  ).join(',') + '}';
}

const C = v => Buffer.from(pjson(v), 'ascii');

const sealC = v =>
  Buffer.from(pjson(v) + '\n', 'ascii');

const equal = (a, b) =>
  pjson(a) === pjson(b);

function readPrivate(p, max) {
  const flags =
    fs.constants.O_RDONLY |
    (fs.constants.O_NOFOLLOW || 0);

  const fd = fs.openSync(p, flags);

  try {
    const st = fs.fstatSync(fd);

    assert(
      st.isFile() && !(st.mode & 0o077),
      'expected private regular file'
    );

    assert(
      st.size > 0 && st.size < max,
      'invalid input size'
    );

    const raw = Buffer.alloc(st.size);
    let off = 0;

    while (off < raw.length) {
      const n = fs.readSync(
        fd, raw, off, raw.length - off, off
      );

      assert(n > 0, 'short read');
      off += n;
    }

    assert(
      fs.fstatSync(fd).size === raw.length,
      'file changed while reading'
    );

    return raw;

  } finally {
    fs.closeSync(fd);
  }
}

function privateDir(p) {
  const st = fs.lstatSync(p);

  assert(
    st.isDirectory() && !(st.mode & 0o077),
    'expected private directory'
  );
}

function parsed(raw, checkpoint = false) {
  const v = parseLossless(raw);

  assert(
    raw.equals(checkpoint ? sealC(v) : C(v)),
    'noncanonical JSON'
  );

  return v;
}

function validateSeal(s, pin) {
  assert(
    fields(s, ['format','previous','nodes','events']),
    'seal shape'
  );

  assert(
    s.format === 'auneya-registry-checkpoint-v0.6',
    'seal version'
  );

  assert(
    s.previous === null || hex64(s.previous),
    'seal previous'
  );

  assert(
    H(sealC(s)) === pin,
    'untrusted checkpoint'
  );

  assert(
    Array.isArray(s.nodes) &&
    s.nodes.length >= 1 &&
    s.nodes.length <= 20000,
    'seal nodes'
  );

  assert(
    Array.isArray(s.events) &&
    s.events.length <= 20000,
    'seal events'
  );

  const nodes = new Map();

  for (const n of s.nodes) {
    assert(
      fields(n, ['id','epoch','fingerprint','state']),
      'node shape'
    );

    assert(
      typeof n.id === 'string' &&
      n.id.length >= 1 &&
      n.id.length <= 128 &&
      !n.id.includes('\0'),
      'node id'
    );

    assert(
      integer(n.epoch) &&
      n.epoch >= 0 &&
      n.epoch <= 20000,
      'node epoch'
    );

    assert(
      hex64(n.fingerprint) &&
      ['active','revoked'].includes(n.state),
      'node key/state'
    );

    assert(!nodes.has(n.id), 'duplicate node');

    nodes.set(n.id, n);
  }

  assert(
    equal(
      s.nodes,
      [...s.nodes].sort((a,b) => cp(a.id,b.id))
    ),
    'node order'
  );

  const hist = new Map(
    [...nodes].map(([id]) => [id, []])
  );

  for (const e of s.events) {
    assert(
      fields(e, ['id','epoch','digest','kind']),
      'event shape'
    );

    assert(
      hist.has(e.id) &&
      integer(e.epoch) &&
      hex64(e.digest),
      'event identity'
    );

    assert(
      ['enroll','rotate','revoke'].includes(e.kind),
      'event type'
    );

    hist.get(e.id).push(e);
  }

  assert(
    equal(
      s.events,
      [...s.events].sort(
        (a,b) => cp(a.id,b.id) || a.epoch-b.epoch
      )
    ),
    'event order'
  );

  for (const [id,n] of nodes) {
    const ev = [...hist.get(id)].sort(
      (a,b) => a.epoch-b.epoch
    );

    assert(
      ev.length === n.epoch+1 &&
      ev[0].kind === 'enroll',
      'history length'
    );

    ev.forEach((e,i) => {
      assert(
        e.epoch === i &&
        (i === 0 || e.kind !== 'enroll'),
        'event order/epoch'
      );

      if (i < ev.length-1) {
        assert(
          e.kind !== 'revoke',
          'event after revoke'
        );
      }
    });

    assert(
      (ev[ev.length-1].kind === 'revoke') ===
      (n.state === 'revoked'),
      'revocation mismatch'
    );
  }

  return nodes;
}

const VER =
  'auneya-nightfall-operator-challenge-v0.5';

const GEN =
  '061a052d49607ff8f4b306c75d622eb' +
  'd230cff4ec3a45a6dffc2f7738d4b20de';

const STATUS = [
  'network',
  'genesis',
  'protocol_version',
  'tip_height',
  'tip',
  'total_work',
  'live_peers',
  'best_peer_height',
  'supply_invariant_ok',
  'loading',
  'stalled_on_fork',
  'reorg_in_flight'
];

function checkChallenge(c, t) {
  assert(
    fields(c, [
      'protocol','kind','nonce',
      'issued_at','expires_at','network','genesis'
    ]),
    'challenge shape'
  );

  assert(
    c.protocol === VER &&
    c.kind === 'challenge' &&
    hex64(c.nonce),
    'challenge version'
  );

  assert(
    c.network === 'mainnet' &&
    c.genesis === GEN,
    'challenge chain'
  );

  assert(
    integer(c.issued_at) &&
    integer(c.expires_at) &&
    BigInt(c.expires_at)-BigInt(c.issued_at) >= 1n &&
    BigInt(c.expires_at)-BigInt(c.issued_at) <= 600n,
    'challenge duration'
  );

  assert(
    BigInt(t) >= BigInt(c.issued_at)-30n &&
    BigInt(t) <= BigInt(c.expires_at)+30n,
    'claimed time not challenge bound'
  );
}

function checkStatus(s, c) {
  assert(fields(s, STATUS), 'status fields');

  assert(
    s.network === c.network &&
    s.genesis === c.genesis &&
    s.protocol_version === 8,
    'chain status'
  );

  assert(
    hex64(s.tip) &&
    typeof s.total_work === 'string' &&
    /^(0|[1-9][0-9]{0,77})$/.test(s.total_work),
    'tip/work'
  );

  for (const f of [
    'tip_height','live_peers','best_peer_height'
  ]) {
    assert(
      integer(s[f]) && s[f] >= 0 &&
      BigInt(s[f]) < (1n << 64n),
      'counter'
    );
  }

  for (const f of [
    'supply_invariant_ok',
    'loading',
    'stalled_on_fork',
    'reorg_in_flight'
  ]) {
    assert(
      typeof s[f] === 'boolean',
      'risk field'
    );
  }
}

function pair(a,b) {
  const x = a.status;
  const y = b.status;

  assert(
    a.node_id !== b.node_id &&
    equal(a.challenge,b.challenge),
    'pair identity'
  );

  if (
    x.tip_height === y.tip_height &&
    x.tip !== y.tip
  ) {
    return 'SAME_HEIGHT_FORK_CONFLICT';
  }

  if (
    x.tip === y.tip &&
    (
      x.total_work !== y.total_work ||
      x.tip_height !== y.tip_height
    )
  ) {
    return 'INCONSISTENT_TIP_CLAIMS';
  }

  if (
    x.tip === y.tip &&
    x.tip_height === y.tip_height &&
    x.total_work === y.total_work
  ) {
    return 'MATCHING_TIP_CLAIMS';
  }

  return 'INCOMPARABLE_HEIGHTS_NOT_A_FORK_PROOF';
}

function groupsOf(receipts, identity) {
  const m = new Map();

  for (const r of receipts) {
    const k = pjson(identity(r));

    if (!m.has(k)) {
      m.set(k, {
        state: identity(r),
        ids: []
      });
    }

    m.get(k).ids.push(r.node_id);
  }

  return [...m.values()].sort(
    (a,b) =>
      compareInt(a.state[0],b.state[0]) ||
      cp(a.state[1],b.state[1]) ||
      cp(a.state[2],b.state[2])
  );
}

function batchReport(receipts, pin, challenge) {
  const groups = groupsOf(
    receipts,
    r => [
      r.status.tip_height,
      r.status.tip,
      r.status.total_work
    ]
  );

  const comps = {};

  for (let i=0; i<receipts.length; i++) {
    for (let j=i+1; j<receipts.length; j++) {
      const k = pair(receipts[i],receipts[j]);
      comps[k] = (comps[k] || 0)+1;
    }
  }

  const verdict =
    comps.SAME_HEIGHT_FORK_CONFLICT
      ? 'CONFLICTING_SAME_HEIGHT_SIGNED_CLAIMS'
    : comps.INCONSISTENT_TIP_CLAIMS
      ? 'INCONSISTENT_SIGNED_CLAIMS'
    : groups.length === 1
      ? 'MATCHING_SIGNED_TIP_CLAIMS'
      : 'DIVERGENT_SIGNED_CLAIMS_NOT_FORK_PROOF';

  const commitment = {
    checkpoint_sha256: pin,
    challenge_sha256: H(C(challenge)),
    receipt_sha256:
      receipts.map(r => H(C(r))).sort(cp)
  };

  return {
    observation_verdict: verdict,
    operator_count: receipts.length,

    operator_ids:
      receipts.map(x => x.node_id).sort(cp),

    claimed_tip_groups: groups.map(g => ({
      tip_height: g.state[0],
      tip: g.state[1],
      total_work: g.state[2],
      operator_ids: g.ids.sort(cp)
    })),

    pairwise_results: comps,

    reported_risk_flags: receipts.some(
      r =>
        r.status.live_peers === 0 ||
        !r.status.supply_invariant_ok ||
        r.status.loading ||
        r.status.stalled_on_fork ||
        r.status.reorg_in_flight
    ),

    format: 'auneya-wvp-evidence-batch-v0.8',
    result: 'PINNED_OPERATOR_SIGNATURES_VALID',
    commitment,
    evidence_sha256: H(C(commitment)),

    wvp_proven:
      'authenticated_pinned_public_operator_claims_only',

    consensus_validated: false,
    sybil_resistance_proven: false,
    independent_devices_proven: false,
    mainnet_mutated: false,
    non_value_research_only: true
  };
}

function capsule(raw, pin, challengeHash) {
  const o = parsed(raw,true);

  assert(
    fields(o, [
      'format','seal','challenge',
      'receipts','keys','report'
    ]),
    'capsule shape'
  );

  assert(
    o.format ===
      'auneya-archived-operator-claims-v0.9',
    'capsule format'
  );

  const nodes = validateSeal(o.seal,pin);

  assert(
    H(C(o.challenge)) === challengeHash,
    'wrong challenge digest'
  );

  assert(
    Array.isArray(o.receipts) &&
    o.receipts.length >= 2 &&
    o.receipts.length <= 16,
    'receipt count'
  );

  assert(object(o.keys), 'key map');

  let prev = '';
  const fps = new Set();

  for (const r of o.receipts) {
    assert(
      fields(r, [
        'protocol','kind','challenge',
        'node_id','observed_at',
        'status','signature_hex'
      ]),
      'receipt fields'
    );

    assert(
      typeof r.node_id === 'string' &&
      integer(r.observed_at),
      'receipt identity'
    );

    checkChallenge(o.challenge,r.observed_at);

    assert(
      r.protocol === VER &&
      r.kind === 'attestation' &&
      equal(r.challenge,o.challenge),
      'receipt challenge'
    );

    checkStatus(r.status,o.challenge);

    assert(
      nodes.has(r.node_id) &&
      nodes.get(r.node_id).state === 'active',
      'untrusted signer'
    );

    const derHex = o.keys[r.node_id];

    assert(
      typeof derHex === 'string' &&
      /^[0-9a-f]{88}$/.test(derHex) &&
      derHex.startsWith(
        '302a300506032b6570032100'
      ),
      'invalid Ed25519 DER'
    );

    const der = Buffer.from(derHex,'hex');
    const fp = H(der);

    assert(
      fp === nodes.get(r.node_id).fingerprint,
      'fingerprint mismatch'
    );

    assert(
      !fps.has(fp) &&
      (prev === '' || cp(prev,r.node_id) < 0),
      'duplicate or unordered witness'
    );

    fps.add(fp);
    prev = r.node_id;

    assert(
      hex128(r.signature_hex),
      'signature format'
    );

    const body = {...r};
    delete body.signature_hex;

    const message = Buffer.concat([
      Buffer.from(
        'AUNEYA-NIGHTFALL-PUBLIC-OBSERVATION-V0.5\0',
        'ascii'
      ),
      C(body)
    ]);

    const publicKey = crypto.createPublicKey({
      key: der,
      format: 'der',
      type: 'spki'
    });

    assert(
      crypto.verify(
        null,
        message,
        publicKey,
        Buffer.from(r.signature_hex,'hex')
      ),
      'invalid Ed25519 signature'
    );
  }

  assert(
    equal(
      keys(o.keys),
      o.receipts.map(x => x.node_id).sort(cp)
    ),
    'extraneous/missing keys'
  );

  assert(
    equal(
      o.report,
      batchReport(o.receipts,pin,o.challenge)
    ),
    'forged archived report'
  );

  return o;
}

const BOUNDARY = {
  authenticated_signed_statements_only: true,
  consensus_validated: false,
  historical_freshness_proven: false,
  operator_independence_proven: false,
  sybil_resistance_proven: false,
  mainnet_active: false,
  transferable_value_created: false
};

function verify(bundle, pin, challengeHash, manifestHash) {
  assert(
    [pin,challengeHash,manifestHash].every(hex64),
    'three independent SHA256 pins required'
  );

  privateDir(bundle);

  const rootNames = fs.readdirSync(bundle).sort(cp);

  assert(
    equal(rootNames,['capsules','manifest.json']),
    'unexpected bundle files'
  );

  const capdir = path.join(bundle,'capsules');
  privateDir(capdir);

  const raw = readPrivate(
    path.join(bundle,'manifest.json'),
    128*1024
  );

  assert(
    H(raw) === manifestHash,
    'manifest pin mismatch'
  );

  const m = parsed(raw,true);

  assert(
    fields(m, [
      'format',
      'checkpoint_sha256',
      'challenge_sha256',
      'capsules',
      'federation_report',
      'security_boundary'
    ]),
    'manifest fields'
  );

  assert(
    m.format === 'auneya-portable-federation-v1.2' &&
    equal(m.security_boundary,BOUNDARY),
    'manifest claim boundary'
  );

  assert(
    m.checkpoint_sha256 === pin &&
    m.challenge_sha256 === challengeHash,
    'wrong independent pins'
  );

  assert(
    Array.isArray(m.capsules) &&
    m.capsules.length >= 1 &&
    m.capsules.length <= 16,
    'invalid capsule count'
  );

  const seen = new Set();
  const receiptsBySigner = new Map();
  const fingerprintBySigner = new Map();
  const caps = [];

  let prev = '';

  for (const e of m.capsules) {
    assert(
      fields(e,['file','sha256','size_bytes']) &&
      hex64(e.sha256),
      'manifest entry'
    );

    assert(
      e.file ===
        'capsules/'+e.sha256+'.json' &&
      integer(e.size_bytes) &&
      e.size_bytes > 0 &&
      e.size_bytes < 3*1024*1024,
      'unsafe capsule filename/size'
    );

    assert(
      !seen.has(e.sha256) &&
      (!prev || cp(prev,e.sha256) < 0),
      'duplicate/noncanonical capsule ordering'
    );

    seen.add(e.sha256);
    prev = e.sha256;
    caps.push(e.sha256);

    const payload = readPrivate(
      path.join(capdir,e.sha256+'.json'),
      3*1024*1024
    );

    assert(
      payload.length === e.size_bytes &&
      H(payload) === e.sha256,
      'capsule tampering'
    );

    const obj = capsule(
      payload,
      pin,
      challengeHash
    );

    for (const r of obj.receipts) {
      const fp = H(
        Buffer.from(
          obj.keys[r.node_id],
          'hex'
        )
      );

      if (fingerprintBySigner.has(r.node_id)) {
        assert(
          fingerprintBySigner.get(r.node_id) === fp,
          'signer key mismatch'
        );
      }

      fingerprintBySigner.set(r.node_id,fp);

      if (!receiptsBySigner.has(r.node_id)) {
        receiptsBySigner.set(
          r.node_id,
          new Map()
        );
      }

      receiptsBySigner.get(r.node_id).set(
        H(C(r)),
        r
      );
    }
  }

  assert(
    equal(
      fs.readdirSync(capdir).sort(cp),
      [...seen].map(x => x+'.json').sort(cp)
    ),
    'missing/undeclared file'
  );

  const byfp = new Map();

  for (const [id,fp] of fingerprintBySigner) {
    if (!byfp.has(fp)) {
      byfp.set(fp,[]);
    }

    byfp.get(fp).push(id);
  }

  const aliases = [...byfp.values()]
    .filter(ids => ids.length > 1)
    .map(ids => ids.sort(cp))
    .sort((a,b) => cp(a[0],b[0]));

  const eq = [...receiptsBySigner]
    .filter(
      ([id,rs]) =>
        new Set(
          [...rs.values()].map(
            r => H(C(r.status))
          )
        ).size > 1
    )
    .map(([id]) => id)
    .sort(cp);

  const samples = [...receiptsBySigner.values()]
    .flatMap(map => [...map.values()]);

  const groups = groupsOf(
    samples,
    r => [
      r.status.tip_height,
      r.status.tip,
      r.status.total_work
    ]
  );

  const heights = new Set(
    groups.map(g => g.state[0])
  );

  const verdict =
    aliases.length
      ? 'DUPLICATE_PUBLIC_KEY_IDENTITIES'
    : eq.length
      ? 'SAME_SIGNER_CONTRADICTORY_STATEMENTS'
    : groups.length === 1
      ? 'MATCHING_SIGNED_TIP_CLAIMS'
    : heights.size < groups.length
      ? 'CONFLICTING_SAME_HEIGHT_SIGNED_CLAIMS'
      : 'DIVERGENT_SIGNED_CLAIMS_NOT_FORK_PROOF';

  const commitment = {
    format: 'auneya-offline-federation-v1.1',
    challenge_sha256: challengeHash,
    checkpoint_sha256: pin,
    capsule_sha256: caps.sort(cp)
  };

  const report = {
    format: 'auneya-offline-federation-v1.1',
    result: 'AUTHENTICATED_ARCHIVED_STATEMENTS_ONLY',
    observation_verdict: verdict,
    archive_count: caps.length,
    distinct_key_count: byfp.size,
    signer_identity_count: receiptsBySigner.size,
    unique_signed_statement_count: samples.length,
    equivocating_signer_ids: eq,
    duplicate_public_key_identities: aliases,

    claimed_tip_groups: groups.map(g => ({
      tip_height: g.state[0],
      tip: g.state[1],
      total_work: g.state[2],
      signed_by: [...new Set(g.ids)].sort(cp)
    })),

    federation_sha256: H(C(commitment)),
    historical_freshness_proven: false,
    operator_independence_proven: false,
    consensus_validated: false,
    non_value_research_only: true
  };

  assert(
    equal(report,m.federation_report),
    'federation report mismatch'
  );

  return {
    result: 'PORTABLE_SIGNED_STATEMENTS_REVERIFIED',
    manifest_sha256: manifestHash,
    capsule_count: caps.length,
    federation_sha256: report.federation_sha256,
    observation_verdict: report.observation_verdict,
    security_boundary: BOUNDARY
  };
}

if (require.main === module) {
  try {
    const args = process.argv.slice(2);
    const opts = {};

    assert(
      args.shift() === 'verify' &&
      args.length === 8,
      'usage: verify --bundle DIR --pin HEX --challenge-sha256 HEX --expected-manifest-sha256 HEX'
    );

    for (let i=0; i<args.length; i+=2) {
      assert(
        [
          '--bundle',
          '--pin',
          '--challenge-sha256',
          '--expected-manifest-sha256'
        ].includes(args[i]) &&
        !Object.hasOwn(opts,args[i]),
        'unexpected argument'
      );

      opts[args[i]] = args[i+1];
    }

    assert(
      Object.keys(opts).length === 4,
      'missing argument'
    );

    console.log(
      JSON.stringify(
        verify(
          opts['--bundle'],
          opts['--pin'],
          opts['--challenge-sha256'],
          opts['--expected-manifest-sha256']
        ),
        null,
        2
      )
    );

  } catch(e) {
    console.error('FAIL-CLOSED:',e.message);
    process.exitCode = 2;
  }
}

module.exports = {verify};
