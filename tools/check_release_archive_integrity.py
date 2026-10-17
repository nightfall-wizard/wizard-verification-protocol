#!/usr/bin/env python3
"""Read-only verification of a historical release archive."""
import hashlib
import json
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "release-packs/nightfall/v1.0.5"
MANIFEST = PACK / "BUNDLE-MANIFEST.json"
ARCHIVE = PACK / "wvp-nightfall-v1.0.5-evidence-pack.tar.gz"
REPORT = ROOT / "reports/nightfall/v1.0.5/RELEASE-PACK.json"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify(manifest_path=MANIFEST, archive_path=ARCHIVE,
           report_path=REPORT):
    errors = []

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = json.loads(report_path.read_text(encoding="utf-8"))

    expected = {}
    for entry in manifest["files"]:
        name = entry["path"]
        if name in expected:
            errors.append(f"duplicate manifest entry: {name}")
        expected[name] = entry["sha256"]

    archive_bytes = archive_path.read_bytes()
    actual_archive_hash = sha256(archive_bytes)

    if actual_archive_hash != report.get("archive_sha256"):
        errors.append("archive SHA-256 differs from release report")

    with tarfile.open(archive_path, "r:gz") as archive:
        members = {}

        for member in archive.getmembers():
            name = member.name

            if not member.isfile():
                errors.append(f"non-regular archive member: {name}")
                continue

            if name in members:
                errors.append(f"duplicate archive member: {name}")
                continue

            members[name] = member

        for name, expected_hash in expected.items():
            member = members.get(name)

            if member is None:
                errors.append(f"missing archive member: {name}")
                continue

            stream = archive.extractfile(member)
            if stream is None:
                errors.append(f"unreadable archive member: {name}")
                continue

            digest = hashlib.sha256()
            for chunk in iter(lambda: stream.read(65536), b""):
                digest.update(chunk)

            if digest.hexdigest() != expected_hash:
                errors.append(f"archive/manifest hash mismatch: {name}")

        for name in sorted(set(members) - set(expected)):
            errors.append(f"unexpected archive member: {name}")

    return errors


def main():
    try:
        errors = verify()
    except (OSError, ValueError, KeyError, tarfile.TarError) as exc:
        print(f"FAIL: verification error: {exc}")
        return 1

    if errors:
        print(f"FAIL: {len(errors)} integrity problem(s)")
        for error in errors:
            print(f" - {error}")
        return 1

    print("PASS: every archive member matches the manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
