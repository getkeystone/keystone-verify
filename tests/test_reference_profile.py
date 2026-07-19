"""Tests for the vendor-neutral reference conversational agent profile.

Confirms the reference profile and its cases load, and that the cases include
the required adversarial probe cases and fail-closed cases.
"""

from pathlib import Path

from keystone_verify.loader import load_cases, load_profile

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILE = REPO_ROOT / "profiles" / "reference-agent-v0.json"
CASES = REPO_ROOT / "profiles" / "reference-agent-v0.cases.jsonl"


class TestReferenceAgentProfile:
    def test_profile_loads(self):
        profile = load_profile(PROFILE)
        assert profile.name == "reference-agent-v0"
        assert profile.response_mapping.answer_field == "reply"
        assert profile.response_mapping.fail_closed_field == "refused"

    def test_cases_load(self):
        cases = load_cases(CASES)
        assert len(cases) >= 6

    def test_has_adversarial_and_fail_closed_cases(self):
        cases = load_cases(CASES)
        adversarial = [c for c in cases if c.category.startswith("adversarial")]
        fail_closed = [c for c in cases if c.category == "fail-closed"]
        assert len(adversarial) >= 2
        assert len(fail_closed) >= 2
