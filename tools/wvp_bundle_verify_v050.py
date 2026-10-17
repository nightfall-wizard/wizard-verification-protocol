#!/usr/bin/env python3
"""WVP 0.5: bind one flat release payload to its digest and detached signature.

Read-only verification. No claim about source-to-binary reproduction or software safety.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,199}\Z", re.ASCII)
SHA_LINE = re.compile(r"([a-fA-F0-9]{64}) [ *]([A-Za-z0-9][A-Za-z0-9._+-]{0,199})\Z", re.ASCII)
MAX_PAYLOAD = 2 * 1024 * 1024 * 1024


class VerificationFailure(ValueError):
    pass


def regular_reader(path: Path, maximum: int):
    """Reject links/devices and identify the same inode before and after open."""
    if not hasattr(os, "O_NOFOLLOW"):
        raise VerificationFailure("O_NOFOLLOW unavailable: refusing unchecked input")
    flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise VerificationFailure("non-regular input: " + path.name)
        fd = os.open(path, flags)
        after = os.fstat(fd)
        if not stat.S_ISREG(after.st_mode) or (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
            os.close(fd)
            raise VerificationFailure("input replaced during open: " + path.name)
        if after.st_size > maximum:
            os.close(fd)
            raise VerificationFailure("input exceeds size limit: " + path.name)
        return os.fdopen(fd, "rb")
    except OSError as exc:
        raise VerificationFailure(f"cannot securely open {path.name}: {exc}") from exc


def small_file(path: Path, limit: int) -> bytes:
    with regular_reader(path, limit) as stream:
        data = stream.read(limit + 1)
    if not data or len(data) > limit:
        raise VerificationFailure("missing, empty, or oversized: " + path.name)
    return data


def verify_bundle(directory: Path, public_key: Path):
    if directory.is_symlink() or not directory.is_dir():
        raise VerificationFailure("bundle must be a real directory")
    entries = list(directory.iterdir())
    if not entries:
        raise VerificationFailure("empty bundle")
    names = set()
    for path in entries:
        if not NAME.fullmatch(path.name) or '..' in path.name:
            raise VerificationFailure("unsafe asset name")
        if not stat.S_ISREG(path.lstat().st_mode):
            raise VerificationFailure("non-regular release entry: " + path.name)
        if path.name in names:
            raise VerificationFailure("duplicate name")
        names.add(path.name)
    checksum_names = [n for n in names if n.endswith(".sha256")]
    signature_names = [n for n in names if n.endswith(".sig")]
    payloads = sorted(names - set(checksum_names) - set(signature_names))
    if len(checksum_names) != 1 or len(signature_names) != 1 or len(payloads) != 1:
        raise VerificationFailure("expected exactly one payload, one .sha256 and one .sig")
    payload = payloads[0]
    if checksum_names[0] != payload + ".sha256" or signature_names[0] != payload + ".sig":
        raise VerificationFailure("checksum/signature filenames do not bind to payload")
    manifest = small_file(directory / checksum_names[0], 1024 * 1024)
    try:
        lines = manifest.decode("ascii").splitlines()
    except UnicodeError as exc:
        raise VerificationFailure("non-ASCII checksum manifest") from exc
    if len(lines) != 1:
        raise VerificationFailure("checksum manifest must cover exactly one payload")
    match = SHA_LINE.fullmatch(lines[0])
    if not match or match.group(2) != payload:
        raise VerificationFailure("checksum manifest does not name exact payload")
    expected = match.group(1).lower()
    signature = small_file(directory / signature_names[0], 16 * 1024)
    key = small_file(public_key, 64 * 1024)
    if b"-----BEGIN PUBLIC KEY-----" not in key:
        raise VerificationFailure("expected explicitly trusted PEM public key")
    digest = hashlib.sha256()
    count = 0
    with tempfile.TemporaryDirectory(prefix="wvp-v050-") as temp:
        snapshot = Path(temp) / "payload"
        with regular_reader(directory / payload, MAX_PAYLOAD) as inp, snapshot.open("xb") as out:
            while True:
                block = inp.read(1024 * 1024)
                if not block:
                    break
                count += len(block)
                if count > MAX_PAYLOAD:
                    raise VerificationFailure("payload exceeds size limit")
                out.write(block)
                digest.update(block)
        if digest.hexdigest() != expected:
            raise VerificationFailure("SHA256 mismatch")
        sig_path = Path(temp) / "signature"
        key_path = Path(temp) / "trusted-public-key.pem"
        sig_path.write_bytes(signature)
        key_path.write_bytes(key)
        try:
            result = subprocess.run(
                ["openssl", "dgst", "-sha256", "-verify", str(key_path),
                 "-signature", str(sig_path), str(snapshot)],
                capture_output=True, text=True, timeout=30, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise VerificationFailure(f"signature verifier unavailable: {exc}") from exc
        if result.returncode != 0 or result.stdout.strip() != "Verified OK":
            raise VerificationFailure("detached RSA SHA256 signature verification failed")
    return {
        "schema_version": 1, "checker": "wvp-bundle-verify", "version": "0.5.0",
        "status": "PASS", "asset": payload, "bytes": count,
        "sha256": expected, "signed_asset_and_checksum_bound": True,
        "signature_verified": True, "audit_proven": False,
        "source_to_release_proven": False, "reproducible_build_proven": False,
        "binary_safety_proven": False,
    }


def main():
    parser = argparse.ArgumentParser(description="WVP v0.5 offline single-asset integrity binding")
    parser.add_argument("--bundle", type=Path, required=True, help="flat directory with payload, payload.sha256 and payload.sig")
    parser.add_argument("--public-key", type=Path, required=True, help="trusted external RSA public key")
    args = parser.parse_args()
    try:
        result = verify_bundle(args.bundle, args.public_key)
    except VerificationFailure as exc:
        print(json.dumps({"version": "0.5.0", "status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
