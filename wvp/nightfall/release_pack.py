
#!/usr/bin/env python3
from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "release-packs/nightfall/v1.0.5"
MANIFEST = PACK / "BUNDLE-MANIFEST.json"
ARCHIVE = PACK / "wvp-nightfall-v1.0.5-evidence-pack.tar.gz"
SHA256SUMS = PACK / "SHA256SUMS.txt"
REPORT = ROOT / "reports/nightfall/v1.0.5/RELEASE-PACK.json"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("WVP Release Pack Check")

    required = [MANIFEST, ARCHIVE, SHA256SUMS, REPORT]
    for p in required:
        if not p.exists():
            print("FAIL: missing", p.relative_to(ROOT))
            return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    files = manifest.get("files", [])
    boundary = manifest.get("safety_boundary", {})

    print("Manifest files:", len(files))
    print("Archive:", ARCHIVE.relative_to(ROOT))

    if len(files) < 30:
        print("FAIL: release pack has too few files")
        return 1

    required_boundary = [
        "no_real_seed",
        "no_private_key",
        "no_live_funds",
        "no_exploit_payloads",
        "sanitized_public_report_included",
        "non_audit_boundary_required",
    ]

    for key in required_boundary:
        if boundary.get(key) is not True:
            print("FAIL: missing safety boundary:", key)
            return 1

    for item in files:
        p = ROOT / item["path"]
        if not p.exists():
            print("FAIL: manifest file missing:", item["path"])
            return 1
        if sha256_file(p) != item["sha256"]:
            print("FAIL: manifest hash mismatch:", item["path"])
            return 1

    actual_archive_sha = sha256_file(ARCHIVE)
    if actual_archive_sha != report.get("archive_sha256"):
        print("FAIL: archive hash mismatch against report")
        return 1

    sums = SHA256SUMS.read_text(encoding="utf-8", errors="replace")
    if actual_archive_sha not in sums:
        print("FAIL: checksum file does not include archive hash")
        return 1

    print("PASS: release pack builder and manifest complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
