import json
import unittest
from pathlib import Path

class SemanticRegressionTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/SEMANTIC-REGRESSION.json"
        self.assertTrue(p.exists())

    def test_report_has_enough_checks(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/SEMANTIC-REGRESSION.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["semantic_checks"], 8)
        self.assertIn("results", data)

    def test_each_result_has_required_fields(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/SEMANTIC-REGRESSION.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        for r in data["results"]:
            self.assertIn(r["status"], ["PASS", "WARN"])
            self.assertIn("fixture", r)
            self.assertIn("required_terms", r)
            self.assertIn("found_terms", r)

if __name__ == "__main__":
    unittest.main()
