#!/usr/bin/env python3

"""
WVP release identity verification.

Separates:
- published WVP releases;
- source package versions;
- AUNEYA research capabilities;
- AUNEYA research previews.

Read-only verification.
"""

import argparse
import json
import re
import subprocess
import tomllib

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPO = (
    'nightfall-wizard/'
    'wizard-verification-protocol'
)

WVP = re.compile(
    r'^v(\d+)\.(\d+)\.(\d+)$'
)

AUNEYA = re.compile(
    r'^auneya-v(\d+)\.(\d+)\.(\d+)$'
)


def latest(releases, pattern):

    versions = []

    for release in releases:

        if not isinstance(release, dict):
            continue

        if release.get('draft'):
            continue

        match = pattern.fullmatch(
            str(release.get('tag_name', ''))
        )

        if not match:
            continue

        if (
            pattern is WVP
            and release.get('prerelease')
        ):
            continue

        versions.append(
            (
                tuple(map(int, match.groups())),
                release
            )
        )

    if not versions:
        return None

    return max(
        versions,
        key=lambda item: item[0]
    )[1]


def report(releases, root=ROOT):

    published_release = latest(
        releases,
        WVP
    )

    assert published_release is not None, (
        'WVP public release missing'
    )

    manifest = (
        root
        / 'reference/rust/wvp-release-check/Cargo.toml'
    )

    with manifest.open('rb') as fp:
        package = tomllib.load(fp)['package']

    with (root / 'Cargo.lock').open('rb') as fp:
        packages = tomllib.load(fp)['package']

    version = package['version']

    assert re.fullmatch(
        r'\d+\.\d+\.\d+',
        version
    ), 'Invalid source version'

    matches = sum(
        item['name'] == 'wvp-release-check'
        and item['version'] == version
        for item in packages
    )

    assert matches == 1, (
        'Cargo/lock disagreement'
    )

    published = (
        published_release['tag_name'][1:]
    )

    source_tuple = tuple(
        map(int, version.split('.'))
    )

    published_tuple = tuple(
        map(int, published.split('.'))
    )

    assert source_tuple >= published_tuple, (
        'Source older than public release'
    )

    capabilities = []

    for path in (
        root / 'docs/auneya'
    ).glob('*.md'):

        titles = (
            path.read_text(
                encoding='utf-8'
            ).splitlines()[0:1]
        )

        match = (
            re.search(
                r'^# AUNEYA/WVP v(\d+)\.(\d+)',
                titles[0]
            )
            if titles
            else None
        )

        if match:
            capabilities.append(
                tuple(
                    map(int, match.groups())
                )
            )

    assert capabilities, (
        'No AUNEYA research capability documentation'
    )

    research = '.'.join(
        map(str, max(capabilities))
    )

    readme = (
        root / 'README.md'
    ).read_text()

    assert readme.count(
        '<!-- WVP-RELEASE-TRUTH:START -->'
    ) == 1

    assert readme.count(
        '<!-- WVP-RELEASE-TRUTH:END -->'
    ) == 1

    assert 'releases/latest' in readme

    assert 'HISTORICAL SNAPSHOT ONLY' in readme

    preview = latest(
        releases,
        AUNEYA
    )

    return {
        'source_version': version,
        'published_wvp':
            published_release['tag_name'],
        'published_wvp_url':
            published_release['html_url'],
        'published_auneya_preview':
            (
                preview or {}
            ).get('tag_name'),
        'latest_documented_auneya_research_capability':
            research,
        'wvp_source_is_published':
            version == published,
        'independent_audit_proven': False,
        'mainnet_or_token_active': False
    }


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--releases-json',
        type=Path
    )

    args = parser.parse_args()

    if args.releases_json:

        releases = json.loads(
            args.releases_json.read_text()
        )

    else:

        output = subprocess.check_output(
            [
                'gh',
                'api',
                f'repos/{REPO}/releases?per_page=100'
            ],
            text=True
        )

        releases = json.loads(output)

    result = report(releases)

    print(
        json.dumps(
            result,
            sort_keys=True,
            indent=2
        )
    )


if __name__ == '__main__':
    main()
