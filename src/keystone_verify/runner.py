"""Runner: send cases to a target and collect judged results.

Sends each case's request dict to the profile's endpoint. Measures
latency. Passes the response to the judge. Collects results.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

import httpx

from keystone_verify.judge import judge
from keystone_verify.models import Case, Profile, Result, RunSummary

logger = logging.getLogger(__name__)


def run(
    profile: Profile,
    cases: list[Case],
    run_id: str | None = None,
) -> tuple[RunSummary, list[Result]]:
    """Run all cases against a target endpoint.

    Returns a summary and the list of per-case results.
    """
    if not run_id:
        run_id = f"eval-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"

    url = f"{profile.base_url}{profile.endpoint}"
    client = httpx.Client(timeout=profile.timeout_s)
    results: list[Result] = []

    print(f"Running {len(cases)} cases against {url}")
    print(f"Profile: {profile.name}")
    print("-" * 60)

    for case in cases:
        try:
            start = time.monotonic()
            resp = client.request(
                method=profile.method,
                url=url,
                json=case.request,
            )
            latency_ms = (time.monotonic() - start) * 1000
            data = resp.json()
            result = judge(case, data, profile, latency_ms)
        except Exception as e:
            result = Result(
                case_id=case.case_id,
                category=case.category,
                bucket=case.bucket,
                passed=False,
                latency_ms=0,
                response_length=0,
                details=f"Request failed: {e}",
            )

        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        line = f"  {status}  {result.case_id} [{result.category}] {round(result.latency_ms)}ms"
        if not result.passed:
            line += f"\n        {result.details}"
        print(line)

    client.close()

    # Build summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    latencies = [r.latency_ms for r in results if r.latency_ms > 0]
    sorted_latencies = sorted(latencies) if latencies else [0]
    p95_idx = int(len(sorted_latencies) * 0.95)

    by_category: dict[str, dict[str, int]] = {}
    by_bucket: dict[str, dict[str, int]] = {}
    for r in results:
        cat = by_category.setdefault(r.category, {"total": 0, "passed": 0})
        cat["total"] += 1
        if r.passed:
            cat["passed"] += 1
        buc = by_bucket.setdefault(r.bucket, {"total": 0, "passed": 0})
        buc["total"] += 1
        if r.passed:
            buc["passed"] += 1

    total_cost = sum(r.cost_cents or 0 for r in results)

    summary = RunSummary(
        run_id=run_id,
        profile=profile.name,
        total=total,
        passed=passed,
        failed=total - passed,
        pass_rate=passed / total if total > 0 else 0,
        by_category=by_category,
        by_bucket=by_bucket,
        mean_latency_ms=sum(latencies) / len(latencies) if latencies else 0,
        p95_latency_ms=sorted_latencies[p95_idx] if sorted_latencies else 0,
        total_cost_cents=total_cost,
    )

    # Print summary
    print("-" * 60)
    print(f"Results: {passed}/{total} ({summary.pass_rate * 100:.0f}%)")
    for cat, c in by_category.items():
        print(f"  {cat}: {c['passed']}/{c['total']}")
    print("By bucket:")
    for buc, c in by_bucket.items():
        print(f"  {buc}: {c['passed']}/{c['total']}")
    print(f"Latency: mean={summary.mean_latency_ms:.0f}ms p95={summary.p95_latency_ms:.0f}ms")
    if total_cost > 0:
        print(f"Cost: {total_cost:.2f} cents total")

    return summary, results
