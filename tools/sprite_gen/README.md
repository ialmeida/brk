# Player sprite generator

One-off authoring tool that calls Gemini's image model ("Nano Banana Pro") directly to
generate the 45 Player animation sprites (15 poses x 3 directions: down/up/side), then
post-processes them into clean pixel art for `actors/player/Player.tscn`. Not used at
runtime by the game.

## Setup

```bash
cd /home/user/brk
python3 -m venv .venv-sprites
source .venv-sprites/bin/activate
pip install -r tools/sprite_gen/requirements.txt
export GEMINI_API_KEY="..."   # never write this to a file
```

## Usage

1. Generate and approve the base `idle_down` pose first -- everything else style-locks to it:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py \
       --reference /path/to/your_reference.jpg \
       --only idle_down
   ```

   Inspect `assets/sprites/player/processed/idle_down.png`. Re-run with
   `--only idle_down --force` (optionally after editing the prompt in `poses.py`) until
   it looks right.

2. Generate the remaining 44 sprites, conditioned on both the reference image and the
   approved idle_down:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py \
       --reference /path/to/your_reference.jpg \
       --base-image assets/sprites/player/processed/idle_down.png \
       --all --skip-existing
   ```

3. Regenerate any outlier after a visual review:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py \
       --reference /path/to/your_reference.jpg \
       --base-image assets/sprites/player/processed/idle_down.png \
       --only basic_kick_2_side --force
   ```

## Notes

- Never place your reference image inside this repo, even temporarily.
- `assets/sprites/player/raw/` holds unprocessed model output (gitignored, local-only).
  Only `assets/sprites/player/processed/` is committed.
- Default model is `gemini-3-pro-image` (the GA "Nano Banana Pro" / Gemini 3 Pro Image
  model). Use `--model gemini-2.5-flash-image` to fall back to the older "Nano Banana"
  model if needed. Do not use `-preview` model id variants (e.g.
  `gemini-3-pro-image-preview`) -- preview ids get deprecated and retired.
- Nano Banana Pro may require a paid/billing-enabled API key (not guaranteed on the
  free tier) -- if you see a quota or billing error, check your Google AI Studio
  project's plan.
- If `--model` returns a model-not-found error, run `client.models.list()` to see
  what's currently available.
