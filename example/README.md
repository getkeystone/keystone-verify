# Example: run Keystone Verify against a public echo endpoint

These two files let you run the harness end to end without any Keystone service.

- `echo_profile.json` targets `https://httpbin.org/post`, a public request-echo
  service. httpbin reflects the POST body back in its `data` field, which the
  profile maps as the answer.
- `sample_cases.jsonl` contains five cases demonstrating the assertion
  vocabulary (`contains`, `contains_any`, `absent`, `min_length`, `severity_in`).

Run it:

```bash
keystone-verify run \
  --profile example/echo_profile.json \
  --cases example/sample_cases.jsonl \
  --output results/
```

Cases `echo-001` through `echo-004` pass. `echo-005` fails on purpose: httpbin
returns no `severity` field, so severity reads `unknown` and the assertion does
not match. That failing case shows how the harness reports a failure and writes
it to the artifacts.

This example exercises the harness mechanics against an echo service. It is not
an evaluation of a real governed system. It requires outbound network access to
`httpbin.org`.
