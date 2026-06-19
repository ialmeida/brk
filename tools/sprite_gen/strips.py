"""Post-processing chain that turns one raw Gemini animation strip into clean,
consistently-scaled, palette-snapped pixel-art frames.

Pipeline per strip (see SPRITE_REGEN_BRIEF.md): key magenta -> harden alpha -> slice into
cells -> compute one scale factor for the whole strip from the median cell silhouette
height -> per cell: Lanczos downscale -> re-harden alpha -> snap to palette -> despeckle
-> recenter on a fixed canvas.
"""

from __future__ import annotations

import statistics

import numpy as np
from PIL import Image

from palette import RGB

MAGENTA: RGB = (255, 0, 255)
MAGENTA_DISTANCE_THRESHOLD = 110
KEY_COLOR_THRESHOLD = 60
BORDER_SAMPLE_PX = 3
ALPHA_HARDEN_THRESHOLD = 128


def sample_background_color(img: Image.Image, border: int = BORDER_SAMPLE_PX) -> RGB:
    """Median color of a thin band around the image edge.

    Gemini doesn't reliably render the requested background as pure #FF00FF -- it can
    come out as a duller, darker magenta. Sampling the strip's own border gives the
    actual rendered key color for this generation instead of assuming an ideal one.
    """
    arr = np.array(img.convert("RGB"), dtype=np.int64)
    band = np.concatenate([
        arr[:border].reshape(-1, 3),
        arr[-border:].reshape(-1, 3),
        arr[:, :border].reshape(-1, 3),
        arr[:, -border:].reshape(-1, 3),
    ])
    r, g, b = np.median(band, axis=0)
    return (int(r), int(g), int(b))


def looks_like_magenta_key(color: RGB) -> bool:
    r, g, b = color
    return (r - g) > 60 and (b - g) > 60


def key_out_background(img: Image.Image, key_color: RGB,
                        threshold: int = KEY_COLOR_THRESHOLD) -> Image.Image:
    arr = np.array(img.convert("RGBA"), dtype=np.int32)
    diff = arr[..., :3] - np.array(key_color, dtype=np.int32)
    dist_sq = np.sum(diff * diff, axis=-1)
    arr[..., 3] = np.where(dist_sq < threshold * threshold, 0, arr[..., 3])
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def reharden_alpha(img: Image.Image, threshold: int = ALPHA_HARDEN_THRESHOLD) -> Image.Image:
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    arr[..., 3] = np.where(arr[..., 3] >= threshold, 255, 0).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def slice_strip(img: Image.Image, n_cells: int) -> list[Image.Image]:
    w, h = img.size
    if w % n_cells != 0:
        raise ValueError(f"Strip width {w} is not evenly divisible by {n_cells} cells")
    cell_w = w // n_cells
    return [img.crop((i * cell_w, 0, (i + 1) * cell_w, h)) for i in range(n_cells)]


def cell_silhouette_height(cell: Image.Image) -> int:
    bbox = cell.getbbox()
    return 0 if bbox is None else bbox[3] - bbox[1]


def strip_scale_factor(cells: list[Image.Image], target_char_height: int) -> float:
    heights = [h for h in (cell_silhouette_height(c) for c in cells) if h > 0]
    if not heights:
        raise ValueError("No visible content in any cell of the strip")
    return target_char_height / statistics.median(heights)


def lanczos_downscale(cell: Image.Image, scale: float) -> Image.Image:
    bbox = cell.getbbox()
    if bbox is None:
        return cell
    cropped = cell.crop(bbox)
    new_w = max(1, round(cropped.width * scale))
    new_h = max(1, round(cropped.height * scale))
    return cropped.resize((new_w, new_h), Image.LANCZOS)


def snap_to_palette(cell: Image.Image, palette: list[RGB]) -> Image.Image:
    arr = np.array(cell.convert("RGBA"), dtype=np.int32)
    pal = np.array(palette, dtype=np.int32)
    diff = arr[:, :, None, :3] - pal[None, None, :, :]
    nearest_idx = np.argmin(np.sum(diff * diff, axis=-1), axis=-1)
    snapped = np.concatenate([pal[nearest_idx], arr[..., 3:4]], axis=-1)
    return Image.fromarray(snapped.astype(np.uint8), "RGBA")


def despeckle(cell: Image.Image) -> Image.Image:
    arr = np.array(cell.convert("RGBA"), dtype=np.uint8)
    opaque = (arr[..., 3] > 0).astype(np.uint8)
    neighbor_sum = np.zeros_like(opaque)
    neighbor_sum[1:, :] += opaque[:-1, :]
    neighbor_sum[:-1, :] += opaque[1:, :]
    neighbor_sum[:, 1:] += opaque[:, :-1]
    neighbor_sum[:, :-1] += opaque[:, 1:]
    isolated = (opaque == 1) & (neighbor_sum == 0)
    arr[..., 3] = np.where(isolated, 0, arr[..., 3])
    return Image.fromarray(arr, "RGBA")


def recenter_on_canvas(cell: Image.Image, canvas_w: int, canvas_h: int, baseline_y: int,
                        align: str = "feet", offset: tuple[int, int] = (0, 0)) -> Image.Image:
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    bbox = cell.getbbox()
    if bbox is None:
        return canvas
    content = cell.crop(bbox)
    cw, ch = content.size
    dx, dy = offset
    x = canvas_w // 2 - cw // 2 + dx
    if align == "feet":
        y = baseline_y - ch + dy
    elif align == "center":
        y = (canvas_h - ch) // 2 + dy
    else:
        raise ValueError(f"Unknown align: {align!r}")
    canvas.paste(content, (x, y), content)
    return canvas


def process_strip(raw_strip: Image.Image, n_cells: int, target_char_height: int,
                   canvas_w: int, canvas_h: int, baseline_y: int, palette: list[RGB],
                   align: str = "feet", offset: tuple[int, int] = (0, 0),
                   scale_mult: float = 1.0) -> tuple[list[Image.Image], RGB]:
    key_color = sample_background_color(raw_strip)
    if not looks_like_magenta_key(key_color):
        raise ValueError(
            f"Sampled background color {key_color} doesn't look like a magenta key -- "
            f"inspect the raw strip for a rendering error before reprocessing.")

    keyed = reharden_alpha(key_out_background(raw_strip, key_color))
    cells = slice_strip(keyed, n_cells)
    scale = strip_scale_factor(cells, target_char_height) * scale_mult

    frames = []
    for cell in cells:
        scaled = lanczos_downscale(cell, scale)
        scaled = reharden_alpha(scaled)
        scaled = snap_to_palette(scaled, palette)
        scaled = despeckle(scaled)
        frames.append(recenter_on_canvas(scaled, canvas_w, canvas_h, baseline_y,
                                          align=align, offset=offset))
    return frames, key_color
