"""Reporter: write structured, reproducible evaluation artifacts.

Produces results.json and run_metadata.json in the output directory.
Same artifact format as keystone-engage and keystone-counsel. These are
plain JSON files: reproducible and inspectable, with no content-integrity
seal or signature.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from keystone_verify.models import Result, RunSummary

logger = logging.getLogger(__name__)

CONTENT_CHECKSUM_FIELD = "content_checksum"


def compute_content_checksum(report: dict) -> str:
    """Optional SHA-256 checksum for detecting accidental modification.

    This is not a cryptographic seal or tamper-evidence mechanism.

    Returns the SHA-256 hex digest of the report's contents, computed over a
    canonical JSON encoding with the content_checksum field itself excluded so
    a report can carry its own checksum without affecting its own value.
    """
    payload = {k: v for k, v in report.items() if k != CONTENT_CHECKSUM_FIELD}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def add_content_checksum(report: dict) -> dict:
    """Return a copy of the report with a content_checksum field added.

    Optional SHA-256 checksum for detecting accidental modification. This is
    not a cryptographic seal or tamper-evidence mechanism.
    """
    stamped = dict(report)
    stamped[CONTENT_CHECKSUM_FIELD] = compute_content_checksum(stamped)
    return stamped


def verify_content_checksum(report: dict) -> bool:
    """Return True if the stored content_checksum matches the report contents.

    Recomputes the checksum over the report (excluding the content_checksum
    field) and compares it to the stored value. This detects accidental
    modification only. It is not a cryptographic seal or tamper-evidence
    mechanism, and it does not protect against deliberate rewriting.
    """
    stored = report.get(CONTENT_CHECKSUM_FIELD)
    if not stored:
        return False
    return compute_content_checksum(report) == stored


def write_artifacts(
    summary: RunSummary,
    results: list[Result],
    output_dir: str | Path,
    content_checksum: bool = False,
) -> Path:
    """Write structured evaluation artifacts to the output directory.

    Creates:
      {output_dir}/{run_id}/results.json
      {output_dir}/{run_id}/run_metadata.json

    When content_checksum is True, run_metadata.json carries an optional
    SHA-256 content_checksum field for detecting accidental modification. It is
    off by default and is not a cryptographic seal or tamper-evidence
    mechanism.
    """
    output_path = Path(output_dir) / summary.run_id
    output_path.mkdir(parents=True, exist_ok=True)

    # results.json: per-case results
    results_data = {
        "eval_entry": f"keystone-verify/{summary.profile}",
        "run_id": summary.run_id,
        "results": [r.model_dump() for r in results],
    }
    results_path = output_path / "results.json"
    with open(results_path, "w") as f:
        json.dump(results_data, f, indent=2, default=str)

    # run_metadata.json: summary and configuration
    metadata = {
        "run_id": summary.run_id,
        "profile": summary.profile,
        "timestamp": summary.timestamp.isoformat(),
        "counts": {
            "total": summary.total,
            "passed": summary.passed,
            "failed": summary.failed,
            "pass_rate": summary.pass_rate,
        },
        "by_category": summary.by_category,
        "by_bucket": summary.by_bucket,
        "latency": {
            "mean_ms": round(summary.mean_latency_ms, 1),
            "p95_ms": round(summary.p95_latency_ms, 1),
        },
    }

    if content_checksum:
        metadata = add_content_checksum(metadata)

    metadata_path = output_path / "run_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Artifacts written to %s", output_path)
    print(f"\nArtifacts saved to {output_path}/")
    return output_path
