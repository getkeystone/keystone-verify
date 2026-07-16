"""Judge: score a response against assertions.

Pure function. No I/O. The profile's response mapping tells the judge
where to find the answer, severity, citations, etc. in the response dict.
The assertions tell the judge what to check.

This is the reusable core of Keystone Verify. Everything else is plumbing.
"""

from __future__ import annotations

from keystone_verify.models import Assertions, Case, Profile, Result


def _join(existing: str, extra: str) -> str:
    return f"{existing}; {extra}" if existing else extra


def judge(
    case: Case,
    response: dict,
    profile: Profile,
    latency_ms: float,
) -> Result:
    """Score a response against a case's assertions.

    Uses the profile's response_mapping to extract fields from the
    response dict. Runs each assertion in the case. Returns a Result
    with pass/fail and details.
    """
    mapping = profile.response_mapping
    assertions = case.assertions

    # Extract fields using profile mapping
    answer = str(response.get(mapping.answer_field, ""))
    severity = str(response.get(mapping.severity_field, "unknown"))
    audit_hash = str(response.get(mapping.audit_hash_field, "")) if mapping.audit_hash_field else ""
    fail_closed = response.get(mapping.fail_closed_field) if mapping.fail_closed_field else None
    citations = response.get(mapping.citations_field, []) if mapping.citations_field else []
    if not isinstance(citations, list):
        citations = []

    details = ""
    passed = True

    # Severity exact match
    if assertions.severity is not None:
        if severity != assertions.severity:
            passed = False
            details = _join(details, f"severity: expected '{assertions.severity}', got '{severity}'")

    # Severity in set
    if assertions.severity_in:
        if severity not in assertions.severity_in:
            passed = False
            details = _join(details, f"severity: expected one of {assertions.severity_in}, got '{severity}'")

    # Minimum length
    if assertions.min_length > 0:
        if len(answer) < assertions.min_length:
            passed = False
            details = _join(details, f"length: expected >={assertions.min_length}, got {len(answer)}")

    # Contains (AND)
    answer_lower = answer.lower()
    missing = [s for s in assertions.contains if s.lower() not in answer_lower]
    if missing:
        passed = False
        details = _join(details, f"missing contains: {missing}")

    # Contains any (OR)
    if assertions.contains_any:
        if not any(s.lower() in answer_lower for s in assertions.contains_any):
            passed = False
            details = _join(
                details,
                f"missing contains_any (need at least one): {assertions.contains_any}",
            )

    # Absent (NONE)
    forbidden = [s for s in assertions.absent if s.lower() in answer_lower]
    if forbidden:
        passed = False
        details = _join(details, f"present but should be absent: {forbidden}")

    # Citations
    if assertions.has_citations is True:
        if not citations:
            passed = False
            details = _join(details, "expected citations but got none")
    elif assertions.has_citations is False:
        if citations:
            passed = False
            details = _join(details, f"expected no citations but got {len(citations)}")

    # Fail-closed
    if assertions.fail_closed is not None:
        if fail_closed != assertions.fail_closed:
            passed = False
            details = _join(
                details,
                f"fail_closed: expected {assertions.fail_closed}, got {fail_closed}",
            )

    # Latency
    if assertions.max_latency_ms is not None:
        if latency_ms > assertions.max_latency_ms:
            passed = False
            details = _join(
                details,
                f"latency: expected <={assertions.max_latency_ms}ms, got {latency_ms:.0f}ms",
            )

    return Result(
        case_id=case.case_id,
        category=case.category,
        bucket=case.bucket,
        passed=passed,
        latency_ms=latency_ms,
        response_length=len(answer),
        details=details,
        pair_id=case.pair_id,
        severity=severity,
        fail_closed=fail_closed,
        audit_hash=audit_hash,
        citations_count=len(citations),
    )
