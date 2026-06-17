"""Prompt text for each Player animation pose, used by generate_sprites.py."""

STYLE_PREAMBLE = (
    "Pixel art sprite of a video game character, in the exact style of classic 16-bit "
    "SNES/Genesis side-scrolling beat-em-up character sprites (like Streets of Rage or "
    "Final Fight). Single character, full body visible head to feet, standing on a flat "
    "invisible ground line.\n\n"
    "CAMERA ANGLE -- this is the most important constraint, follow it exactly: a true "
    "90-degree side view, like a photo taken from directly to the character's left so "
    "they appear walking/fighting to the right across the screen. The body is a narrow "
    "side silhouette, not a wide front silhouette. The head is turned in profile: only "
    "ONE eye, ONE eyebrow, and the side/back of the head and ONE ear are visible -- the "
    "nose, lips, and chin show a profile (side) outline, never two eyes and never a "
    "symmetric front-on face. The torso shows only the near shoulder, with the far "
    "shoulder hidden or barely visible behind it -- never two symmetric shoulders facing "
    "the viewer. Any shirt logo, collar, or button line should run vertically along the "
    "narrow profile of the torso, not appear as a centered front-facing emblem. Do NOT "
    "generate a front-facing portrait, a mugshot-style pose, or a 3/4 angle -- this must "
    "read as a flat side silhouette like a character-select sprite, not a portrait.\n\n"
    "Solid flat-color pixel-art shading with a limited color palette and a visible pixel "
    "grid (no smooth gradients, no anti-aliased painterly rendering, no photo-realistic "
    "rendering). Transparent background (no ground, no scenery, no shadow gradient -- "
    "alpha background only). Centered in frame with consistent character scale and "
    "proportions. Likeness: base the character's face, hair, skin tone, and build "
    "loosely on the attached reference photo of a real person, but fully stylized as a "
    "pixel-art game sprite seen from the side -- not photo-realistic, not a front-facing "
    "portrait."
)

STYLE_LOCK_INSTRUCTION = (
    "You are given two reference images: (1) a photo of a real person's face, used "
    "only for facial likeness, and (2) an already-approved pixel-art sprite of this "
    "exact character in an idle pose, which defines the exact art style, color "
    "palette, proportions, and outline thickness to match exactly. Generate a NEW pose "
    "of the SAME character matching image (2)'s style precisely, using image (1) only "
    "for facial likeness reference."
)

# Order matters only for the idle-first two-phase workflow in generate_sprites.py.
POSE_PROMPTS: dict[str, str] = {
    "idle": (
        "Neutral idle stance, relaxed standing pose, arms loosely at sides, weight "
        "balanced, ready stance, facing right."
    ),
    "move": (
        "Mid-stride running/walking pose, one leg forward one leg back, dynamic "
        "running animation key pose, facing right, leaning slightly forward."
    ),
    "charge_loop": (
        "Crouched charging stance, knees bent, both hands drawn together at chest or "
        "waist level glowing with gathering energy, head down in concentration, "
        "facing right."
    ),
    "release": (
        "Energy blast release pose, both arms thrust forward releasing a burst of "
        "energy from the hands, dynamic forward lunge, facing right."
    ),
    "hurt": (
        "Recoiling flinch pose from taking a hit, body leaning backward off-balance, "
        "arms raised defensively, pained expression, facing right."
    ),
    "basic_punch_1": (
        "Beginning jab punch, lead arm extending forward at chest height, light "
        "weight transfer, facing right, first hit of a 3-punch combo (subtle "
        "extension)."
    ),
    "basic_punch_2": (
        "Second punch of a jab combo, opposite arm extending further forward than "
        "punch 1, more weight transfer and rotation, facing right, medium extension."
    ),
    "basic_punch_3": (
        "Final heavy punch of a 3-hit combo, full body rotation, arm fully extended "
        "forward with maximum reach, strongest pose of the punch combo, facing right."
    ),
    "basic_kick_1": (
        "Beginning kick, leg starting to lift forward at low height, light "
        "extension, facing right, first hit of a 3-kick combo."
    ),
    "basic_kick_2": (
        "Second kick of a combo, leg extended further forward at mid height, more "
        "rotation and balance lean, facing right, medium extension."
    ),
    "basic_kick_3": (
        "Final heavy roundhouse-style kick, leg fully extended at high/maximum "
        "reach, full body commitment and rotation, strongest pose of the kick combo, "
        "facing right."
    ),
    "master_1": (
        "First hit of a powerful master combo: a strong punch with forward lunge, "
        "more intensity than basic_punch poses, facing right."
    ),
    "master_2": (
        "Second hit of the master combo: a strong kick with forward momentum, more "
        "intensity than basic_kick poses, facing right."
    ),
    "master_3": (
        "Third hit of the master combo: another strong kick, body coiled for the "
        "next strike, building intensity, facing right."
    ),
    "master_4": (
        "Final finishing blow of the master combo: a massive heavy haymaker punch, "
        "maximum exaggerated extension and impact energy, dramatic finishing-move "
        "pose, the most intense and largest pose in the whole set, facing right."
    ),
}

POSE_NAMES: list[str] = list(POSE_PROMPTS.keys())
