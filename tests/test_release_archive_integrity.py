import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from tools.check_release_archive_integrity import verify


class ReleaseArchiveIntegrityTests(unittest.TestCase):
    def test_matching_archive_passes(self):
        self.check_case(b"correct", b"correct", False)

    def test_mismatching_archive_fails(self):
        self.check_case(b"correct", b"wrong", True)

    def test_missing_member_fails(self):
        self.check_case(b"correct", None, True)

    def test_unexpected_member_fails(self):
        self.check_case(b"correct", b"correct", True, extra=True)

    def check_case(self, expected_data, archived_data,
                   should_fail, extra=False):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_path = root / "pack.tar.gz"
            manifest_path = root / "manifest.json"
            report_path = root / "report.json"

            manifest_path.write_text(json.dumps({
                "files": [{
                    "path": "sample.txt",
                    "sha256": hashlib.sha256(
                        expected_data
                    ).hexdigest()
                }]
            }))

            with tarfile.open(archive_path, "w:gz") as archive:
                if archived_data is not None:
                    self.add_file(archive, "sample.txt", archived_data)
                if extra:
                    self.add_file(archive, "extra.txt", b"extra")

            report_path.write_text(json.dumps({
                "archive_sha256": hashlib.sha256(
                    archive_path.read_bytes()
                ).hexdigest()
            }))

            errors = verify(manifest_path, archive_path, report_path)
            self.assertEqual(bool(errors), should_fail)

    @staticmethod
    def add_file(archive, name, data):
        info = tarfile.TarInfo(name)
        info.size = len(data)
        archive.addfile(info, io.BytesIO(data))


if __name__ == "__main__":
    unittest.main()
