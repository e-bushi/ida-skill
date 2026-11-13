"""Compact banners for an idk reveal.

Each letter is 3 columns and 3 rows, drawn with █ ▀ ▄. A plain space
separates glyphs. There is no shade character. 18 letters is about 72
columns. A name that fits is one line. Otherwise each word is its own
line. A word that still does not fit, or that uses a character this
font does not have, falls back to spaced caps with a ■.

The idk card still uses this banner. The choice question does not.
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
