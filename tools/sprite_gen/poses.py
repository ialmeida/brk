"""Prompt text for Player animation strips, used by generate_sprites.py.

Each animation+direction generates ONE multi-frame strip in a single Gemini call (see
SPRITE_REGEN_BRIEF.md Method B) instead of one call per static frame, so frames within an
animation stay visually consistent with each other.
"""

STYLE_PREAMBLE_GENERIC = (
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
    "person with clearly defined arms, legs, and torso, not a tiny stub-limbed blob. "
    "HEAD WIDTH vs SHOULDERS -- check this explicitly: measured at their widest points, "
    "the head must be AT LEAST as wide as the shoulder bar, ideally slightly wider -- "
    "because of the steep top-down angle, the wide dome of the head should visually "
    "cover or overhang the shoulders below it, never read as a smaller head perched "
    "narrower than the shoulders/torso. A head that looks narrower than the shoulders is "
    "a normal-human-proportion mistake and is wrong.\n\n"
    "LIMB LENGTH DURING ACTION POSES -- this is a common failure mode, watch for it "
    "specifically: the arms and legs are short and stocky at rest, and they MUST STAY "
    "THAT SAME SHORT LENGTH even when fully extended for a kick, punch, or lunge. A "
    "fully-extended chibi leg is a short stubby leg swung up to an extreme ANGLE -- it "
    "does not grow longer, and it reaches noticeably LESS far/high than a realistically "
    "proportioned human leg would for the same pose. If a kick or punch would require a "
    "normal-length limb to look fully extended, draw the chibi limb at a more extreme "
    "angle instead of stretching it -- never lengthen an arm or leg past its own resting "
    "size to make a strike reach further. The head's absolute size (its width and height "
    "in pixels relative to the canvas) must also stay IDENTICAL across every frame, "
    "including the most dynamic action frames -- never shrink the head to make a pose "
    "read as more dynamic or to balance out a more extended limb.\n\n"
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
)
# The character-specific likeness/hairstyle/outfit prose lives per-character in
# characters.py (Character.likeness_prose) and is appended to STYLE_PREAMBLE_GENERIC by
# build_style_preamble(), so the generic camera/proportion scaffolding above stays shared
# across every character while only the appearance description varies.


def build_style_preamble(likeness_prose: str) -> str:
    """Full style preamble for one character: shared scaffolding + that character's likeness."""
    return STYLE_PREAMBLE_GENERIC + likeness_prose

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
    "side": "The character is turned to face screen-right (east), shown from a 3/4 angle so one side of their body and face profile are visible, for this ENTIRE pose and in EVERY frame -- the head stays turned at this same profile angle throughout, even as the legs and arms move through the stride or attack. Do NOT let the head swing back toward a frontal, both-eyes-visible view in any frame just because the body is mid-motion; only one eye and one side of the glasses/face should ever be visible, the same way in every frame. The hair silhouette must stay exactly as short and close-cropped as the reference idle pose -- do NOT add extra volume, height, or poof to the hair just because the head is turned; it should look like the same flat, neat haircut simply rotated, not a bigger or fluffier hairstyle.",
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

TURNAROUND_BODY = (
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
    "is wrong, even for a fast walk, a punch, or any other high-energy pose. This also means "
    "the head-to-body size ratio: measure image (2)'s head height against its total "
    "standing height and match that SAME ratio exactly -- the head is large and the body is "
    "short and stocky, roughly chibi-doll proportions, NOT a normal or slender human build. "
    "Do NOT shrink the head or lengthen/slim the torso and legs just because the character "
    "is mid-stride or mid-action -- a longer-legged, smaller-headed, more normally-proportioned "
    "figure is wrong even if the motion itself is otherwise correct. This applies with equal "
    "force to the single most dynamic, full-extension frame of the pose (the highest kick, "
    "the longest punch reach, the deepest lunge) -- that frame is exactly where proportions "
    "most often drift toward a normal human build, and it is exactly where they must NOT. "
    "Measure the extended arm or leg in that frame against image (2)'s resting arm/leg "
    "length: it must be the SAME length, just rotated to a more extreme angle, not a longer "
    "limb. If reaching the described extension would require a longer limb, favor a more "
    "extreme angle and a bigger forward lean/lunge of the short chibi body over actually "
    "lengthening the limb.\n\n"
    "HEAD ANGLE AND WIDTH IN ACTION POSES -- another common drift to watch for: the most "
    "dynamic, full-extension frame of a pose is also exactly where the head most often "
    "tilts away from the steep top-down dome angle into a more face-forward or 3/4 "
    "profile angle, and where the head's width narrows to look smaller than the "
    "shoulders. Neither is acceptable. In every frame, including the full-extension "
    "frame, the head must keep reading as the SAME flat-topped, wide dome seen from "
    "above as in image (2), at least as wide as the shoulder bar beneath it -- a body "
    "twisting or lunging into a strike rotates the SHOULDERS and TORSO, not the camera "
    "angle on the head. If this is a frame for the 'up' (facing away) direction "
    "specifically, the face (eyes, cheek, jaw, glasses lenses) must still be completely "
    "hidden behind the back of the head in that full-extension frame, exactly as it is "
    "in the resting frames -- a kick or punch thrown by a character facing away never "
    "reveals any part of the face, no matter how far the body twists into the strike."
)

