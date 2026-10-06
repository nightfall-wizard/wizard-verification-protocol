
import json
import unittest
from pathlib import Path

class RuntimeToyHarnessTests(unittest.TestCase):
    def test_report_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "reports/nightfall/v1.0.5/RUNTIME-TOY-HARNESS.json").exists())

    def test_toy_vector_count(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/RUNTIME-TOY-HARNESS.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        self.assertGreaterEqual(data["toy_vector_count"], 10)
        self.assertEqual(data["toy_vector_pass"], data["toy_vector_count"])
        self.assertEqual(data["toy_vector_fail"], 0)

    def test_toy_input_files_exist(self):
        root = Path(__file__).resolve().parents[1]
        toy_root = root / "toy-inputs/nightfall/v1.0.5"
        files = list(toy_root.glob("toy-*.json"))

        self.assertGreaterEqual(len(files), 10)

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "reports/nightfall/v1.0.5/RUNTIME-TOY-HARNESS.json"
        data = json.loads(p.read_text(encoding="utf-8"))

        b = data["safety_boundary"]
        self.assertTrue(b["no_real_seed"])
        self.assertTrue(b["no_private_key"])
        self.assertTrue(b["no_wallet_file"])
        self.assertTrue(b["no_live_funds"])
        self.assertTrue(b["no_live_rpc_mutation"])
        self.assertTrue(b["no_exploit_payloads"])
        self.assertTrue(b["non_audit_boundary_required"])

    def test_runtime_docs_exist(self):
        root = Path(__file__).resolve().parents[1]
        required = [
            "docs/RUNTIME-TOY-HARNESS-METHOD.md",
            "docs/TOY-INPUT-SAFETY-BOUNDARY.md",
            "docs/RUNTIME-HARNESS-LIMITATIONS.md",
        ]
        for rel in required:
            self.assertTrue((root / rel).exists())

if __name__ == "__main__":
    unittest.main()
