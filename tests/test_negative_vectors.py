import json
import unittest
from pathlib import Path

class NegativeVectorTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/NEGATIVE-VECTORS.json"
        self.assertTrue(p.exists())

    def test_vector_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/NEGATIVE-VECTORS.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["vector_count"], 10)

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/NEGATIVE-VECTORS.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        boundary = data["safety_boundary"]
        self.assertTrue(boundary["no_real_seed"])
        self.assertTrue(boundary["no_private_key"])
        self.assertTrue(boundary["no_live_funds"])
        self.assertTrue(boundary["no_undisclosed_exploit_detail"])

    def test_vector_files_are_safe(self):
        root = Path(__file__).resolve().parents[1]
        d = root / "negative-vectors/nightfall/v1.0.5"
        files = list(d.glob("*.json"))
        self.assertGreaterEqual(len(files), 10)
        for f in files:
            item = json.loads(f.read_text(encoding="utf-8"))
            self.assertFalse(item["contains_secret"])
            self.assertFalse(item["contains_live_funds"])
            self.assertEqual(item["payload"]["kind"], "non_executable_placeholder")

if __name__ == "__main__":
    unittest.main()
