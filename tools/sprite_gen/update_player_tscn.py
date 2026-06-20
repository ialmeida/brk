"""Rewires Player.tscn's texture ext_resources and SpriteFrames sub-resource to the new
multi-frame strip-sliced sprites in assets/sprites/player/processed/, replacing the old
single-frame-per-animation PNGs. Leaves every other part of the scene (scripts, the
CapsuleShape2D, the AnimationPlayer combat-timing Animation/AnimationLibrary resources,
the node tree) untouched.

Frame counts and the pose/direction list come straight from poses.py, so this stays
correct if those ever change. Safe to re-run: it locates the two blocks it owns by
content, not by line number, and regenerates them deterministically.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from poses import ANIMATION_FRAME_COUNTS, STRIP_NAMES  # noqa: E402

TSCN_PATH = Path(__file__).parent.parent.parent / "actors" / "player" / "Player.tscn"
SPRITE_DIR = "res://assets/sprites/player/processed"

FIRST_TEXTURE_ID = 14
LOOP_POSES = {"idle", "move", "charge_loop"}
LOOP_SPEED = 6.0
RELEASE_SPEED = 8.0
HURT_GAMEPLAY_LENGTH = 0.4
ATTACK_GAMEPLAY_LENGTH = 0.12

Manifest = list[tuple[str, str, int, list[int]]]  # (name, pose, frame_count, ext_ids)


def pose_and_direction(name: str) -> tuple[str, str]:
    for direction in ("down", "up", "side"):
        suffix = f"_{direction}"
        if name.endswith(suffix):
            return name[: -len(suffix)], direction
    raise ValueError(f"Can't split direction out of strip name {name!r}")


def animation_speed(pose: str, frame_count: int) -> float:
    if pose in LOOP_POSES:
        return LOOP_SPEED
    if pose == "release":
        return RELEASE_SPEED
    if pose == "hurt":
        return frame_count / HURT_GAMEPLAY_LENGTH
    return frame_count / ATTACK_GAMEPLAY_LENGTH


def format_speed(value: float) -> str:
    rounded = round(value, 3)
    return f"{rounded:.1f}" if rounded == int(rounded) else repr(rounded)


def build_frame_manifest() -> Manifest:
    manifest: Manifest = []
    next_id = FIRST_TEXTURE_ID
    for name in STRIP_NAMES:
        pose, _direction = pose_and_direction(name)
        count = ANIMATION_FRAME_COUNTS[pose]
        ids = list(range(next_id, next_id + count))
        next_id += count
        manifest.append((name, pose, count, ids))
    return manifest


def build_ext_resource_lines(manifest: Manifest) -> list[str]:
    lines = []
    for name, _pose, count, ids in manifest:
        for i, ext_id in zip(range(count), ids):
            lines.append(
                f'[ext_resource type="Texture2D" path="{SPRITE_DIR}/{name}_{i}.png" id="{ext_id}"]'
            )
    return lines


def format_frames(ids: list[int]) -> str:
    frame_strs = [f'{{\n"duration": 1.0,\n"texture": ExtResource("{ext_id}")\n}}' for ext_id in ids]
    return "[" + ", ".join(frame_strs) + "]"


def format_animation_entry(name: str, pose: str, count: int, ids: list[int]) -> str:
    loop = "true" if pose in LOOP_POSES else "false"
    speed = format_speed(animation_speed(pose, count))
    frames = format_frames(ids)
    return f'{{\n"frames": {frames},\n"loop": {loop},\n"name": &"{name}",\n"speed": {speed}\n}}'


def build_sprite_frames_lines(manifest: Manifest) -> list[str]:
    entries = [format_animation_entry(name, pose, count, ids) for name, pose, count, ids in manifest]
    block = (
        '[sub_resource type="SpriteFrames" id="SpriteFrames_player"]\n'
        f"animations = [{', '.join(entries)}]"
    )
    return block.split("\n")


def regenerate(tscn_path: Path = TSCN_PATH) -> None:
    lines = tscn_path.read_text().split("\n")
    manifest = build_frame_manifest()

    ext_start = next(i for i, l in enumerate(lines) if l.startswith('[ext_resource type="Texture2D"'))
    ext_end = ext_start
    while ext_end < len(lines) and lines[ext_end].startswith('[ext_resource type="Texture2D"'):
        ext_end += 1

    sf_start = next(i for i, l in enumerate(lines) if l.startswith('[sub_resource type="SpriteFrames"'))
    node_start = next(i for i in range(sf_start, len(lines)) if lines[i].startswith('[node name="Player"'))
    sf_end = node_start - 1  # blank separator line right before the node tree, kept as-is

    new_ext_lines = build_ext_resource_lines(manifest)
    new_sf_lines = build_sprite_frames_lines(manifest)

    new_lines = (
        lines[:ext_start]
        + new_ext_lines
        + lines[ext_end:sf_start]
        + new_sf_lines
        + lines[sf_end:]
    )

    total_textures = sum(count for _name, _pose, count, _ids in manifest)
    non_texture_ext = ext_start - 2  # header + blank line before first ext_resource... computed below instead
    # Non-texture ext_resources are everything before the first Texture2D ext_resource line,
    # minus the gd_scene header line and the blank line separating it from the resource list.
    non_texture_ext = sum(1 for l in lines[:ext_start] if l.startswith("[ext_resource"))
    sub_resource_count = sum(1 for l in lines if l.startswith("[sub_resource"))
    load_steps = non_texture_ext + total_textures + sub_resource_count + 1

    new_lines[0] = f"[gd_scene load_steps={load_steps} format=3]"

    tscn_path.write_text("\n".join(new_lines))
    print(f"Rewired {len(manifest)} animations, {total_textures} texture ext_resources "
          f"(ids {FIRST_TEXTURE_ID}-{FIRST_TEXTURE_ID + total_textures - 1}), load_steps={load_steps}")


if __name__ == "__main__":
    regenerate()
