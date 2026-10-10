# AUNEYA Durable Delivery v0.2

## Scope

Experimental local crash recovery for signed witness-proof delivery.

This extends the existing AUNEYA two-node research prototype.

## Persistent outbox

The sender stores the complete canonical packet in SQLite
before attempting delivery.

Pending messages survive sender restarts.

The delivery worker retries pending messages.

## Persistent inbox

The receiver verifies the existing Ed25519 witness-proof
signature, schema and trusted chain context.

The receiver stores accepted message IDs in SQLite.

An already accepted proof is not inserted twice.

## Delivery acknowledgement

The receiver returns the message ID with the acknowledgement.

The sender compares that ID against its pending outbox entry.

A missing or mismatched acknowledgement leaves the message pending.

An already accepted message is acknowledged without creating
another receiver entry.

## Persistence

Both SQLite databases use:

- WAL journal mode
- synchronous FULL
- Primary-key uniqueness

## Failure tests

The conformance test covers:

- Offline receiver
- Pending-message persistence
- Mismatched acknowledgement
- Invalid chain
- Invalid genesis
- Invalid signature
- Duplicate JSON keys
- Lost acknowledgement after receiver commit
- Sender restart
- Receiver restart
- Duplicate-delivery rejection

## Verification

Run:

bash conformance/auneya-durable-delivery-v0.2.sh

## Manual commands

Queue:

python3 tools/auneya/auneya_durable_delivery_v02.py queue \
  --database sender.sqlite \
  --packet signed-research-packet.json

Send once:

python3 tools/auneya/auneya_durable_delivery_v02.py flush-once \
  --database sender.sqlite \
  --peer http://127.0.0.1:PORT/receive

Retry worker:

python3 tools/auneya/auneya_durable_delivery_v02.py worker \
  --database sender.sqlite \
  --peer http://127.0.0.1:PORT/receive

The receiver must be started separately with its trusted
public key, chain ID, genesis ID and witness ID.

## Limitations

Research only.

Local 127.0.0.1 communication.

No communication between independent devices.

No TLS transport.

The application acknowledgement is not cryptographically
authenticated against a malicious local peer.

No distributed consensus.

No cross-node atomic transaction guarantee.

No guarantee about the real-world truth of simulated evidence.

SQLite durability remains subject to Android and hardware limits.

The worker is not an Android system service and must be restarted
after a device reboot.

No mainnet.

No actual token.

No transferable asset.

No real wallet.

No financial value.

No independent security audit claimed.
