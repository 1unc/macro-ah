"""Config-Modell (pydantic) und JSON-Persistenz."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


CALIBRATION_KEYS: tuple[str, ...] = (
    "ah_create_btn",
    "ah_inv_top_left",
    "ah_inv_bottom_right",
    "ah_green_check",
    "ah_price_field",
    "ah_confirm_btn",
    "inv_top_left",
    "inv_bottom_right",
)


CALIBRATION_STEPS: tuple[tuple[str, str], ...] = (
    ("ah_create_btn",       "/ah GUI: Button 'Auktion erstellen'"),
    ("ah_inv_top_left",     "/ah GUI: Oberster linker Inventar-Slot"),
    ("ah_inv_bottom_right", "/ah GUI: Unterer rechter Slot (Hotbar rechts)"),
    ("ah_green_check",      "/ah GUI: Gruener Haken in 'Stueck auswaehlen'"),
    ("ah_price_field",      "/ah GUI: Preis-Eingabefeld"),
    ("ah_confirm_btn",      "/ah GUI: Button 'Angebot erstellen'"),
    ("inv_top_left",        "Normales Inventar (E): oben links"),
    ("inv_bottom_right",    "Normales Inventar (E): Hotbar unten rechts"),
)


class Point(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)


class Config(BaseModel):
    points: dict[str, Point] = Field(default_factory=dict)

    def is_calibrated(self) -> bool:
        return all(k in self.points for k in CALIBRATION_KEYS)

    def point(self, key: str) -> tuple[int, int]:
        return self.points[key].as_tuple()


def _coerce_point(raw: Any) -> Point:
    """Akzeptiert Legacy [x, y] list ebenso wie {'x': ..., 'y': ...}."""
    if isinstance(raw, Point):
        return raw
    if isinstance(raw, dict):
        return Point(**raw)
    if isinstance(raw, (list, tuple)) and len(raw) == 2:
        return Point(x=int(raw[0]), y=int(raw[1]))
    raise ValueError(f"Ungueltiges Point-Format: {raw!r}")


def config_from_dict(data: dict[str, Any]) -> Config:
    raw_points = data.get("points", {}) or {}
    points = {key: _coerce_point(val) for key, val in raw_points.items()}
    return Config(points=points)


def load_config(path: Path) -> Config:
    if not path.exists():
        return Config()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return config_from_dict(data)


def save_config(cfg: Config, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cfg.model_dump(), f, indent=2)
