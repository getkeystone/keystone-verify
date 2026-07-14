# Keystone Verify

Standalone evaluation harness for governed AI systems.

Keystone Verify is the evaluation methodology behind the Keystone platform, extracted and released as a reusable tool. It points at any HTTP endpoint, runs declarative assertions against the responses, and produces sealed evaluation artifacts.

This is not a benchmark vanity project and not a prompt-by-prompt spot check. It is infrastructure for proving whether a governed AI system actually behaves the way its builders claim.

## What it does

Verify takes two inputs:

- a **profile** describing how to talk to a target endpoint and how to map its response fields,
- a **cases file** containing request payloads and declarative assertions.

It sends requests, scores responses, and writes sealed outputs including per-case results and aggregate run metadata.

The core judgment path is deliberately simple:

**case + response + profile = result**

That judge is a pure function with no I/O, which makes the evaluation logic directly testable and reusable.

## Why it exists

Most AI teams still evaluate systems informally:

- manual spot checks,
- screenshots in docs,
- one-off scripts,
- failing cases overwritten by the latest passing run.

That is not enough for governed AI.

Keystone Verify exists to make evaluation a first-class artifact. Systems should not only produce answers; they should produce evidence that they behave correctly, fail safely, and stay within operational constraints.

## Platform role

Keystone Verify is one extension in the broader Keystone platform:

- **Engage** proves governed conversational AI for regulated customer interaction.
- **Counsel** proves authorization-first retrieval for regulated content.
- **Verify** proves the evaluation methodology itself as a portable tool.

It is the piece that turns platform claims into inspectable evidence.

## What it evaluates

Verify supports declarative assertions for:

- severity,
- content presence,
- content alternatives,
- forbidden content,
- citations,
- fail-closed behavior,
- latency thresholds,
- cost thresholds.

This allows the same evaluation framework to test both retrieval systems and agent systems, as long as the endpoint’s response shape is described in a profile.

## Why the profile model matters

Verify does not hardcode one product’s schema.

Profiles define:

- endpoint URL,
- HTTP method,
- request shape,
- field mapping from the target response into Verify’s assertion vocabulary.

That means the same harness can evaluate different systems without rewriting the evaluator. Write a new profile, keep the same discipline.

## What makes it different

The goal is not only to measure quality. The goal is to preserve evidence.

Verify is designed for:

- reproducible eval runs,
- sealed output artifacts,
- explicit failing and passing lineage,
- portable assertions across systems,
- governance-relevant checks such as fail-closed behavior and citation presence.

In the Keystone platform itself, this methodology was strong enough to surface real bugs in the systems it evaluated. That is the standard: evaluation should be able to embarrass the system, not flatter it.

## Output artifacts

A run produces sealed artifacts such as:

- `results.json` — per-case outcomes,
- `run_metadata.json` — aggregate statistics including latency and cost reporting.

These artifacts make the result inspectable after the run, rather than leaving evaluation trapped in terminal output or dashboards.

## Current use in Keystone

Verify is used to evaluate the Keystone platform’s governed retrieval and governed agent systems. It supports the same discipline across the platform:

- failing runs preserved alongside passing runs,
- eval sets expanded through adversarial discovery,
- claims tied to proof artifacts instead of presentation copy.

## Current stack

- Python
- JSON / JSONL case definitions
- HTTP-targeted evaluation
- Pure-function judge core
- CLI workflow

## Repo goals

This repository exists to prove that evaluation for governed AI can be treated as infrastructure.

Specifically, it aims to show that:

- evaluation logic can be profile-driven instead of product-specific,
- governance-relevant assertions can be expressed declaratively,
- failing evidence can be preserved instead of overwritten,
- latency and cost can be evaluated alongside correctness,
- the methodology itself can be portable across systems and domains.

## Example CLI

```bash
keystone-verify run --profile profiles/engage.json --cases cases.jsonl --output out/
```

## Relation to the rest of Keystone

- [`keystone-engage`] uses this discipline for governed conversational agents.
- [`keystone-counsel`] uses it for authorization-first retrieval.
- [`keystone-ledger`](https://github.com/getkeystone/keystone-ledger) tracks evaluation lineage and proof artifacts.

## License

Apache 2.0
