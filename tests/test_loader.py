"""Tests for the loader module."""

import json
from pathlib import Path

from keystone_verify.loader import load_cases, load_profile


class TestLoadProfile:
    def test_load_valid_profile(self, tmp_path):
        p = tmp_path / "test.json"
        p.write_text(json.dumps({
            "name": "test",
            "base_url": "http://localhost",
            "endpoint": "/test",
        }))
        profile = load_profile(p)
        assert profile.name == "test"
        assert profile.base_url == "http://localhost"
        assert profile.endpoint == "/test"
        assert profile.response_mapping.answer_field == "message"


class TestLoadCases:
    def test_load_valid_cases(self, tmp_path):
        p = tmp_path / "cases.jsonl"
        p.write_text(
            json.dumps({"case_id": "C-001", "category": "test", "request": {"q": "hi"}, "assertions": {}}) + "\n"
            + json.dumps({"case_id": "C-002", "category": "test", "request": {"q": "bye"}, "assertions": {"severity": "tier_0"}}) + "\n"
        )
        cases = load_cases(p)
        assert len(cases) == 2
        assert cases[0].case_id == "C-001"
        assert cases[1].assertions.severity == "tier_0"

    def test_skip_comments_and_blanks(self, tmp_path):
        p = tmp_path / "cases.jsonl"
        p.write_text(
            "# comment\n"
            "\n"
            + json.dumps({"case_id": "C-001", "category": "test", "request": {}, "assertions": {}}) + "\n"
        )
        cases = load_cases(p)
        assert len(cases) == 1
