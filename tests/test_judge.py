"""Tests for the Keystone Verify judge engine.

Tests assertions in isolation. No live endpoint required.
The judge is a pure function: case + response + profile -> result.
"""

import pytest

from keystone_verify.judge import judge
from keystone_verify.models import Assertions, Case, Profile, ResponseMapping


@pytest.fixture
def profile():
    return Profile(
        name="test",
        base_url="http://localhost",
        endpoint="/test",
        response_mapping=ResponseMapping(
            answer_field="message",
            severity_field="severity",
            citations_field="evidence",
            audit_hash_field="audit_hash",
            fail_closed_field="fail_closed",
        ),
    )


def _case(assertions: dict, case_id: str = "T-001") -> Case:
    return Case(
        case_id=case_id,
        category="test",
        request={"query": "test"},
        assertions=Assertions(**assertions),
    )


class TestSeverityAssertions:
    def test_exact_match_pass(self, profile):
        r = judge(_case({"severity": "tier_0"}), {"message": "ok", "severity": "tier_0"}, profile, 100)
        assert r.passed

    def test_exact_match_fail(self, profile):
        r = judge(_case({"severity": "tier_0"}), {"message": "ok", "severity": "tier_2"}, profile, 100)
        assert not r.passed
        assert "severity" in r.details

    def test_severity_in_pass(self, profile):
        r = judge(_case({"severity_in": ["tier_2", "tier_3"]}), {"message": "ok", "severity": "tier_3"}, profile, 100)
        assert r.passed

    def test_severity_in_fail(self, profile):
        r = judge(_case({"severity_in": ["tier_2", "tier_3"]}), {"message": "ok", "severity": "tier_0"}, profile, 100)
        assert not r.passed


class TestContentAssertions:
    def test_contains_pass(self, profile):
        r = judge(_case({"contains": ["hello", "world"]}), {"message": "Hello World!", "severity": "tier_0"}, profile, 100)
        assert r.passed

    def test_contains_fail(self, profile):
        r = judge(_case({"contains": ["hello", "missing"]}), {"message": "Hello World!", "severity": "tier_0"}, profile, 100)
        assert not r.passed
        assert "missing" in r.details

    def test_contains_any_pass(self, profile):
        r = judge(_case({"contains_any": ["foo", "world"]}), {"message": "Hello World!", "severity": "tier_0"}, profile, 100)
        assert r.passed

    def test_contains_any_fail(self, profile):
        r = judge(_case({"contains_any": ["foo", "bar"]}), {"message": "Hello World!", "severity": "tier_0"}, profile, 100)
        assert not r.passed

    def test_absent_pass(self, profile):
        r = judge(_case({"absent": ["forbidden"]}), {"message": "Hello World!", "severity": "tier_0"}, profile, 100)
        assert r.passed

    def test_absent_fail(self, profile):
        r = judge(_case({"absent": ["hello"]}), {"message": "Hello World!", "severity": "tier_0"}, profile, 100)
        assert not r.passed

    def test_min_length_pass(self, profile):
        r = judge(_case({"min_length": 5}), {"message": "Hello World!", "severity": "tier_0"}, profile, 100)
        assert r.passed

    def test_min_length_fail(self, profile):
        r = judge(_case({"min_length": 100}), {"message": "short", "severity": "tier_0"}, profile, 100)
        assert not r.passed


class TestCitationAssertions:
    def test_has_citations_pass(self, profile):
        r = judge(_case({"has_citations": True}), {"message": "ok", "severity": "tier_0", "evidence": [{"source": "doc.md"}]}, profile, 100)
        assert r.passed

    def test_has_citations_fail(self, profile):
        r = judge(_case({"has_citations": True}), {"message": "ok", "severity": "tier_0", "evidence": []}, profile, 100)
        assert not r.passed


class TestFailClosedAssertions:
    def test_fail_closed_expected_true(self, profile):
        r = judge(_case({"fail_closed": True}), {"message": "denied", "severity": "tier_2", "fail_closed": True}, profile, 100)
        assert r.passed

    def test_fail_closed_expected_but_false(self, profile):
        r = judge(_case({"fail_closed": True}), {"message": "ok", "severity": "tier_0", "fail_closed": False}, profile, 100)
        assert not r.passed


class TestLatencyAssertions:
    def test_latency_within_limit(self, profile):
        r = judge(_case({"max_latency_ms": 5000}), {"message": "ok", "severity": "tier_0"}, profile, 3000)
        assert r.passed

    def test_latency_exceeds_limit(self, profile):
        r = judge(_case({"max_latency_ms": 1000}), {"message": "ok", "severity": "tier_0"}, profile, 2000)
        assert not r.passed


class TestCombinedAssertions:
    def test_multiple_assertions_all_pass(self, profile):
        r = judge(
            _case({"severity": "tier_0", "min_length": 5, "contains": ["hello"]}),
            {"message": "Hello World!", "severity": "tier_0"},
            profile,
            100,
        )
        assert r.passed

    def test_multiple_assertions_one_fails(self, profile):
        r = judge(
            _case({"severity": "tier_0", "min_length": 5, "contains": ["missing"]}),
            {"message": "Hello World!", "severity": "tier_0"},
            profile,
            100,
        )
        assert not r.passed


class TestProfileMapping:
    def test_different_field_names(self):
        """Profile maps non-standard field names correctly."""
        p = Profile(
            name="custom",
            base_url="http://localhost",
            endpoint="/custom",
            response_mapping=ResponseMapping(
                answer_field="response_text",
                severity_field="risk_level",
            ),
        )
        r = judge(
            _case({"severity": "low", "contains": ["test"]}),
            {"response_text": "This is a test.", "risk_level": "low"},
            p,
            100,
        )
        assert r.passed
