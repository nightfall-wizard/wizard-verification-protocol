#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / ".tmp/auneya-local-simulation-evidence-pack-v0.1"

CHECKS = [
    ("claim_schema", "conformance/auneya-claim-schema-v0.1.sh"),
    ("witness_proof_schema", "conformance/auneya-witness-proof-schema-v0.1.sh"),
    ("event_schema", "conformance/auneya-event-schema-v0.1.sh"),
    ("pulse_flow", "conformance/auneya-pulse-flow-v0.1.sh"),
    ("local_witness_runner", "conformance/auneya-local-witness-runner-v0.1.sh"),
    ("local_witness_display", "conformance/auneya-local-witness-display-v0.1.sh"),
    ("one_command_local_demo", "conformance/auneya-one-command-local-demo-v0.1.sh"),
    ("local_claim_selection", "conformance/auneya-local-claim-selection-v0.1.sh"),
    ("local_collection_ledger", "conformance/auneya-local-collection-ledger-simulation-v0.1.sh"),
    ("local_collection_status", "conformance/auneya-local-collection-status-display-v0.1.sh"),
    ("local_collect_command", "conformance/auneya-local-collect-command-v0.1.sh"),
    ("minimal_fair_genesis_launch_path", "conformance/auneya-minimal-fair-genesis-launch-path-v0.1.sh"),
]

def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))

def run(check_id, cmd, expect_zero=True, env=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=e, timeout=240)
        ok = (p.returncode == 0) if expect_zero else (p.returncode != 0)
        out = p.stdout[-2500:]
        code = p.returncode
    except subprocess.TimeoutExpired as ex:
        ok = False
        out = str(ex.stdout or "")[-2500:] + "\nTIMEOUT"
        code = 124
    return {"id": check_id, "status": "pass" if ok else "fail", "exit_code": code, "command": " ".join(cmd), "output_tail": out}

def existing_conformance():
    out = []
    for cid, script in CHECKS:
        if (ROOT / script).exists():
            out.append(run(cid, ["bash", script]))
        else:
            out.append({"id": cid, "status": "missing", "exit_code": None, "command": "bash " + script, "output_tail": "missing"})
    return out

def demo_checks():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True, exist_ok=True)

    demo = ROOT / "tools/auneya/auneya_one_command_local_demo.sh"
    valid = ROOT / "fixtures/auneya/claims/valid-release-reality.json"
    invalid = ROOT / "fixtures/auneya/claims/invalid-private-data-claim.json"
    out = []

    if not demo.exists() or not valid.exists():
        return [{"id": "local_demo_files_exist", "status": "fail", "exit_code": 1, "command": "check demo files", "output_tail": "demo or valid fixture missing"}]

    env = {
        "AUNEYA_DEMO_OUT_DIR": str(TMP / "demo"),
        "AUNEYA_WITNESS_ID": "witness_android_termux_local_001",
        "AUNEYA_START_TIME": "2026-10-06T00:11:00Z",
    }

    out.append(run("local_demo_evidence_run", ["bash", rel(demo), rel(valid)], True, env))

    flow_path = TMP / "demo/local-flow.json"
    display_path = TMP / "demo/local-display.txt"
    compact_path = TMP / "demo/local-display-compact.txt"
    compact = compact_path.read_text("utf-8") if compact_path.exists() else ""

    try:
        flow = json.loads(flow_path.read_text("utf-8"))
    except Exception:
        flow = {}

    observed = {
        "flow_file_created": flow_path.exists(),
        "display_file_created": display_path.exists(),
        "compact_file_created": compact_path.exists(),
        "schema_version_ok": flow.get("schema_version") == "auneya-pulse-flow-v0.1",
        "flow_type_ok": flow.get("flow_type") == "phone_witness_loop",
        "pulses_present": isinstance(flow.get("pulses"), list) and len(flow.get("pulses")) > 0,
        "micro_proofs_present": isinstance(flow.get("micro_proofs"), list) and len(flow.get("micro_proofs")) > 0,
        "transferable_false": "transferable=false" in compact,
        "market_value_false": "market_value_claimed=false" in compact,
        "mainnet_not_active": "mainnet=not_active" in compact,
    }

    out.append({
        "id": "local_demo_boundary_validation",
        "status": "pass" if all(observed.values()) else "fail",
        "exit_code": 0 if all(observed.values()) else 1,
        "command": "validate local demo artifacts",
        "observed": observed,
        "output_tail": json.dumps(observed, indent=2),
    })

    if invalid.exists():
        bad_env = dict(env)
        bad_env["AUNEYA_DEMO_OUT_DIR"] = str(TMP / "private")
        out.append(run("invalid_private_claim_rejected", ["bash", rel(demo), rel(invalid)], False, bad_env))
    else:
        out.append({"id": "invalid_private_claim_rejected", "status": "missing", "exit_code": None, "command": rel(invalid), "output_tail": "missing"})

    return out

def main():
    checks = existing_conformance() + demo_checks()
    ok = all(c["status"] == "pass" for c in checks)

    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        head = "unknown"

    evidence = {
        "evidence_pack": "auneya-local-simulation-evidence-v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_head": head,
        "mode": "local_non_value_simulation",
        "network": "none",
        "mainnet_active": False,
        "token_created": False,
        "market_value_claimed": False,
        "transferable": False,
        "overall_status": "pass" if ok else "fail",
        "checks": checks,
    }

    out_dir = ROOT / "reports/auneya/local-simulation-v0.1"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "AUNEYA-LOCAL-SIMULATION-EVIDENCE-v0.1.json"
    md_path = out_dir / "AUNEYA-LOCAL-SIMULATION-EVIDENCE-v0.1.md"

    json_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n", "utf-8")

    lines = [
        "# AUNEYA Local Simulation Evidence v0.1",
        "",
        "Status: " + evidence["overall_status"].upper(),
        "",
        "Mode: local non-value simulation",
        "Network: none",
        "Mainnet active: false",
        "Token created: false",
        "Market value claimed: false",
        "Transferable: false",
        "",
        "## Checks",
        "",
        "| Check | Status | Exit |",
        "|---|---:|---:|",
    ]

    for c in checks:
        lines.append("| `" + c["id"] + "` | `" + c["status"] + "` | `" + str(c["exit_code"]) + "` |")

    lines += [
        "",
        "## Boundary",
        "",
        "This evidence pack does not create AUNEYA, neya, a token, market value, transferability, mainnet activity, investment claims or legal clearance.",
        "",
        "Legal review is required before any public token launch, listing, sale, transferability or market-value communication.",
        "",
    ]

    md_path.write_text("\n".join(lines), "utf-8")

    print("Evidence JSON:", json_path)
    print("Evidence MD:  ", md_path)
    print("Status:       ", evidence["overall_status"].upper())

    raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
