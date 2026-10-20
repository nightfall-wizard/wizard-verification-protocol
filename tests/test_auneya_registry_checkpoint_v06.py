"""Independent offline, adversarial checks of AUNEYA registry checkpoints."""
import hashlib
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools' / 'auneya'))
import auneya_registry_checkpoint_v06 as cp

DER = bytes.fromhex('302a300506032b6570032100') + bytes(range(32))


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        d = Path(self.tmp.name)
        self.db, self.first, self.second = d/'registry.db', d/'a.json', d/'b.json'
        with sqlite3.connect(self.db) as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('CREATE TABLE nodes (node_id TEXT PRIMARY KEY, epoch INTEGER, fingerprint TEXT, public_der BLOB, state TEXT)')
            db.execute('CREATE TABLE events (node_id TEXT, epoch INTEGER, event_digest TEXT, kind TEXT, PRIMARY KEY(node_id,epoch))')
            db.execute('INSERT INTO nodes VALUES (?,?,?,?,?)', ('operator_a', 0, hashlib.sha256(DER).hexdigest(), DER, 'active'))
            db.execute('INSERT INTO events VALUES (?,?,?,?)', ('operator_a', 0, 'a'*64, 'enroll'))
        self.db.chmod(0o600)
        self.pin = cp.write_new(self.first, cp.snapshot(self.db))

    def edit(self, commands):
        with sqlite3.connect(self.db) as db:
            for command in commands:
                db.execute(command)

    def test_pin_and_wal(self):
        cp.verify(self.db, self.first, self.pin)
        writer = sqlite3.connect(self.db)
        self.addCleanup(writer.close)
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute("UPDATE nodes SET epoch=1 WHERE node_id='operator_a'")
        writer.execute("INSERT INTO events VALUES ('operator_a',1,'" + 'b'*64 + "','rotate')")
        writer.commit()
        with self.assertRaisesRegex(cp.CheckpointError, 'STATE DIFFERS'):
            cp.verify(self.db, self.first, self.pin)
        new = cp.advance(self.db, self.first, self.pin)
        newpin = cp.write_new(self.second, new)
        cp.verify(self.db, self.second, newpin)
        self.assertEqual(new['previous'], self.pin)

    def test_reject_key_swap(self):
        self.edit(["UPDATE nodes SET public_der=X'" + (DER[:-1]+b'X').hex() + "'"])
        with self.assertRaisesRegex(cp.CheckpointError, 'fingerprint'):
            cp.snapshot(self.db)

    def test_reject_state_tamper(self):
        self.edit(["UPDATE nodes SET state='revoked'", "UPDATE events SET kind='revoke'"])
        with self.assertRaises(cp.CheckpointError):
            cp.verify(self.db, self.first, self.pin)

    def test_reject_rollback(self):
        self.edit(["UPDATE nodes SET epoch=1", "INSERT INTO events VALUES ('operator_a',1,'" + 'b'*64 + "','rotate')"])
        next_state = cp.advance(self.db, self.first, self.pin)
        pin2 = cp.write_new(self.second, next_state)
        self.edit(["UPDATE nodes SET epoch=0", "DELETE FROM events WHERE epoch=1"])
        with self.assertRaisesRegex(cp.CheckpointError, 'rollback|rewrite'):
            cp.advance(self.db, self.second, pin2)

    def test_rotation_changes_key_only_with_event(self):
        new_der = DER[:-1] + b'X'
        self.edit(["UPDATE nodes SET epoch=1,fingerprint='" + hashlib.sha256(new_der).hexdigest() + "', public_der=X'" + new_der.hex() + "'",
                   "INSERT INTO events VALUES ('operator_a',1,'" + 'b'*64 + "','rotate')"])
        nxt = cp.advance(self.db, self.first, self.pin)
        self.assertNotEqual(nxt['nodes'][0]['fingerprint'], cp.read_seal(self.first, self.pin)['nodes'][0]['fingerprint'])
        self.edit(["UPDATE events SET kind='revoke' WHERE epoch=1", "UPDATE nodes SET state='revoked'"])
        with self.assertRaises(cp.CheckpointError):
            cp.advance(self.db, self.first, self.pin)

    def test_valid_revocation(self):
        self.edit(["UPDATE nodes SET epoch=1", "INSERT INTO events VALUES ('operator_a',1,'" + 'b'*64 + "','revoke')",
                   "UPDATE nodes SET state='revoked'"])
        state = cp.advance(self.db, self.first, self.pin)
        self.assertEqual(state['nodes'][0]['state'], 'revoked')

    def test_reject_wrong_pin_and_tampered_seal(self):
        with self.assertRaisesRegex(cp.CheckpointError, 'PIN MISMATCH'):
            cp.verify(self.db, self.first, '0'*64)
        self.first.write_bytes(self.first.read_bytes() + b' ')
        with self.assertRaisesRegex(cp.CheckpointError, 'PIN MISMATCH'):
            cp.verify(self.db, self.first, self.pin)

    def test_bad_permissions_symlinks_and_exclusive_creation(self):
        self.db.chmod(0o644)
        with self.assertRaises(cp.CheckpointError): cp.snapshot(self.db)
        self.db.chmod(0o600)
        link = self.db.parent/'link.db'
        link.symlink_to(self.db)
        with self.assertRaises(cp.CheckpointError): cp.snapshot(link)
        with self.assertRaises(FileExistsError): cp.write_new(self.first, cp.snapshot(self.db))

    def test_duplicate_json_and_noncanonical_rejected(self):
        raw = b'{"format":"x","format":"y"}\n'
        self.first.write_bytes(raw)
        with self.assertRaises(cp.CheckpointError):
            cp.read_seal(self.first, hashlib.sha256(raw).hexdigest())

    def test_reject_deleted_history_and_resurrection(self):
        self.edit(["UPDATE nodes SET epoch=1,state='revoked'", "INSERT INTO events VALUES ('operator_a',1,'" + 'b'*64 + "','revoke')"])
        state = cp.advance(self.db, self.first, self.pin)
        pin2 = cp.write_new(self.second, state)
        self.edit(["UPDATE nodes SET state='active'"])
        with self.assertRaises(cp.CheckpointError):
            cp.advance(self.db, self.second, pin2)

    def test_reject_event_rewrite_and_schema_drift(self):
        self.edit(["UPDATE events SET event_digest='"+'f'*64+"'"])
        with self.assertRaises(cp.CheckpointError): cp.advance(self.db, self.first, self.pin)
        self.edit(["ALTER TABLE nodes ADD COLUMN injected TEXT"])
        with self.assertRaises(cp.CheckpointError): cp.snapshot(self.db)


if __name__ == '__main__':
    unittest.main(verbosity=2)
