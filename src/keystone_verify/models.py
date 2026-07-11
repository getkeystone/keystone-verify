"""Models for Keystone Verify.

Profile: how to talk to a target endpoint (field mapping).
Case: what to send and what to assert about the response.
Result: what happened when a case ran.
RunSummary: aggregate statistics for a complete run.

The profile is the abstraction that makes the harness endpoint-agnostic.
The same case format works across Engage, Counsel, or any endpoint
whose response shape is described in a profile.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


# --- Profile: how to talk to a target ---


class ResponseMapping(BaseModel):
    """Maps generic assertion names to target-specific response fields."""

    answer_field: str = "message"
    severity_field: str = "severity"
    citations_field: str | None = "evidence"
    audit_hash_field: str | None = "audit_hash"
    fail_closed_field: str | None = None
    length_source: str | None = None  # if None, uses len(answer_field)


class Profile(BaseModel):
    """How to reach and interpret a target endpoint."""

    name: str
    base_url: str
    endpoint: str
    method: str = "POST"
    timeout_s: int = 60
    response_mapping: ResponseMapping = Field(default_factory=ResponseMapping)
    description: str = ""


# --- Case: what to send and assert ---


class Assertions(BaseModel):
    """Declarative checks against a response.

    severity: exact match on severity field.
    severity_in: pass if severity is any of these.
    min_length: answer must be at least this long.
    contains: AND semantics, all must be present (case-insensitive).
    contains_any: OR semantics, at least one must be present.
    absent: NONE may be present.
    has_citations: if true, citations list must be non-empty.
    fail_closed: if set, fail_closed field must match.
    max_latency_ms: response must arrive within this time.
    max_cost_cents: cost field must not exceed this value.
    """

    severity: str | None = None
    severity_in: list[str] = Field(default_factory=list)
    min_length: int = 0
    contains: list[str] = Field(default_factory=list)
    contains_any: list[str] = Field(default_factory=list)
    absent: list[str] = Field(default_factory=list)
    has_citations: bool | None = None
    fail_closed: bool | None = None
    max_latency_ms: int | None = None
    max_cost_cents: float | None = None


class Case(BaseModel):
    """An eval case: request payload plus assertions."""

    case_id: str
    category: str
    request: dict[str, Any]
    assertions: Assertions
    description: str = ""
    bucket: str = "core-regression"
    pair_id: str | None = None


# --- Result: what happened ---


class Result(BaseModel):
    """Result of running one case."""

    case_id: str
    category: str
    bucket: str
    passed: bool
    latency_ms: float
    response_length: int
    details: str = ""
    pair_id: str | None = None
    severity: str = ""
    fail_closed: bool | None = None
    audit_hash: str = ""
    citations_count: int = 0
    cost_cents: float | None = None


# --- Run summary ---


class RunSummary(BaseModel):
    """Aggregate statistics for a completed run."""

    run_id: str
    profile: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0
    by_category: dict[str, dict[str, int]] = Field(default_factory=dict)
    by_bucket: dict[str, dict[str, int]] = Field(default_factory=dict)
    mean_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    total_cost_cents: float = 0.0
