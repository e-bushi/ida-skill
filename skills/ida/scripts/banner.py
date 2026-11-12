"""Compact banners for an idk reveal.

Each letter is 3 columns and 3 rows, drawn with █ ▀ ▄ so the strokes
stay crisp. A ░ sits one column to the right of a stroke, only in an
empty cell, so the banner stays 3 rows tall. A letter plus that shadow
is 4 columns. 18 letters is 72 columns. A name that fits is one line.
Otherwise each word is its own line. A word that still does not fit,
or that uses a character this font does not have, falls back to spaced
caps with a ■.
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
}

MAX_COLS = 72
FILL = set("█▀▄")


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
    rows = [row + " " for row in rows]
    painted = []
    for row in rows:
        chars = list(row)
        for x, ch in enumerate(chars[:-1]):
            if ch in FILL and chars[x + 1] == " ":
                chars[x + 1] = "░"
        painted.append("".join(chars).rstrip())
    return painted


def _width(token: str) -> int:
    return max((len(line) for line in _raster(token)), default=0)


def _fallback(token: str) -> list[str]:
    return ["■ " + spaced_caps(token)]


def question_banner(name: str, max_cols: int = 62) -> list[str]:
    """Banner rows for the choice box. Each line is at most max_cols.

    Words share a 3-row line while they fit. The next word starts another
    3-row line. A word this font cannot draw, or that is wider than
    max_cols, is printed in spaced caps.
    """
    words = _words(name.replace(",", " "))
    if not words:
        return _wrap_caps(name, max_cols)
    groups: list[list[str]] = []
    current: list[str] = []
    for word in words:
        drawable = _supported(word) and _width(word) <= max_cols
        if not drawable:
            if current:
                groups.append(current)
                current = []
            groups.append([word])
            continue
        trial = current + [word]
        if current and _width(" ".join(trial)) <= max_cols:
            current = trial
        else:
            if current:
                groups.append(current)
            current = [word]
    if current:
        groups.append(current)
    lines: list[str] = []
    for group in groups:
        word = group[0]
        if len(group) == 1 and (not _supported(word) or _width(word) > max_cols):
            lines.extend(_wrap_caps(word, max_cols))
            continue
        lines.extend(_raster(" ".join(group)))
    return lines or _wrap_caps(name, max_cols)


def _wrap_caps(text: str, max_cols: int) -> list[str]:
    raw = spaced_caps(text)
    if len(raw) <= max_cols:
        return [raw]
    lines: list[str] = []
    current = ""
    for word in raw.split(" "):
        if not word:
            continue
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_cols:
            current = current + " " + word
        else:
            lines.append(current)
            current = word
        while len(current) > max_cols:
            lines.append(current[:max_cols])
            current = current[max_cols:]
    if current:
        lines.append(current)
    return lines or [raw[:max_cols]]


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
