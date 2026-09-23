#!/usr/bin/env python3
"""Convert reference SVG number files to an SVG font file."""
import re
import os

REFERENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference")
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
OUTPUT = os.path.join(DIST_DIR, "dice-font.svg")

UNITS_PER_EM = 1000
ASCENDER = 900
DESCENDER = -100

def flip_y_in_d(d):
    """Flip y-coordinates in an SVG path d attribute.

    In the source SVGs, y increases downward (0 at top, 1000 at bottom).
    In SVG fonts, y increases upward (0 at baseline, units-per-em at top).
    Baseline in source SVGs is at y=800.
    So: font_y = 800 - svg_y
    """
    BASELINE_Y = 800

    tokens = re.findall(
        r'[MmZzLlHhVvCcSsQqTtAa]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',
        d
    )

    result = []
    i = 0
    current_cmd = None

    # How many coordinate values each command consumes per repeat
    cmd_sizes = {
        'M': 2, 'L': 2, 'T': 2,
        'H': 1, 'V': 1,
        'C': 6, 'S': 4, 'Q': 4,
        'A': 7,
        'm': 2, 'l': 2, 't': 2,
        'h': 1, 'v': 1,
        'c': 6, 's': 4, 'q': 4,
        'a': 7,
    }
    # Which positions in the param list are y-coordinates (0-indexed)
    # For a full repeat of the command
    y_positions = {
        'M': [1], 'L': [1], 'T': [1],
        'V': [0],
        'C': [1, 3, 5],
        'S': [1, 3],
        'Q': [1, 3],
        'A': [1, 3, 5],  # actually: rx ry x-rotation large-arc sweep x y -> y is [6], but also ry=[1] is not a position
        'm': [1], 'l': [1], 't': [1],
        'v': [0],
        'c': [1, 3, 5],
        's': [1, 3],
        'q': [1, 3],
    }
    # A: rx ry x-rotation large-arc-flag sweep-flag x y
    # Only the last y (index 6) is a y-coordinate to flip
    y_positions['A'] = [6]
    y_positions['a'] = [6]

    seen_move = False
    while i < len(tokens):
        token = tokens[i]

        if re.match(r'[MmZzLlHhVvCcSsQqTtAa]', token):
            current_cmd = token
            result.append(token)
            i += 1
            if current_cmd in ('Z', 'z'):
                continue
            continue

        # We're parsing parameters for current_cmd
        if current_cmd is None:
            i += 1
            continue

        base = current_cmd.upper()
        size = cmd_sizes.get(base, 0)
        if size == 0:
            i += 1
            continue

        is_relative = current_cmd.islower() and not (current_cmd in ('m', 'M') and not seen_move)
        if current_cmd in ('m', 'M'):
            seen_move = True
        y_pos = set(y_positions.get(base, []))

        # Collect one full set of parameters
        params = []
        for j in range(size):
            if i < len(tokens) and not re.match(r'[MmZzLlHhVvCcSsQqTtAa]', tokens[i]):
                params.append(tokens[i])
                i += 1
            else:
                params.append('0')

        # Transform y-coordinates
        for j in range(size):
            val = params[j]
            if j in y_pos:
                fval = float(val)
                if is_relative:
                    transformed = -fval
                else:
                    transformed = BASELINE_Y - fval
                # Format nicely
                if transformed == int(transformed):
                    result.append(str(int(transformed)))
                else:
                    result.append(f"{transformed:.6f}".rstrip('0').rstrip('.'))
            else:
                result.append(val)

    return ' '.join(result)


def extract_path_d(svg_path):
    """Extract the d attribute from the first path element in an SVG file."""
    with open(svg_path, 'r') as f:
        content = f.read()

    # Match the d attribute - handle multiline
    match = re.search(r'<path\b[^>]*\bd="([^"]*)"', content, re.DOTALL)
    if not match:
        # Try with single quotes
        match = re.search(r"<path\b[^>]*\bd='([^']*)'", content, re.DOTALL)
    if not match:
        raise ValueError(f"No path d attribute found in {svg_path}")

    d = match.group(1).strip()
    # Collapse whitespace
    d = re.sub(r'\s+', ' ', d)
    return d


def build_svg_font():
    glyphs = []

    for digit in range(10):
        svg_file = os.path.join(REFERENCE_DIR, f"{digit}.svg")
        if not os.path.exists(svg_file):
            print(f"Warning: {svg_file} not found, skipping")
            continue

        d = extract_path_d(svg_file)
        d = flip_y_in_d(d)

        # Unicode code point for the digit character
        unicode_char = str(digit)

        # Width: we'll set a uniform advance width
        # The source SVGs are 1000px wide; use 600 as a reasonable advance
        advance_width = 600

        glyph = f'      <glyph glyph-name="{digit}" unicode="{unicode_char}" d="{d}" />'
        glyphs.append(glyph)

    font_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <defs>
    <font id="dice-font" horiz-adv-x="600">
      <font-face
        font-family="dice-font"
        units-per-em="{UNITS_PER_EM}"
        ascent="{ASCENDER}"
        descent="{DESCENDER}"
        alphabetic="0"
        panose-1="0 0 0 0 0 0 0 0 0 0"
      />
{chr(10).join(glyphs)}
    </font>
  </defs>
</svg>
'''

    os.makedirs(DIST_DIR, exist_ok=True)
    with open(OUTPUT, 'w') as f:
        f.write(font_svg)

    print(f"Font written to {OUTPUT}")
    print(f"Contains {len(glyphs)} glyphs (0-9)")


if __name__ == '__main__':
    build_svg_font()
