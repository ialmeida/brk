# Player sprite generator

One-off authoring tool that calls Gemini's image model ("nano banana") directly to
generate the 15 Player animation poses, then post-processes them into clean pixel art
for `actors/player/Player.tscn`. Not used at runtime by the game.

## Setup

```bash
cd /home/user/brk
python3 -m venv .venv-sprites
source .venv-sprites/bin/activate
pip install -r tools/sprite_gen/requirements.txt
export GEMINI_API_KEY="..."   # never write this to a file
```

## Usage

1. Generate and approve the base `idle` pose first -- everything else style-locks to it:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py \
       --reference /path/to/your_photo.jpg \
       --only idle
   ```

   Inspect `assets/sprites/player/processed/idle.png`. Re-run with `--only idle --force`
   (optionally after editing the prompt in `poses.py`) until it looks right.

2. Generate the remaining 14 poses, conditioned on both the photo and the approved idle:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py \
       --reference /path/to/your_photo.jpg \
       --base-image assets/sprites/player/processed/idle.png \
       --all --skip-existing
   ```

3. Regenerate any outlier after a visual review:

   ```bash
   python3 tools/sprite_gen/generate_sprites.py \
       --reference /path/to/your_photo.jpg \
       --base-image assets/sprites/player/processed/idle.png \
       --only basic_kick_2 --force
   ```

## Notes

- Never place your reference photo inside this repo, even temporarily.
- `assets/sprites/player/raw/` holds unprocessed model output (gitignored, local-only).
  Only `assets/sprites/player/processed/` is committed.
- If `--model` (default `gemini-2.5-flash-image`, the GA "nano banana" model) returns a
  model-not-found error, run `client.models.list()` to see what's currently available --
  newer options as of writing include `gemini-3.1-flash-image` and `gemini-3-pro-image`.
