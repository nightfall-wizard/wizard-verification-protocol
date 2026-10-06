import json
import unittest
from pathlib import Path

class CommandProbeTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/COMMAND-PROBES.json"
        self.assertTrue(p.exists())

    def test_probe_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/COMMAND-PROBES.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["probe_count"], 8)

    def test_each_probe_has_required_fields(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/COMMAND-PROBES.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        for r in data["results"]:
            self.assertIn(r["status"], ["PASS", "WARN"])
            self.assertIn("id", r)
            self.assertIn("cmd", r)
            self.assertIn("class", r)

if __name__ == "__main__":
    unittest.main()
