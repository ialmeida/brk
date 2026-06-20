"""Write export_presets.cfg for the Web export, embedding the rotate-overlay HTML.

Run from anywhere; writes to the repo root. Used by .github/workflows/deploy-web.yml so the
preset (including the portrait rotate-overlay markup) is produced the same way locally as
in CI -- run this script and inspect export_presets.cfg before pushing.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROTATE_OVERLAY_HTML = REPO_ROOT / "web" / "rotate_overlay.html"
EXPORT_PRESETS_CFG = REPO_ROOT / "export_presets.cfg"

TEMPLATE = """[preset.0]

name="Web"
platform="Web"
runnable=true
advanced_options=false
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="build/web/index.html"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false
script_export_mode=1

[preset.0.options]

custom_template/debug=""
custom_template/release=""
variant/extensions_support=false
variant/thread_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/custom_html_shell=""
html/head_include={head_include}
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
progressive_web_app/offline_page=""
progressive_web_app/display=1
progressive_web_app/orientation=0
progressive_web_app/icon_144x144=""
progressive_web_app/icon_180x180=""
progressive_web_app/icon_512x512=""
progressive_web_app/background_color=Color(0, 0, 0, 1)
"""


def main() -> None:
    head_include_html = ROTATE_OVERLAY_HTML.read_text()
    cfg = TEMPLATE.format(head_include=json.dumps(head_include_html))
    EXPORT_PRESETS_CFG.write_text(cfg)
    print(f"Wrote {EXPORT_PRESETS_CFG}")


if __name__ == "__main__":
    main()
