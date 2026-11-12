"""Compact banners for an idk reveal.

Each letter is 3 columns and 3 rows, drawn with █ ▀ ▄. A plain space
separates glyphs. There is no shade character. 18 letters is about 72
columns. A name that fits is one line. Otherwise each word is its own
line. A word that still does not fit, or that uses a character this
font does not have, falls back to spaced caps with a ■.

The choice-box banner never wraps. A short name uses this 3-row font.
A longer name uses a 2-row font. A name that still does not fit is one
row of uppercase.
"""

from __future__ import annotations

from common import SPACER

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

# Two rows. Each glyph ends with a space so letters stay apart.
# Wider letters are the ones a 2-column body cannot draw.
SMALL = {
    "A": ["▀█ ", "█▀ "],
    "B": ["██ ", "██ "],
    "C": ["▄▀ ", "▀  "],
    "D": ["█▄ ", "█▀ "],
    "E": ["█▀ ", "█▄ "],
    "F": ["█▀ ", "█  "],
    "G": ["▄▀ ", "▀█ "],
    "H": ["█▀█ ", "█ █ "],
    "I": ["█ ", "█ "],
    "J": ["▀█ ", "▄▀ "],
    "K": ["█▀ ", "█▀ "],
    "L": ["█  ", "█▄ "],
    "M": ["█▄█ ", "█ █ "],
    "N": ["█▀█ ", "█ █ "],
    "O": ["▄▀ ", "▀▄ "],
    "P": ["██ ", "█  "],
    "Q": ["▄▀ ", "▀█ "],
    "R": ["█▀ ", "▀█ "],
    "S": ["▀▄ ", "▄▀ "],
    "T": ["▀▀ ", " █ "],
    "U": ["█▄ ", "▀▄ "],
    "V": ["█▄ ", "▀  "],
    "W": ["█▄█ ", "▀▄▀ "],
    "X": ["█▀ ", "▀█ "],
    "Y": ["█▀ ", "▄  "],
    "Z": ["▀█ ", "█▄ "],
    "0": ["▄▀ ", "▀▄ "],
    "1": ["▀█ ", "▄█ "],
    "2": ["▀▀ ", "█▄ "],
    "3": ["▀█ ", "▄▀ "],
    "4": ["█▀ ", "▀█ "],
    "5": ["█▀ ", "▄▀ "],
    "6": ["█▄ ", "▀▄ "],
    "7": ["▀▀ ", " █ "],
    "8": ["▄▀ ", "▄▀ "],
    "9": ["▄▀ ", "▀█ "],
    " ": [" ", " "],
    "'": ["▀ ", "  "],
    "-": ["  ", "▀ "],
    ".": ["  ", "▄ "],
    "/": [" █ ", "█  "],
    ",": ["  ", "▄ "],
    "?": ["▀█ ", " ▄ "],
}

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


def _plain_name(name: str) -> str:
    text = str(name).replace("\u2013", "-").replace("\u2014", "-").replace("\u2019", "'")
    return " ".join(text.upper().split())


def _fits(lines: list[str], max_cols: int) -> bool:
    return bool(lines) and max(len(line) for line in lines) <= max_cols


def _tier1_lines(text: str, max_cols: int) -> list[str] | None:
    if not text or not _supported(text):
        return None
    lines = _raster(text)
    if _fits(lines, max_cols):
        return lines
    return None


def _raster_small(token: str) -> list[str]:
    rows = ["", ""]
    for ch in token:
        glyph = SMALL[ch]
        rows[0] += glyph[0]
        rows[1] += glyph[1]
    return [row.rstrip() for row in rows]


def _tier2_lines(text: str, max_cols: int) -> list[str] | None:
    if not text or any(ch not in SMALL for ch in text):
        return None
    lines = _raster_small(text)
    if _fits(lines, max_cols):
        return lines
    return None


def _tier3_lines(text: str, max_cols: int) -> list[str]:
    upper = text.upper()
    spaced = spaced_caps(text)
    if len(spaced) <= max_cols:
        return [spaced]
    return [upper]


def question_tier(name: str, max_cols: int = 60) -> int:
    """1 is the 3-row font, 2 is the 2-row font, 3 is one uppercase row."""
    text = _plain_name(name)
    if _tier1_lines(text, max_cols) is not None:
        return 1
    if _tier2_lines(text, max_cols) is not None:
        return 2
    return 3


def question_banner(name: str, max_cols: int = 60) -> list[str]:
    """One banner line for the choice box, at most 3 rows tall.

    The whole name stays on that line. Tier 1 is the 3-row block font
    when it fits in max_cols. Tier 2 is the 2-row font. Tier 3 is one
    row of spaced caps when that fits, otherwise plain uppercase.
    """
    text = _plain_name(name)
    if not text:
        return [""]
    tier1 = _tier1_lines(text, max_cols)
    if tier1 is not None:
        return tier1
    tier2 = _tier2_lines(text, max_cols)
    if tier2 is not None:
        return tier2
    return _tier3_lines(text, max_cols)


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
