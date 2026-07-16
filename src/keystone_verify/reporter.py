"""Reporter: write structured, reproducible evaluation artifacts.

Produces results.json and run_metadata.json in the output directory.
Same artifact format as keystone-engage and keystone-counsel. These are
plain JSON files: reproducible and inspectable, with no content-integrity
seal or signature.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from keystone_verify.models import Result, RunSummary

logger = logging.getLogger(__name__)


def write_artifacts(
    summary: RunSummary,
    results: list[Result],
    output_dir: str | Path,
) -> Path:
    """Write structured evaluation artifacts to the output directory.

    Creates:
      {output_dir}/{run_id}/results.json
      {output_dir}/{run_id}/run_metadata.json
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
    metadata_path = output_path / "run_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Artifacts written to %s", output_path)
    print(f"\nArtifacts saved to {output_path}/")
    return output_path
