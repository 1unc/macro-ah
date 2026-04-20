"""Tests fuer Config-Modell und JSON-Persistenz (inkl. Legacy-Format)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from macro_ah.config import (
    CALIBRATION_KEYS,
    Config,
    Point,
    config_from_dict,
    load_config,
    save_config,
)


class TestPoint:
    def test_valid_point(self) -> None:
        p = Point(x=120, y=240)
        assert p.as_tuple() == (120, 240)

    def test_negative_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Point(x=-1, y=0)


class TestConfigFromDict:
    def test_empty(self) -> None:
        cfg = config_from_dict({})
        assert cfg.points == {}
        assert cfg.is_calibrated() is False

    def test_modern_dict_format(self) -> None:
        data = {"points": {"ah_create_btn": {"x": 100, "y": 200}}}
        cfg = config_from_dict(data)
        assert cfg.points["ah_create_btn"] == Point(x=100, y=200)

    def test_legacy_list_format_migrated(self) -> None:
        data = {"points": {"ah_create_btn": [100, 200]}}
        cfg = config_from_dict(data)
        assert cfg.point("ah_create_btn") == (100, 200)

    def test_mixed_formats_accepted(self) -> None:
        data = {
            "points": {
                "ah_create_btn": [10, 20],
                "inv_top_left": {"x": 30, "y": 40},
            }
        }
        cfg = config_from_dict(data)
        assert cfg.point("ah_create_btn") == (10, 20)
        assert cfg.point("inv_top_left") == (30, 40)

    def test_invalid_format_raises(self) -> None:
        with pytest.raises(ValueError, match="Point"):
            config_from_dict({"points": {"foo": "bar"}})


class TestIsCalibrated:
    def test_all_keys_present(self) -> None:
        points = {k: Point(x=i, y=i) for i, k in enumerate(CALIBRATION_KEYS)}
        cfg = Config(points=points)
        assert cfg.is_calibrated() is True

    def test_missing_key(self) -> None:
        points = {k: Point(x=0, y=0) for k in CALIBRATION_KEYS[:-1]}
        cfg = Config(points=points)
        assert cfg.is_calibrated() is False


class TestSaveLoadRoundtrip:
    def test_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "config.json"
        cfg_in = Config(points={k: Point(x=i * 10, y=i * 20) for i, k in enumerate(CALIBRATION_KEYS)})
        save_config(cfg_in, path)

        cfg_out = load_config(path)
        assert cfg_out.is_calibrated()
        for k in CALIBRATION_KEYS:
            assert cfg_out.points[k] == cfg_in.points[k]

    def test_load_missing_returns_empty(self, tmp_path: Path) -> None:
        cfg = load_config(tmp_path / "does_not_exist.json")
        assert cfg.points == {}

    def test_load_legacy_file(self, tmp_path: Path) -> None:
        path = tmp_path / "legacy.json"
        legacy = {"points": {k: [i, i * 2] for i, k in enumerate(CALIBRATION_KEYS)}}
        path.write_text(json.dumps(legacy), encoding="utf-8")

        cfg = load_config(path)
        assert cfg.is_calibrated()
        assert cfg.point("ah_create_btn") == (0, 0)
        assert cfg.point("inv_bottom_right") == (7, 14)
