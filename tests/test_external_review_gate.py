
import json
import unittest
from pathlib import Path

class ExternalReviewGateTests(unittest.TestCase):
    def test_external_review_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports/nightfall/v1.0.5/EXTERNAL-REVIEW.json").exists())

    def test_issue_quality_gate_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports/nightfall/v1.0.5/ISSUE-QUALITY-GATE.json").exists())

    def test_review_item_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/EXTERNAL-REVIEW.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        self.assertGreaterEqual(data["review_item_count"], 12)
        self.assertEqual(data["review_item_pass"], data["review_item_count"])

    def test_gate_rule_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/ISSUE-QUALITY-GATE.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        self.assertGreaterEqual(data["gate_rule_count"], 12)
        self.assertEqual(data["gate_rule_pass"], data["gate_rule_count"])

    def test_required_docs_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            "docs/EXTERNAL-REVIEW-PREPARATION.md",
            "docs/ISSUE-QUALITY-GATE-METHOD.md",
            "docs/EXTERNAL-REVIEW-REQUEST.md",
            "docs/REVIEW-SCOPE.md",
            "docs/REVIEWER-RESPONSE-LOG.md",
        ]
        for rel in required:
            self.assertTrue((root / rel).exists())

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/EXTERNAL-REVIEW.json"
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
