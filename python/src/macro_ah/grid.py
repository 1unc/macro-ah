"""Reine Slot-Grid-Mathematik und Pixel-Analyse (keine OS-Zugriffe).

Diese Funktionen sind seiteneffektfrei und damit unit-testbar.
"""

from __future__ import annotations

from typing import Protocol


GRID_COLS: int = 9
GRID_ROWS: int = 4
SACRIFICE_SLOT_INDEX: int = 0  # oben-links
EMPTY_STDDEV_THRESHOLD: float = 14.0


class ImageLike(Protocol):
    """Minimales PIL.Image-Interface: Crop liefert wieder ein ImageLike."""

    def crop(self, box: tuple[int, int, int, int]) -> "ImageLike": ...


def build_slot_grid(
    top_left: tuple[int, int],
    bottom_right: tuple[int, int],
    cols: int = GRID_COLS,
    rows: int = GRID_ROWS,
) -> list[tuple[int, int]]:
    """Berechnet aus zwei Eckpunkten ein cols x rows Raster (row-major)."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    dx = (x2 - x1) / (cols - 1)
    dy = (y2 - y1) / (rows - 1)
    return [
        (int(round(x1 + col * dx)), int(round(y1 + row * dy)))
        for row in range(rows)
        for col in range(cols)
    ]


def stddev_average(stddev: list[float]) -> float:
    """Durchschnitt ueber Kanal-Stddevs (PIL liefert [r_std, g_std, b_std])."""
    if not stddev:
        return 0.0
    return sum(stddev) / len(stddev)


def is_slot_empty_from_stddev(
    avg_stddev: float,
    threshold: float = EMPTY_STDDEV_THRESHOLD,
) -> bool:
    return avg_stddev < threshold


def non_sacrifice_indices(
    grid_length: int,
    sacrifice_index: int = SACRIFICE_SLOT_INDEX,
) -> list[int]:
    return [i for i in range(grid_length) if i != sacrifice_index]
