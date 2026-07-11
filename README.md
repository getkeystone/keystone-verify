# Keystone Verify

Standalone evaluation harness for governed AI systems. Points at any RAG or agent endpoint over HTTP. Runs declarative assertions. Produces sealed evaluation artifacts.

Part of the [Keystone Applied Intelligence](https://getkeystone.ai) platform.

## What this is

Verify is the evaluation methodology from Keystone, extracted and released as a reusable tool. You give it a target endpoint and a set of cases. It sends the queries, scores the responses, and produces sealed artifacts with cost-accuracy joint reporting.

The methodology found four real bugs in keystone-engage's own system. This is that methodology as a tool you can run against yours.

## Quick start

```bash
uv sync
keystone-verify run --profile profiles/engage.json --cases cases.jsonl
```

## How it works

**Profiles** describe how to talk to a target endpoint: URL, HTTP method, and a field mapping that translates the target's response shape into Verify's generic assertion vocabulary.

**Cases** are JSONL files where each line is a request payload plus declarative assertions (severity, content, citations, fail-closed, latency, cost).

**The judge** is a pure function: case + response + profile = result. No I/O. Fully testable in isolation.

**Sealed artifacts** follow the same format used by keystone-engage and keystone-counsel: `results.json` with per-case outcomes, `run_metadata.json` with aggregate statistics.

## Assertions

| Assertion | Semantics |
|-----------|-----------|
| `severity` | Exact match on severity field |
| `severity_in` | Pass if severity is any of the listed values |
| `min_length` | Answer must be at least N characters |
| `contains` | AND: all strings must be present (case-insensitive) |
| `contains_any` | OR: at least one string must be present |
| `absent` | NONE of these strings may be present |
| `has_citations` | Citations list must be non-empty (true) or empty (false) |
| `fail_closed` | fail_closed field must match |
| `max_latency_ms` | Response must arrive within N milliseconds |
| `max_cost_cents` | Cost must not exceed N cents |

## Profiles

Profiles are JSON files in `profiles/`. Two reference profiles are included:

- `engage.json`: targets keystone-engage (/engage endpoint, `message`/`severity`/`evidence` fields)
- `counsel.json`: targets keystone-counsel (/counsel endpoint, `answer`/`severity`/`citations` fields)

Write your own profile to target any HTTP endpoint.

## Platform

Verify is the third extension in the Keystone platform alongside [keystone-engage](https://github.com/getkeystone/keystone-engage) and [keystone-counsel](https://github.com/getkeystone/keystone-counsel). Together they demonstrate the orchestration discipline: one platform, three agent types, shared substrate, independent eval ledgers.
