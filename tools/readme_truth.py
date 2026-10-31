#!/usr/bin/env python3

"""
Evidence-first README.

The README is derived from:
- local source files;
- local technical documentation;
- adversarial regression test files;
- the engineering roadmap;
- published GitHub release evidence.

Actions:

--refresh
    Query live GitHub releases and regenerate README.

--check
    Deterministic offline verification.

--check-live
    Compare the recorded releases against GitHub.
"""

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]

REPO = (
    'nightfall-wizard/'
    'wizard-verification-protocol'
)

SNAP = (
    'docs/status/'
    'WVP-AUNEYA-PUBLISHED-RELEASES.json'
)

LATEST = (
    'https://github.com/'
    + REPO
    + '/releases/latest'
)


# Each milestone requires source, documentation,
# and an existing regression test.

MILESTONES = (
    (
        '0.5',
        'Signed challenges',
        'auneya_nightfall_challenge_v05.py',
        'AUNEYA-NIGHTFALL-CHALLENGE-V0.5.md',
        'test_auneya_nightfall_challenge_v05.py'
    ),
    (
        '0.6',
        'Registry checkpoint binding',
        'auneya_registry_checkpoint_v06.py',
        'AUNEYA-REGISTRY-CHECKPOINT-V0.6.md',
        'test_auneya_registry_checkpoint_v06.py'
    ),
    (
        '0.7',
        'Pinned observations',
        'auneya_pinned_observation_v07.py',
        'AUNEYA-PINNED-OBSERVATION-V0.7.md',
        'test_auneya_pinned_observation_v07.py'
    ),
    (
        '0.8',
        'Multi-witness evidence',
        'auneya_wvp_evidence_batch_v08.py',
        'AUNEYA-WVP-EVIDENCE-BATCH-V0.8.md',
        'test_auneya_wvp_evidence_batch_v08.py'
    ),
    (
        '0.9',
        'Canonical evidence archives',
        'auneya_archive_v09.py',
        'AUNEYA-ARCHIVAL-EVIDENCE-V0.9.md',
        'test_auneya_archive_v09.py'
    ),
    (
        '1.0',
        'Transactional archives',
        'auneya_archive_v10.py',
        'AUNEYA-TRANSACTIONAL-ARCHIVE-V1.0.md',
        'test_auneya_archive_v10.py'
    ),
    (
        '1.1',
        'Federated evidence research',
        'auneya_federation_v11.py',
        'AUNEYA-FEDERATED-WITNESS-EVIDENCE-V1.1.md',
        'test_auneya_federation_v11.py'
    ),
    (
        '1.2',
        'Portable offline verification',
        'auneya_portable_v12.py',
        'AUNEYA-PORTABLE-FEDERATION-V1.2.md',
        'test_auneya_portable_v12.py'
    ),
    (
        '1.3',
        'Independent Ed25519 verification',
        'auneya_independent_v13.js',
        'AUNEYA-INDEPENDENT-VERIFICATION-V1.3.md',
        'test_auneya_independent_v13.py'
    ),
    (
        '1.4',
        'Lossless cross-language interop',
        'auneya_independent_v14.js',
        'AUNEYA-LOSSLESS-INTEROPERABILITY-V1.4.md',
        'test_auneya_independent_v14.py'
    ),
    (
        '1.5',
        'Temporal evidence admission',
        'auneya_admission_v15.py',
        'AUNEYA-TEMPORAL-ADMISSION-V1.5.md',
        'test_auneya_admission_v15.py'
    ),
    (
        '1.6',
        'Signed peer-envelope admission',
        'auneya_peer_gate_v16.py',
        'AUNEYA-PEER-EVIDENCE-GATE-V1.6.md',
        'test_auneya_peer_gate_v16.py'
    ),
    (
        '1.7',
        'Bounded local TCP transport',
        'auneya_transport_v17.py',
        'AUNEYA-TRANSPORT-V1.7.md',
        'test_auneya_transport_v17.py'
    ),
    (
        '1.8',
        'Authenticated local receipts',
        'auneya_receipt_v18.py',
        'AUNEYA-AUTHENTICATED-RECEIPTS-V1.8.md',
        'test_auneya_receipt_v18.py'
    ),
    (
        '1.9',
        'Signed offline replay checkpoints',
        'auneya_anchor_v19.py',
        'AUNEYA-EXTERNAL-REPLAY-ANCHORS-V1.9.md',
        'test_auneya_anchor_v19.py'
    ),
    (
        '1.10',
        'Offline independent high-water keeper research',
        'auneya_witness_v110.py',
        'AUNEYA-INDEPENDENT-HIGHWATER-V1.10.md',
        'test_auneya_witness_v110.py'
    ),
)


