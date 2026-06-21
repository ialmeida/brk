"""Quick visual-review artifacts for a processed animation strip: a looping GIF preview
and a static contact sheet PNG."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

GIF_BACKDROP = (128, 128, 128, 255)


def save_loop_gif(frames: list[Image.Image], out_path: Path, fps: int = 8) -> None:
    composited = []
    for frame in frames:
        backdrop = Image.new("RGBA", frame.size, GIF_BACKDROP)
        backdrop.paste(frame, (0, 0), frame)
        composited.append(backdrop.convert("RGB"))
    duration_ms = round(1000 / fps)
    composited[0].save(out_path, save_all=True, append_images=composited[1:],
                        duration=duration_ms, loop=0)


def build_sheet(frames: list[Image.Image], padding: int = 1) -> Image.Image:
    if not frames:
        raise ValueError("No frames to assemble into a sheet")
    cell_w, cell_h = frames[0].size
    sheet_w = cell_w * len(frames) + padding * (len(frames) - 1)
    sheet = Image.new("RGBA", (sheet_w, cell_h), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i * (cell_w + padding), 0), frame)
    return sheet


def save_sheet(frames: list[Image.Image], out_path: Path, padding: int = 1) -> None:
    build_sheet(frames, padding=padding).save(out_path)
