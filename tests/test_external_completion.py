
import json
import unittest
from pathlib import Path

class ExternalCompletionTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports/nightfall/v1.0.5/EXTERNAL-COMPLETION.json").exists())

    def test_control_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/EXTERNAL-COMPLETION.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        self.assertGreaterEqual(data["control_count"], 14)
        self.assertEqual(data["control_pass"], data["control_count"])

    def test_required_docs_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            "docs/EXTERNAL-COMPLETION-CHECKLIST.md",
            "docs/PR-MERGE-WORKFLOW.md",
            "docs/BRANCH-PROTECTION-VERIFICATION.md",
            "docs/CI-HISTORY-VERIFICATION.md",
            "docs/INDEPENDENT-REVIEW-TRACKER.md",
            "docs/FINAL-COMPLETION-BOUNDARY.md",
        ]
        for rel in required:
            self.assertTrue((root / rel).exists())

    def test_required_templates_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            "templates/external/final-completion-record.md",
            "templates/external/pr-merge-record.md",
            "templates/external/branch-protection-record.md",
            "templates/external/ci-run-record.md",
            "templates/external/external-review-record.md",
        ]
        for rel in required:
            self.assertTrue((root / rel).exists())

    def test_progress_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/EXTERNAL-COMPLETION.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        self.assertEqual(data["local_completion_percent_after_success"], 99)
        self.assertEqual(data["remaining_external_completion_percent"], 1)
        self.assertFalse(data["termux_can_set_true_100_percent"])

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/EXTERNAL-COMPLETION.json"
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
