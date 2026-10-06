import json
import unittest
from pathlib import Path

class ConformanceScoreTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/CONFORMANCE-SCORE.json"
        self.assertTrue(p.exists())

    def test_public_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/PUBLIC-REPORT.md"
        self.assertTrue(p.exists())

    def test_score_threshold(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/CONFORMANCE-SCORE.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["score_percent"], 80)

    def test_non_audit_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/CONFORMANCE-SCORE.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertTrue(data["non_audit_boundary"])
        self.assertTrue(data["public_report_sanitized"])

    def test_requirements_exist(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/CONFORMANCE-SCORE.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["requirements"]), 10)
        for item in data["requirements"]:
            self.assertIn(item["status"], ["PASS", "WARN", "FAIL"])

if __name__ == "__main__":
    unittest.main()
