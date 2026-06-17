# Player sprite generator

One-off authoring tool that calls Gemini's image model ("nano banana") directly to
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
- If `--model` (default `gemini-2.5-flash-image`, the GA "nano banana" model) returns a
  model-not-found error, run `client.models.list()` to see what's currently available --
  newer options as of writing include `gemini-3.1-flash-image` and `gemini-3-pro-image`.
