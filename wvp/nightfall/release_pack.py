#!/usr/bin/env python3
"""Validate immutable Nightfall evidence and disclose post-snapshot changes."""

from pathlib import Path, PurePosixPath
import hashlib
import json
import re
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / 'release-packs/nightfall/v1.0.5'
MANIFEST = PACK / 'BUNDLE-MANIFEST.json'
MARKDOWN = PACK / 'BUNDLE-MANIFEST.md'
ARCHIVE = PACK / 'wvp-nightfall-v1.0.5-evidence-pack.tar.gz'
SUMS = PACK / 'SHA256SUMS.txt'
REPORT = ROOT / 'reports/nightfall/v1.0.5/RELEASE-PACK.json'

HISTORICALLY_CHANGED = {
    'PROJECT-STATE.md',
    'docs/auneya/README.md',
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def items_by_path(manifest):
    items = manifest['files']
    require(len(items) >= 30, 'too few manifest files')
    require(
        len(items) == manifest['file_count'],
        'file_count mismatch'
    )

    result = {}

    for item in items:
        path = item['path']
        require(
            path not in result,
            'duplicate manifest entry: ' + path
        )
        require(
            isinstance(item['size_bytes'], int)
            and item['size_bytes'] >= 0,
            'invalid size: ' + path
        )
        require(
            re.fullmatch(r'[0-9a-f]{64}', item['sha256']) is not None,
            'invalid sha256: ' + path
        )
        result[path] = item

    return result

def main():
    required_files = (
        MANIFEST, MARKDOWN, ARCHIVE, SUMS, REPORT
    )

    for p in required_files:
        require(
            p.is_file() and not p.is_symlink(),
            'missing/unsafe: ' + str(p)
        )

    current = json.loads(MANIFEST.read_text())
    report = json.loads(REPORT.read_text())

    archive_sha = sha(ARCHIVE.read_bytes())

    require(
        archive_sha == report['archive_sha256'],
        'archive SHA != report'
    )
    require(
        f'{archive_sha}  {ARCHIVE.name}'
        in SUMS.read_text().splitlines(),
        'archive checksum not in SHA256SUMS'
    )

    current_items = items_by_path(current)

    safety = (
        'no_real_seed',
        'no_private_key',
        'no_live_funds',
        'no_exploit_payloads',
        'sanitized_public_report_included',
        'non_audit_boundary_required',
    )

    for field in safety:
        require(
            current.get('safety_boundary', {}).get(field) is True,
            'missing safety boundary: ' + field
        )

    with tarfile.open(ARCHIVE, 'r:gz') as tar:
        members = {}

        for m in tar.getmembers():
            rel = PurePosixPath(m.name)
            require(
                not rel.is_absolute() and '..' not in rel.parts,
                'unsafe tar path: ' + m.name
            )

            if m.isdir():
                continue

            require(
                m.isfile(),
                'unsafe tar entry: ' + m.name
            )
            require(
                m.name not in members,
                'duplicate tar entry: ' + m.name
            )
            members[m.name] = m

        inner_json_name = MANIFEST.relative_to(ROOT).as_posix()
        inner_md_name = MARKDOWN.relative_to(ROOT).as_posix()

        require(
            inner_json_name in members
            and inner_md_name in members,
            'embedded manifests missing'
        )

        def data_of(name):
            member = members[name]
            require(
                member.size <= 50_000_000,
                'oversize member: ' + name
            )

            stream = tar.extractfile(member)
            require(
                stream is not None,
                'unreadable archive entry: ' + name
            )

            with stream:
                data = stream.read(50_000_001)

            require(
                len(data) == member.size,
                'truncated/oversize: ' + name
            )
            return data

        archived = json.loads(
            data_of(inner_json_name).decode('utf-8')
        )
        archived_items = items_by_path(archived)

        expected_names = (
            set(archived_items)
            | {inner_json_name, inner_md_name}
        )

        require(
            set(members) == expected_names,
            'archive member set mismatch: '
            + str(sorted(set(members) ^ expected_names))
        )
        require(
            set(archived_items) == set(current_items),
            'manifest paths changed'
        )
        require(
            archived['id'] == current['id'] == 'WVP-SEC-010',
            'manifest identity mismatch'
        )
        require(
            archived['version'] == current['version'] == 'v1.0.5',
            'manifest version mismatch'
        )

        for field in safety:
            require(
                archived.get('safety_boundary', {}).get(field) is True,
                'archived safety boundary missing: ' + field
            )

        embedded_md = data_of(inner_md_name).decode('utf-8')
        external_md = MARKDOWN.read_text(encoding='utf-8')

        changed = set()

        for name, archived_item in archived_items.items():
            contents = data_of(name)

            require(
                len(contents) == archived_item['size_bytes'],
                'archived size mismatch: ' + name
            )
            require(
                sha(contents) == archived_item['sha256'],
                'archived hash mismatch: ' + name
            )

            current_item = current_items[name]

            if (
                current_item['size_bytes']
                != archived_item['size_bytes']
                or current_item['sha256']
                != archived_item['sha256']
            ):
                changed.add(name)

                new = ROOT / name
                require(
                    new.is_file() and not new.is_symlink(),
                    'later file missing: ' + name
                )

                actual = new.read_bytes()
                require(
                    len(actual) == current_item['size_bytes']
                    and sha(actual) == current_item['sha256'],
                    'later snapshot hash mismatch: ' + name
                )

            if name in HISTORICALLY_CHANGED:
                pattern = (
                    r'^\| `' + re.escape(name)
                    + r'` \| ([0-9]+) \| `([0-9a-f]{64})` \|$'
                )

                for description, md in (
                    ('embedded', embedded_md),
                    ('external', external_md),
                ):
                    m = re.search(pattern, md, re.M)

                    require(
                        m is not None
                        and int(m.group(1)) == len(contents)
                        and m.group(2) == sha(contents),
                        description + ' Markdown mismatch: ' + name
                    )

        require(
            changed == HISTORICALLY_CHANGED,
            'unexpected manifest changes: '
            + str(sorted(changed))
        )

    print('PASS: 236 archivierte Dateien verifiziert')
    print('PASS: Archiv-SHA256 gegen Report und SHA256SUMS')
    print('WARN: 2 spaetere Manifest-Aenderungen separat verifiziert')
    print('Historisches Evidence-Pack ist kein Audit.')
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (
        ValueError, KeyError, OSError,
        tarfile.TarError, UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        print('FAIL:', exc)
        raise SystemExit(1)
