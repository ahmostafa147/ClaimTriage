"""Storage utilities for audit logs, hashing, and file operations."""
import hashlib
import json
from pathlib import Path
from typing import Any
import shutil


def sha256_file(file_path: str | Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(data: dict[str, Any]) -> str:
    """Compute SHA256 hash of JSON data."""
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def append_jsonl(file_path: str | Path, data: dict[str, Any]) -> None:
    """Append a JSON line to a file."""
    with open(file_path, "a") as f:
        f.write(json.dumps(data) + "\n")


def read_jsonl(file_path: str | Path) -> list[dict[str, Any]]:
    """Read all lines from a JSONL file."""
    if not Path(file_path).exists():
        return []
    lines = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(json.loads(line))
    return lines


def load_yaml_rules(rules_path: str | Path = "rules.yaml") -> dict[str, Any]:
    """Load rules from YAML file."""
    import yaml
    with open(rules_path, "r") as f:
        return yaml.safe_load(f)


def save_yaml_rules(rules_content: str, rules_path: str | Path = "rules.yaml") -> None:
    """Save rules YAML content to file and backup previous version."""
    rules_path = Path(rules_path)
    if rules_path.exists():
        backup_path = rules_path.parent / "last_rules.yaml"
        shutil.copy(rules_path, backup_path)

    with open(rules_path, "w") as f:
        f.write(rules_content)


def get_rules_diff(rules_path: str | Path = "rules.yaml") -> dict[str, Any]:
    """Get diff between current and last rules."""
    rules_path = Path(rules_path)
    backup_path = rules_path.parent / "last_rules.yaml"

    diff = {"changed": False, "old": None, "new": None}

    if rules_path.exists():
        with open(rules_path) as f:
            diff["new"] = f.read()

    if backup_path.exists():
        with open(backup_path) as f:
            diff["old"] = f.read()
        diff["changed"] = diff["old"] != diff["new"]

    return diff
