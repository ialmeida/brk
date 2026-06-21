#!/usr/bin/env python3
"""Generate Player animation sprite strips via Gemini's image model ("Nano Banana Pro").

Reads GEMINI_API_KEY from the environment only -- never pass it as a CLI flag.

Workflow:
    1. turnaround          -- generate the master reference turnaround (down/up/side)
    2. approve-turnaround   -- post-process the approved raw turnaround into the style-lock reference
    3. strip --canary       -- generate the two canary strips (idle_down, move_side) for review
    4. strip --all          -- generate the remaining strips once the canaries are approved

See tools/sprite_gen/README.md for the full walkthrough.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import time
from pathlib import Path

from PIL import Image

import gif
import poses
import qa
import strips
from characters import DEFAULT_CHARACTER, get_character
from poses import (
    ANIMATION_ALIGN,
    ANIMATION_FRAME_COUNTS,
    CANARY_NAMES,
    DEFAULT_ALIGN,
    SIBLING_LOCK_INSTRUCTION,
    STRIP_NAMES,
    STYLE_LOCK_INSTRUCTION,
    build_prompts,
    sibling_of,
)

DEFAULT_MODEL = "gemini-3-pro-image"
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 3

CANVAS_W = 48
CANVAS_H = 64
BASELINE_Y = 60
TARGET_CHAR_HEIGHT = 52
TURNAROUND_CELLS = 3
STRIP_ASPECT_RATIO = "21:9"
STRIP_IMAGE_SIZE = "2K"

# qa_sheets is character-agnostic (review artifacts only, gitignored); the per-character
# input/output paths and palette come from the resolved Character (see characters.py).
QA_DIR = Path("tools/sprite_gen/qa_sheets")
STRIP_NAMES_SET = set(STRIP_NAMES)


def extract_image_from_response(response) -> Image.Image:
    for part in response.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline is not None and inline.data:
            return Image.open(io.BytesIO(inline.data))
    raise RuntimeError("No image part found in Gemini response")


def generate_one(client, model: str, prompt: str, reference_img: Image.Image,
                  base_img: Image.Image | None, sibling_img: Image.Image | None = None,
                  aspect_ratio: str | None = None,
                  image_size: str | None = None) -> Image.Image:
    from google.genai import types

    # Images must be ordered so the instruction text's references line up: (1) likeness photo,
    # (2) turnaround style-lock, (3) sibling proportion anchor.
    contents: list = [reference_img]
    instructions: list[str] = []
    if base_img is not None:
        contents.append(base_img)
        instructions.append(STYLE_LOCK_INSTRUCTION)
    if sibling_img is not None and base_img is not None:
        contents.append(sibling_img)
        instructions.append(SIBLING_LOCK_INSTRUCTION)
    if instructions:
        contents.append("\n\n".join([*instructions, prompt]))
    else:
        contents.append(prompt)

    image_config = None
    if aspect_ratio or image_size:
        image_config = types.ImageConfig(aspect_ratio=aspect_ratio, image_size=image_size)
    config = types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"],
                                          image_config=image_config)

    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            response = client.models.generate_content(model=model, contents=contents, config=config)
            return extract_image_from_response(response)
        except Exception as exc:  # noqa: BLE001 - report and retry, don't crash the whole batch
            last_error = exc
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    raise RuntimeError(f"Generation failed after retries: {last_error}")


def make_client():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        sys.exit("GEMINI_API_KEY is not set. Export it in your shell first -- never pass it as a flag.")
    try:
        from google import genai
    except ImportError:
        sys.exit("google-genai is not installed. Run: pip install -r tools/sprite_gen/requirements.txt")
    return genai.Client(api_key=api_key)


def cmd_turnaround(args: argparse.Namespace) -> int:
    if not args.reference.exists():
        sys.exit(f"Reference photo not found: {args.reference}")
    char = get_character(args.character)
    out = args.out or char.reference_dir / "turnaround_raw.png"
    turnaround_prompt = build_prompts(char.likeness_prose)["turnaround_prompt"]
    client = make_client()
    reference_img = Image.open(args.reference).convert("RGB")

    print("Generating master turnaround (down / up / side)...")
    raw = generate_one(client, args.model, turnaround_prompt, reference_img, None,
                        aspect_ratio=STRIP_ASPECT_RATIO, image_size=STRIP_IMAGE_SIZE)
    out.parent.mkdir(parents=True, exist_ok=True)
    raw.convert("RGBA").save(out)
    print(f"Wrote {out} ({raw.size[0]}x{raw.size[1]}) -- inspect it by eye against the "
          f"identity and perspective checklists in SPRITE_REGEN_BRIEF.md, then run "
          f"approve-turnaround once it looks right.")
    return 0


def cmd_approve_turnaround(args: argparse.Namespace) -> int:
    char = get_character(args.character)
    raw = args.raw or char.reference_dir / "turnaround_raw.png"
    out = args.out or char.turnaround_path
    if not raw.exists():
        sys.exit(f"Raw turnaround not found: {raw}")
    palette = char.load_palette()
    raw_img = Image.open(raw).convert("RGBA")
    frames, key_color = strips.process_strip(raw_img, n_cells=TURNAROUND_CELLS,
                                              target_char_height=TARGET_CHAR_HEIGHT,
                                              canvas_w=CANVAS_W, canvas_h=CANVAS_H,
                                              baseline_y=BASELINE_Y, palette=palette, align="feet")
    print(f"Sampled background key color: {key_color}")
    sheet = Image.new("RGBA", (CANVAS_W * len(frames), CANVAS_H), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i * CANVAS_W, 0), frame)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"Wrote {out} (down/up/side, {CANVAS_W}x{CANVAS_H} each) -- this is now the "
          f"style-lock reference fed into every later strip generation.")
    return 0


def build_strip_list(args: argparse.Namespace) -> list[str]:
    if args.all:
        return list(STRIP_NAMES)
    if args.canary:
        return list(CANARY_NAMES)
    for name in args.only:
        if name not in STRIP_NAMES_SET:
            sys.exit(f"Unknown strip name: {name!r}. Valid names: {', '.join(STRIP_NAMES)}")
    return args.only


def load_sibling_anchor(char, name: str) -> Image.Image | None:
    """The proportion-anchor image for `name` (see poses.sibling_of), or None.

    Prefer the high-res raw sibling strip (best visual reference) when it's present locally;
    otherwise assemble the committed processed frames into a sheet. Either is fine as a
    proportion/scale anchor; missing both just means we fall back to the turnaround alone.
    """
    sibling = sibling_of(name)
    if sibling is None:
        return None
    raw_path = char.raw_dir / f"{sibling}_strip.png"
    if raw_path.exists():
        return Image.open(raw_path).convert("RGBA")
    n_frames = ANIMATION_FRAME_COUNTS[sibling.rsplit("_", 1)[0]]
    frame_paths = [char.out_dir / f"{sibling}_{i}.png" for i in range(n_frames)]
    if all(p.exists() for p in frame_paths):
        frames = [Image.open(p).convert("RGBA") for p in frame_paths]
        return gif.build_sheet(frames)
    print(f"  (sibling anchor {sibling} not found on disk -- using turnaround only for {name})")
    return None


def process_and_save_strip(name: str, raw_strip: Image.Image, palette: list,
                            out_paths: list[Path], hair_colors: list | None = None,
                            head_targets: dict | None = None) -> tuple[str, qa.QAResult]:
    pose, direction = name.rsplit("_", 1)
    n_frames = ANIMATION_FRAME_COUNTS[pose]
    align = ANIMATION_ALIGN.get(pose, DEFAULT_ALIGN)

    frames, key_color = strips.process_strip(raw_strip, n_cells=n_frames,
                                               target_char_height=TARGET_CHAR_HEIGHT,
                                               canvas_w=CANVAS_W, canvas_h=CANVAS_H,
                                               baseline_y=BASELINE_Y, palette=palette,
                                               align=align)
    for path, frame in zip(out_paths, frames):
        frame.save(path)

    gif.save_sheet(frames, QA_DIR / f"{name}_sheet.png")
    gif.save_loop_gif(frames, QA_DIR / f"{name}.gif")

    result = qa.check_strip(frames, pose, direction, canvas_w=CANVAS_W,
                             canvas_h=CANVAS_H, baseline_y=BASELINE_Y,
                             target_char_height=TARGET_CHAR_HEIGHT, palette=palette,
                             align=align, key_color=key_color,
                             hair_colors=hair_colors, head_targets=head_targets)
    status = "ok" if result.passed else f"ok (QA FAILED: {len(result.failures)} issue(s))"
    return status, result


def compute_head_targets(turnaround_path: Path, hair_colors: list) -> dict | None:
    """Per-direction target head ratios from the approved turnaround, or None if it's missing.

    Returning None disables the head check gracefully rather than crashing the batch.
    """
    if not turnaround_path.exists():
        print(f"  (turnaround {turnaround_path} not found -- skipping head-ratio QA check)")
        return None
    turnaround_img = Image.open(turnaround_path).convert("RGBA")
    return qa.head_targets_from_turnaround(turnaround_img, TURNAROUND_CELLS,
                                           poses.TURNAROUND_DIRECTIONS, hair_colors)


def cmd_strip(args: argparse.Namespace) -> int:
    char = get_character(args.character)
    turnaround_path = args.turnaround or char.turnaround_path
    if not args.reference.exists():
        sys.exit(f"Reference photo not found: {args.reference}")
    if not turnaround_path.exists():
        sys.exit(f"Approved turnaround not found: {turnaround_path}. Run the turnaround and "
                  f"approve-turnaround commands first.")

    client = make_client()
    reference_img = Image.open(args.reference).convert("RGB")
    turnaround_img = Image.open(turnaround_path).convert("RGBA")
    palette = char.load_palette()
    hair_colors = char.resolve_hair_colors()
    head_targets = qa.head_targets_from_turnaround(turnaround_img, TURNAROUND_CELLS,
                                                   poses.TURNAROUND_DIRECTIONS, hair_colors)
    strip_prompts = build_prompts(char.likeness_prose)["strip_prompts"]

    names = build_strip_list(args)
    char.raw_dir.mkdir(parents=True, exist_ok=True)
    char.out_dir.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    results: dict[str, str] = {}
    qa_results: list[qa.QAResult] = []
    for name in names:
        n_frames = ANIMATION_FRAME_COUNTS[name.rsplit("_", 1)[0]]
        out_paths = [char.out_dir / f"{name}_{i}.png" for i in range(n_frames)]

        if args.skip_existing and all(p.exists() for p in out_paths):
            results[name] = "skipped (already exists)"
            continue

        print(f"Generating strip {name} ({n_frames} frames)...")
        try:
            sibling_img = load_sibling_anchor(char, name)
            raw_strip = generate_one(client, args.model, strip_prompts[name], reference_img,
                                      turnaround_img, sibling_img=sibling_img,
                                      aspect_ratio=STRIP_ASPECT_RATIO,
                                      image_size=STRIP_IMAGE_SIZE)
            raw_strip.convert("RGBA").save(char.raw_dir / f"{name}_strip.png")

            status, result = process_and_save_strip(name, raw_strip, palette, out_paths,
                                                     hair_colors=hair_colors,
                                                     head_targets=head_targets)
            qa_results.append(result)
            results[name] = status
        except Exception as exc:  # noqa: BLE001 - continue the batch on per-strip failure
            results[name] = f"FAILED: {exc}"

    print("\n--- Summary ---")
    failures = 0
    for name, status in results.items():
        print(f"{name:20s} {status}")
        if status.startswith("FAILED") or "QA FAILED" in status:
            failures += 1

    if qa_results:
        report_path = QA_DIR / "qa_report.txt"
        qa.write_report(qa_results, report_path)
        print(f"\nQA report written to {report_path}")
        print(f"Review the sheet PNG + GIF for each generated strip in {QA_DIR} before "
              f"treating any of them as done.")

    return 1 if failures else 0


def cmd_reprocess(args: argparse.Namespace) -> int:
    """Re-run the post-processing chain on already-generated raw strips, with no new API calls."""
    char = get_character(args.character)
    palette = char.load_palette()
    hair_colors = char.resolve_hair_colors()
    head_targets = compute_head_targets(char.turnaround_path, hair_colors)
    names = build_strip_list(args)
    char.out_dir.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    results: dict[str, str] = {}
    qa_results: list[qa.QAResult] = []
    for name in names:
        raw_path = char.raw_dir / f"{name}_strip.png"
        if not raw_path.exists():
            results[name] = f"FAILED: raw strip not found at {raw_path}"
            continue
        n_frames = ANIMATION_FRAME_COUNTS[name.rsplit("_", 1)[0]]
        out_paths = [char.out_dir / f"{name}_{i}.png" for i in range(n_frames)]
        print(f"Reprocessing strip {name} ({n_frames} frames)...")
        try:
            raw_strip = Image.open(raw_path).convert("RGBA")
            status, result = process_and_save_strip(name, raw_strip, palette, out_paths,
                                                     hair_colors=hair_colors,
                                                     head_targets=head_targets)
            qa_results.append(result)
            results[name] = status
        except Exception as exc:  # noqa: BLE001 - continue the batch on per-strip failure
            results[name] = f"FAILED: {exc}"

    print("\n--- Summary ---")
    failures = 0
    for name, status in results.items():
        print(f"{name:20s} {status}")
        if status.startswith("FAILED") or "QA FAILED" in status:
            failures += 1

    if qa_results:
        report_path = QA_DIR / "qa_report.txt"
        qa.write_report(qa_results, report_path)
        print(f"\nQA report written to {report_path}")

    return 1 if failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_character_arg(p: argparse.ArgumentParser) -> None:
        # Attached per-subcommand (not at the top level) so it can be passed in the natural
        # position, e.g. `strip --character player --reference ...`.
        p.add_argument("--character", default=DEFAULT_CHARACTER,
                       help=f"Which character config to use (default: {DEFAULT_CHARACTER}). Selects "
                            f"reference/raw/out dirs, palette, turnaround, and likeness prose.")

    # Character-dependent path defaults are resolved inside each command (default=None here)
    # so the values follow --character instead of being frozen to one character at parse time.
    p_turn = sub.add_parser("turnaround", help="Generate the master reference turnaround")
    p_turn.add_argument("--reference", required=True, type=Path,
                         help="Path to the user's reference art (read-only, never copied into the repo)")
    p_turn.add_argument("--out", type=Path, default=None,
                         help="Defaults to <character reference_dir>/turnaround_raw.png")
    add_character_arg(p_turn)
    p_turn.set_defaults(func=cmd_turnaround)

    p_approve = sub.add_parser("approve-turnaround",
                                help="Post-process the approved raw turnaround into the style-lock reference")
    p_approve.add_argument("--raw", type=Path, default=None,
                            help="Defaults to <character reference_dir>/turnaround_raw.png")
    p_approve.add_argument("--out", type=Path, default=None,
                            help="Defaults to <character reference_dir>/turnaround.png")
    add_character_arg(p_approve)
    p_approve.set_defaults(func=cmd_approve_turnaround)

    p_strip = sub.add_parser("strip", help="Generate one or more animation strips")
    p_strip.add_argument("--reference", required=True, type=Path,
                          help="Path to the user's reference art (read-only, never copied into the repo)")
    p_strip.add_argument("--turnaround", type=Path, default=None,
                          help="Defaults to <character reference_dir>/turnaround.png")
    group = p_strip.add_mutually_exclusive_group(required=True)
    group.add_argument("--only", action="append", dest="only", metavar="NAME",
                        help="Generate only this strip (repeatable)")
    group.add_argument("--canary", action="store_true", help="Generate the two canary strips")
    group.add_argument("--all", action="store_true", help="Generate all 45 strips")
    p_strip.add_argument("--skip-existing", dest="skip_existing", action="store_true", default=True)
    p_strip.add_argument("--force", dest="skip_existing", action="store_false",
                          help="Overwrite existing outputs instead of skipping them")
    add_character_arg(p_strip)
    p_strip.set_defaults(func=cmd_strip)

    p_reprocess = sub.add_parser("reprocess",
                                  help="Re-run post-processing on already-generated raw strips (no API calls)")
    group_r = p_reprocess.add_mutually_exclusive_group(required=True)
    group_r.add_argument("--only", action="append", dest="only", metavar="NAME",
                          help="Reprocess only this strip (repeatable)")
    group_r.add_argument("--canary", action="store_true", help="Reprocess the two canary strips")
    group_r.add_argument("--all", action="store_true", help="Reprocess all 45 strips")
    add_character_arg(p_reprocess)
    p_reprocess.set_defaults(func=cmd_reprocess)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
