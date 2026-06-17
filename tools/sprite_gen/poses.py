"""Prompt text for each Player animation pose x direction, used by generate_sprites.py."""

STYLE_PREAMBLE = (
    "Pixel art sprite of a video game character, in a steep top-down action-RPG camera "
    "angle, in the exact style of classic top-down chibi RPG sprites (Secret of Mana, "
    "Chrono Trigger overworld sprites, Pokemon overworld sprites, Stardew Valley) -- "
    "anime-influenced character art with vibrant colors and clean linework. Single "
    "character, full body visible head to feet, standing on a flat invisible ground line.\n\n"
    "BODY PROPORTIONS -- this is critical, follow it exactly: moderate CHIBI proportions "
    "like Chrono Trigger or Secret of Mana overworld sprites -- NOT realistic human "
    "proportions, but also NOT an extreme bobble-head caricature. The head is somewhat "
    "enlarged, roughly 1/4 to 1/3 of the character's total height -- noticeably bigger "
    "than a real human head-to-body ratio, but the body must still read as a small "
    "person with clearly defined arms, legs, and torso, not a tiny stub-limbed blob.\n\n"
    "CAMERA ANGLE -- this is also critical, follow it exactly: a steep top-down "
    "perspective looking down at roughly a 60-75 degree angle from horizontal (much "
    "closer to a bird's-eye view than a side-on view), as if the camera is high above "
    "the player looking nearly straight down. You should clearly see the top/crown of "
    "the character's head and the tops of their shoulders, with the face small, "
    "compressed, and foreshortened beneath the large head -- this is NOT a flat "
    "90-degree side profile (no side-scrolling beat-em-up silhouette) and NOT an "
    "eye-level 3/4 portrait-style view -- it must read as a small character viewed "
    "from high above, the way a player-controlled sprite looks in a top-down RPG.\n\n"
    "Solid flat-color pixel-art shading with a limited color palette and a visible pixel "
    "grid (no smooth gradients, no anti-aliased painterly rendering, no photo-realistic "
    "rendering). Transparent background (no ground, no scenery, no shadow gradient -- "
    "alpha background only). Centered in frame with consistent character scale and "
    "proportions. Likeness: base the character's face, hair, skin tone, and build on the "
    "attached reference image of the character, keeping the same anime art style, while "
    "rendering it as a chibi top-down pixel-art game sprite. Match the reference image's "
    "hairstyle shape and silhouette exactly -- same haircut, same hair length, same "
    "spiky/messy shape on top -- do not change the hairstyle. The character wears normal "
    "clear-lens prescription glasses with a dark/black frame that has a clearly visible "
    "dark rim outline -- the lenses are clear and see-through, never dark sunglasses, "
    "tinted lenses, or opaque shades."
)

STYLE_LOCK_INSTRUCTION = (
    "You are given two reference images: (1) a reference image of the character, used "
    "only for likeness (face, hair, skin tone, build, outfit), and (2) an already-approved "
    "pixel-art sprite of this exact character in an idle pose, which defines the exact art "
    "style, color palette, proportions, and outline thickness to match exactly. Generate a "
    "NEW pose of the SAME character matching image (2)'s style precisely, using image (1) "
    "only for likeness reference."
)

DIRECTION_PROMPTS: dict[str, str] = {
    "down": "The character faces the viewer/camera (south), so their face and front of body are visible.",
    "up": "The character faces away from the viewer/camera (north), so the back of their head and body are visible, with little to no face visible.",
    "side": "The character is turned to face screen-right (east), shown from a 3/4 angle so one side of their body and face profile are visible.",
}

# Order matters only for the idle-first two-phase workflow in generate_sprites.py.
POSE_PROMPTS: dict[str, str] = {
    "idle": (
        "Neutral idle stance, relaxed standing pose, arms loosely at sides, weight "
        "balanced, ready stance."
    ),
    "move": (
        "Mid-stride running/walking pose, one leg forward one leg back, dynamic "
        "running animation key pose, leaning slightly forward."
    ),
    "charge_loop": (
        "Crouched charging stance, knees bent, both hands drawn together at chest or "
        "waist level glowing with gathering energy, head down in concentration."
    ),
    "release": (
        "Energy blast release pose, both arms thrust forward releasing a burst of "
        "energy from the hands, dynamic forward lunge."
    ),
    "hurt": (
        "Recoiling flinch pose from taking a hit, body leaning backward off-balance, "
        "arms raised defensively, pained expression."
    ),
    "basic_punch_1": (
        "Beginning jab punch, lead arm extending forward at chest height, light "
        "weight transfer, first hit of a 3-punch combo (subtle extension)."
    ),
    "basic_punch_2": (
        "Second punch of a jab combo, opposite arm extending further forward than "
        "punch 1, more weight transfer and rotation, medium extension."
    ),
    "basic_punch_3": (
        "Final heavy punch of a 3-hit combo, full body rotation, arm fully extended "
        "forward with maximum reach, strongest pose of the punch combo."
    ),
    "basic_kick_1": (
        "Beginning kick, leg starting to lift forward at low height, light "
        "extension, first hit of a 3-kick combo."
    ),
    "basic_kick_2": (
        "Second kick of a combo, leg extended further forward at mid height, more "
        "rotation and balance lean, medium extension."
    ),
    "basic_kick_3": (
        "Final heavy roundhouse-style kick, leg fully extended at high/maximum "
        "reach, full body commitment and rotation, strongest pose of the kick combo."
    ),
    "master_1": (
        "First hit of a powerful master combo: a strong punch with forward lunge, "
        "more intensity than basic_punch poses."
    ),
    "master_2": (
        "Second hit of the master combo: a strong kick with forward momentum, more "
        "intensity than basic_kick poses."
    ),
    "master_3": (
        "Third hit of the master combo: another strong kick, body coiled for the "
        "next strike, building intensity."
    ),
    "master_4": (
        "Final finishing blow of the master combo: a massive heavy haymaker punch, "
        "maximum exaggerated extension and impact energy, dramatic finishing-move "
        "pose, the most intense and largest pose in the whole set."
    ),
}

_BASE_POSE_NAMES: list[str] = list(POSE_PROMPTS.keys())
_DIRECTIONS: list[str] = ["down", "up", "side"]

# Flatten to 45 pose x direction combinations. idle_down comes first so it can serve as
# the sole two-phase style-lock anchor for all other 44 sprites in generate_sprites.py.
POSE_PROMPTS = {
    f"{pose}_{direction}": f"{DIRECTION_PROMPTS[direction]} {POSE_PROMPTS[pose]}"
    for pose in _BASE_POSE_NAMES
    for direction in _DIRECTIONS
}

POSE_NAMES: list[str] = list(POSE_PROMPTS.keys())