def require(root, path):

    if not (root / path).is_file():
        raise ValueError(
            'Missing evidence: ' + path
        )


def versions(value):

    return tuple(
        map(
            int,
            value.split('.')
        )
    )


def manifest_version(root):

    path = (
        'reference/rust/'
        'wvp-release-check/Cargo.toml'
    )

    require(root, path)
    require(root, 'Cargo.lock')

    with (root / path).open('rb') as f:
        pkg = tomllib.load(f)['package']

    with (root / 'Cargo.lock').open('rb') as f:
        lock = tomllib.load(f)['package']

    version = pkg['version']

    if not re.fullmatch(
        r'\d+\.\d+\.\d+',
        version
    ):
        raise ValueError(
            'Invalid source semver'
        )

    matches = sum(
        item['name'] == 'wvp-release-check'
        and item['version'] == version
        for item in lock
    )

    if matches != 1:
        raise ValueError(
            'Cargo.toml / Cargo.lock mismatch'
        )

    return version


def live_tags():

    raw = subprocess.check_output(
        [
            'gh',
            'api',
            f'repos/{REPO}/releases?per_page=100'
        ],
        text=True,
        timeout=60
    )

    releases = json.loads(raw)

    if not isinstance(releases, list):
        raise ValueError(
            'GitHub releases response is not a list'
        )

    def pick(pattern, stable_only):

        matches = []

        for release in releases:

            tag = str(
                release.get('tag_name', '')
            )

            found = re.fullmatch(
                pattern,
                tag
            )

            if (
                found
                and not release.get('draft')
                and (
                    not stable_only
                    or not release.get('prerelease')
                )
            ):
                matches.append(
                    (
                        tuple(
                            map(
                                int,
                                found.groups()
                            )
                        ),
                        tag
                    )
                )

        if not matches:
            raise ValueError(
                'No published release for '
                + pattern
            )

        return max(matches)[1]

    return {
        'wvp': pick(
            r'v(\d+)\.(\d+)\.(\d+)',
            True
        ),
        'auneya_preview': pick(
            r'auneya-v(\d+)\.(\d+)\.(\d+)',
            False
        )
    }


def refresh_snapshot(root):

    tags = live_tags()

    target = root / SNAP

    if target.exists():

        current = json.loads(
            target.read_text(
                encoding='utf-8'
            )
        )

        if all(
            current.get(key) == value
            for key, value in tags.items()
        ):
            return

    data = {
        'format':
            'wvp-auneya-published-release-snapshot-v1',

        'observed_utc':
            dt.datetime.now(
                dt.timezone.utc
            ).strftime(
                '%Y-%m-%dT%H:%M:%SZ'
            ),

        **tags
    }

    target.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    target.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True
        ) + '\n',
        encoding='utf-8'
    )


