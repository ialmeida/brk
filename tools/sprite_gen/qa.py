"""Automated acceptance checks for processed sprite frames, per SPRITE_REGEN_BRIEF.md.

These cover the auto-checkable criteria only (dimensions, palette, key fringe, baseline,
height). The brief's identity/motion criteria require a human to look at the sheet/GIF --
no check here substitutes for that.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from palette import RGB
from strips import KEY_COLOR_THRESHOLD, MAGENTA

FILL_RATIO_THRESHOLD = 0.97

# Head-dome proportion check. The hair forms a solid dark dome at the very top of the
# silhouette; its diameter (widest hair row in the top band) over the silhouette height is a
# direction-stable proxy for head-to-body ratio that catches the head-shrink the total-height
# check misses. Targets are derived per-direction from the approved turnaround (no magic
# constant); a strip FAILs if its largest-headed frame is more than HEAD_RATIO_TOL below the
# matching target. Calibrated against the committed processed frames: at tol 0.18 this fails
# the clearly head-shrunken strips (release_side, hurt_side, basic_kick_3_side, master_2_up,
# master_3_up) while passing the known-good ones. The mildest drift (e.g. move_side, move_up)
# is not separable from accepted strips by head diameter alone, so it is left to the sibling
# image anchor (poses.sibling_of) to prevent rather than to this check to catch -- the measured
# ratio is always reported so even passing strips carry a visible proportion signal.
HEAD_DOME_TOP_BAND = 12
HEAD_HAIR_COLOR_DIST = 40
HEAD_RATIO_TOL = 0.18


def head_diameter(frame: Image.Image, hair_colors: list[RGB],
                  top_band: int = HEAD_DOME_TOP_BAND,
                  color_dist: int = HEAD_HAIR_COLOR_DIST) -> tuple[int, int]:
    """Hair-dome diameter and silhouette height for one frame, in pixels.

    Diameter = the most hair-colored pixels in any single row within the top `top_band` rows
    of the silhouette (the dome band, before the face/shoulders). Returns (0, 0) for an empty
    frame and (0, silh) when no hair is found.
    """
    arr = np.array(frame.convert("RGBA"))
    opaque = arr[..., 3] > 0
    rows = np.where(opaque.any(axis=1))[0]
    if rows.size == 0:
        return 0, 0
    top, bottom = int(rows[0]), int(rows[-1])
    silh = bottom - top + 1
    rgb = arr[..., :3].astype(np.int32)
    hair = np.array(hair_colors, dtype=np.int32)
    dist_sq = np.min(((rgb[:, :, None, :] - hair[None, None, :, :]) ** 2).sum(axis=-1), axis=-1)
    is_hair = opaque & (dist_sq < color_dist * color_dist)
    band = is_hair[top:min(top + top_band, bottom + 1)]
    diameter = int(band.sum(axis=1).max()) if band.size else 0
    return diameter, silh


def head_ratio(frame: Image.Image, hair_colors: list[RGB]) -> float | None:
    diameter, silh = head_diameter(frame, hair_colors)
    if silh <= 0 or diameter <= 0:
        return None
    return diameter / silh


def head_targets_from_turnaround(turnaround_img: Image.Image, n_cells: int,
                                 directions: list[str], hair_colors: list[RGB]) -> dict[str, float]:
    """Per-direction target head-dome ratio, derived from the approved turnaround sheet.

    The turnaround is one cell per direction (down/up/side) in the same neutral pose, so each
    cell's ratio is that direction's ground-truth proportion for this character.
    """
    w, h = turnaround_img.size
    cell_w = w // n_cells
    targets: dict[str, float] = {}
    for i, direction in enumerate(directions):
        cell = turnaround_img.crop((i * cell_w, 0, (i + 1) * cell_w, h))
        ratio = head_ratio(cell, hair_colors)
        if ratio is not None:
            targets[direction] = ratio
    return targets


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
    head_ratio: float | None = None
    head_target: float | None = None


def check_strip(frames: list[Image.Image], anim_name: str, direction: str,
                 key_color: RGB = MAGENTA, head_targets: dict[str, float] | None = None,
                 hair_colors: list[RGB] | None = None, head_ratio_tol: float = HEAD_RATIO_TOL,
                 **kwargs) -> QAResult:
    failures = []
    for i, frame in enumerate(frames):
        failures.extend(f"frame {i}: {failure}"
                         for failure in check_frame(frame, key_color=key_color, **kwargs))

    strip_head_ratio: float | None = None
    target: float | None = None
    if head_targets is not None and hair_colors is not None:
        # Use the largest-headed frame: action poses can partly occlude the dome (a raised arm
        # in front of the face), which only ever lowers the measured diameter, so the max over
        # frames is the best unoccluded estimate of the strip's true head size.
        ratios = [r for r in (head_ratio(frame, hair_colors) for frame in frames) if r is not None]
        if ratios:
            strip_head_ratio = max(ratios)
            target = head_targets.get(direction)
            if target is not None and strip_head_ratio < target * (1 - head_ratio_tol):
                failures.append(
                    f"head-dome ratio {strip_head_ratio:.3f} below {target * (1 - head_ratio_tol):.3f} "
                    f"(target {target:.3f} for '{direction}' from turnaround, tol "
                    f"{head_ratio_tol:.0%}) -- head reads too small/narrow vs the turnaround")

    return QAResult(anim_name=anim_name, direction=direction, passed=not failures,
                    failures=failures, head_ratio=strip_head_ratio, head_target=target)


def write_report(results: list[QAResult], out_path: Path) -> None:
    n_failed = sum(1 for r in results if not r.passed)
    lines = [f"QA report: {len(results)} strip(s), {n_failed} failed", ""]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"[{status}] {r.anim_name}_{r.direction}")
        if r.head_ratio is not None:
            target = f"{r.head_target:.3f}" if r.head_target is not None else "n/a"
            lines.append(f"    head-dome ratio {r.head_ratio:.3f} (target {target})")
        lines.extend(f"    - {failure}" for failure in r.failures)
    out_path.write_text("\n".join(lines) + "\n")
