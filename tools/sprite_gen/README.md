# Player sprite generator

One-off authoring tool that calls Gemini's image model ("Nano Banana Pro") directly to
generate the 45 Player animation sprites (15 animations x 3 directions: down/up/side),
each as a multi-frame strip, then post-processes the strips into clean, consistently
scaled and palette-snapped pixel art for `actors/player/Player.tscn`. Not used at runtime
by the game. The method (one Gemini call per whole animation strip, fixed magenta key
color, locked palette, per-strip scale normalization, fixed canvas + baseline) is
documented in `SPRITE_REGEN_BRIEF.md`.

## Setup

```bash
cd /home/user/brk
python3 -m venv .venv-sprites
source .venv-sprites/bin/activate
pip install -r tools/sprite_gen/requirements.txt
export GEMINI_API_KEY="..."   # never write this to a file
```

## Usage

1. Generate the master reference turnaround (3 cells: down / up / side, same neutral
   idle pose, magenta background) and inspect it by eye:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py turnaround \
       --reference /path/to/your_reference.png
   ```

   Inspect `tools/sprite_gen/reference/turnaround_raw.png` against the identity checklist
   (hair, glasses, shirt stripes, crest, denim, sneakers, watch) and the perspective
   checklist (true 3/4 top-down angle, not a front-on portrait) in `SPRITE_REGEN_BRIEF.md`.
   Re-run (optionally after editing `TURNAROUND_PROMPT` in `poses.py`) until it looks right.

2. Once happy, post-process it into the style-lock reference used by every later call:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py approve-turnaround
   ```

   This writes `tools/sprite_gen/reference/turnaround.png` -- a *generated* sheet, safe to
   commit (it contains no personal data, unlike the `--reference` image above).

3. Generate the two canary strips (`idle_down`, `move_side`) and review the sheet PNG +
   GIF + QA report for each before spending on the rest:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py strip \
       --reference /path/to/your_reference.png --canary
   ```

   Sheets/GIFs land in `tools/sprite_gen/qa_sheets/` (gitignored). Iterate on the prompt
   text in `poses.py` or the processing chain in `strips.py` as needed, then re-run with
   `--only idle_down --force` (or `move_side`) to regenerate just the one bad strip.

4. Generate the remaining 43 strips:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py strip \
       --reference /path/to/your_reference.png --all --skip-existing
   ```

5. Regenerate any single outlier strip after a visual review:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py strip \
       --reference /path/to/your_reference.png --only basic_kick_2_side --force
   ```

6. Wire the sliced frames into `actors/player/Player.tscn`:

   ```bash
   python3 tools/sprite_gen/update_player_tscn.py
   ```

## Multiple characters

Every command takes `--character NAME` (default `player`). A character bundles its
reference/raw/output directories, palette, approved turnaround, optional hair-color override,
and the likeness/hairstyle/outfit prose, all in `characters.py`. The generic camera-angle,
chibi-proportion, and strip-format prose stays shared in `poses.py`, so adding a character is
just one `Character(...)` entry (paths + palette + likeness prose) -- no prompt copy-paste.
Add a new character by registering it in `characters.CHARACTERS`, then run any command with
`--character <name>`.

## Proportion consistency

Two mechanisms keep the head reading as the same-size dome across a pose's directions and a
combo's links:

- **QA head-dome check** (`qa.py`): the hair forms a solid dark dome at the top of the
  silhouette; its diameter over the silhouette height is a direction-stable proxy for the
  head-to-body ratio. Per-direction targets are derived dynamically from the approved
  `turnaround.png` (no hardcoded ratio), and a strip FAILs in `qa_report.txt` if its
  largest-headed frame is more than the tolerance below target. The measured ratio is printed
  for every strip, pass or fail, as a graded signal next to the existing height check.
- **Sibling image anchor** (`poses.sibling_of`): when a strip is a later link in a combo
  (`basic_kick_2/3`, `master_2/3/4`, ...) or a harder-angle variant of a pose (`side`/`up`),
  the generator passes the already-approved sibling strip (the chain base in the same
  direction, or the pose's `down` variant) as an extra reference image with an explicit
  "match this head size and proportions exactly" instruction. The base/`down` strips must be
  generated and approved first so the anchor exists on disk.

## Notes

- Never place your personal `--reference` image inside this repo, even temporarily. The
  committed `tools/sprite_gen/reference/turnaround.png` is different: it's AI-generated
  pixel art, not personal data, so it's safe to commit as the style-lock reference.
- `assets/sprites/player/raw/` holds unprocessed model strip output (gitignored,
  local-only). Only the sliced frames in `assets/sprites/player/processed/` are committed.
- Default model is `gemini-3-pro-image` (the GA "Nano Banana Pro" / Gemini 3 Pro Image
  model). Use `--model gemini-2.5-flash-image` to fall back to the older "Nano Banana"
  model if needed. Do not use `-preview` model id variants (e.g.
  `gemini-3-pro-image-preview`) -- preview ids get deprecated and retired.
- Nano Banana Pro may require a paid/billing-enabled API key (not guaranteed on the
  free tier) -- if you see a quota or billing error, check your Google AI Studio
  project's plan.
- If `--model` returns a model-not-found error, run `client.models.list()` to see
  what's currently available.
