# Keystone Verify

[![CI](https://github.com/getkeystone/keystone-verify/actions/workflows/ci.yml/badge.svg)](https://github.com/getkeystone/keystone-verify/actions/workflows/ci.yml)

Standalone evaluation infrastructure for governed AI systems.

## What this is

At the center of Keystone Verify is a judge: a pure function that takes a case, a response, a profile, and a latency measurement, and returns a result. `latency_ms` is an explicit input, not something the judge measures itself; the runner measures it separately over the network call. The judge does no I/O and has no side effects, so for the same explicit inputs it always produces the same result. That makes the evaluation logic directly testable, and it is covered by unit tests.

Around that judge is an HTTP harness for compatible endpoints: ones whose JSON request and response shapes can be represented by a Verify profile (one configured base URL and endpoint, a configurable HTTP method, a JSON request body, and a small set of named top-level response fields). Describe how to read the target's responses in a profile, write cases with declarative assertions, and run them. The harness sends each request, scores each response with the judge, and writes structured, inspectable JSON artifacts.

It is not a benchmark toy or a prompt-by-prompt spot check. It exists to evaluate whether a target endpoint's observed responses satisfy the assertions defined in a given set of cases and profile: that it refuses when a case expects it to, cites what a case expects it to, and stays within the limits a case declares. A passing run establishes only that the responses observed during that run, for those cases, under that profile and configuration, satisfied the defined assertions. It does not establish general correctness, production suitability, safety, authorization correctness beyond what the assertions check, independent validation, or behavior on inputs the cases do not cover.

## How it works

Three inputs produce one result:

- A profile (JSON) describes how to reach a target endpoint and how to map its response fields into the assertion vocabulary.
- A cases file (JSONL, one case per line) contains request payloads and declarative assertions.
- The judge scores each response against its case's assertions.

The core path is `case + response + profile = result`, and the judge that computes it is a pure function. The runner handles HTTP and latency measurement, and the reporter writes the artifacts. The judgment itself is isolated and side-effect free.

## The judge

`judge(case, response, profile, latency_ms)` returns a `Result`. It reads fields from the response using the profile's mapping, then checks the case's assertions:

- `severity` (exact match) and `severity_in` (one of a set)
- `min_length` (length of the mapped field at least this long; see Response mapping below for which field)
- `contains` (AND: all substrings present)
- `contains_any` (OR: at least one present)
- `absent` (NONE: none present)
- `has_citations` (citations list must be non-empty or empty)
- `fail_closed` (fail-closed flag matches)
- `max_latency_ms` (`latency_ms`, the runner-supplied measurement, within a time budget)

The judge is deterministic with respect to its explicit inputs: it does no I/O and has no side effects. This says nothing about whether the target endpoint, the model behind it, or a full run against a live service is deterministic; those are the runner's concern, not the judge's. The judge is covered by unit tests in `tests/test_judge.py`, which exercise the judgment logic directly against constructed inputs, without a running endpoint.

### Response mapping

A profile's `response_mapping` names the top-level response fields the judge reads: `answer_field` (default `message`), `severity_field`, `citations_field`, `audit_hash_field`, `fail_closed_field`, and `length_source`. `min_length` and the reported `response_length` measure `answer_field`, unless `length_source` names a different top-level field, in which case that field is measured instead; `contains`, `contains_any`, and `absent` always read `answer_field`. There is no support for nested-path field extraction, request headers or auth, or response bodies that are not a single JSON object with these fields at the top level.

## Running it

Clone and install:

```bash
git clone https://github.com/getkeystone/keystone-verify
cd keystone-verify
pip install -e .
```

The `example/` directory contains a self-contained profile and cases that run against `httpbin.org/post`, a public request-echo service, so you can exercise the harness without any Keystone service running:

```bash
keystone-verify run \
  --profile example/echo_profile.json \
  --cases example/sample_cases.jsonl \
  --output results/
```

Each case prints `PASS` or `FAIL` with a one-line reason for failures, followed by a summary. The run writes `results/<run_id>/results.json` and `results/<run_id>/run_metadata.json`. In this example, four cases pass and one (`echo-005`) fails on purpose to show how a failing assertion is reported. Running the example requires outbound network access to `httpbin.org`.

The `profiles/` directory contains profiles that target the Keystone Engage and Counsel endpoints (`localhost:8100` and `localhost:8200`). Those require the corresponding services to be running. The example profile is the self-contained one.

The `profiles/` directory also includes vendor-neutral reference profiles for hypothetical governed endpoints, useful as templates when writing your own: `reference-agent-v0` (a generic governed conversational agent) and `reference-legal-intake-v0` (a governed legal intake agent that gathers facts and escalates to a licensed specialist rather than giving legal advice). Each ships with a companion `*.cases.jsonl` file that includes adversarial probe cases and fail-closed escalation cases. These describe hypothetical endpoints at `localhost:9100`/`localhost:9200`; no corresponding service ships in this or any Keystone repository, and their presence is not evidence that such a system exists or that it has passed evaluation. Running them requires pointing `base_url` at a real endpoint that implements the mapped response shape.

## HTTP and failure behavior

The runner sends each case's `request` as a JSON body to the profile's configured `base_url` + `endpoint` and method, measures wall-clock latency around that call, and passes `response.json()` to the judge. It does not call `raise_for_status()`: an HTTP 4xx or 5xx response with a valid JSON body is judged the same as a 200, so a case can assert against an endpoint's structured error or refusal response regardless of status code. If the response body is not valid JSON, or the request itself fails (connection error, timeout, and so on), the case is recorded as failed with the exception message in `details` and `latency_ms` reported as `0`, not the latency actually measured before the failure. An empty case file produces a run with zero cases and no error. `p95_latency_ms` is computed as the value at `int(n * 0.95)` in the sorted latency list, an approximation, not a statistically rigorous percentile method.

## Output format

A run writes two structured JSON files under `results/<run_id>/`:

- `results.json`: one entry per case with the outcome, the failure detail, latency, response length, and the extracted severity, citation count, and audit hash.
- `run_metadata.json`: run-level statistics, including pass and fail counts, per-category and per-bucket breakdowns, and latency (mean and p95).

These are plain JSON files: structured and inspectable after a run, rather than trapped in terminal output. Neither file retains the request or response bodies, the profile's full content, a hash of the cases file, the target's commit or model version, or Verify's own version, so they do not carry enough context to reconstruct the system under test or the run's environment. They are inspectable evidence of what a run reported, not reproducibility artifacts in that stronger sense.

By default neither file carries a content-integrity mechanism. Passing `--content-checksum` adds an unkeyed SHA-256 `content_checksum` field to `run_metadata.json` only; `results.json` is never checksummed. See Optional content checksum below for exactly what that does and does not establish.

## Optional content checksum

`keystone-verify run --content-checksum` adds a `content_checksum` field to `run_metadata.json`: a SHA-256 hex digest computed over the metadata's own contents (with the checksum field itself excluded from the input). It is off by default.

This checksum can detect accidental modification of `run_metadata.json` relative to the digest stored at write time: if the file changes and the checksum is not recomputed to match, verification fails. It cannot detect deliberate tampering: an actor able to rewrite `run_metadata.json` can recompute a matching checksum over their edited content, since the digest is unkeyed and computed the same way regardless of who runs it. It is not a signature, not a keyed MAC, not independent witnessing, not external anchoring, not cryptographic sealing, and not strong tamper evidence in any adversarial sense. `results.json` carries no checksum under any option. Tests for this mechanism live in `tests/test_reporter.py`.

## Platform framing

Keystone Verify is standalone evaluation infrastructure. It can evaluate Engage, Counsel, or other compatible endpoints when represented by a Verify profile. It does not run inside the served path of Engage or Counsel, does not consume a shared runtime or substrate with them, and its existence does not imply that a composed execution runtime spanning these repositories exists.

## Related repos

- [`keystone-engage`](https://github.com/getkeystone/keystone-engage): independently composed conversational reference implementation.
- [`keystone-counsel`](https://github.com/getkeystone/keystone-counsel): independently composed authorization-first retrieval reference implementation.
- [`keystone-gov`](https://github.com/getkeystone/keystone-gov): governed retrieval reference implementation.
- [`keystone-ledger`](https://github.com/getkeystone/keystone-ledger): retained internal evaluation artifacts and lineage.

## Links

- Website: [getkeystone.ai](https://getkeystone.ai)
- Public evaluation ledger: [keystone-ledger](https://github.com/getkeystone/keystone-ledger)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

## License

Apache-2.0. See [LICENSE](LICENSE).
