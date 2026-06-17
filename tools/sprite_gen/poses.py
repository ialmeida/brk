"""Prompt text for each Player animation pose x direction, used by generate_sprites.py."""

STYLE_PREAMBLE = (
    "Pixel art sprite of a video game character, in an elevated 3/4 top-down action-RPG "
    "camera angle, in the exact style of SNES/GBA Zelda (A Link to the Past, Oracle of "
    "Seasons/Ages) and Chrono Trigger -- anime-influenced character art with vibrant colors, "
    "expressive proportions, and clean linework. Single character, full body visible head to "
    "feet, standing on a flat invisible ground line.\n\n"
    "CAMERA ANGLE -- this is the most important constraint, follow it exactly: an elevated "
    "3/4 perspective looking down at roughly a 30-45 degree angle, as if the camera is above "
    "and slightly behind the player looking down at the action. This is NOT a flat 90-degree "
    "side profile (no flat side-scrolling beat-em-up silhouette) and NOT a flat bird's-eye "
    "view straight down -- it is the classic top-down action-RPG sprite angle where you can "
    "see the top of the character's head/shoulders as well as their face and body.\n\n"
    "Solid flat-color pixel-art shading with a limited color palette and a visible pixel "
    "grid (no smooth gradients, no anti-aliased painterly rendering, no photo-realistic "
    "rendering). Transparent background (no ground, no scenery, no shadow gradient -- "
    "alpha background only). Centered in frame with consistent character scale and "
    "proportions. Likeness: base the character's face, hair, skin tone, and build on the "
    "attached reference image of the character, keeping the same anime art style, while "
    "rendering it as a top-down pixel-art game sprite."
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
