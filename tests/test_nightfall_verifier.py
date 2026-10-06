import subprocess
import tempfile
import unittest
from pathlib import Path

class TestVerifier(unittest.TestCase):
    def test_runs(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            nf = Path(d) / "nightfall"
            (nf / "docs").mkdir(parents=True)
            (nf / ".github/workflows").mkdir(parents=True)
            spec = "UTXO kernel_excess minted burned "
            spec += "coinbase maturity 1440"
            (nf / "docs/SPEC.md").write_text(spec)
            (nf / "SECURITY.md").write_text("not independent")
            (nf / ".github/workflows/ci.yml").write_text("name: ci")
            cmd = [
                "python3",
                str(root / "wvp/nightfall/verifier.py"),
                "--repo",
                str(nf),
            ]
            res = subprocess.run(
                cmd,
                cwd=root,
                text=True,
                stdout=subprocess.PIPE,
            )
            self.assertEqual(res.returncode, 0)
            self.assertIn("Verdict:", res.stdout)

if __name__ == "__main__":
    unittest.main()
