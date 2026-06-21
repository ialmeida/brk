"""Per-character configuration for the sprite generator.

Everything that varies between characters lives here: the input/output paths, the locked
palette, the approved turnaround, an optional hair-color override for the QA head check, and
the character-specific likeness/hairstyle/outfit prose woven into the prompt preamble. The
generic camera/proportion/strip-format prose stays shared in poses.py.

Paths are relative to the repo root (every command is run from there -- see README.md).
Select a character with the generate_sprites.py `--character` flag; `player` is the default
so existing commands keep working unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from palette import RGB, derive_hair_colors, load_palette

# --- Player likeness ---------------------------------------------------------------------
# Extracted verbatim from the old poses.STYLE_PREAMBLE tail so the assembled prompt text is
# byte-for-byte unchanged for the player character.
PLAYER_LIKENESS = (
    "Likeness: base the character's face, hair, skin tone, and build on the attached "
    "reference image of the character, keeping the same anime art style, while rendering "
    "it as a chibi top-down pixel-art game sprite. Match the reference image's hairstyle "
    "exactly: short, neat hair that sits close to the head with a small side-swept fringe, "
    "cropped short at the back and sides -- the hair must NOT extend past the nape of the "
    "neck or hang down the back of the head. NOT spiky, NOT voluminous, NOT long at the "
    "back, NOT a tall or poofy anime hairstyle. Keep the hair silhouette small and "
    "close-cropped like the reference. The character wears normal clear-lens prescription "
    "glasses with a dark/black frame that has a clearly visible dark rim outline -- the "
    "lenses are clear and see-through, never dark sunglasses, tinted lenses, or opaque "
    "shades."
)


@dataclass(frozen=True)
class Character:
    name: str
    reference_dir: Path  # holds the approved turnaround (NOT the private --reference photo)
    raw_dir: Path        # gitignored, local-only raw model strip output
    out_dir: Path        # committed sliced/processed frames
    palette_path: Path
    likeness_prose: str
    # Optional explicit override for the QA head-dome detector; when None it's derived from
    # the palette's near-black ramp (palette.derive_hair_colors).
    hair_colors: tuple[RGB, ...] | None = None
    turnaround_name: str = "turnaround.png"

    @property
    def turnaround_path(self) -> Path:
        return self.reference_dir / self.turnaround_name

    def load_palette(self) -> list[RGB]:
        return load_palette(self.palette_path)

    def resolve_hair_colors(self) -> list[RGB]:
        if self.hair_colors is not None:
            return list(self.hair_colors)
        return derive_hair_colors(self.load_palette())


CHARACTERS: dict[str, Character] = {
    "player": Character(
        name="player",
        reference_dir=Path("tools/sprite_gen/reference"),
        raw_dir=Path("assets/sprites/player/raw"),
        out_dir=Path("assets/sprites/player/processed"),
        palette_path=Path("tools/sprite_gen/palette.json"),
        likeness_prose=PLAYER_LIKENESS,
    ),
}

DEFAULT_CHARACTER = "player"


def get_character(name: str) -> Character:
    try:
        return CHARACTERS[name]
    except KeyError:
        valid = ", ".join(sorted(CHARACTERS))
        raise SystemExit(f"Unknown character: {name!r}. Known characters: {valid}")
