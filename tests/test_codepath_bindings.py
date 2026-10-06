import json
import unittest
from pathlib import Path

class CodepathBindingTests(unittest.TestCase):
    def test_binding_report_exists_and_has_fixtures(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/CODEPATH-BINDINGS.json"
        self.assertTrue(p.exists())
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["binding_count"], 8)
        self.assertIn("bindings", data)

    def test_each_binding_has_status(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/CODEPATH-BINDINGS.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        for item in data["bindings"]:
            self.assertIn(item["status"], ["bound", "unbound"])
            self.assertIn("fixture", item)
            self.assertIn("terms", item)

if __name__ == "__main__":
    unittest.main()
