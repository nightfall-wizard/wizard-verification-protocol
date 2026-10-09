import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools/auneya"
sys.path.insert(0, str(TOOLS))

from auneya_attestation_binding import signing_message
from auneya_witness_proof_integration import (
    payload_hash,
    verify_proof,
    unsigned_payload,
)

FIXTURE = (
    ROOT / "fixtures/auneya/witness-proofs/"
    "valid-download-integrity-prooflet.json"
)

CHAIN = "auneya-research-alpha-v1"
OTHER_CHAIN = "auneya-research-beta-v1"


def openssl(*args):
    subprocess.run(
        ["openssl", *map(str, args)],
        check=True,
        capture_output=True,
        timeout=15,
    )


class WitnessProofIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

        self.private = self.directory / "private.pem"
        self.public = self.directory / "public.pem"
        self.signature = self.directory / "signature.bin"
        self.message = self.directory / "message.bin"

        openssl(
            "genpkey", "-algorithm", "ED25519",
            "-out", self.private,
        )
        openssl(
            "pkey", "-in", self.private,
            "-pubout", "-out", self.public,
        )

        self.proof = json.loads(FIXTURE.read_text())
        self.proof["integrity"] = {
            "proof_hash": "",
            "signature_status": "signed",
            "signature_algorithm": "ed25519",
        }

        self.proof["integrity"]["proof_hash"] = payload_hash(
            self.proof
        )

        self.witness = self.proof["witness"]["witness_id"]

        self.message.write_bytes(
            signing_message(
                CHAIN,
                self.witness,
                payload_hash(self.proof),
            )
        )

        openssl(
            "pkeyutl", "-sign",
            "-inkey", self.private,
            "-rawin", "-in", self.message,
            "-out", self.signature,
        )

    def check(self, proof=None, chain=CHAIN, witness=None):
        return verify_proof(
            self.proof if proof is None else proof,
            chain,
            self.witness if witness is None else witness,
            self.public,
            self.signature,
        )


    def test_signed_schema_invalid_extra_field_rejected(self):
        proof = copy.deepcopy(self.proof)
        proof["unexpected_security_field"] = "not_in_schema"
        proof["integrity"]["proof_hash"] = payload_hash(proof)

        self.message.write_bytes(
            signing_message(
                CHAIN,
                self.witness,
                payload_hash(proof),
            )
        )

        openssl(
            "pkeyutl", "-sign",
            "-inkey", self.private,
            "-rawin", "-in", self.message,
            "-out", self.signature,
        )

        self.assertFalse(
            self.check(proof),
            "Schema-invalid signed proof must be rejected",
        )


    def test_unknown_schema_keyword_rejected(self):
        from unittest.mock import patch

        schema_path = (
            ROOT / "schemas/"
            "auneya-witness-proof-v0.1.schema.json"
        )

        schema = json.loads(schema_path.read_text())
        schema["properties"]["proof_id"]["not"] = {
            "type": "string"
        }

        original_read_text = Path.read_text

        def patched_read_text(path, *args, **kwargs):
            if path.resolve() == schema_path.resolve():
                return json.dumps(schema)
            return original_read_text(
                path, *args, **kwargs
            )

        with patch.object(
            Path, "read_text", patched_read_text
        ):
            self.assertFalse(
                self.check(),
                "Unsupported schema keyword must fail closed",
            )


    def test_schema_drift_rejected(self):
        from unittest.mock import patch

        schema_path = (
            ROOT / "schemas/"
            "auneya-witness-proof-v0.1.schema.json"
        )
        original = json.loads(schema_path.read_text())
        original_read = Path.read_text

        cases = {
            "minimum_on_string": lambda s:
                s["properties"]["proof_id"].update(
                    {"minimum": 999999}
                ),
            "properties_on_string": lambda s:
                s["properties"]["proof_id"].update(
                    {"properties": {
                        "forbidden": {"type": "boolean"}
                    }}
                ),
            "required_on_string": lambda s:
                s["properties"]["proof_id"].update(
                    {"required": ["forbidden"]}
                ),
            "unknown_keyword": lambda s:
                s["properties"]["non_value_notice"].update(
                    {"not": {"type": "string"}}
                ),
            "unsupported_format": lambda s:
                s["properties"]["created_at"].update(
                    {"format": "email"}
                ),
            "missing_array_items": lambda s:
                s["properties"]["evidence"].pop("items"),
            "open_object": lambda s:
                s["properties"]["witness"].update(
                    {"additionalProperties": True}
                ),
            "invalid_required": lambda s:
                s["properties"]["witness"].update(
                    {"required": ["nonexistent"]}
                ),
            "negative_minimum": lambda s:
                s["properties"]["timing"]["properties"][
                    "duration_ms"
                ].update({"minimum": -1}),
            "invalid_pattern": lambda s:
                s["properties"]["proof_id"].update(
                    {"pattern": "["}
                ),
        }

        for name, mutate in cases.items():
            with self.subTest(case=name):
                schema = copy.deepcopy(original)
                mutate(schema)

                def patched_read(path, *args, **kwargs):
                    if path.resolve() == schema_path.resolve():
                        return json.dumps(schema)
                    return original_read(
                        path, *args, **kwargs
                    )

                with patch.object(
                    Path, "read_text", patched_read
                ):
                    self.assertFalse(
                        self.check(),
                        f"Schema drift accepted: {name}",
                    )

    def test_valid_proof(self):
        self.assertTrue(self.check())

    def test_modified_claim_hash(self):
        proof = copy.deepcopy(self.proof)
        proof["claim_hash"] = "sha256:" + "a" * 64
        self.assertFalse(self.check(proof))

    def test_modified_evidence(self):
        proof = copy.deepcopy(self.proof)
        proof["evidence"][0]["evidence_hash"] = (
            "sha256:" + "b" * 64
        )
        self.assertFalse(self.check(proof))

    def test_modified_status(self):
        proof = copy.deepcopy(self.proof)
        proof["observed_status"] = "false"
        self.assertFalse(self.check(proof))

    def test_cross_chain_replay(self):
        self.assertFalse(self.check(chain=OTHER_CHAIN))

    def test_wrong_witness(self):
        self.assertFalse(
            self.check(witness="witness_android_termux_002")
        )

    def test_modified_signature(self):
        raw = bytearray(self.signature.read_bytes())
        raw[0] ^= 1
        self.signature.write_bytes(raw)
        self.assertFalse(self.check())

    def test_missing_signature(self):
        self.signature.unlink()
        self.assertFalse(self.check())

    def test_wrong_proof_hash(self):
        proof = copy.deepcopy(self.proof)
        proof["integrity"]["proof_hash"] = (
            "sha256:" + "0" * 64
        )
        self.assertFalse(self.check(proof))

    def test_unsigned_proof_rejected(self):
        proof = copy.deepcopy(self.proof)
        proof["integrity"]["signature_status"] = (
            "unsigned_research_fixture"
        )
        self.assertFalse(self.check(proof))

    def test_wrong_algorithm(self):
        proof = copy.deepcopy(self.proof)
        proof["integrity"]["signature_algorithm"] = "rsa"
        self.assertFalse(self.check(proof))

    def test_inline_signature_rejected(self):
        proof = copy.deepcopy(self.proof)
        proof["integrity"]["signature"] = "untrusted"
        self.assertFalse(self.check(proof))

    def test_missing_integrity(self):
        proof = copy.deepcopy(self.proof)
        del proof["integrity"]
        self.assertFalse(self.check(proof))

    def test_canonical_payload_deterministic(self):
        proof = copy.deepcopy(self.proof)
        reordered = dict(reversed(list(proof.items())))
        self.assertEqual(
            unsigned_payload(proof),
            unsigned_payload(reordered),
        )


if __name__ == "__main__":
    unittest.main()
