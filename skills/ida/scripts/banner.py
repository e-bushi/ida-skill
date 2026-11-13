"""Compact banners for an idk reveal.

Each letter is 3 columns and 3 rows, drawn with █ ▀ ▄. A plain space
separates glyphs. There is no shade character. 18 letters is about 72
columns. A name that fits is one line. Otherwise each word is its own
line. A word that still does not fit, or that uses a character this
font does not have, falls back to spaced caps with a ■.

The choice-box banner is lowercase Sora. A name that fits uses 5 rows.
Otherwise it uses 4 rows. If that is still too wide, each word is its
own 4-row line. Plain text is only for a word wider than the frame.
"""

from __future__ import annotations

from common import SPACER
from sora_glyphs import SORA4, SORA5

# Three rows, top to bottom. Width is the string length.
FONT = {
    "A": ["▀█▀", "█▀█", "▀ ▀"],
    "B": ["█▀▄", "█▀█", "█▄▀"],
    "C": ["▄▀▀", "█  ", "▀▄▄"],
    "D": ["█▀▄", "█ █", "█▄▀"],
    "E": ["█▀▀", "█▀ ", "█▄▄"],
    "F": ["█▀▀", "█▀ ", "█  "],
    "G": ["▄▀▀", "█▄█", "▀▄▀"],
    "H": ["█ █", "█▀█", "█ █"],
    "I": ["▀█▀", " █ ", "▄█▄"],
    "J": [" ▀█", "  █", "▀▄▀"],
    "K": ["█ █", "█▀ ", "█ █"],
    "L": ["█  ", "█  ", "█▄▄"],
    "M": ["█▄█", "███", "█ █"],
    "N": ["█▀█", "███", "█ █"],
    "O": ["▄▀▄", "█ █", "▀▄▀"],
    "P": ["█▀▄", "█▀▀", "█  "],
    "Q": ["▄▀▄", "█ █", "▀▄█"],
    "R": ["█▀▄", "█▀█", "█ █"],
    "S": ["▄▀▀", "▀▀▄", "▀▄▀"],
    "T": ["▀█▀", " █ ", " █ "],
    "U": ["█ █", "█ █", "▀▄▀"],
    "V": ["█ █", "█ █", " ▀ "],
    "W": ["█ █", "███", "█▀█"],
    "X": ["█ █", " █ ", "█ █"],
    "Y": ["█ █", " ▀ ", " █ "],
    "Z": ["▀▀█", " █ ", "█▄▄"],
    "0": ["▄▀▄", "█ █", "▀▄▀"],
    "1": [" █ ", "▀█ ", "▄█▄"],
    "2": ["▀▀▄", " ▀ ", "█▄▄"],
    "3": ["▀▀▄", " ▀▄", "▄▄▀"],
    "4": ["█ █", "▀▀█", "  █"],
    "5": ["█▀▀", "▀▀▄", "▄▄▀"],
    "6": ["▄▀ ", "█▀▄", "▀▄▀"],
    "7": ["▀▀█", " █ ", "█  "],
    "8": ["▄▀▄", "▀▄▀", "▄▀▄"],
    "9": ["▄▀▄", "▀▄█", "▄▄▀"],
    " ": ["  ", "  ", "  "],
    "'": ["▀", " ", " "],
    "-": ["   ", "▀▀▀", "   "],
    ".": ["   ", "   ", " ▄ "],
    "/": ["  █", " █ ", "█  "],
    ",": ["   ", "   ", " ▄ "],
    "?": ["▀▀▄", " ▀ ", " ▄ "],
}

# Question banner, traced from Sora Bold. See sora_glyphs.py.
# Interior of the 64-column frame: two spaces of inset, so the art is 62.
CONTENT_MAX = 62
LETTER_GAP = " "
WORD_GAP = "  "


def _banner_text(name: str) -> str:
    text = str(name).replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")
    return " ".join(text.lower().split())


