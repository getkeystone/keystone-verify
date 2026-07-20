# Keystone Verify

[![CI](https://github.com/getkeystone/keystone-verify/actions/workflows/ci.yml/badge.svg)](https://github.com/getkeystone/keystone-verify/actions/workflows/ci.yml)

Evaluation harness for governed AI systems.

## What this is

At the center of Keystone Verify is a judge: a pure function that takes a case, a response, a profile, and a latency measurement, and returns a result. It has no I/O and no side effects, so the same inputs always produce the same result. That makes the evaluation logic directly testable, and it is covered by unit tests.

Around that judge is an endpoint-agnostic harness. Point it at any HTTP endpoint, describe how to read that endpoint's responses in a profile, write cases with declarative assertions, and run them. The harness sends each request, scores each response with the judge, and writes structured, reproducible JSON artifacts.

It is not a benchmark toy or a prompt-by-prompt spot check. It exists to prove whether a governed AI system behaves the way its builders claim: that it refuses when it should, cites what it should, and stays within its stated limits.

## How it works

Three inputs produce one result:

- A profile (JSON) describes how to reach a target endpoint and how to map its response fields into the assertion vocabulary.
- A cases file (JSONL, one case per line) contains request payloads and declarative assertions.
- The judge scores each response against its case's assertions.

The core path is `case + response + profile = result`, and the judge that computes it is a pure function. The runner handles HTTP and latency measurement, and the reporter writes the artifacts. The judgment itself is isolated and side-effect free.

## The judge

`judge(case, response, profile, latency_ms)` returns a `Result`. It reads fields from the response using the profile's mapping, then checks the case's assertions:

- `severity` (exact match) and `severity_in` (one of a set)
- `min_length` (answer at least this long)
- `contains` (AND: all substrings present)
- `contains_any` (OR: at least one present)
- `absent` (NONE: none present)
- `has_citations` (citations list must be non-empty or empty)
- `fail_closed` (fail-closed flag matches)
- `max_latency_ms` (response within a time budget)

The judge has no I/O and no side effects. It is deterministic, and it is covered by unit tests in `tests/test_judge.py`. Because the judgment is a pure function, the evaluation logic can be tested directly, without a running endpoint.

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

The `profiles/` directory also includes vendor-neutral reference profiles for hypothetical governed endpoints, useful as templates when writing your own: `reference-agent-v0` (a generic governed conversational agent) and `reference-legal-intake-v0` (a governed legal intake agent that gathers facts and escalates to a licensed specialist rather than giving legal advice). Each ships with a companion `*.cases.jsonl` file that includes adversarial probe cases and fail-closed escalation cases.

## Output format

A run writes two structured JSON files under `results/<run_id>/`:

- `results.json`: one entry per case with the outcome, the failure detail, latency, response length, and the extracted severity, citation count, and audit hash.
- `run_metadata.json`: run-level statistics, including pass and fail counts, per-category and per-bucket breakdowns, and latency (mean and p95).

These are plain JSON files. They are reproducible and inspectable after the run, rather than trapped in terminal output. They carry no content-integrity hash or signature.

## Platform role

Keystone Verify is one of three extensions in the Keystone platform. Engage is a governed conversational agent for regulated customer interaction, and Counsel is authorization-first retrieval for regulated content. Verify runs against both, and against any other HTTP endpoint whose response shape can be described in a profile. It is the piece that turns platform claims into inspectable evidence.

## Related repos

- [`keystone-engage`](https://github.com/getkeystone/keystone-engage): governed conversational agent for regulated customer interaction.
- [`keystone-counsel`](https://github.com/getkeystone/keystone-counsel): authorization-first retrieval for regulated content.
- [`keystone-gov`](https://github.com/getkeystone/keystone-gov): governed RAG reference implementation for regulated enterprise content.
- [`keystone-ledger`](https://github.com/getkeystone/keystone-ledger): evaluation lineage and proof artifacts.

## Links

- Website: [getkeystone.ai](https://getkeystone.ai)
- Public evaluation ledger: [keystone-ledger](https://github.com/getkeystone/keystone-ledger)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

## License

Apache-2.0. See [LICENSE](LICENSE).
