
import json
import unittest
from pathlib import Path

class CiHardeningTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports/nightfall/v1.0.5/CI-HARDENING.json").exists())

    def test_control_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/CI-HARDENING.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["control_count"], 12)
        self.assertEqual(data["control_pass"], data["control_count"])

    def test_required_workflow_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / ".github/workflows/wvp-required-checks.yml"
        self.assertTrue(p.exists())
        text = p.read_text(encoding="utf-8")
        self.assertIn("permissions:", text)
        self.assertIn("contents: read", text)
        self.assertIn("persist-credentials: false", text)
        self.assertIn("timeout-minutes:", text)
        self.assertIn("wvp/nightfall/ci_hardening.py", text)

    def test_branch_protection_template_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "templates/github/branch-protection-required-checks.json"
        self.assertTrue(p.exists())
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertIn("WVP Required Checks / required", data["required_status_checks"]["contexts"])

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/CI-HARDENING.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        b = data["safety_boundary"]
        self.assertTrue(b["no_real_seed"])
        self.assertTrue(b["no_private_key"])
        self.assertTrue(b["no_live_funds"])
        self.assertTrue(b["no_exploit_payloads"])
        self.assertTrue(b["no_write_token_required"])

if __name__ == "__main__":
    unittest.main()
