"""Pillow pipeline that turns raw Gemini image output into clean pixel-art sprites."""

from __future__ import annotations

from collections import deque

from PIL import Image

TARGET_CANVAS = 64
TARGET_CHAR_HEIGHT = 56
BG_COLOR_DISTANCE_THRESHOLD = 24
ALPHA_SNAP_THRESHOLD = 127


def _color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sum((ca - cb) ** 2 for ca, cb in zip(a, b)) ** 0.5


def _border_reference_colors(img: Image.Image) -> list[tuple[int, int, int]]:
    """Cluster border pixel colors so a 2-tone checkerboard 'transparency' placeholder
    (which some model outputs draw literally instead of real alpha) is fully captured,
    not just whichever single shade the four corners happen to land on."""
    w, h = img.size
    border = [img.getpixel((x, 0)) for x in range(w)] + [img.getpixel((x, h - 1)) for x in range(w)]
    border += [img.getpixel((0, y)) for y in range(h)] + [img.getpixel((w - 1, y)) for y in range(h)]

    references: list[tuple[int, int, int]] = []
    for r, g, b, _a in border:
        color = (r, g, b)
        if not any(_color_distance(color, ref) < BG_COLOR_DISTANCE_THRESHOLD for ref in references):
            references.append(color)
    return references


def _key_out_background(img: Image.Image) -> Image.Image:
    """If the image has no real alpha channel, flood-fill the background out from the
    canvas border, matching against all detected border reference colors (handles a
    checkerboard 'transparency' placeholder, not just a single flat background color).
    Flood-fill connectivity (rather than a global color-distance pass) keeps this from
    punching holes in same-colored regions inside the character silhouette, e.g. a
    white shirt, since those aren't reachable from the border."""
    has_alpha = any(px[3] < 250 for px in img.getdata())
    if has_alpha:
        return img

    w, h = img.size
    references = _border_reference_colors(img)
    pixels = img.load()

    def is_background(x: int, y: int) -> bool:
        r, g, b, _a = pixels[x, y]
        return any(_color_distance((r, g, b), ref) < BG_COLOR_DISTANCE_THRESHOLD for ref in references)

    visited = bytearray(w * h)
    queue: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        idx = y * w + x
        if not visited[idx] and is_background(x, y):
            visited[idx] = 1
            queue.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while queue:
        x, y = queue.popleft()
        r, g, b, _a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h:
                nidx = ny * w + nx
                if not visited[nidx] and is_background(nx, ny):
                    visited[nidx] = 1
                    queue.append((nx, ny))

    return img


def _snap_alpha(img: Image.Image) -> Image.Image:
    r, g, b, a = img.split()
    a = a.point(lambda v: 255 if v >= ALPHA_SNAP_THRESHOLD else 0)
    return Image.merge("RGBA", (r, g, b, a))


def _quantize_preserving_alpha(img: Image.Image, colors: int) -> Image.Image:
    alpha = img.split()[3]
    rgb = img.convert("RGB")
    quantized = rgb.quantize(colors=colors, method=Image.MEDIANCUT,
                              dither=Image.Dither.NONE).convert("RGBA")
    quantized.putalpha(alpha)
    return quantized


def _keyed_and_cropped(raw: Image.Image) -> Image.Image:
    img = raw.convert("RGBA")
    img = _key_out_background(img)
    img = _snap_alpha(img)
    bbox = img.getbbox()
    if bbox is not None:
        img = img.crop(bbox)
    return img


def natural_scale(raw: Image.Image) -> float:
    """The scale factor that maps this image's own cropped height to TARGET_CHAR_HEIGHT.

    Used to derive a single reference scale from the approved idle pose, which is then
    applied to every other pose so character size stays consistent across poses instead
    of independently renormalizing each pose's own bounding box (which varies with
    pose -- e.g. a raised arm or crouch -- and otherwise makes the character look bigger
    or smaller from pose to pose)."""
    h = _keyed_and_cropped(raw).size[1]
    if h == 0:
        raise ValueError("Image has no visible content after background removal")
    return TARGET_CHAR_HEIGHT / h


def process_image(raw: Image.Image, quantize_colors: int | None = 32,
                   scale: float | None = None) -> Image.Image:
    """Clean up a raw model PNG into a crisp, consistently-anchored sprite.

    If `scale` is omitted, the image is scaled to make its own cropped height exactly
    TARGET_CHAR_HEIGHT. Pass a fixed `scale` (see `natural_scale`) to keep character size
    consistent with a reference pose instead.
    """
    img = _keyed_and_cropped(raw)

    w, h = img.size
    if h == 0:
        raise ValueError("Image has no visible content after background removal")
    if scale is None:
        scale = TARGET_CHAR_HEIGHT / h
    new_w = max(1, round(w * scale))
    new_h = max(1, round(h * scale))
    img = img.resize((new_w, new_h), Image.NEAREST)

    if quantize_colors:
        img = _quantize_preserving_alpha(img, quantize_colors)

    canvas = Image.new("RGBA", (TARGET_CANVAS, TARGET_CANVAS), (0, 0, 0, 0))
    paste_x = (TARGET_CANVAS - new_w) // 2
    paste_y = TARGET_CANVAS - new_h - 4  # feet ~4px from the bottom edge
    canvas.paste(img, (paste_x, max(0, paste_y)), img)
    return canvas
