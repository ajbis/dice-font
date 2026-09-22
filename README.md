# dice-font

## Building

Generate the SVG font from the reference digit paths:

```bash
python3 build-font.py
```

**Note:** This SVG font does not include kerning pairs — it only contains the raw glyph outlines. Kerning is tuned later in FontForge, saved as a `.sfd` file.

Open `dist/dice-font.svg` in FontForge, adjust kerning visually, save the project as `dist/dice-font.sfd`, then export as `dist/dice-font.ttf`.

Convert the TTF to WOFF2:

```bash
cd dist
woff2_compress dice-font.ttf
```

## Testing

Serve the dist folder locally:

```bash
./serve.sh
```

Then open http://localhost:8000 in your browser.

## Status

Spacing/kerning is still a work in progress and will be refined visually in FontForge.