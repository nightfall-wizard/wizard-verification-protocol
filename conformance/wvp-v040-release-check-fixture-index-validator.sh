#!/usr/bin/env bash
set -euo pipefail

INDEX="${1:-fixtures/release-check/FIXTURE-INDEX.json}"

echo "=== WVP v0.4 RELEASE-CHECK FIXTURE INDEX VALIDATOR ==="
echo "Index: $INDEX"

test -s "$INDEX"

python3 - "$INDEX" <<'PY2'
import json
import sys
from pathlib import Path

index_path = Path(sys.argv[1])
data = json.loads(index_path.read_text(encoding="utf-8"))

if not isinstance(data, dict):
    raise SystemExit("FAIL: index root must be object.")

fixtures = data.get("fixtures")
if not isinstance(fixtures, list):
    raise SystemExit("FAIL: index.fixtures must be list.")

required = {"FRC-003", "FRC-004", "FRC-005", "FRC-006", "FRC-007"}
seen = set()
implemented = set()

for row in fixtures:
    if not isinstance(row, dict):
        raise SystemExit("FAIL: fixture row must be object.")

    fixture_id = row.get("id")
    status = row.get("status")
    path_value = row.get("path")

    if not isinstance(fixture_id, str) or not fixture_id.startswith("FRC-"):
        raise SystemExit("FAIL: invalid fixture id.")

    if fixture_id in seen:
        raise SystemExit(f"FAIL: duplicate fixture id: {fixture_id}")
    seen.add(fixture_id)

    if status not in {"planned", "implemented", "reserved"}:
        raise SystemExit(f"FAIL: invalid status for {fixture_id}")

    if status == "implemented":
        implemented.add(fixture_id)

        if not isinstance(path_value, str) or not path_value:
            raise SystemExit(f"FAIL: implemented fixture missing path: {fixture_id}")

        if ".." in path_value or path_value.startswith("/"):
            raise SystemExit(f"FAIL: unsafe fixture path: {fixture_id}")

        if not path_value.startswith("fixtures/release-check/"):
            raise SystemExit(f"FAIL: fixture path outside release-check tree: {fixture_id}")

        base = Path(path_value)
        for name in ["input.json", "expected.json", "README.md"]:
            candidate = base / name
            if not candidate.is_file():
                raise SystemExit(f"FAIL: {fixture_id} missing {name}")

        json.loads((base / "input.json").read_text(encoding="utf-8"))
        json.loads((base / "expected.json").read_text(encoding="utf-8"))

missing = sorted(required - implemented)
if missing:
    raise SystemExit("FAIL: required implemented fixtures missing: " + ", ".join(missing))

print("RESULT: PASS")
print(f"fixtures_total={len(fixtures)}")
print(f"implemented_required={','.join(sorted(required))}")
PY2