_BASE_POSE_NAMES: list[str] = list(STRIP_POSE_PROMPTS.keys())
_DIRECTIONS: list[str] = ["down", "up", "side"]

# Strip names are independent of the (character-specific) prompt text so update_player_tscn.py
# and qa wiring can rely on them without building any character's prompts.
STRIP_NAMES: list[str] = [f"{pose}_{direction}"
                          for pose in _BASE_POSE_NAMES
                          for direction in _DIRECTIONS]

CANARY_NAMES: list[str] = ["idle_down", "move_side"]


def build_prompts(likeness_prose: str) -> dict[str, object]:
    """Assemble every prompt for one character from the shared scaffolding + their likeness.

    Returns {"strip_prompts": {name: prompt}, "turnaround_prompt": prompt}. The generic
    camera/proportion/strip text is identical for every character; only the likeness block
    (woven into the style preamble) varies.
    """
    preamble = build_style_preamble(likeness_prose)
    strip_prompts = {
        f"{pose}_{direction}": (
            f"{preamble}\n\n"
            f"{STRIP_STYLE_PREAMBLE.format(n=ANIMATION_FRAME_COUNTS[pose])}\n\n"
            f"{DIRECTION_PROMPTS[direction]}\n\n"
            f"{STRIP_POSE_PROMPTS[pose]}\n\n"
            f"{STYLE_RECAP}"
        )
        for pose in _BASE_POSE_NAMES
        for direction in _DIRECTIONS
    }
    turnaround_prompt = f"{preamble}\n\n{TURNAROUND_BODY}"
    return {"strip_prompts": strip_prompts, "turnaround_prompt": turnaround_prompt}


# --- Sibling anchoring -------------------------------------------------------------------
# A later link in a combo chain, or a harder-angle variant of a pose, drifts in head/body
# proportion when generated only from text + the static turnaround. To pin it down we pass an
# already-approved sibling strip as an extra reference image (see SIBLING_LOCK_INSTRUCTION).
# CHAIN_BASE maps each non-first combo link to the first (lightest) link of its chain; the
# resolution rule below is data-driven so new combos/characters reuse it without edits here.
CHAIN_BASE: dict[str, str] = {
    "basic_punch_2": "basic_punch_1",
    "basic_punch_3": "basic_punch_1",
    "basic_kick_2": "basic_kick_1",
    "basic_kick_3": "basic_kick_1",
    "master_2": "master_1",
    "master_3": "master_1",
    "master_4": "master_1",
}
ANCHOR_DIRECTION = "down"  # the most reliable angle; side/up variants anchor to it

SIBLING_LOCK_INSTRUCTION = (
    "You are also given image (3): an already-approved sprite strip of THIS SAME character in "
    "this exact top-down pixel-art style, generated earlier and confirmed correct. Image (3) "
    "is a PROPORTION AND SCALE anchor only: match its head size and head diameter (the width "
    "of the dome seen from above), its head-to-body size ratio, its short stocky limb length, "
    "its shoulder width, and its overall character scale EXACTLY. The new strip you generate "
    "must look like the same character at the same size as image (3), just in the new pose and "
    "direction described below. Do NOT copy image (3)'s specific pose, facing direction, or "
    "frame count -- only its proportions and scale. If the requested pose is a later, heavier "
    "hit in a combo, the character must NOT become slimmer, taller, or smaller-headed than "
    "image (3); a heavier hit changes the pose's energy, never the character's proportions."
)


def sibling_of(name: str) -> str | None:
    """Best already-approved sibling strip to use as a proportion anchor, or None.

    Combo links anchor to their chain base in the SAME direction; a side/up variant of a base
    pose anchors to that pose's down variant. The chain rule takes precedence over the
    direction rule, and a down-facing base pose has no sibling (turnaround anchor only).
    """
    pose, direction = name.rsplit("_", 1)
    if pose in CHAIN_BASE:
        return f"{CHAIN_BASE[pose]}_{direction}"
    if direction != ANCHOR_DIRECTION:
        return f"{pose}_{ANCHOR_DIRECTION}"
    return None
