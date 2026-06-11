#!/usr/bin/env python3
"""
Darken the structural background colors of a Zed theme JSON.
Usage: ./darken-themes.py <input.json> <output.json> <amount>
"""

import json
import sys
import re
import copy

# Tokens that are structural backgrounds to darken
BG_TOKENS = {
    "background",
    "surface.background",
    "elevated_surface.background",
    "panel.background",
    "editor.background",
    "editor.gutter.background",
    "terminal.background",
    "status_bar.background",
    "title_bar.background",
    "title_bar.inactive_background",
    "toolbar.background",
    "tab_bar.background",
    "tab.active_background",
    "tab.inactive_background",
    "element.background",
    "element.hover",
    "element.active",
    "element.selected",
    "element.disabled",
    "ghost_element.background",
    "ghost_element.hover",
    "ghost_element.active",
    "ghost_element.selected",
    "ghost_element.disabled",
    "border",
    "border.variant",
    "border.focused",
    "border.selected",
    "border.disabled",
    "scrollbar.thumb.background",
    "scrollbar.thumb.hover_background",
    "scrollbar.thumb.border",
    "scrollbar.thumb.active_background",
    "scrollbar.track.background",
    "scrollbar.track.border",
    "editor.subheader.background",
    "editor.active_line.background",
    "editor.highlighted_line.background",
    "editor.line_number",
    "editor.active_line_number",
    "editor.hover_line_number",
    "editor.invisible",
    "editor.wrap_guide",
    "editor.active_wrap_guide",
    "editor.document_highlight.read_background",
    "editor.document_highlight.write_background",
    "editor.indent_guide",
    "editor.indent_guide_active",
}


def is_bg_token(key):
    """Check if a token key is a structural background token."""
    # Don't darken status/semantic backgrounds
    semantic_prefixes = [
        "conflict.",
        "created.",
        "deleted.",
        "error.",
        "hidden.",
        "hint.",
        "ignored.",
        "info.",
        "modified.",
        "predictive.",
        "renamed.",
        "success.",
        "unreachable.",
        "warning.",
        "search.",
        "drop_target.",
        "pane.",
        "panel.focused_",
        "version_control.",
    ]
    for prefix in semantic_prefixes:
        if key.startswith(prefix):
            return False

    # Darken if it's explicitly in our list
    if key in BG_TOKENS:
        return True

    # Darken tokens ending with .background that aren't semantic
    if key.endswith(".background"):
        return True

    return False


def darken_hex(hex_color, amount):
    """Darken a hex color by subtracting `amount` from each RGB channel (0-255)."""
    if hex_color is None:
        return None
    if not isinstance(hex_color, str):
        return hex_color
    hex_color = str(hex_color)
    if (
        hex_color.lower() == "transparent"
        or hex_color == "#00000000"
        or hex_color == "none"
    ):
        return hex_color

    # Parse hex
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)

    if len(h) == 6:
        try:
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            a = ""
        except ValueError:
            return hex_color
    elif len(h) == 8:
        try:
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            a = h[6:8]
        except ValueError:
            return hex_color
    else:
        return hex_color

    # Subtract amount, floor at 0
    r = max(0, r - amount)
    g = max(0, g - amount)
    b = max(0, b - amount)

    return f"#{r:02x}{g:02x}{b:02x}{a}"


def process_theme(input_path, output_path, amount):
    """Read, darken, rename, and write theme JSON."""
    with open(input_path, "r") as f:
        content = f.read()

    # Check for JSON5 comment on line 1 (JetBrains themes)
    has_comment = content.startswith("//")

    # Parse JSON
    data = json.loads(
        content if not has_comment else "\n".join(content.split("\n")[1:])
    )

    # Rename: add " Darker" to pack name and variant names
    data["name"] = data["name"] + " Darker"
    for theme in data.get("themes", []):
        if "name" in theme:
            theme["name"] = theme["name"] + " Darker"

    # Darken structural background colors in each theme variant
    for theme in data.get("themes", []):
        if "style" not in theme:
            continue

        style = theme["style"]
        for key, value in list(style.items()):
            if is_bg_token(key):
                style[key] = darken_hex(value, amount)

    # Write output
    json_str = json.dumps(data, indent=2)

    # If original had a comment, preserve it
    if has_comment:
        json_str = content.split("\n")[0] + "\n" + json_str

    with open(output_path, "w") as f:
        f.write(json_str)
        f.write("\n")

    print(f"✓ {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.json> [amount]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    amount = int(sys.argv[3]) if len(sys.argv) > 3 else 17

    process_theme(input_path, output_path, amount)