def evidence(root):

    required = (
        'docs/auneya/AUNEYA-PROTOCOL-CHARTER.md',
        'docs/auneya/AUNEYA-WHITEPAPER-V0.1-DRAFT.md',
        'docs/auneya/AUNEYA-ROADMAP-V1.9.md',
        'docs/auneya/AUNEYA-EXTERNAL-REPLAY-ANCHORS-V1.9.md',
        'tools/wvp_release_truth.py',
        'tests/test_wvp_release_truth.py',
        'reference/rust/wvp-release-check/src/lib.rs',
        'reference/rust/wvp-release-check/tests/adversarial_classification.rs',
        'tools/auneya/auneya_one_command_local_demo.sh',
        'docs/release/WVP-RELEASE-TRUTH-AND-AUNEYA-GATES.md',
        'SECURITY.md',
        'LICENSE',
        SNAP
    )

    for path in required:
        require(root, path)

    for _, _, src, doc, test in MILESTONES:

        require(
            root,
            'tools/auneya/' + src
        )

        require(
            root,
            'docs/auneya/' + doc
        )

        require(
            root,
            'tests/' + test
        )

    roadmap = (
        root
        / 'docs/auneya/AUNEYA-ROADMAP-V1.9.md'
    ).read_text(
        encoding='utf-8'
    )

    for item in (
        'GATE 1',
        'GATE 2',
        'GATE 3',
        'GATE 4',
        'GATE 5',
        'GATE 6',
        'PARTIALLY IMPLEMENTED',
        'BLOCKED',
        'INCOMPLETE'
    ):

        if item not in roadmap:
            raise ValueError(
                'Roadmap status changed; '
                'review required: ' + item
            )

    # Do not silently ignore a newer roadmap.

    for path in (
        root / 'docs/auneya'
    ).glob(
        'AUNEYA-ROADMAP-V*.md'
    ):

        match = re.fullmatch(
            r'AUNEYA-ROADMAP-V(\d+)\.(\d+)\.md',
            path.name
        )

        if (
            match
            and tuple(
                map(
                    int,
                    match.groups()
                )
            ) > (1, 9)
        ):
            raise ValueError(
                'Newer roadmap requires '
                'explicit README generator review: '
                + path.name
            )

    snapshot = json.loads(
        (root / SNAP).read_text(
            encoding='utf-8'
        )
    )

    if snapshot.get('format') != (
        'wvp-auneya-published-release-snapshot-v1'
    ):
        raise ValueError(
            'Unknown release snapshot format'
        )

    try:

        dt.datetime.strptime(
            snapshot['observed_utc'],
            '%Y-%m-%dT%H:%M:%SZ'
        )

    except (KeyError, ValueError) as exc:

        raise ValueError(
            'Invalid release snapshot timestamp'
        ) from exc

    wvp = snapshot.get(
        'wvp',
        ''
    )

    preview = snapshot.get(
        'auneya_preview',
        ''
    )

    if (
        not re.fullmatch(
            r'v\d+\.\d+\.\d+',
            wvp
        )
        or not re.fullmatch(
            r'auneya-v\d+\.\d+\.\d+',
            preview
        )
    ):
        raise ValueError(
            'Invalid published release identities'
        )

    source = manifest_version(root)

    if versions(
        wvp[1:]
    ) > versions(
        source
    ):
        raise ValueError(
            'Published WVP newer than local source'
        )

    if versions(
        preview[len('auneya-v'):]
    ) > versions(
        MILESTONES[-1][0]
    ):
        raise ValueError(
            'AUNEYA preview newer than documented '
            'research capability'
        )

    return source, snapshot


