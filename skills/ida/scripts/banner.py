"""5x5 block banners for an idk reveal.

Fill is █. A drop shadow ░ sits one column right and one row down,
and only where that cell is not already fill. Letters are 5 wide with
a 1-column gap, so a line of n letters is 6n columns including the
last shadow. 12 letters is 72 columns. Longer words, and words with a
character this font does not have, fall back to spaced caps with a ■.
"""

from __future__ import annotations

# Rows are top to bottom. 1 is fill. a-q are Bill's. r-z, digits, and
# marks follow the same 5-wide grid.
FONT = {
    "A": ["01110", "10001", "11111", "10001", "10001"],
    "B": ["11110", "10001", "11110", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "11110", "10000", "11111"],
    "F": ["11111", "10000", "11110", "10000", "10000"],
    "G": ["01111", "10000", "10011", "10001", "01111"],
    "H": ["10001", "10001", "11111", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00001", "00001", "10001", "01110"],
    "K": ["10001", "10010", "11100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001"],
    "O": ["01110", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "11110", "10000", "10000"],
    "Q": ["01110", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "11110", "10010", "10001"],
    "S": ["01111", "10000", "01110", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10101", "11011", "10001"],
    "X": ["10001", "01010", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100"],
    "Z": ["11111", "00010", "00100", "01000", "11111"],
    "0": ["01110", "10001", "10001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00110", "01000", "11111"],
    "3": ["11110", "00001", "01110", "00001", "11110"],
    "4": ["10010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "11110"],
    "6": ["01110", "10000", "11110", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000"],
    "8": ["01110", "10001", "01110", "10001", "01110"],
    "9": ["01110", "10001", "01111", "00001", "01110"],
    " ": ["00000", "00000", "00000", "00000", "00000"],
    "'": ["00100", "00100", "00000", "00000", "00000"],
    "-": ["00000", "00000", "01110", "00000", "00000"],
    ".": ["00000", "00000", "00000", "01100", "01100"],
}

MAX_GLYPHS = 12
MAX_COLS = 72
PITCH = 6


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
    glyphs = list(token)
    width = PITCH * len(glyphs)
    height = 6
    fill = [[False] * width for _ in range(height)]
    shade = [[False] * width for _ in range(height)]
    for index, ch in enumerate(glyphs):
        origin = index * PITCH
        for y, row in enumerate(FONT[ch]):
            for x, bit in enumerate(row):
                if bit != "1":
                    continue
                fill[y][origin + x] = True
                sy, sx = y + 1, origin + x + 1
                if sy < height and sx < width:
                    shade[sy][sx] = True
    lines = []
    for y in range(height):
        chars = []
        for x in range(width):
            if fill[y][x]:
                chars.append("█")
            elif shade[y][x]:
                chars.append("░")
            else:
                chars.append(" ")
        lines.append("".join(chars).rstrip())
    return lines


def _fallback(token: str) -> list[str]:
    return ["■ " + spaced_caps(token)]


def render_name(name: str) -> list[str]:
    """Plain banner lines, each at most 72 columns."""
    words = _words(name)
    glyphs = list(" ".join(words))
    one_line = (
        bool(glyphs)
        and _supported("".join(glyphs))
        and len(glyphs) <= MAX_GLYPHS
        and PITCH * len(glyphs) <= MAX_COLS
    )
    if one_line:
        return _raster("".join(glyphs))
    lines: list[str] = []
    for index, word in enumerate(words):
        if index:
            lines.append("")
        if len(word) > MAX_GLYPHS or not _supported(word):
            lines.extend(_fallback(word))
        else:
            lines.extend(_raster(word))
    return lines or _fallback(name)
