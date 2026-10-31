"""
Local deterministic documentation regression tests.
"""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    'readme_truth',
    ROOT / 'tools/readme_truth.py'
)

mod = importlib.util.module_from_spec(spec)

spec.loader.exec_module(mod)


class ReadmeRealityTests(unittest.TestCase):

    def test_generator_matches_tracked_readme(self):

        self.assertEqual(
            mod.render(ROOT),
            (ROOT / 'README.md').read_text(
                encoding='utf-8'
            )
        )

    def test_reproduction_is_deterministic(self):

        self.assertEqual(
            mod.render(ROOT),
            mod.render(ROOT)
        )

    def test_no_network_claim_or_economic_promotion(self):

        doc = mod.render(ROOT)

        for phrase in (
            'public P2P networking',
            'mainnet readiness',
            'HISTORICAL SNAPSHOT ONLY',
            'releases/latest',
            'Gate 3',
            'AUNEYA technical whitepaper'
        ):

            self.assertIn(
                phrase,
                doc
            )


    def test_v110_research_identity_and_security_boundary(self):

        doc = mod.render(ROOT)

        self.assertIn(
            '| v1.10 | Offline independent high-water keeper research |',
            doc
        )

        self.assertIn(
            'not a published v1.10 release',
            doc
        )

        self.assertIn(
            'no independently proven remote retention',
            doc
        )

        self.assertIn(
            'independent physical-device trials',
            doc
        )

    def test_missing_source_is_rejected(self):

        bad = mod.MILESTONES + (
            (
                '2.0',
                'fictional',
                'missing.py',
                'missing.md',
                'missing.py'
            ),
        )

        with patch.object(
            mod,
            'MILESTONES',
            bad
        ):

            with self.assertRaisesRegex(
                ValueError,
                'Missing evidence'
            ):

                mod.render(ROOT)

    def test_published_source_cannot_exceed_local_version(self):

        with patch.object(
            mod,
            'manifest_version',
            return_value='0.0.1'
        ):

            with self.assertRaisesRegex(
                ValueError,
                'newer than local source'
            ):

                mod.evidence(ROOT)


if __name__ == '__main__':
    unittest.main()
