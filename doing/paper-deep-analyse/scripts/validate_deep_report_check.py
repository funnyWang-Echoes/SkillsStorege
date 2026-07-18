#!/usr/bin/env python3
"""
校验最终 deep-report-check.json，拒绝草稿占位符冒充最终验收。
"""

import json
import re
import sys
from pathlib import Path


PLACEHOLDER_PATTERN = re.compile(r"(TODO\s*[:：]|待补\s*[:：]|占位\s*[:：]|^placeholder\s*[:：]|placeholder\s*[:：])", re.I)


def walk_strings(value, path="$"):
    """递归枚举 JSON 中的字符串值"""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, f"{path}.{key}")


def fallback_validate(data: dict) -> list[str]:
    """在 jsonschema 不可用时做最关键的最终件校验"""
    errors: list[str] = []
    if data.get("manual_fields_required"):
        errors.append("manual_fields_required must be absent or empty in final deep-report-check.json.")
    for path, text in walk_strings(data):
        if PLACEHOLDER_PATTERN.search(text):
            errors.append(f"placeholder text remains at {path}.")
    if data.get("subagent_review", {}).get("supported") is True:
        review = data.get("subagent_review", {})
        if review.get("attempted") is not True:
            errors.append("subagent_review.supported=true requires attempted=true.")
        if review.get("findings_count", 0) < 3:
            errors.append("subagent_review.supported=true requires findings_count>=3.")
    return errors


def main() -> int:
    """校验 deep-report-check JSON"""
    if len(sys.argv) not in (2, 3):
        print("Usage: python validate_deep_report_check.py <deep-report-check.json> [schema.json]")
        return 1

    check_path = Path(sys.argv[1])
    schema_path = Path(sys.argv[2]) if len(sys.argv) == 3 else Path(__file__).resolve().parents[1] / "schemas" / "deep-report-check.schema.json"
    data = json.loads(check_path.read_text(encoding="utf-8"))
    errors = fallback_validate(data)

    try:
        import jsonschema
    except ImportError:
        if not errors:
            print("Warning: jsonschema is not installed; fallback validation passed.")
            return 0
    else:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        for error in validator.iter_errors(data):
            errors.append(f"{error.json_path}: {error.message}")

    if errors:
        print("deep-report-check validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("deep-report-check validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
