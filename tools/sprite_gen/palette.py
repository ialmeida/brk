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


def _luma(rgb: RGB) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


HAIR_LUMA_THRESHOLD = 60.0


def derive_hair_colors(palette: list[RGB], luma_threshold: float = HAIR_LUMA_THRESHOLD) -> list[RGB]:
    """The dark subset of the palette that the hair dome can render as, used by the QA head check.

    The hair forms the solid dark mass at the very top of the silhouette. Detecting it by
    luminance keeps this data-driven (no hand-labeled ramp), so it generalizes to future
    characters' palettes. The threshold is deliberately broad: Gemini sometimes renders the
    hair as a dark *navy/blue-gray* rather than pure black, so it palette-snaps onto the dark
    denim ramp (e.g. #222B31, #263643) instead of the near-black outline ramp -- a near-black-
    only set undercounts the dome badly on those strips. luma<60 captures the near-black ramp
    plus the dark-navy entries (and the darkest sneaker grey). Including non-hair dark colors is
    harmless because the head check only measures the top dome band, where no legs/shoes appear.
    If a future palette makes this ambiguous, set Character.hair_colors explicitly to override.
    """
    hair = [c for c in palette if _luma(c) < luma_threshold]
    if not hair:  # degenerate palette -- fall back to the single darkest color
        hair = [min(palette, key=_luma)]
    return hair