def render(root=ROOT):

    source, snap = evidence(root)

    research = MILESTONES[-1][0]

    p_wvp = (
        f'https://github.com/{REPO}/'
        f'releases/tag/{snap["wvp"]}'
    )

    p_aun = (
        f'https://github.com/{REPO}/'
        f'releases/tag/{snap["auneya_preview"]}'
    )

    lines = [
        '# Wizard Verification Protocol (WVP) & AUNEYA',
        '',
        '**Built and maintained by [nightfall-wizard](https://github.com/nightfall-wizard).**',
        '',
        '> No claim without proof. No proof without reproduction. No verification without adversarial testing.',
        '',
        f'[![Published WVP](https://img.shields.io/github/v/release/{REPO}?include_prereleases=false&label=WVP%20published)]({LATEST})',
        f'[![README truth](https://github.com/{REPO}/actions/workflows/readme-truth.yml/badge.svg)](https://github.com/{REPO}/actions/workflows/readme-truth.yml)',
        '',
        '## The two-layer vision',
        '',
        '**WVP** is an evidence-first, adversarial verification framework for reproducible checks of public software and project claims. ',
        '**AUNEYA** researches a phone-first witness protocol for lawful public digital evidence. ',
        'WVP is its verification core; AUNEYA is the proposed network layer, not an already operating public network.',
        '',
        '<!-- WVP-RELEASE-TRUTH:START -->',
        '## Release truth — independent identities',
        '',
        '| Track | Verified status |',
        '| --- | --- |',
        f'| WVP published stable | **[{snap["wvp"]}]({p_wvp})** · [always-current release]({LATEST}) |',
        f'| WVP source package | **`{source}`** · [`Cargo.toml`](reference/rust/wvp-release-check/Cargo.toml); source is not a release |',
        f'| AUNEYA published research preview | **[{snap["auneya_preview"]}]({p_aun})** · distinct from WVP |',
        f'| AUNEYA research implementation | **v{research}** · [offline high-water witness](docs/auneya/AUNEYA-INDEPENDENT-HIGHWATER-V1.10.md); not a published v{research} release |',
        '',
        f'*Release API snapshot checked on {snap["observed_utc"]} UTC; this snapshot is not real-time. ',
        f'The WVP `releases/latest` link is live. Source: [`published release evidence`]({SNAP}).*',
        '<!-- WVP-RELEASE-TRUTH:END -->',
        '',
        '## WVP verification surface',
        '',
        '- [Rust release checker](reference/rust/wvp-release-check/src/lib.rs) and [adversarial classification tests](reference/rust/wvp-release-check/tests/adversarial_classification.rs) separate recorded evidence from unsupported release claims.',
        '- [Release-truth guard](tools/wvp_release_truth.py) distinguishes published WVP, source packages and AUNEYA research versions.',
        '- [Evidence-first release policy](docs/release/WVP-RELEASE-TRUTH-AND-AUNEYA-GATES.md) documents strict claim boundaries.',
        '',
        '## AUNEYA implemented research milestones',
        '',
        'Each row links to committed source, an engineering document and an adversarial test file.',
        '**File existence is evidence of implementation, not proof that an independent audit passed.**',
        '',
        '| Version | Capability | Source / specification / tests |',
        '| --- | --- | --- |'
    ]

    for version, title, src, doc, test in MILESTONES:

        lines.append(
            f'| v{version} | {title} | '
            f'[code](tools/auneya/{src}) · '
            f'[spec](docs/auneya/{doc}) · '
            f'[tests](tests/{test}) |'
        )

    lines += [
        '',
        '## Roadmap and research gates',
        '',
        'Based on the [v1.9 engineering roadmap](docs/auneya/AUNEYA-ROADMAP-V1.9.md):',
        '',
        '| Gate | Current evidence boundary |',
        '| --- | --- |',
        '| 1 · Authenticated peer evidence | Implemented as local research capability (v1.6) |',
        '| 2 · Peer transport | Partially implemented: bounded localhost TCP + signed responder receipts (v1.7/v1.8) |',
        '| 3 · External replay anchors | Partially implemented: signed checkpoints (v1.9) and offline keeper receipts (v1.10); no independently proven remote retention |',
        '| 4 · Public reproducibility | Incomplete: normative schemas, interoperability and independent replication remain |',
        '| 5 · External validation | Not completed: real second-device trials, independent cryptographic/privacy/security/legal reviews |',
        '| 6 · Production decision | **BLOCKED** · no automatic network or economic activation |',
        '',
        '**Next engineering priority (Gate 3):** independent physical-device trials,',
        'authenticated receipt retention, rollback/recovery attack tests across distinct devices,',
        'and reproducible signed acceptance vectors.',
        'The existing v1.9 checkpoint file stored beside its database is **not** an independent anchor.',
        'A v1.10 keeper in the same rollback domain also does not establish independent retention.',
        '',
        '## Start and reproduce locally (Termux)',
        '',
        '```sh',
        './tools/auneya/auneya_one_command_local_demo.sh',
        'python3 -m unittest discover -s tests -p "test_auneya_anchor_v19.py" -v',
        'python3 -m unittest discover -s tests -p "test_auneya_witness_v110.py" -v',
        'python3 -m unittest discover -s tests -p "test_wvp_release_truth.py" -v',
        'python3 tools/readme_truth.py --check',
        '```',
        '',
        'The demo is **local non-value simulation**, not real token collection.',
        'Cryptographic tests may require `openssl` and `node` on the device.',
        'The README checker validates traceability and freshness against the checked-in release snapshot.',
        '',
        '## Canonical project documents',
        '',
        '- [Protocol Charter](docs/auneya/AUNEYA-PROTOCOL-CHARTER.md) — purpose, legal and economic boundaries.',
        '- [AUNEYA technical whitepaper v0.1 DRAFT](docs/auneya/AUNEYA-WHITEPAPER-V0.1-DRAFT.md) — research, **not** final protocol approval.',
        '- [AUNEYA engineering roadmap v1.9](docs/auneya/AUNEYA-ROADMAP-V1.9.md) — six gates and remaining work.',
        '- [WVP release identity policy](docs/release/WVP-RELEASE-TRUTH-AND-AUNEYA-GATES.md) — release/source distinction.',
        '- [Security disclosures](SECURITY.md) · [MIT license](LICENSE).',
        '',
        '## Security and honest claim boundaries',
        '',
        'WVP/AUNEYA currently **do not claim**: an independent security audit;',
        'independent witness/device identity; public P2P networking; global consensus;',
        'Sybil resistance; trusted time; distributed rollback immunity; reproducible binary builds;',
        'mainnet readiness; economic activation; transferable units; or legal clearance.',
        'An Ed25519 signature proves possession of a signing key, not observer independence or factual truth.',
        '',
        '<!-- WVP-V050-PUBLISHED:START -->',
        '## Historical release notes',
        '',
        f'WVP [v0.5.0](https://github.com/{REPO}/releases/tag/v0.5.0) is an already published historical release,',
        'not an unreleased source candidate.',
        '<!-- WVP-V050-PUBLISHED:END -->',
        '<!-- WVP:V040-PUBLIC-STATUS:START -->',
        '',
        '**HISTORICAL SNAPSHOT ONLY:** WVP',
        f'[v0.4.0](https://github.com/{REPO}/releases/tag/v0.4.0) was published;',
        'older prepared-not-released records describe a past pre-publication stage, not current status.',
        'Earlier README text is preserved in Git history.',
        '<!-- WVP:V040-PUBLIC-STATUS:END -->',
        '',
        '## Maintainer workflow',
        '',
        'The README is generated by [`tools/readme_truth.py`](tools/readme_truth.py) and checked by',
        '[CI](.github/workflows/readme-truth.yml). To refresh against public GitHub release facts,',
        'run `python3 tools/readme_truth.py --refresh` in an authenticated Termux environment.',
        'A scheduled CI check detects release changes; it does **not** silently modify releases or the protocol.',
        ''
    ]

    return '\n'.join(line.rstrip() for line in lines)


