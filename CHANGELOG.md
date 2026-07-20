# Changelog

All notable changes to Keystone Verify are documented here. The format follows
Keep a Changelog, and the project uses semantic versioning.

## [Unreleased]

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
