"""Prompt text for Player animation strips, used by generate_sprites.py.

Each animation+direction generates ONE multi-frame strip in a single Gemini call (see
SPRITE_REGEN_BRIEF.md Method B) instead of one call per static frame, so frames within an
animation stay visually consistent with each other.
"""

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
    "CAMERA ANGLE -- this is also critical, and the single most common mistake to avoid: "
    "this is a TOP-DOWN GAME SPRITE, not a character portrait, bust shot, or "
    "character-select art. This is NOT a picture OF the character's face -- it is a "
    "picture of the character seen from ABOVE. Imagine a camera mounted on the ceiling "
    "a few meters above the character, tilted down at roughly a 60-75 degree angle "
    "(much closer to a bird's-eye view straight down than to eye-level). Reference the "
    "EXACT look of: Chrono Trigger overworld sprites, Secret of Mana overworld sprites, "
    "Pokemon Gen 3-5 overworld sprites, Stardew Valley character sprites -- in all of "
    "these, you mostly see the TOP of the character's head and hair, not their face. "
    "Concretely, in the final image: the crown/top of the head and hair occupy the "
    "majority of the head shape, reading as a flattened, wide oval/dome; the hairline "
    "sits very high, near the very top of the head shape; the face is compressed into a "
    "small band near the BOTTOM of the head, with the eyes sitting low, close to the "
    "bottom edge of the head, and almost no bare forehead skin visible between the "
    "eyebrows and the hairline; the chin and jaw are barely visible, foreshortened "
    "almost out of view, with the head appearing to sit nearly directly on the "
    "shoulders with little to no visible neck; the shoulders read as a wide, flat "
    "horizontal bar/shelf because you are looking down onto their top surface, not "
    "their front; the legs and feet appear short and visually compressed due to the "
    "steep downward foreshortening. Do NOT draw a normal face-forward head with a "
    "visible vertical forehead, centered eyes, and a visible chin -- that is an "
    "eye-level portrait angle and is WRONG for this sprite. This is also NOT a flat "
    "90-degree side profile (no side-scrolling beat-em-up silhouette).\n\n"
    "Solid flat-color pixel-art shading with a limited color palette and a visible pixel "
    "grid (no smooth gradients, no anti-aliased painterly rendering, no photo-realistic "
    "rendering). Centered in frame with consistent character scale and proportions. "
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

STYLE_LOCK_INSTRUCTION = (
    "You are given two reference images: (1) a reference image of the character, a normal "
    "eye-level photo used ONLY for likeness -- face shape, skin tone, glasses, hair color, "
    "outfit colors. Image (1) is NOT a camera-angle or silhouette reference; ignore its "
    "eye-level framing entirely. (2) an already-approved turnaround sheet of this exact "
    "character in this exact top-down pixel-art style -- this is the ONLY ground truth for "
    "camera angle, head/hair silhouette, body proportions, color palette, scale, and outline "
    "thickness. Match image (2) precisely, including its hair: because of the steep top-down "
    "camera angle, image (2)'s hair correctly reads as a rounded, dome-shaped mass covering "
    "most of the head, with almost no face visible beneath it -- that dome shape is correct "
    "and required, NOT a mistake to fix. Do NOT flatten the hair or revert to an eye-level "
    "portrait angle with more face showing just because image (1) is a normal front-facing "
    "photo. Generate the requested NEW strip of the SAME character matching image (2)'s "
    "camera angle, style, scale, and baseline precisely, using image (1) only for likeness."
)

STRIP_STYLE_PREAMBLE = (
    "Output a single horizontal strip image containing exactly {n} evenly-spaced, "
    "equal-width cells side by side, left to right, one animation frame per cell. The "
    "character must be the same size, same scale, and same baseline (feet at the same "
    "height) in every cell -- only the pose changes between cells, not the character's "
    "scale or vertical position. Fill the ENTIRE background of every cell with a single "
    "solid flat magenta color (#FF00FF, RGB 255,0,255) -- no gradient, no shadow, no "
    "ground line, no scenery, no cell borders or dividers, no text or labels. The magenta "
    "background color must never appear anywhere on the character itself (skin, hair, "
    "clothes, accessories)."
)

DIRECTION_PROMPTS: dict[str, str] = {
    "down": "The character faces the viewer/camera (south), so their face and front of body are visible. This is still the same steep top-down camera angle as every other direction, NOT an eye-level portrait shot -- the top of the head and hair must still occupy most of the head shape (a rounded dome from above), the hairline sits high, and only a small compressed band of face shows near the bottom of the head with the eyes low and almost no bare forehead. Do NOT widen the visible face or shrink the hair just because the character is facing forward.",
    "up": "The character faces away from the viewer/camera (north) for this ENTIRE pose, including during attacks -- they do NOT turn, twist, or rotate back toward the camera even while punching, kicking, or charging energy. Show only the back of their head and body. Their face must NOT be visible at all, not even in partial profile -- punches and kicks are thrown straight ahead, away from the camera, with the back of the head still fully covering the face.",
    "side": "The character is turned to face screen-right (east), shown from a 3/4 angle so one side of their body and face profile are visible. The hair silhouette must stay exactly as short and close-cropped as the reference idle pose -- do NOT add extra volume, height, or poof to the hair just because the head is turned; it should look like the same flat, neat haircut simply rotated, not a bigger or fluffier hairstyle.",
}

