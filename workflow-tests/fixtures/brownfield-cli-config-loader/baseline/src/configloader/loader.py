"""JSON configuration loader."""
import json
from pathlib import Path


def load_config(path):
    """Load a JSON config file and return as dict.

    Raises FileNotFoundError if path does not exist.
    Raises ValueError if JSON is malformed.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e