def _paint(text: str, font: dict) -> list[str]:
    """One banner line. One column between letters, two between words."""
    height = len(next(iter(font.values())))
    rows = [""] * height
    for word_index, word in enumerate(text.split(" ")):
        if word_index:
            for y in range(height):
                rows[y] += WORD_GAP
        for char_index, ch in enumerate(word):
            if char_index:
                for y in range(height):
                    rows[y] += LETTER_GAP
            glyph = font[ch]
            for y in range(height):
                rows[y] += glyph[y]
    return [row.rstrip() for row in rows]


def _paint_width(text: str, font: dict) -> int:
    return max(len(row) for row in _paint(text, font))


def _known(text: str, font: dict) -> bool:
    return all(ch == " " or ch in font for ch in text)


def question_tier(name: str, max_cols: int = CONTENT_MAX) -> str:
    """5, 4, wrap, or plain.

    5 is one 5-row line. 4 is one 4-row line. wrap is one 4-row line per
    word. plain is lowercase text, used only when a single word is wider
    than the frame at 4 rows.
    """
    text = _banner_text(name)
    if not text:
        return "plain"
    if _known(text, SORA5) and _paint_width(text, SORA5) <= max_cols:
        return "5"
    if _known(text, SORA4) and _paint_width(text, SORA4) <= max_cols:
        return "4"
    words = text.split()
    if words and _known(text, SORA4) and all(_paint_width(word, SORA4) <= max_cols for word in words):
        return "wrap"
    return "plain"


def question_banner(name: str, max_cols: int = CONTENT_MAX) -> list[str]:
    """Lowercase Sora banner for the choice box. Lines are at most max_cols."""
    text = _banner_text(name)
    if not text:
        return [""]
    tier = question_tier(text, max_cols)
    if tier == "5":
        return _paint(text, SORA5)
    if tier == "4":
        return _paint(text, SORA4)
    if tier == "wrap":
        lines: list[str] = []
        for index, word in enumerate(text.split()):
            if index:
                lines.append("")
            lines.extend(_paint(word, SORA4))
        return lines
    return [text]


MAX_COLS = 72


def spaced_caps(text: str) -> str:
    words = text.upper().split()
    parts = []
    for word in words:
        chars: list[str] = []
        for ch in word:
            if ch in "'’" and chars:
                chars[-1] = chars[-1] + ch
            else:
                chars.append(ch)
        parts.append(" ".join(chars))
    return "   ".join(parts)


def _words(name: str) -> list[str]:
    pieces: list[str] = []
    for raw in name.upper().split():
        if "-" not in raw:
            pieces.append(raw)
            continue
        bits = [bit for bit in raw.split("-") if bit]
        for index, bit in enumerate(bits):
            pieces.append(bit + "-" if index < len(bits) - 1 else bit)
    return pieces


def _supported(token: str) -> bool:
    return all(ch in FONT for ch in token)


def _raster(token: str) -> list[str]:
    rows = ["", "", ""]
    for index, ch in enumerate(token):
        if index:
            rows = [row + " " for row in rows]
        glyph = FONT[ch]
        for y in range(3):
            rows[y] += glyph[y]
    return [row.rstrip() for row in rows]


def _width(token: str) -> int:
    return max((len(line) for line in _raster(token)), default=0)


def _fallback(token: str) -> list[str]:
    return ["■ " + spaced_caps(token)]


def render_name(name: str) -> list[str]:
    """Plain banner lines, each at most 72 columns, at most 3 rows per word."""
    words = _words(name)
    if not words:
        return _fallback(name)
    joined = " ".join(words)
    if _supported(joined) and _width(joined) <= MAX_COLS:
        return _raster(joined)
    lines: list[str] = []
    for index, word in enumerate(words):
        if index:
            lines.append(SPACER)
        if not _supported(word) or _width(word) > MAX_COLS:
            lines.extend(_fallback(word))
        else:
            lines.extend(_raster(word))
    return lines or _fallback(name)
