"""Offline cryptographic cross-evidence regression tests for WVP v0.5."""
import hashlib
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "tools" / "wvp_bundle_verify_v050.py"
spec = importlib.util.spec_from_file_location("wvp_bundle_v050", SRC)
wvp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wvp)


def openssl(*args):
    subprocess.run(["openssl", *map(str, args)], check=True, capture_output=True)


class BundleBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = Path(tempfile.mkdtemp(prefix="wvp050keys-"))
        cls.private = cls.keys / "private.pem"
        cls.public = cls.keys / "public.pem"
        cls.other_private = cls.keys / "other-private.pem"
        cls.other_public = cls.keys / "other-public.pem"
        for private, public in [(cls.private, cls.public), (cls.other_private, cls.other_public)]:
            openssl("genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", private)
            openssl("pkey", "-in", private, "-pubout", "-out", public)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.keys)

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="wvp050fixture-"))
        self.asset = self.root / "archive.tar.gz"
        self.asset.write_bytes(b"WVP content\n")
        self.manifest = self.root / (self.asset.name + ".sha256")
        self.sig = self.root / (self.asset.name + ".sig")
        self.rebuild()

    def tearDown(self):
        shutil.rmtree(self.root)

    def rebuild(self):
        sha = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        self.manifest.write_text(sha + "  " + self.asset.name + "\n")
        openssl("dgst", "-sha256", "-sign", self.private, "-out", self.sig, self.asset)

    def denied(self):
        with self.assertRaises(wvp.VerificationFailure):
            wvp.verify_bundle(self.root, self.public)

    def test_valid_packet(self):
        r = wvp.verify_bundle(self.root, self.public)
        self.assertEqual(r["status"], "PASS")
        self.assertTrue(r["signature_verified"])
        self.assertFalse(r["source_to_release_proven"])

    def test_tampered_binary(self):
        self.asset.write_bytes(b"evil")
        self.denied()

    def test_tampered_checksum(self):
        self.manifest.write_text("0" * 64 + "  archive.tar.gz\n")
        self.denied()

    def test_tampered_signature(self):
        buf = bytearray(self.sig.read_bytes())
        buf[0] ^= 1
        self.sig.write_bytes(buf)
        self.denied()

    def test_wrong_trust_key(self):
        with self.assertRaises(wvp.VerificationFailure):
            wvp.verify_bundle(self.root, self.other_public)

    def test_signature_for_different_bytes(self):
        openssl("dgst", "-sha256", "-sign", self.private, "-out", self.sig, self.manifest)
        self.denied()

    def test_checksum_references_other_asset(self):
        sha = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        self.manifest.write_text(sha + "  other.tar.gz\n")
        self.denied()

    def test_manifest_with_two_records(self):
        self.manifest.write_text(self.manifest.read_text() * 2)
        self.denied()

    def test_extra_unsigned_asset(self):
        (self.root / "unsigned.bin").write_bytes(b"something")
        self.denied()

    def test_extra_checksum(self):
        (self.root / "other.sha256").write_text("garbage")
        self.denied()

    def test_extra_signature(self):
        (self.root / "other.sig").write_bytes(b"garbage")
        self.denied()

    def test_missing_signature(self):
        self.sig.unlink()
        self.denied()

    def test_missing_checksum(self):
        self.manifest.unlink()
        self.denied()

    def test_symlink_asset(self):
        copy = self.root.parent / (self.root.name + "-original")
        self.asset.rename(copy)
        try:
            self.asset.symlink_to(copy)
            self.denied()
        finally:
            copy.unlink()

    def test_symlink_public_key(self):
        link = self.root.parent / (self.root.name + "-public-link")
        link.symlink_to(self.public)
        try:
            with self.assertRaises(wvp.VerificationFailure):
                wvp.verify_bundle(self.root, link)
        finally:
            link.unlink()

    def test_asset_filename_mismatch(self):
        self.sig.rename(self.root / "unexpected.sig")
        self.denied()


if __name__ == "__main__":
    unittest.main()