ANIMATION_FRAME_COUNTS: dict[str, int] = {
    "idle": 4,
    "move": 4,
    "charge_loop": 4,
    "release": 3,
    "hurt": 3,
    "basic_punch_1": 3,
    "basic_punch_2": 3,
    "basic_punch_3": 3,
    "basic_kick_1": 3,
    "basic_kick_2": 3,
    "basic_kick_3": 3,
    "master_1": 3,
    "master_2": 3,
    "master_3": 3,
    "master_4": 3,
}

ANIMATION_ALIGN: dict[str, str] = {
    "hurt": "center",
}
DEFAULT_ALIGN = "feet"

STRIP_POSE_PROMPTS: dict[str, str] = {
    "idle": (
        "A seamless looping idle breathing cycle in 4 frames: neutral standing stance, "
        "arms loosely at sides, weight balanced. The 4 frames must NOT all look the same -- "
        "this is an animation, and the difference between frames must be clearly visible "
        "at a glance when the frames are compared side by side, not a one-pixel nudge. "
        "Frame 1: rest pose, shoulders relaxed and down. Frame 2: a clear, visible inhale -- "
        "shoulders and chest noticeably raised higher than frame 1, an obvious lift a "
        "player would notice immediately. Frame 3: rest pose again, identical to frame 1. "
        "Frame 4: a clear, visible exhale/settle -- shoulders noticeably lower than the "
        "frame-1 rest pose, plus a small weight shift to one side. Keep the overall mood a "
        "calm idle loop, not an action pose, but the shoulder/chest height must visibly "
        "change between frames 1, 2, and 4 -- do not render them as near-duplicates. Frame "
        "4 must flow naturally back into frame 1 for a seamless loop."
    ),
    "move": (
        "A seamless looping walk cycle in 4 frames covering one full stride. The leg and "
        "arm positions MUST be clearly, visibly different from frame to frame -- a walk "
        "cycle where the legs look the same in every frame is wrong and unacceptable. "
        "Frame 1: wide contact pose -- legs scissored far apart, front leg stretched "
        "forward with the foot planted well ahead of the body, back leg stretched backward "
        "with the heel lifting off the ground; this must be an exaggerated, wide stride, "
        "not a small shuffle. Frame 2: passing pose -- legs crossing directly under the "
        "body, the moving leg bent sharply at the knee and lifted clear of the ground "
        "mid-swing. Frame 3: wide contact pose again, mirrored left/right from frame 1 (the "
        "OTHER leg now stretched forward, the OTHER leg stretched back) -- this must look "
        "like a mirror image of frame 1's leg positions, not a repeat of the same pose. "
        "Frame 4: passing pose again, mirrored from frame 2. Arms swing opposite the legs "
        "throughout, with a visibly different arm position in every frame to match. The "
        "cycle must loop seamlessly from frame 4 back to frame 1."
    ),
    "charge_loop": (
        "A seamless looping energy-charging cycle in 4 frames: crouched charging stance, "
        "knees bent, both hands drawn together at chest or waist level gathering energy, "
        "head down in concentration. Frames 1 and 3 show a smaller, dimmer gathered energy "
        "glow; frames 2 and 4 show a slightly larger, brighter pulse of the same glow -- a "
        "subtle pulsing animation, with the character's pose itself staying essentially "
        "still. The cycle must loop seamlessly from frame 4 back to frame 1."
    ),
    "release": (
        "A 3-frame energy blast release: frame 1 anticipation, both hands pulled back with "
        "energy gathered just before release; frame 2 full release, both arms thrust "
        "forward unleashing a burst of energy from the hands, dynamic forward lunge; frame "
        "3 brief follow-through, arms still extended forward as the burst fades."
    ),
    "hurt": (
        "A 3-frame hit-reaction flinch: frame 1 impact, body jolting backward off-balance, "
        "pained expression; frame 2 peak recoil, body leaning further back, arms raised "
        "defensively; frame 3 starting to recover, body beginning to straighten back up."
    ),
    "basic_punch_1": (
        "A 3-frame beginning jab punch: frame 1 anticipation wind-up with lead arm pulled "
        "back slightly; frame 2 full extension/contact, lead arm extended forward at chest "
        "height with light weight transfer; frame 3 brief follow-through, arm starting to "
        "draw back. First, lightest hit of a 3-punch combo."
    ),
    "basic_punch_2": (
        "A 3-frame second punch of the combo: frame 1 anticipation wind-up, opposite arm "
        "pulled back with more rotation than punch 1; frame 2 full extension/contact, arm "
        "extending further forward than punch 1 with more weight transfer and body "
        "rotation; frame 3 brief follow-through. Medium hit of a 3-punch combo."
    ),
    "basic_punch_3": (
        "A 3-frame final heavy punch of the combo: frame 1 anticipation wind-up with full "
        "body coil; frame 2 full extension/contact, full body rotation, arm fully extended "
        "forward with maximum reach -- strongest pose of the punch combo; frame 3 brief "
        "follow-through, body still rotated from the strike."
    ),
    "basic_kick_1": (
        "A 3-frame beginning kick: frame 1 anticipation, leg starting to lift with weight "
        "shifting onto the standing leg; frame 2 full extension/contact, leg extended "
        "forward at low height, light extension; frame 3 brief follow-through, leg starting "
        "to lower. First, lightest hit of a 3-kick combo."
    ),
    "basic_kick_2": (
        "A 3-frame second kick of the combo: frame 1 anticipation, leg lifting higher with "
        "more body rotation than kick 1; frame 2 full extension/contact, leg extended "
        "further forward at mid height with more rotation and balance lean; frame 3 brief "
        "follow-through. Medium hit of a 3-kick combo."
    ),
    "basic_kick_3": (
        "A 3-frame final heavy roundhouse-style kick: frame 1 anticipation, full body coil "
        "and weight shift; frame 2 full extension/contact, leg fully extended at "
        "high/maximum reach with full body commitment and rotation -- strongest pose of the "
        "kick combo; frame 3 brief follow-through, body still rotated from the strike."
    ),
    "master_1": (
        "A 3-frame powerful master combo first hit: frame 1 anticipation wind-up with more "
        "intensity than basic_punch poses; frame 2 full extension/contact, a strong punch "
        "with forward lunge; frame 3 brief follow-through."
    ),
    "master_2": (
        "A 3-frame master combo second hit: frame 1 anticipation wind-up with more "
        "intensity than basic_kick poses; frame 2 full extension/contact, a strong kick "
        "with forward momentum; frame 3 brief follow-through."
    ),
    "master_3": (
        "A 3-frame master combo third hit: frame 1 anticipation, body coiling for another "
        "strike; frame 2 full extension/contact, another strong kick with building "
        "intensity; frame 3 brief follow-through, body still coiled from the strike."
    ),
    "master_4": (
        "A 3-frame master combo finishing blow: frame 1 anticipation, full-body wind-up for "
        "the biggest hit in the set; frame 2 full extension/contact, a massive heavy "
        "haymaker punch thrown with full-body rotation and weight transfer, dramatic "
        "finishing-move pose, the most intense pose in the whole set; frame 3 brief "
        "follow-through. In every frame, the punching fist and hand must stay the SAME "
        "normal size as the character's other hand and the rest of their body -- do NOT "
        "draw an oversized, close-up, or exaggerated giant fist; proportions must match "
        "every other pose exactly."
    ),
}

