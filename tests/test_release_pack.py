import json
import unittest
from pathlib import Path
import hashlib

class ReleasePackTests(unittest.TestCase):
    def test_manifest_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "release-packs/nightfall/v1.0.5/BUNDLE-MANIFEST.json").exists())

    def test_archive_exists(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "release-packs/nightfall/v1.0.5/wvp-nightfall-v1.0.5-evidence-pack.tar.gz").exists())

    def test_manifest_has_files(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "release-packs/nightfall/v1.0.5/BUNDLE-MANIFEST.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertGreaterEqual(data["file_count"], 30)
        self.assertIn("files", data)

    def test_safety_boundary(self):
        root = Path(__file__).resolve().parents[1]
        p = root / "release-packs/nightfall/v1.0.5/BUNDLE-MANIFEST.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        b = data["safety_boundary"]
        self.assertTrue(b["no_real_seed"])
        self.assertTrue(b["no_private_key"])
        self.assertTrue(b["no_live_funds"])
        self.assertTrue(b["no_exploit_payloads"])

    def test_release_report_hash_matches_archive(self):
        root = Path(__file__).resolve().parents[1]
        report = json.loads((root / "reports/nightfall/v1.0.5/RELEASE-PACK.json").read_text(encoding="utf-8"))
        archive = root / report["archive"]
        h = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.assertEqual(h, report["archive_sha256"])

if __name__ == "__main__":
    unittest.main()
