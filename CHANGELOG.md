# Changelog

All notable changes to Keystone Verify are documented here. The format follows
Keep a Changelog, and the project uses semantic versioning.

## [Unreleased]

### Fixed
- `ResponseMapping.length_source` was defined but never read; `min_length`
  and `response_length` always measured `answer_field`. `judge.py` now
  measures `length_source` when a profile sets it, matching the field's
  documented intent. `contains`/`contains_any`/`absent` are unaffected and
  still always read `answer_field`. Covered by new tests in
  `tests/test_judge.py`.

### Changed
- README, package docstrings, and `pyproject.toml` no longer describe
  Verify as endpoint-agnostic or able to target "any HTTP endpoint" / "any
  RAG or agent endpoint." It evaluates compatible endpoints: ones whose
  JSON request/response shapes can be represented by a Verify profile.
  Documented the concrete boundary (one base URL/endpoint, JSON body, a
  fixed set of top-level response fields; no headers, auth, nested-path
  extraction, or non-JSON responses).
- README no longer says Verify exists to "prove" that a system behaves as
  claimed. Replaced with: it evaluates whether observed responses satisfy
  the assertions defined in a given set of cases and profile, and a
  passing run does not establish general correctness, production
  suitability, safety, or independent validation.
- README and `reporter.py` no longer call artifacts "reproducible."
  `results.json` and `run_metadata.json` do not retain request/response
  bodies, target commit, model version, or Verify's own version, so they
  do not support reconstructing the system under test. Now described as
  "structured, inspectable" run artifacts.
- README corrected: artifacts are not universally free of any
  content-integrity mechanism. `--content-checksum` adds an unkeyed
  SHA-256 checksum to `run_metadata.json` only (off by default); documented
  exactly what that does and does not establish, and that `results.json`
  is never checksummed.
- Removed "one of three extensions in the Keystone platform" and "the
  piece that turns platform claims into inspectable evidence." Verify is
  standalone evaluation infrastructure that can evaluate Engage, Counsel,
  or other compatible endpoints; it does not run inside their served path
  or imply a shared runtime.
- Related-repo descriptions aligned with current framing (Engage and
  Counsel as independently composed reference implementations, Gov as a
  governed retrieval reference implementation, Ledger as retained internal
  evaluation artifacts and lineage rather than "proof artifacts").
- Documented that the runner does not call `raise_for_status()`: a 4xx/5xx
  response with a valid JSON body is judged like a 200. Documented that a
  non-JSON response or request failure is recorded with `latency_ms=0`
  rather than the latency measured before the failure, and that
  `p95_latency_ms` is an approximation (`int(n * 0.95)` in the sorted
  list), not a statistically rigorous percentile method. No behavior
  changed; this was previously undocumented.

### Added
- `profiles/reference-legal-intake-v0.json` and
  `profiles/reference-legal-intake-v0.cases.jsonl`: a vendor-neutral reference
  profile for a hypothetical governed legal intake conversational agent, a
  regulated, high-stakes domain distinct from the retrieval and generic-agent
  profiles. Twelve cases spanning happy-path intake, unauthorized-practice-of-law
  boundary escalation, adversarial probes, and ambiguous-urgency triage
  escalation. No new judge types; uses the existing assertion vocabulary.
- `tests/test_reference_legal_intake.py`: confirms the profile loads, the case
  count, and the presence of escalation-expected and adversarial cases.

## [0.9.0] - 2026-07-19

### Added
- Optional `content_checksum` field in `run_metadata.json`. When enabled, the
  reporter writes a SHA-256 over the run metadata (excluding the checksum field
  itself) for detecting accidental modification. Off by default. This is not a
  cryptographic seal or tamper-evidence mechanism. Enable it with
  `keystone-verify run ... --content-checksum`.
- `compute_content_checksum`, `add_content_checksum`, and
  `verify_content_checksum` helpers in `reporter.py`, with round-trip tests.
- `profiles/reference-agent-v0.json` and
  `profiles/reference-agent-v0.cases.jsonl`: a vendor-neutral reference profile
  for a hypothetical governed conversational agent, with two adversarial probe
  cases and two fail-closed cases.
- GitHub Actions CI (`.github/workflows/ci.yml`) running `uv run pytest` on
  push to main and on pull requests, against Python 3.11 and 3.12.
- This changelog, plus README links to the changelog, the website, and the
  public evaluation ledger, and a CI status badge.

### Notes
- The default report format is unchanged: plain JSON with no content-integrity
  hash unless `--content-checksum` is passed.
- No architecture, license, or profile-format changes. The package remains
  pydantic based with JSON profiles under the Apache-2.0 license.

## [0.1.0] - 2026-07-16

### Added
- Initial release of Keystone Verify, a standalone, endpoint-agnostic evaluation
  harness for governed AI systems.
- Pure-function judge (`judge.py`) with a declarative assertion vocabulary:
  severity, severity_in, min_length, contains, contains_any, absent,
  has_citations, fail_closed, and max_latency_ms.
- Pydantic models (`models.py`): Profile, ResponseMapping, Case, Assertions,
  Result, and RunSummary.
- JSON profile loader and JSONL case loader (`loader.py`).
- HTTP runner with latency measurement (`runner.py`).
- Reporter writing plain-JSON `results.json` and `run_metadata.json` artifacts
  (`reporter.py`).
- Click CLI with a `run` command (`cli.py`).
- A self-contained example against httpbin.org, plus profiles targeting the
  Keystone Engage and Counsel endpoints.
- Apache-2.0 license.
