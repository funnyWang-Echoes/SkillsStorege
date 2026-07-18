#!/usr/bin/env python3
"""
Single source of truth for analysis_profile thresholds.

All scripts (generate_html.py, collect_report_counts.py, check_html_render.py)
import PROFILE_RULES from here instead of defining their own copy.

Usage:
    from thresholds import PROFILE_RULES, get_rules
    rules = get_rules("standard")
    min_cards = rules["reading_cards"]
"""
from __future__ import annotations

import json
from pathlib import Path

_THRESHOLDS_PATH = Path(__file__).resolve().parent.parent / "schemas" / "thresholds.json"

PROFILE_RULES: dict[str, dict] = {}


def _load() -> dict[str, dict]:
    global PROFILE_RULES
    if not PROFILE_RULES:
        data = json.loads(_THRESHOLDS_PATH.read_text(encoding="utf-8"))
        PROFILE_RULES = {
            k: v for k, v in data.items() if not k.startswith("_")
        }
    return PROFILE_RULES


def get_rules(profile: str) -> dict:
    rules = _load()
    if profile not in rules:
        raise ValueError(f"Unknown analysis_profile: {profile}. Use short, standard, or long.")
    return rules[profile]


def all_profiles() -> dict[str, dict]:
    return _load()


if __name__ == "__main__":
    import sys
    rules = all_profiles()
    for profile, vals in rules.items():
        print(f"\n[{profile}]")
        for k, v in sorted(vals.items()):
            print(f"  {k}: {v}")
