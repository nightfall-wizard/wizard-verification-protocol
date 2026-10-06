import json
import unittest
from pathlib import Path

class SupplyInvariantTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/SUPPLY-INVARIANT-MAP.json"
        self.assertTrue(p.exists())

    def test_claim_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/SUPPLY-INVARIANT-MAP.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["claim_count"], 8)

    def test_probe_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/SUPPLY-INVARIANT-MAP.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["probe_count"], 5)

    def test_each_claim_has_required_fields(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/SUPPLY-INVARIANT-MAP.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        for c in data["claims"]:
            self.assertIn(c["status"], ["PASS", "WARN"])
            self.assertIn("id", c)
            self.assertIn("must", c)
            self.assertIn("hits", c)

if __name__ == "__main__":
    unittest.main()
