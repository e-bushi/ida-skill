"""Compact banners for an idk reveal.

Each letter is 3 columns and 3 rows, drawn with █ ▀ ▄. A plain space
separates glyphs. There is no shade character. 18 letters is about 72
columns. A name that fits is one line. Otherwise each word is its own
line. A word that still does not fit, or that uses a character this
font does not have, falls back to spaced caps with a ■.

The choice-box banner never wraps. A short name uses a 5-row letterform.
A longer name uses a 4-row letterform. A name that still does not fit
is one row of plain uppercase.
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

def _glyph(*rows: str) -> tuple[str, ...]:
    """Pad one letterform and leave a blank column after it."""
    width = max(len(row) for row in rows)
    return tuple(row.ljust(width) + " " for row in rows)


# Five-row letterforms for short names. Strokes are ASCII, not half blocks.
LARGE = {
    "A": _glyph("  _  ", " / \\ ", "/___\\", "|   |", "|   |"),
    "B": _glyph(" __  ", "|  \\ ", "|__/ ", "|  \\ ", "|__/ "),
    "C": _glyph("  __ ", " /   ", "|    ", "|    ", " \\__ "),
    "D": _glyph(" __  ", "|  \\ ", "|   |", "|   |", "|__/ "),
    "E": _glyph(" ____", "|    ", "|___ ", "|    ", "|____"),
    "F": _glyph(" ____", "|    ", "|___ ", "|    ", "|    "),
    "G": _glyph("  __ ", " /   ", "|  _ ", "|   |", " \\__|"),
    "H": _glyph("|   |", "|   |", "|___|", "|   |", "|   |"),
    "I": _glyph("___", " | ", " | ", " | ", "_|_"),
    "J": _glyph("   _", "   |", "   |", "\\  |", " \\_|"),
    "K": _glyph("|  /", "| / ", "|<  ", "| \\ ", "|  \\"),
    "L": _glyph("|   ", "|   ", "|   ", "|   ", "|___"),
    "M": _glyph("|\\   /|", "| \\ / |", "|  V  |", "|     |", "|     |"),
    "N": _glyph("|\\  |", "| \\ |", "|  \\|", "|   |", "|   |"),
    "O": _glyph("  __ ", " /  \\", "|    |", "|    |", " \\__/"),
    "P": _glyph(" __ ", "|  \\", "|__/", "|   ", "|   "),
    "Q": _glyph("  __ ", " /  \\", "|    |", " \\__/ ", "    \\"),
    "R": _glyph(" __ ", "|  \\", "|__/", "|  \\", "|   \\"),
    "S": _glyph("  __", " /  ", " \\_ ", "   \\", " __/"),
    "T": _glyph("____", " || ", " || ", " || ", " || "),
    "U": _glyph("|   |", "|   |", "|   |", "|   |", " \\_/ "),
    "V": _glyph("|   |", "|   |", "|   |", " \\ / ", "  V  "),
    "W": _glyph("      ", "\\    /", "\\    /", "\\ /\\ /", " V  V "),
    "X": _glyph("\\   /", " \\ / ", "  X  ", " / \\ ", "/   \\"),
    "Y": _glyph("\\   /", " \\ / ", "  |  ", "  |  ", "  |  "),
    "Z": _glyph("____", "   /", "  / ", " /  ", "/___"),
    "0": _glyph(" .-. ", "|  /|", "| / |", "|/  |", " '-' "),
    "1": _glyph(" /|", "  |", "  |", "  |", "_/ "),
    "2": _glyph(" __ ", "/  \\", "  / ", " /  ", "/___"),
    "3": _glyph(" __ ", "   \\", " __/", "   \\", " __/"),
    "4": _glyph("|  |", "|  |", "|__|", "   |", "   |"),
    "5": _glyph(" ___", "|   ", "|__ ", "   \\", " __/"),
    "6": _glyph("  __", " /  ", "|__ ", "|  \\", " \\_/"),
    "7": _glyph("____", "   /", "  / ", " /  ", "/   "),
    "8": _glyph(" __ ", "/  \\", " \\_/ ", "/  \\", " \\__/"),
    "9": _glyph(" __ ", "/  \\", " \\_|", "   |", " __/"),
    "&": _glyph(" __ ", "(  )", " \\_/ ", "/  \\", "\\__/\\"),
    "-": _glyph("    ", "    ", " __ ", "    ", "    "),
    ".": _glyph("   ", "   ", "   ", "   ", " . "),
    "'": _glyph(" ' ", "   ", "   ", "   ", "   "),
    "/": _glyph("   /", "  / ", " /  ", "/   ", "    "),
    ",": _glyph("   ", "   ", "   ", " , ", ",  "),
    "?": _glyph(" __ ", "/  \\", "  / ", " /  ", " .  "),
    " ": _glyph(" ", " ", " ", " ", " "),
}

# Four-row letterforms. Narrower than LARGE, still a full letter.
MEDIUM = {
    "A": _glyph(" A ", "/ \\", "---", "| |"),
    "B": _glyph("__", "| \\", "|_|", "|_|"),
    "C": _glyph(" __", "/  ", "|  ", "\\__"),
    "D": _glyph("__", "| \\", "| |", "|_/"),
    "E": _glyph("___", "|  ", "|_ ", "|__"),
    "F": _glyph("___", "|  ", "|_ ", "|  "),
    "G": _glyph(" __", "/  ", "| _", "\\_|"),
    "H": _glyph("| |", "|_|", "| |", "| |"),
    "I": _glyph("_", "|", "|", "|"),
    "J": _glyph("  |", "  |", "\\ |", "\\_|"),
    "K": _glyph("| /", "|/ ", "|\\ ", "| \\"),
    "L": _glyph("|  ", "|  ", "|  ", "|__"),
    "M": _glyph("|\\ /|", "| V |", "|   |", "|   |"),
    "N": _glyph("|\\ |", "| \\|", "|  |", "|  |"),
    "O": _glyph(" __", "/  \\", "|  |", "\\__/"),
    "P": _glyph("__", "| \\", "|_|", "|  "),
    "Q": _glyph(" __", "/  \\", "\\__/", "   \\"),
    "R": _glyph("__", "| \\", "|_|", "| \\"),
    "S": _glyph(" __", "/  ", "\\_ ", "__/"),
    "T": _glyph("___", " | ", " | ", " | "),
    "U": _glyph("| |", "| |", "| |", "\\_/"),
    "V": _glyph("| |", "| |", "\\ /", " V "),
    "W": _glyph("\\ \\ /", " \\ V /", "  V V ", "      "),
    "X": _glyph("\\ /", " X ", "/ \\", "/ \\"),
    "Y": _glyph("\\ /", " V ", " | ", " | "),
    "Z": _glyph("___", "  /", " / ", "/__"),
    "0": _glyph(" _ ", "/ /", "|/|", "'-'"),
    "1": _glyph("/|", " |", " |", "_|"),
    "2": _glyph("__", "  \\", " / ", "/__"),
    "3": _glyph("__", "  \\", "__/", "__/"),
    "4": _glyph("| |", "|_|", "  |", "  |"),
    "5": _glyph("___", "|_ ", "  \\", "__/"),
    "6": _glyph(" __", "/  ", "|_ ", "\\_/"),
    "7": _glyph("___", "  /", " / ", "/  "),
    "8": _glyph(" __", "/  \\", "\\__/", "\\__/"),
    "9": _glyph("__", "\\/", "_|", "__/"),
    "&": _glyph(" _", "(_)", "/ \\", "\\_\\"),
    "-": _glyph("   ", "___", "   ", "   "),
    ".": _glyph("  ", "  ", "  ", " ."),
    "'": _glyph(" '", "  ", "  ", "  "),
    "/": _glyph("  /", " / ", "/  ", "   "),
    ",": _glyph("  ", "  ", "  ", " ,"),
    "?": _glyph("__", "  \\", " / ", " . "),
    " ": _glyph(" ", " ", " ", " "),
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


def _raster_font(token: str, font: dict) -> list[str]:
    height = len(next(iter(font.values())))
    rows = [""] * height
    for ch in token:
        glyph = font[ch]
        for y in range(height):
            rows[y] += glyph[y]
    return [row.rstrip() for row in rows]


def _tier_lines(text: str, font: dict, max_cols: int) -> list[str] | None:
    if not text or any(ch not in font for ch in text):
        return None
    lines = _raster_font(text, font)
    if _fits(lines, max_cols):
        return lines
    return None


def question_tier(name: str, max_cols: int = 60) -> int:
    """1 is the 5-row font, 2 is the 4-row font, 3 is plain uppercase."""
    text = _plain_name(name)
    if _tier_lines(text, LARGE, max_cols) is not None:
        return 1
    if _tier_lines(text, MEDIUM, max_cols) is not None:
        return 2
    return 3


def question_banner(name: str, max_cols: int = 60) -> list[str]:
    """One banner line for the choice box.

    The whole name stays on that line. Tier 1 is the 5-row letterform
    when it fits in max_cols. Tier 2 is the 4-row letterform. Tier 3 is
    one row of plain uppercase.
    """
    text = _plain_name(name)
    if not text:
        return [""]
    large = _tier_lines(text, LARGE, max_cols)
    if large is not None:
        return large
    medium = _tier_lines(text, MEDIUM, max_cols)
    if medium is not None:
        return medium
    return [text.upper()]


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
