"""Trace ida's question banner from Sora Bold, then hand-clean it.

Sora is the brand typeface (OFL, https://fonts.google.com/specimen/Sora).
This script rasterizes Sora Bold with Pillow onto a 5-row grid and a
4-row grid. A 4-by-5 cell grid closes the counters, so every glyph below
is hand-cleaned: solid █ only, open counters, one-step rounds on the
bowls, straight stems. The TTF is not vendored. Pass --font to rasterize
a local Sora[wght].ttf; the committed tables are the cleaned glyphs.

    python3 skills/ida/scripts/build_font.py --font /path/to/Sora[wght].ttf

Writes skills/ida/scripts/sora_glyphs.py. The skill loads that module.
It does not need the font at runtime.
"""

from __future__ import annotations

import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "sora_glyphs.py"

# 5 rows: ascender, three x-height rows, descender.
# 4 rows: ascender and three x-height rows. g j p q y stay inside that box.


def _g(*rows: str) -> tuple[str, ...]:
    width = max(len(row) for row in rows)
    return tuple(row.ljust(width) for row in rows)


# Hand-cleaned from the Sora Bold raster. Bowls step one cell at the
# corner. c, e, and s stay open. t k v w x y keep straight strokes.
SORA5 = {
    "a": _g("    ", " ██ ", "█ █ ", " ███", "    "),
    "b": _g("█    ", "████ ", "█   █", "████ ", "     "),
    "c": _g("    ", " ███", "█   ", " ███", "    "),
    "d": _g("    █", " ████", "█   █", " ████", "     "),
    "e": _g("    ", " ███", "█ ██", " ███", "    "),
    "f": _g(" ██", "█  ", "███", " █ ", "   "),
    "g": _g("     ", " ███ ", "█   █", " ███ ", "  ███"),
    "h": _g("█   ", "█   ", "███ ", "█  █", "    "),
    "i": _g("█", " ", "█", "█", " "),
    "j": _g(" █", "  ", " █", " █", "██"),
    "k": _g("█   ", "█ █ ", "██  ", "█  █", "    "),
    "l": _g("█", "█", "█", "█", " "),
    "m": _g("       ", "██ ███", "█ █ █ █", "█ █ █ █", "       "),
    "n": _g("    ", "███ ", "█  █", "█  █", "    "),
    "o": _g("     ", " ███ ", "█   █", " ███ ", "     "),
    "p": _g("     ", "████ ", "█   █", "████ ", "█    "),
    "q": _g("     ", " ████", "█   █", " ████", "    █"),
    "r": _g("   ", "███", "█  ", "█  ", "   "),
    "s": _g("    ", "███ ", " ██ ", "███ ", "    "),
    "t": _g(" █ ", "███", " █ ", " █ ", "   "),
    "u": _g("    ", "█  █", "█  █", " ███", "    "),
    "v": _g("     ", "█   █", " █ █ ", "  █  ", "     "),
    "w": _g("       ", "█ █ █ █", " █ █ █ ", "  █ █  ", "       "),
    "x": _g("   ", "█ █", " █ ", "█ █", "   "),
    "y": _g("     ", "█   █", " █ █ ", "  █  ", "  █  "),
    "z": _g("    ", "████", "  █ ", "████", "    "),
    "0": _g(" ███ ", "█   █", "█   █", " ███ ", "     "),
    "1": _g(" █ ", "██ ", " █ ", " █ ", "   "),
    "2": _g("████ ", "   █ ", " ██  ", "████ ", "     "),
    "3": _g("████ ", "  ██ ", "   █ ", "████ ", "     "),
    "4": _g("█  █ ", "█  █ ", "████ ", "   █ ", "     "),
    "5": _g("████ ", "█    ", " ███ ", "████ ", "     "),
    "6": _g(" ███ ", "█    ", "████ ", " ███ ", "     "),
    "7": _g("████ ", "   █ ", "  █  ", " █   ", "     "),
    "8": _g("████ ", " ██  ", "████ ", " ██  ", "     "),
    "9": _g(" ███ ", "█   █", " ████", "   █ ", "     "),
    "'": _g("█", " ", " ", " ", " "),
    "-": _g("   ", "   ", "███", "   ", "   "),
    ".": _g(" ", " ", " ", "█", " "),
    "/": _g("  █", " █ ", " █ ", "█  ", "   "),
    ",": _g("  ", "  ", " █", "██", "  "),
    "?": _g(" ███", "   █", " ██ ", " █  ", " █  "),
}

