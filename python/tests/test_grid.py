"""Tests fuer die reinen Grid-/Pixel-Hilfsfunktionen."""

from __future__ import annotations

from macro_ah.grid import (
    EMPTY_STDDEV_THRESHOLD,
    GRID_COLS,
    GRID_ROWS,
    SACRIFICE_SLOT_INDEX,
    build_slot_grid,
    is_slot_empty_from_stddev,
    non_sacrifice_indices,
    stddev_average,
)


class TestBuildSlotGrid:
    def test_default_9x4_has_36_slots(self) -> None:
        grid = build_slot_grid((0, 0), (800, 300))
        assert len(grid) == GRID_COLS * GRID_ROWS == 36

    def test_corners_are_exact(self) -> None:
        grid = build_slot_grid((100, 50), (900, 350))
        assert grid[0] == (100, 50)
        assert grid[GRID_COLS - 1] == (900, 50)
        assert grid[-GRID_COLS] == (100, 350)
        assert grid[-1] == (900, 350)

    def test_row_major_order(self) -> None:
        grid = build_slot_grid((0, 0), (80, 30))
        # Zeile 0: y=0, Zeile 1: y=10, ...
        for col in range(GRID_COLS):
            assert grid[col][1] == 0
            assert grid[col + GRID_COLS][1] == 10

    def test_equidistant_spacing(self) -> None:
        grid = build_slot_grid((0, 0), (800, 300))
        dx = grid[1][0] - grid[0][0]
        dy = grid[GRID_COLS][1] - grid[0][1]
        assert dx == 100
        assert dy == 100

    def test_custom_dimensions(self) -> None:
        grid = build_slot_grid((0, 0), (20, 10), cols=3, rows=2)
        assert len(grid) == 6
        assert grid == [(0, 0), (10, 0), (20, 0), (0, 10), (10, 10), (20, 10)]


class TestEmptySlotDetection:
    def test_uniform_colour_is_empty(self) -> None:
        assert is_slot_empty_from_stddev(0.0) is True
        assert is_slot_empty_from_stddev(EMPTY_STDDEV_THRESHOLD - 0.01) is True

    def test_high_variance_is_full(self) -> None:
        assert is_slot_empty_from_stddev(EMPTY_STDDEV_THRESHOLD) is False
        assert is_slot_empty_from_stddev(50.0) is False

    def test_custom_threshold(self) -> None:
        assert is_slot_empty_from_stddev(20.0, threshold=25.0) is True
        assert is_slot_empty_from_stddev(30.0, threshold=25.0) is False


class TestStddevAverage:
    def test_three_channels(self) -> None:
        assert stddev_average([3.0, 6.0, 9.0]) == 6.0

    def test_empty_list_returns_zero(self) -> None:
        assert stddev_average([]) == 0.0


class TestNonSacrificeIndices:
    def test_excludes_default_sacrifice(self) -> None:
        indices = non_sacrifice_indices(36)
        assert SACRIFICE_SLOT_INDEX not in indices
        assert len(indices) == 35

    def test_custom_sacrifice(self) -> None:
        indices = non_sacrifice_indices(5, sacrifice_index=2)
        assert indices == [0, 1, 3, 4]