TURNAROUND_PROMPT = (
    f"{STYLE_PREAMBLE}\n\n"
    "Output a single horizontal turnaround reference strip containing exactly 3 "
    "evenly-spaced, equal-width cells side by side, left to right: cell 1 = character "
    "facing the viewer/camera (south, facing down), cell 2 = character facing away from "
    "the viewer/camera (north, facing up, back of head and body visible, face hidden), "
    "cell 3 = character turned to face screen-right (east) shown from a 3/4 angle with one "
    "side of their body and face profile visible. All 3 cells show the exact SAME neutral "
    "idle standing pose (arms loosely at sides, weight balanced), the exact same character "
    "scale, and the exact same baseline (feet at the same height) -- only the facing "
    "direction changes between cells. Fill the ENTIRE background of every cell with a "
    "single solid flat magenta color (#FF00FF, RGB 255,0,255) -- no gradient, no shadow, no "
    "ground line, no scenery, no cell borders or dividers, no text or labels. The magenta "
    "background color must never appear anywhere on the character itself."
)
TURNAROUND_DIRECTIONS: list[str] = ["down", "up", "side"]

STYLE_RECAP = (
    "Final reminder before finalizing every cell: no matter how dynamic or energetic this "
    "particular motion is, every cell must keep the EXACT same steep top-down camera angle, "
    "the same small dome-shaped close-cropped hair silhouette, and the same chibi "
    "proportions as the approved turnaround reference (image 2) -- a bigger or fluffier "
    "hairstyle, more exposed forehead/face, or a more face-forward eye-level portrait angle "
    "is wrong, even for a fast walk, a punch, or any other high-energy pose."
)

_BASE_POSE_NAMES: list[str] = list(STRIP_POSE_PROMPTS.keys())
_DIRECTIONS: list[str] = ["down", "up", "side"]

STRIP_PROMPTS: dict[str, str] = {
    f"{pose}_{direction}": (
        f"{STYLE_PREAMBLE}\n\n"
        f"{STRIP_STYLE_PREAMBLE.format(n=ANIMATION_FRAME_COUNTS[pose])}\n\n"
        f"{DIRECTION_PROMPTS[direction]}\n\n"
        f"{STRIP_POSE_PROMPTS[pose]}\n\n"
        f"{STYLE_RECAP}"
    )
    for pose in _BASE_POSE_NAMES
    for direction in _DIRECTIONS
}

STRIP_NAMES: list[str] = list(STRIP_PROMPTS.keys())

CANARY_NAMES: list[str] = ["idle_down", "move_side"]
