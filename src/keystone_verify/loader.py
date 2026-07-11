"""Load profiles and cases from disk.

Profiles are single JSON files. Cases are JSONL (one case per line).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from keystone_verify.models import Case, Profile

logger = logging.getLogger(__name__)


def load_profile(path: str | Path) -> Profile:
    """Load a target profile from a JSON file."""
    path = Path(path)
    with open(path) as f:
        data = json.load(f)
    profile = Profile(**data)
    logger.info("Loaded profile: %s (%s%s)", profile.name, profile.base_url, profile.endpoint)
    return profile


def load_cases(path: str | Path) -> list[Case]:
    """Load eval cases from a JSONL file."""
    path = Path(path)
    cases: list[Case] = []
    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                cases.append(Case(**json.loads(line)))
            except Exception as e:
                logger.warning("Skipping line %d: %s", line_num, e)
    logger.info("Loaded %d eval cases from %s", len(cases), path.name)
    return cases