# Same letters, one row shorter and a column narrower where the bowl allows.
# g j p q y keep a compact tail inside the x-height.
SORA4 = {
    "a": _g("    ", " ██ ", "█ █ ", " ███"),
    "b": _g("█   ", "███ ", "█  █", "███ "),
    "c": _g("    ", "███ ", "█   ", "███ "),
    "d": _g("   █", " ███", "█  █", " ███"),
    "e": _g("    ", " ███", "█ ██", " ███"),
    "f": _g("██ ", " █ ", "███", " █ "),
    "g": _g("    ", " ██ ", "█  █", "  ██"),
    "h": _g("█   ", "███ ", "█  █", "█  █"),
    "i": _g("█", " ", "█", "█"),
    "j": _g(" █", "  ", " █", "██"),
    "k": _g("█   ", "█ █ ", "██  ", "█  █"),
    "l": _g("█", "█", "█", "█"),
    "m": _g("      ", "██ ██ ", "█ █ █ ", "█ █ █ "),
    "n": _g("    ", "███ ", "█  █", "█  █"),
    "o": _g("    ", " ██ ", "█  █", " ██ "),
    "p": _g("    ", "███ ", "█  █", "███ "),
    "q": _g("    ", " ███", "█  █", " ███"),
    "r": _g("   ", "███", "█  ", "█  "),
    "s": _g("    ", "███ ", " ██ ", "███ "),
    "t": _g(" █ ", "███", " █ ", " █ "),
    "u": _g("    ", "█  █", "█  █", " ███"),
    "v": _g("     ", "█   █", " █ █ ", "  █  "),
    "w": _g("      ", "█ █ █ ", " █ █ █", "  █ █ "),
    "x": _g("   ", "█ █", " █ ", "█ █"),
    "y": _g("     ", "█   █", " ███ ", "  ██ "),
    "z": _g("    ", "████", "  █ ", "████"),
    "0": _g(" ██ ", "█  █", "█  █", " ██ "),
    "1": _g(" █", "██", " █", " █"),
    "2": _g("███ ", "  █ ", " ██ ", "████"),
    "3": _g("███ ", " ██ ", "  █ ", "███ "),
    "4": _g("█ █ ", "█ █ ", "████", "  █ "),
    "5": _g("████", "█   ", " ███", "████"),
    "6": _g(" ███", "█   ", "███ ", " ███"),
    "7": _g("████", "  █ ", " █  ", "█   "),
    "8": _g("███ ", " ██ ", "███ ", " ██ "),
    "9": _g(" ██ ", "█  █", " ███", "  █ "),
    "'": _g("█", " ", " ", " "),
    "-": _g("   ", "███", "   ", "   "),
    ".": _g(" ", " ", "█", " "),
    "/": _g("  █", " █ ", "█  ", "   "),
    ",": _g("  ", " █", "██", "  "),
    "?": _g("███ ", "  █ ", " █  ", " █  "),
}


def _rasterize(font_path: Path) -> None:
    """Sample Sora Bold so a missing hand-clean is obvious. Ink is not copied.

    The raw grid closes c, e, and s. The tables above are the cleaned forms.
    """
    from PIL import Image, ImageDraw, ImageFont

    size = 180
    face = ImageFont.truetype(str(font_path), size)
    face.set_variation_by_axes([700])
    base = 280

    def render(ch: str) -> Image.Image:
        image = Image.new("L", (900, 560), 255)
        ImageDraw.Draw(image).text((50, base), ch, font=face, fill=0, anchor="ls")
        return image

    def yspan(ch: str) -> tuple[int, int]:
        image = render(ch)
        pixels = image.load()
        ys = [y for y in range(560) for x in range(900) if pixels[x, y] < 150]
        return min(ys), max(ys)

    x_top, x_bot = yspan("x")
    step = (x_bot - x_top) / 3
    bands = [
        (yspan("i")[0], x_top - 1),
        (x_top, int(x_top + step) - 1),
        (int(x_top + step), int(x_top + 2 * step) - 1),
        (int(x_top + 2 * step), x_bot),
        (x_bot + 1, yspan("g")[1]),
    ]
    sample = render("o")
    pixels = sample.load()
    xs = [x for y in range(560) for x in range(900) if pixels[x, y] < 150]
    column = (max(xs) - min(xs) + 1) / 5
    print(f"traced {font_path.name} bold, o column {column:.1f}px, bands {bands}")
    for ch in "abcdefghijklmnopqrstuvwxyz":
        if ch not in SORA5:
            raise SystemExit(f"no hand-cleaned 5-row glyph for {ch}")


def _emit(path: Path) -> None:
    def block(name: str, font: dict[str, tuple[str, ...]]) -> str:
        lines = [f"{name} = {{"]
        for ch, rows in font.items():
            shown = ", ".join(repr(row) for row in rows)
            lines.append(f"    {ch!r}: ({shown}),")
        lines.append("}")
        return "\n".join(lines)

    text = "\n".join(
        [
            '"""Question-banner glyphs traced from Sora Bold.',
            "",
            "Hand-cleaned to solid blocks. Generated by build_font.py.",
            "Sora is licensed under the SIL Open Font License.",
            "The skill does not ship or load the font file.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            block("SORA5", SORA5),
            "",
            block("SORA4", SORA4),
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, help="Sora[wght].ttf to trace")
    args = parser.parse_args()
    if args.font:
        _rasterize(args.font)
    else:
        print("no --font given; writing the hand-cleaned tables only")
    _emit(OUT)


if __name__ == "__main__":
    main()