def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    group = parser.add_mutually_exclusive_group(
        required=True
    )

    group.add_argument(
        '--refresh',
        action='store_true'
    )

    group.add_argument(
        '--check',
        action='store_true'
    )

    group.add_argument(
        '--check-live',
        action='store_true'
    )

    args = parser.parse_args()

    if args.check_live:

        evidence(ROOT)

        saved = json.loads(
            (ROOT / SNAP).read_text(
                encoding='utf-8'
            )
        )

        actual = live_tags()

        if any(
            actual[key] != saved[key]
            for key in actual
        ):
            raise ValueError(
                'New published release: '
                'run --refresh and update README'
            )

        print(
            'PASS: recorded published releases '
            'still current'
        )

        return

    if args.refresh:
        refresh_snapshot(ROOT)

    expected = render(ROOT)

    readme = ROOT / 'README.md'

    if args.check:

        if (
            not readme.exists()
            or readme.read_text(
                encoding='utf-8'
            ) != expected
        ):
            raise ValueError(
                'README drift: use --refresh '
                'to regenerate'
            )

        print(
            'PASS: README, source, docs, '
            'test links, roadmap and '
            'release snapshot agree'
        )

    else:

        if (
            not readme.exists()
            or readme.read_text(
                encoding='utf-8'
            ) != expected
        ):

            readme.write_text(
                expected,
                encoding='utf-8'
            )

            print(
                'README updated from verifiable '
                'repository evidence'
            )

        else:

            print(
                'README already current'
            )


if __name__ == '__main__':

    try:
        main()

    except (
        ValueError,
        OSError,
        subprocess.CalledProcessError
    ) as exc:

        sys.exit(
            'FAIL CLOSED: ' + str(exc)
        )
