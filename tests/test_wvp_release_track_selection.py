"""
Offline regression for WVP release track selection.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT /
    'conformance/release-check-self-release-checksum.sh'
)

MOCK_GH = r'''#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]

repo = 'nightfall-wizard/wizard-verification-protocol'

name = 'wvp-v0.5.1-source.tar.gz'

content = b'fictional reproducible WVP source fixture\n'

releases = [
    dict(
        tag_name='auneya-v1.5.0',
        draft=False,
        prerelease=True,
        published_at='2026-10-30T12:08:24Z'
    ),
    dict(
        tag_name='v0.5.0',
        draft=False,
        prerelease=False,
        published_at='2026-10-17T21:04:45Z'
    ),
    dict(
        tag_name='v0.5.1',
        draft=False,
        prerelease=False,
        published_at='2026-10-30T08:46:16Z'
    ),
    dict(
        tag_name='v9.0.0',
        draft=True,
        prerelease=False,
        published_at='2026-11-02T00:00:00Z'
    )
]

if os.environ.get('MOCK_NO_WVP'):

    releases = [
        x for x in releases
        if not x['tag_name'].startswith('v')
    ]

if args[0] == 'api':

    assert args[1] == (
        'repos/' + repo + '/releases?per_page=100'
    ), args

    print(
        json.dumps(releases)
    )

elif args[:2] == ['release', 'view']:

    assert args[2] == 'v0.5.1', args

    print(
        json.dumps({
            'assets': [
                {'name': name},
                {'name': name + '.sha256'}
            ],
            'body': 'Source-only unsigned'
        })
    )

elif args[:2] == ['release', 'download']:

    assert args[2] == 'v0.5.1', args

    dest = Path(
        args[args.index('--dir') + 1]
    )

    dest.mkdir(
        parents=True,
        exist_ok=True
    )

    payload = content

    if os.environ.get('MOCK_TAMPER'):
        payload += b'evil'

    (dest / name).write_bytes(
        payload
    )

    checksum = (
        hashlib.sha256(content).hexdigest()
        + '  '
        + name
        + '\n'
    )

    (dest / (name + '.sha256')).write_text(
        checksum
    )

else:

    sys.exit(
        'Unexpected gh command: ' + repr(args)
    )
'''


class StableWvpSelection(unittest.TestCase):

    def setUp(self):

        self.tmp = tempfile.TemporaryDirectory(
            prefix='wvp-release-track-'
        )

        self.addCleanup(
            self.tmp.cleanup
        )

        self.root = Path(
            self.tmp.name
        )

        (self.root / 'conformance').mkdir()

        (self.root / 'mockbin').mkdir()

        shutil.copyfile(
            SOURCE,
            self.root / 'conformance' / SOURCE.name
        )

        gh = self.root / 'mockbin' / 'gh'

        gh.write_text(
            MOCK_GH
        )

        gh.chmod(
            0o700
        )

    def run_check(self, **extra):

        env = os.environ.copy()

        env['PATH'] = (
            str(self.root / 'mockbin')
            + os.pathsep
            + env['PATH']
        )

        env.update(
            extra
        )

        return subprocess.run(
            [
                'bash',
                str(
                    self.root /
                    'conformance' /
                    SOURCE.name
                )
            ],
            text=True,
            capture_output=True,
            env=env,
            timeout=20
        )

    def test_selects_stable_wvp(self):

        result = self.run_check()

        self.assertEqual(
            result.returncode,
            0,
            result.stdout + result.stderr
        )

        self.assertIn(
            'Tag: v0.5.1',
            result.stdout
        )

        self.assertIn(
            'RESULT: PASS',
            result.stdout
        )

    def test_corrupted_checksum_fails_closed(self):

        result = self.run_check(
            MOCK_TAMPER='1'
        )

        self.assertNotEqual(
            result.returncode,
            0
        )

        self.assertNotIn(
            'RESULT: PASS',
            result.stdout
        )

    def test_missing_stable_release_fails_closed(self):

        result = self.run_check(
            MOCK_NO_WVP='1'
        )

        self.assertNotEqual(
            result.returncode,
            0
        )

        self.assertNotIn(
            'RESULT: PASS',
            result.stdout
        )


if __name__ == '__main__':

    unittest.main()
