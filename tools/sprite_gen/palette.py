"""Locked color palette used to snap every generated sprite pixel to a fixed set of colors."""

from __future__ import annotations

import json
from pathlib import Path

PALETTE_PATH = Path(__file__).parent / "palette.json"

RGB = tuple[int, int, int]


def load_palette(path: Path = PALETTE_PATH) -> list[RGB]:
    data = json.loads(path.read_text())
    return [_hex_to_rgb(h) for h in data["flat"]]


def _hex_to_rgb(h: str) -> RGB:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def nearest_palette_color(rgb: RGB, palette: list[RGB]) -> RGB:
    return min(palette, key=lambda p: sum((a - b) ** 2 for a, b in zip(rgb, p)))
