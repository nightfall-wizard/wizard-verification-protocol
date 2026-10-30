import importlib.util
import unittest

from pathlib import Path

SRC = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    'truth',
    SRC / 'tools/wvp_release_truth.py'
)

mod = importlib.util.module_from_spec(spec)

spec.loader.exec_module(mod)


class ReleaseTruthTests(unittest.TestCase):

    def test_wvp_semver_not_auneya_capability(self):

        releases = [
            {
                'tag_name': 'v0.5.0',
                'draft': False,
                'prerelease': False
            },
            {
                'tag_name': 'v0.4.0',
                'draft': False,
                'prerelease': False
            },
            {
                'tag_name': 'auneya-v1.4.0',
                'draft': False,
                'prerelease': True
            },
            {
                'tag_name': 'v9.0.0',
                'draft': True,
                'prerelease': False
            },
            {
                'tag_name': 'v1.0.0',
                'draft': False,
                'prerelease': True
            }
        ]

        self.assertEqual(
            mod.latest(
                releases,
                mod.WVP
            )['tag_name'],
            'v0.5.0'
        )

        self.assertEqual(
            mod.latest(
                releases,
                mod.AUNEYA
            )['tag_name'],
            'auneya-v1.4.0'
        )

    def test_semver_numeric_ordering(self):

        releases = [
            {'tag_name': 'v0.9.0'},
            {'tag_name': 'v0.10.0'},
            {'tag_name': 'v0.8.99'}
        ]

        self.assertEqual(
            mod.latest(
                releases,
                mod.WVP
            )['tag_name'],
            'v0.10.0'
        )

    def test_no_release_fail_closed(self):

        with self.assertRaises(AssertionError):
            mod.report([], SRC)

    def test_report_uses_live_release_and_package_identity(self):

        releases = [
            {
                'tag_name': 'v0.5.0',
                'html_url': (
                    'https://github.com/'
                    'nightfall-wizard/'
                    'wizard-verification-protocol/'
                    'releases/tag/v0.5.0'
                )
            }
        ]

        result = mod.report(
            releases,
            SRC
        )

        self.assertEqual(
            result['published_wvp'],
            'v0.5.0'
        )

        self.assertGreaterEqual(
            tuple(
                map(
                    int,
                    result['source_version'].split('.')
                )
            ),
            (0, 5, 0)
        )

        self.assertGreaterEqual(
            tuple(
                map(
                    int,
                    result[
                        'latest_documented_auneya_research_capability'
                    ].split('.')
                )
            ),
            (1, 4)
        )

        self.assertFalse(
            result['independent_audit_proven']
        )
