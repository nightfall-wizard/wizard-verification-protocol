import json
import unittest
from pathlib import Path

class ReleaseIntegrityTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/RELEASE-INTEGRITY.json"
        self.assertTrue(p.exists())

    def test_evidence_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/RELEASE-INTEGRITY.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["evidence_count"], 8)

    def test_hashes_exist(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/RELEASE-INTEGRITY.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertIn("hashes", data)
        self.assertGreaterEqual(len(data["hashes"]), 3)

    def test_each_result_has_required_fields(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/RELEASE-INTEGRITY.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        for r in data["results"]:
            self.assertIn(r["status"], ["PASS", "WARN"])
            self.assertIn("id", r)
            self.assertIn("cmd", r)
            self.assertIn("class", r)

if __name__ == "__main__":
    unittest.main()
