"""Unit tests for config loader. @requirement REQ-001, REQ-002, REQ-003"""
import pytest

from configloader.loader import load_config


def test_loads_valid_json(tmp_path):
    """@requirement REQ-001"""
    p = tmp_path / "c.json"
    p.write_text('{"key": "value"}', encoding="utf-8")
    assert load_config(str(p)) == {"key": "value"}


def test_missing_file_raises(tmp_path):
    """@requirement REQ-002"""
    with pytest.raises(FileNotFoundError):
        load_config(str(tmp_path / "missing.json"))


def test_invalid_json_raises(tmp_path):
    """@requirement REQ-003"""
    p = tmp_path / "bad.json"
    p.write_text("{not valid", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(str(p))
