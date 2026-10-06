
import json
import unittest
from pathlib import Path

class HandoffReadinessTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports/nightfall/v1.0.5/MAINTAINER-HANDOFF.json").exists())

    def test_merge_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports/nightfall/v1.0.5/MERGE-READINESS.json").exists())

    def test_readiness_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/MAINTAINER-HANDOFF.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["readiness_count"], 10)
        self.assertEqual(data["readiness_pass"], data["readiness_count"])

    def test_required_docs_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            "docs/MAINTAINER-HANDOFF.md",
            "docs/MERGE-READINESS-CHECKLIST.md",
            "docs/FINAL-ROADMAP.md",
            "docs/POST-MERGE-OPERATIONS.md",
            "docs/REVIEWER-GUIDE.md",
        ]
        for rel in required:
            self.assertTrue((root / rel).exists())

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/MAINTAINER-HANDOFF.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        b = data["safety_boundary"]
        self.assertTrue(b["no_real_seed"])
        self.assertTrue(b["no_private_key"])
        self.assertTrue(b["no_live_funds"])
        self.assertTrue(b["no_exploit_payloads"])
        self.assertTrue(b["non_audit_boundary_required"])

if __name__ == "__main__":
    unittest.main()
