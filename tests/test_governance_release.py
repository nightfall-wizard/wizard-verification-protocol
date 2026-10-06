
import json
import unittest
from pathlib import Path

class GovernanceReleaseTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports/nightfall/v1.0.5/GOVERNANCE-RELEASE.json").exists())

    def test_control_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/GOVERNANCE-RELEASE.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        self.assertGreaterEqual(data["control_count"], 15)
        self.assertEqual(data["control_pass"], data["control_count"])

    def test_required_docs_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            "docs/GOVERNANCE.md",
            "docs/VERSIONING-POLICY.md",
            "docs/RELEASE-PROCESS.md",
            "docs/CHANGELOG-POLICY.md",
            "docs/EVIDENCE-REFRESH-CADENCE.md",
            "docs/MAINTAINER-ROLES.md",
            "CHANGELOG.md",
        ]
        for rel in required:
            self.assertTrue((root / rel).exists())

    def test_required_templates_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            "templates/governance/release-checklist.md",
            "templates/governance/versioned-release-note.md",
            "templates/governance/evidence-refresh-issue.md",
            "templates/governance/maintainer-decision-record.md",
            "templates/governance/governance-review-comment.md",
        ]
        for rel in required:
            self.assertTrue((root / rel).exists())

    def test_progress_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/GOVERNANCE-RELEASE.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        self.assertEqual(data["local_completion_percent_after_success"], 98)
        self.assertEqual(data["remaining_external_completion_percent"], 2)

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/GOVERNANCE-RELEASE.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        b = data["safety_boundary"]
        self.assertTrue(b["no_real_seed"])
        self.assertTrue(b["no_private_key"])
        self.assertTrue(b["no_wallet_file"])
        self.assertTrue(b["no_live_funds"])
        self.assertTrue(b["no_exploit_payloads"])
        self.assertTrue(b["non_audit_boundary_required"])

if __name__ == "__main__":
    unittest.main()
