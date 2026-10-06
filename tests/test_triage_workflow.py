import json
import unittest
from pathlib import Path

class TriageWorkflowTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/FINDINGS-TRIAGE.json"
        self.assertTrue(p.exists())

    def test_class_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/FINDINGS-TRIAGE.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["class_count"], 9)

    def test_severity_policy(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/FINDINGS-TRIAGE.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        severities = data["severity_levels"]
        high = [s for s in severities if s["level"] in ["HIGH", "CRITICAL"]]
        self.assertTrue(high)
        for item in high:
            self.assertTrue(item["private_default"])

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/FINDINGS-TRIAGE.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        b = data["safety_boundary"]
        self.assertTrue(b["no_real_seed"])
        self.assertTrue(b["no_private_key"])
        self.assertTrue(b["no_live_funds"])
        self.assertTrue(b["no_exploit_payloads"])
        self.assertTrue(b["no_public_zero_day_details"])

    def test_templates_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            "templates/security/finding-record.json",
            "templates/security/sanitized-finding.md",
            "templates/security/private-disclosure-checklist.md",
        ]
        for rel in required:
            self.assertTrue((root / rel).exists())

if __name__ == "__main__":
    unittest.main()
