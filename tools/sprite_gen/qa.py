"""Automated acceptance checks for processed sprite frames, per SPRITE_REGEN_BRIEF.md.

These cover the auto-checkable criteria only (dimensions, palette, key fringe, baseline,
height). The brief's identity/motion criteria require a human to look at the sheet/GIF --
no check here substitutes for that.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from palette import RGB
from strips import KEY_COLOR_THRESHOLD, MAGENTA

FILL_RATIO_THRESHOLD = 0.97


def check_frame(frame: Image.Image, canvas_w: int, canvas_h: int, baseline_y: int,
                 target_char_height: int, palette: list[RGB], align: str = "feet",
                 height_tolerance: int = 3, baseline_tolerance: int = 1,
                 key_color: RGB = MAGENTA) -> list[str]:
    failures: list[str] = []

    if frame.size != (canvas_w, canvas_h):
        failures.append(f"size {frame.size} != expected ({canvas_w}, {canvas_h})")

    rgba = frame.convert("RGBA")
    pixels = rgba.load()
    w, h = rgba.size
    palette_set = set(palette)
    key_threshold_sq = KEY_COLOR_THRESHOLD ** 2
    off_palette = 0
    key_fringe = 0
    opaque_total = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            opaque_total += 1
            if (r, g, b) not in palette_set:
                off_palette += 1
            dist_sq = sum((c1 - c2) ** 2 for c1, c2 in zip((r, g, b), key_color))
            if dist_sq < key_threshold_sq:
                key_fringe += 1
    if off_palette:
        failures.append(f"{off_palette} opaque pixel(s) not in palette")
    if key_fringe:
        failures.append(f"{key_fringe} opaque pixel(s) within key-color distance (fringe)")

    bbox = rgba.getbbox()
    if bbox is None:
        failures.append("frame has no visible content")
        return failures

    bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    fill_ratio = opaque_total / bbox_area if bbox_area else 0.0
    if fill_ratio > FILL_RATIO_THRESHOLD:
        failures.append(
            f"bbox fill ratio {fill_ratio:.2f} > {FILL_RATIO_THRESHOLD} -- looks like an "
            f"unkeyed background block, not a character silhouette")

    if align == "feet":
        bbox_bottom = bbox[3]
        bbox_height = bbox[3] - bbox[1]
        if abs(bbox_bottom - baseline_y) > baseline_tolerance:
            failures.append(
                f"baseline off by {bbox_bottom - baseline_y}px "
                f"(bbox_bottom={bbox_bottom}, baseline_y={baseline_y})")
        if abs(bbox_height - target_char_height) > height_tolerance:
            failures.append(
                f"silhouette height {bbox_height}px off target {target_char_height}px "
                f"by more than {height_tolerance}px")

    return failures


@dataclass
class QAResult:
    anim_name: str
    direction: str
    passed: bool
    failures: list[str] = field(default_factory=list)


def check_strip(frames: list[Image.Image], anim_name: str, direction: str,
                 key_color: RGB = MAGENTA, **kwargs) -> QAResult:
    failures = []
    for i, frame in enumerate(frames):
        failures.extend(f"frame {i}: {failure}"
                         for failure in check_frame(frame, key_color=key_color, **kwargs))
    return QAResult(anim_name=anim_name, direction=direction, passed=not failures, failures=failures)


def write_report(results: list[QAResult], out_path: Path) -> None:
    n_failed = sum(1 for r in results if not r.passed)
    lines = [f"QA report: {len(results)} strip(s), {n_failed} failed", ""]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"[{status}] {r.anim_name}_{r.direction}")
        lines.extend(f"    - {failure}" for failure in r.failures)
    out_path.write_text("\n".join(lines) + "\n")
