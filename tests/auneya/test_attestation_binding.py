import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "tools/auneya/auneya_attestation_binding.py"

spec = importlib.util.spec_from_file_location("auneya_attestation", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CHAIN = "auneya-research-alpha-v1"
OTHER_CHAIN = "auneya-research-beta-v1"
WITNESS = "witness_android_termux_001"
OTHER_WITNESS = "witness_android_termux_002"
PAYLOAD = b"public-research-evidence-v1"


def openssl(*args):
    return subprocess.run(
        ["openssl", *map(str, args)],
        check=True,
        capture_output=True,
        timeout=15,
    )


class AttestationBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.key = self.dir / "private.pem"
        self.pub = self.dir / "public.pem"
        self.sig = self.dir / "signature.bin"
        self.msg = self.dir / "message.bin"

        openssl(
            "genpkey", "-algorithm", "ED25519",
            "-out", self.key,
        )
        openssl(
            "pkey", "-in", self.key,
            "-pubout", "-out", self.pub,
        )

        self.msg.write_bytes(
            mod.signing_message(
                CHAIN, WITNESS, mod.hash_payload(PAYLOAD)
            )
        )
        openssl(
            "pkeyutl", "-sign",
            "-inkey", self.key,
            "-rawin", "-in", self.msg,
            "-out", self.sig,
        )

    def check(self, chain=CHAIN, witness=WITNESS, payload=PAYLOAD):
        return mod.verify(
            self.pub, self.sig, chain, witness, payload
        )

    def test_valid_attestation(self):
        self.assertTrue(self.check())

    def test_modified_payload_rejected(self):
        self.assertFalse(self.check(payload=b"altered"))

    def test_cross_chain_replay_rejected(self):
        self.assertFalse(self.check(chain=OTHER_CHAIN))

    def test_wrong_witness_context_rejected(self):
        self.assertFalse(self.check(witness=OTHER_WITNESS))

    def test_tampered_signature_rejected(self):
        data = bytearray(self.sig.read_bytes())
        data[0] ^= 1
        self.sig.write_bytes(data)
        self.assertFalse(self.check())

    def test_wrong_public_key_rejected(self):
        other = self.dir / "other.pem"
        openssl(
            "genpkey", "-algorithm", "ED25519",
            "-out", other,
        )
        openssl(
            "pkey", "-in", other,
            "-pubout", "-out", self.pub,
        )
        self.assertFalse(self.check())

    def test_malformed_signature_rejected(self):
        self.sig.write_bytes(b"invalid")
        self.assertFalse(self.check())

    def test_symlink_signature_rejected(self):
        target = self.dir / "original.sig"
        target.write_bytes(self.sig.read_bytes())
        self.sig.unlink()
        self.sig.symlink_to(target)
        self.assertFalse(self.check())

    def test_missing_signature_rejected(self):
        self.sig.unlink()
        self.assertFalse(self.check())

    def test_missing_chain_rejected(self):
        with self.assertRaises(mod.AttestationError):
            self.check(chain="")

    def test_invalid_payload_hash_rejected(self):
        with self.assertRaises(mod.AttestationError):
            mod.signing_message(CHAIN, WITNESS, "sha256:bad")

    def test_domain_is_deterministic(self):
        first = mod.signing_message(
            CHAIN, WITNESS, mod.hash_payload(PAYLOAD)
        )
        second = mod.signing_message(
            CHAIN, WITNESS, mod.hash_payload(PAYLOAD)
        )
        self.assertEqual(first, second)
        self.assertTrue(first.startswith(mod.DOMAIN))

    def test_context_has_unambiguous_encoding(self):
        first = mod.signing_message(
            CHAIN, WITNESS, mod.hash_payload(PAYLOAD)
        )
        second = mod.signing_message(
            OTHER_CHAIN, WITNESS, mod.hash_payload(PAYLOAD)
        )
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
