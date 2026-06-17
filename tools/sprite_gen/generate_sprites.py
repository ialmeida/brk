#!/usr/bin/env python3
"""Generate 16-bit pixel-art Player sprites via Gemini's image model ("nano banana").

Reads GEMINI_API_KEY from the environment only -- never pass it as a CLI flag.

Usage:
    python3 generate_sprites.py --reference /path/to/photo.jpg --only idle
    python3 generate_sprites.py --reference /path/to/photo.jpg \
        --base-image assets/sprites/player/raw/idle.png --all --skip-existing
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import time
from pathlib import Path

from PIL import Image

from poses import POSE_NAMES, POSE_PROMPTS, STYLE_LOCK_INSTRUCTION, STYLE_PREAMBLE
from postprocess import process_image

DEFAULT_MODEL = "gemini-2.5-flash-image"
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path,
                         help="Path to the user's reference photo (read-only, never copied into the repo)")
    parser.add_argument("--base-image", type=Path, default=None,
                         help="Approved idle.png used to style-lock the other 14 poses")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--only", action="append", dest="only", metavar="NAME",
                        help="Generate only this pose (repeatable)")
    group.add_argument("--all", action="store_true", help="Generate all 15 poses")
    parser.add_argument("--skip-existing", dest="skip_existing", action="store_true", default=True)
    parser.add_argument("--force", dest="skip_existing", action="store_false",
                         help="Overwrite existing outputs instead of skipping them")
    parser.add_argument("--raw-dir", type=Path, default=Path("assets/sprites/player/raw"))
    parser.add_argument("--out-dir", type=Path, default=Path("assets/sprites/player/processed"))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--quantize", type=int, default=32,
                         help="Palette color count for post-processing (0 to disable)")
    return parser.parse_args()


def build_pose_list(args: argparse.Namespace) -> list[str]:
    if args.all:
        names = list(POSE_NAMES)
    else:
        names = args.only
        for name in names:
            if name not in POSE_PROMPTS:
                sys.exit(f"Unknown pose name: {name!r}. Valid names: {', '.join(POSE_NAMES)}")
    return names


def extract_image_from_response(response) -> Image.Image:
    for part in response.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline is not None and inline.data:
            return Image.open(io.BytesIO(inline.data))
    raise RuntimeError("No image part found in Gemini response")


def generate_one(client, model: str, prompt: str, reference_img: Image.Image,
                  base_img: Image.Image | None) -> Image.Image:
    contents: list = [reference_img]
    if base_img is not None:
        contents.append(base_img)
        contents.append(f"{STYLE_PREAMBLE}\n\n{STYLE_LOCK_INSTRUCTION}\n\n{prompt}")
    else:
        contents.append(f"{STYLE_PREAMBLE}\n\n{prompt}")

    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            response = client.models.generate_content(model=model, contents=contents)
            return extract_image_from_response(response)
        except Exception as exc:  # noqa: BLE001 - report and retry, don't crash the whole batch
            last_error = exc
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    raise RuntimeError(f"Generation failed after retries: {last_error}")


def main() -> int:
    args = parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        sys.exit("GEMINI_API_KEY is not set. Export it in your shell first -- never pass it as a flag.")

    if not args.reference.exists():
        sys.exit(f"Reference photo not found: {args.reference}")

    try:
        from google import genai
    except ImportError:
        sys.exit("google-genai is not installed. Run: pip install -r tools/sprite_gen/requirements.txt")

    client = genai.Client(api_key=api_key)
    reference_img = Image.open(args.reference).convert("RGB")

    base_img = None
    if args.base_image is not None:
        if not args.base_image.exists():
            sys.exit(f"--base-image not found: {args.base_image}")
        base_img = Image.open(args.base_image).convert("RGBA")

    pose_names = build_pose_list(args)
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, str] = {}
    for name in pose_names:
        out_path = args.out_dir / f"{name}.png"
        raw_path = args.raw_dir / f"{name}.png"

        if args.skip_existing and out_path.exists():
            results[name] = "skipped (already exists)"
            continue

        if name != "idle_down" and base_img is None:
            results[name] = "skipped (no --base-image provided; generate+approve idle_down first)"
            continue

        print(f"Generating {name}...")
        try:
            pose_base = None if name == "idle_down" else base_img
            raw_img = generate_one(client, args.model, POSE_PROMPTS[name], reference_img, pose_base)
            raw_img.convert("RGBA").save(raw_path)
            processed = process_image(raw_img, quantize_colors=args.quantize or None)
            processed.save(out_path)
            results[name] = "ok"
        except Exception as exc:  # noqa: BLE001 - continue the batch on per-pose failure
            results[name] = f"FAILED: {exc}"

    print("\n--- Summary ---")
    failures = 0
    for name, status in results.items():
        print(f"{name:16s} {status}")
        if status.startswith("FAILED"):
            failures += 1

    if "idle_down" in pose_names and results.get("idle_down") == "ok":
        print(f"\nInspect {args.out_dir / 'idle_down.png'} now before generating the other poses.")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
