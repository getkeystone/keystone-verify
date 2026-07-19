"""Tests for the reporter's optional content checksum.

The checksum is an optional SHA-256 for detecting accidental modification. It
is not a cryptographic seal or tamper-evidence mechanism.
"""

import json

from keystone_verify.models import RunSummary
from keystone_verify.reporter import (
    CONTENT_CHECKSUM_FIELD,
    add_content_checksum,
    compute_content_checksum,
    verify_content_checksum,
    write_artifacts,
)


def _sample_report() -> dict:
    return {
        "run_id": "eval-20260719T000000",
        "profile": "reference-agent-v0",
        "counts": {"total": 6, "passed": 6, "failed": 0, "pass_rate": 1.0},
        "by_category": {"happy-path": {"total": 2, "passed": 2}},
    }


class TestContentChecksum:
    def test_roundtrip_matches(self):
        report = add_content_checksum(_sample_report())
        assert CONTENT_CHECKSUM_FIELD in report
        assert verify_content_checksum(report) is True

    def test_checksum_excludes_itself(self):
        # Recomputing over the stamped report must equal the stored value,
        # which is only possible if the field is excluded from its own input.
        report = add_content_checksum(_sample_report())
        assert compute_content_checksum(report) == report[CONTENT_CHECKSUM_FIELD]

    def test_detects_modification(self):
        report = add_content_checksum(_sample_report())
        report["counts"]["passed"] = 5
        assert verify_content_checksum(report) is False

    def test_missing_checksum_does_not_verify(self):
        assert verify_content_checksum(_sample_report()) is False

    def test_deterministic(self):
        assert compute_content_checksum(_sample_report()) == compute_content_checksum(_sample_report())


class TestWriteArtifactsChecksum:
    def test_included_when_enabled(self, tmp_path):
        summary = RunSummary(run_id="eval-on", profile="p", total=1, passed=1, failed=0, pass_rate=1.0)
        out = write_artifacts(summary, [], tmp_path, content_checksum=True)
        meta = json.loads((out / "run_metadata.json").read_text())
        assert CONTENT_CHECKSUM_FIELD in meta
        assert verify_content_checksum(meta) is True

    def test_omitted_by_default(self, tmp_path):
        summary = RunSummary(run_id="eval-off", profile="p", total=1, passed=1, failed=0, pass_rate=1.0)
        out = write_artifacts(summary, [], tmp_path, content_checksum=False)
        meta = json.loads((out / "run_metadata.json").read_text())
        assert CONTENT_CHECKSUM_FIELD not in meta
