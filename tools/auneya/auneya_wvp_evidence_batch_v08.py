#!/usr/bin/env python3

"""
AUNEYA/WVP v0.8

Bounded pinned multi-operator evidence.

Offline research only.

No consensus validation.
No independence proof.
No economic activation.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import time

import auneya_nightfall_challenge_v05 as v5
import auneya_pinned_observation_v07 as v7
import auneya_registry_checkpoint_v06 as v6
import auneya_trusted_node_identity_v04 as identities


MAX_RECEIPTS = 16

RISK_FIELDS = (
    "loading",
    "stalled_on_fork",
    "reorg_in_flight",
)


class BatchError(ValueError):
    pass


def summarize(receipts):

    groups = {}

    comparisons = Counter()

    for receipt in receipts:

        status = receipt["status"]

        identity = (
            status["tip_height"],
            status["tip"],
            status["total_work"],
        )

        groups.setdefault(
            identity,
            [],
        ).append(
            receipt["node_id"]
        )

    for index, first in enumerate(receipts):

        for second in receipts[index + 1:]:

            comparison = v5.compare_verified(
                first,
                second,
            )

            comparisons[
                comparison["result"]
            ] += 1

    if comparisons["SAME_HEIGHT_FORK_CONFLICT"]:

        verdict = (
            "CONFLICTING_SAME_HEIGHT_SIGNED_CLAIMS"
        )

    elif comparisons["INCONSISTENT_TIP_CLAIMS"]:

        verdict = (
            "INCONSISTENT_SIGNED_CLAIMS"
        )

    elif len(groups) == 1:

        verdict = (
            "MATCHING_SIGNED_TIP_CLAIMS"
        )

    else:

        verdict = (
            "DIVERGENT_SIGNED_CLAIMS_NOT_FORK_PROOF"
        )

    risk = any(

        receipt["status"]["live_peers"] == 0

        or not receipt["status"][
            "supply_invariant_ok"
        ]

        or any(
            receipt["status"][field]
            for field in RISK_FIELDS
        )

        for receipt in receipts

    )

    return {

        "observation_verdict": verdict,

        "operator_count": len(receipts),

        "operator_ids": sorted(
            receipt["node_id"]
            for receipt in receipts
        ),

        "claimed_tip_groups": [

            {
                "tip_height": height,

                "tip": tip,

                "total_work": work,

                "operator_ids": sorted(nodes),
            }

            for (height, tip, work), nodes
            in sorted(groups.items())

        ],

        "pairwise_results": dict(
            sorted(comparisons.items())
        ),

        "reported_risk_flags": risk,
    }


def verify_batch(
    challenge,
    receipts,
    registry,
    seal,
    expected_sha256,
    replay_db,
    now=None,
):

    if (
        not isinstance(receipts, list)
        or not 2 <= len(receipts) <= MAX_RECEIPTS
    ):

        raise BatchError(
            "require 2 to 16 signed operator receipts"
        )

    v7.ensure_not_input(
        replay_db,
        registry,
        seal,
    )

    pinned = v6.read_seal(
        seal,
        expected_sha256,
    )

    now = (
        int(time.time())
        if now is None
        else now
    )

    with tempfile.TemporaryDirectory(
        prefix="auneya-v08-pinned-"
    ) as folder:

        frozen_file = (
            Path(folder) / "registry.sqlite"
        )

        frozen = v7.snapshot_copy(
            registry,
            frozen_file,
        )

        for key in ("nodes", "events"):

            if frozen[key] != pinned[key]:

                raise BatchError(
                    "registry differs from externally "
                    "pinned checkpoint"
                )

        # Every signature is checked against the
        # same frozen trusted registry.

        checked = [

            v5.verify_receipt(
                challenge,
                receipt,
                frozen_file,
                now,
            )

            for receipt in receipts

        ]

        node_ids = [

            receipt["node_id"]
            for receipt in checked

        ]

        if len(set(node_ids)) != len(node_ids):

            raise BatchError(
                "duplicate signer identity"
            )

        pinned_nodes = {

            node["id"]: node

            for node in pinned["nodes"]

        }

        fingerprints = [

            pinned_nodes[node_id]["fingerprint"]

            for node_id in node_ids

        ]

        # Distinct node names with identical public
        # keys must not count as distinct witnesses.

        if (
            len(set(fingerprints))
            != len(fingerprints)
        ):

            raise BatchError(
                "multiple signer identities "
                "share one public key"
            )

        result = summarize(checked)

        receipt_hashes = sorted(

            hashlib.sha256(
                v5.canonical(receipt)
            ).hexdigest()

            for receipt in checked

        )

        challenge_hash = hashlib.sha256(
            v5.canonical(challenge)
        ).hexdigest()

        commitment = {

            "checkpoint_sha256": expected_sha256,

            "challenge_sha256": challenge_hash,

            "receipt_sha256": receipt_hashes,
        }

        evidence_hash = hashlib.sha256(
            v5.canonical(commitment)
        ).hexdigest()

        result.update({

            "format":
                "auneya-wvp-evidence-batch-v0.8",

            "result":
                "PINNED_OPERATOR_SIGNATURES_VALID",

            "commitment": commitment,

            "evidence_sha256": evidence_hash,

            "wvp_proven":
                "authenticated_pinned_public_operator_claims_only",

            "consensus_validated": False,

            "sybil_resistance_proven": False,

            "independent_devices_proven": False,

            "mainnet_mutated": False,

            "non_value_research_only": True,
        })

        # Check live registry again immediately
        # before replay ledger consumption.

        live = v6.snapshot(registry)

        for key in ("nodes", "events"):

            if live[key] != pinned[key]:

                raise BatchError(
                    "live registry changed "
                    "since checkpoint"
                )

        # Existing v0.5 transaction ensures:
        # all receipts committed or none.

        v5.record_once(
            replay_db,
            checked,
        )

        return result


def main():

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    for name in (
        "challenge",
        "registry",
        "seal",
        "expected-sha256",
        "replay-db",
    ):

        parser.add_argument(
            "--" + name,
            required=True,
        )

    parser.add_argument(
        "--receipt",
        action="append",
        required=True,
    )

    args = parser.parse_args()

    try:

        if not 2 <= len(args.receipt) <= MAX_RECEIPTS:

            raise BatchError(
                "require 2 to 16 receipt files"
            )

        receipts = [

            v5.read(path)
            for path in args.receipt

        ]

        result = verify_batch(

            v5.read(args.challenge),

            receipts,

            args.registry,

            args.seal,

            args.expected_sha256,

            args.replay_db,

        )

        print(
            json.dumps(
                result,
                indent=2,
                sort_keys=True,
            )
        )

    except (
        BatchError,
        v5.ChallengeError,
        v6.CheckpointError,
        v7.PinnedError,
        identities.IdentityError,
        sqlite3.Error,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        IndexError,
    ) as exc:

        parser.exit(
            2,
            "FAIL-CLOSED: " + str(exc) + "\n",
        )


if __name__ == "__main__":
    main()
