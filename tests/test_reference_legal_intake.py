"""Tests for the vendor-neutral reference legal intake profile.

Confirms the profile and its cases load, the case count is as expected, and the
cases include the escalation-expected cases (unauthorized-practice-of-law
boundary and urgent triage) and adversarial probe cases.
"""

from pathlib import Path

from keystone_verify.loader import load_cases, load_profile

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILE = REPO_ROOT / "profiles" / "reference-legal-intake-v0.json"
CASES = REPO_ROOT / "profiles" / "reference-legal-intake-v0.cases.jsonl"


class TestReferenceLegalIntakeProfile:
    def test_profile_loads(self):
        profile = load_profile(PROFILE)
        assert profile.name == "reference-legal-intake-v0"
        assert profile.response_mapping.answer_field == "reply"
        assert profile.response_mapping.fail_closed_field == "escalated"

    def test_case_count(self):
        cases = load_cases(CASES)
        assert len(cases) == 12

    def test_has_escalation_and_adversarial_cases(self):
        cases = load_cases(CASES)
        escalation = [c for c in cases if c.assertions.fail_closed is True]
        adversarial = [c for c in cases if c.category.startswith("adversarial")]
        assert len(escalation) >= 3
        assert len(adversarial) >= 2
